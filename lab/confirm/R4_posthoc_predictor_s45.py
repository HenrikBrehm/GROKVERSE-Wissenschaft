"""R4 post hoc (session 45, EXPLORATION / calibration on seen R4 runs; no training). Program C: build a predictor of WHICH five
frequencies a network ends up using, from quantities known before training, fit it here, freeze it, and test it later on
untouched runs (EXP-100 random-split runs; see mask_prediction_s45.py).

Predictor score per frequency k (k = 1..56):  S_k(a) = a * pct_mask(k) + (1 - a) * pct_init(k),
  pct_mask = percentile of M0c(k) of the run's own split (lab/confirm/R4_posthoc_mask_s45.py), pct_init = percentile of the
  run's W_E power at step 0 (initialization). Predicted set = top 5 of S. Measure: overlap |predicted top 5 & learned top 5| / 5,
  learned = W_E power at step t. Chance overlap 5/56 * 5 / 5 = 0.089.
Fit: a on the grid 0, 0.1, ..., 1, maximizing the mean overlap over all 240 R4 runs at t = 2000; also reported at t = 8000 and the
  overlap of mask only (a = 1) and init only (a = 0). The fitted a is frozen in the output json with the git commit and must not
  be changed after the test data are seen.
  python lab/confirm/R4_posthoc_predictor_s45.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "confirm"))
from R4_posthoc_mask_s45 import SPL, UNITS, m0c, spectrum  # noqa: E402

GRID = np.round(np.arange(0, 1.01, 0.1), 2)


def pct(x: np.ndarray) -> np.ndarray:
    return np.argsort(np.argsort(x)) / (len(x) - 1)


def overlap(score: np.ndarray, learned: np.ndarray) -> float:
    return len(set(np.argsort(-score)[:5]) & set(np.argsort(-learned)[:5])) / 5


def main() -> None:
    runs = []
    for u in range(UNITS):
        pm = {s: pct(m0c(np.load(SPL / f"r4_u{u}_s{s}.npy"))) for s in (0, 1)}
        for init in (2600 + 2 * u, 2601 + 2 * u):
            for s in (0, 1):
                runs.append({"pm": pm[s], "pi": pct(spectrum(u, init, s, 0)), 2000: spectrum(u, init, s, 2000),
                             8000: spectrum(u, init, s, 8000)})
    out: dict = {"note": "calibration on seen R4 runs (exploration); a is frozen for the later out-of-sample test",
                 "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=LAB.parent, capture_output=True, text=True).stdout.strip(),
                 "n_runs": len(runs), "chance_overlap": 5 / 56}
    for t in (2000, 8000):
        curve = {float(a): float(np.mean([overlap(a * r["pm"] + (1 - a) * r["pi"], r[t]) for r in runs])) for a in GRID}
        out[f"overlap_t{t}"] = curve
    best = max(out["overlap_t2000"], key=out["overlap_t2000"].get)
    out["a_frozen"] = best
    out["summary"] = {f"t{t}": {"mask_only": out[f"overlap_t{t}"][1.0], "init_only": out[f"overlap_t{t}"][0.0],
                                "combined_at_a_frozen": out[f"overlap_t{t}"][best]} for t in (2000, 8000)}
    # session 45, after the independent recomputation (numbers were quoted from it): unit bootstrap of mask-only minus init-only
    # at t = 2000 and the placebo with another unit's split (u + 1 mod 60, same s)
    mo = np.array([overlap(r["pm"], r[2000]) for r in runs]).reshape(UNITS, 4).mean(1)
    io = np.array([overlap(r["pi"], r[2000]) for r in runs]).reshape(UNITS, 4).mean(1)
    rng = np.random.default_rng(1)
    bi = rng.integers(0, UNITS, (20000, UNITS))
    d = mo - io
    out["mask_minus_init_t2000"] = {"mean": float(d.mean()), "ci95": [float(np.quantile(d[bi].mean(1), 0.025)),
                                                                     float(np.quantile(d[bi].mean(1), 0.975))]}
    pl = []
    for i, r in enumerate(runs):
        u, s = i // 4, i % 2
        other = pct(m0c(np.load(SPL / f"r4_u{(u + 1) % UNITS}_s{s}.npy")))
        pl.append(overlap(other, r[2000]))
    out["placebo_other_unit_mask_t2000"] = float(np.mean(pl))
    (LAB / "confirm/R4_posthoc_predictor_s45.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if not k.startswith("overlap_")}, indent=1))
    print("curve t2000:", out["overlap_t2000"])


if __name__ == "__main__":
    main()
