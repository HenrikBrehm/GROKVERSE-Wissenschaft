"""EXP-094 (pilot, exploration): large steps at fixed Lambda with Adam's beta windows matched in Lambda. Definition, predictions and
readings: README.md (fixed before any EXP-094 run). Run under guarded_run.py with the global python.

pi, validity, loading and displacement selectivity exactly as EXP-092 (functions imported from its analyze.py, pointed at this
experiment's design). Paired over seeds, 95 % percentile bootstrap (10 000, rng 94):
  d2 = pi(n24) - pi(c2b), d4 = pi(n24) - pi(c4b), d8 = pi(n24) - pi(c8b)   (deficit left after matching the windows)
  m4 = pi(c4b) - pi(c4)                                                     (what matching buys at c = 4)
Readings:
  'Auswertungen zaehlen'   d4 and d8 CI lower > 0.03 and mean d8 > mean d4
  'Fenster erklaeren'      d4 and d8 CIs inside [-0.05, +0.05]
  else 'teilweise'. Fewer than 10 valid seeds -> 'nicht auswertbar'.
Secondary (descriptive): d2, m4, cell means of pi, selectivity f and norm N at the switch; prospective check of the post hoc
line pi = -1.389 + 9.428 f (EXP-093 posthoc_state_s41.json, fixed before this run): MAE over the five cell means.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(HERE))
import design as D  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp092", LAB / "experiments/EXP-092-momentum-lag-clock/analyze.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)
E.D, E.SPL, E.RAW = D, HERE / "splits", HERE / "raw"

MIN_VALID, N_BOOT, HI, EQ = 10, 10_000, 0.03, 0.05
LINE = (-1.3894541968592156, 9.428517843120291)      # pi on f, EXP-092/093 cell means (post hoc, session 41)


def boot_ci(x: np.ndarray, seed: int = 94) -> list[float]:
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), size=(N_BOOT, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def verdict(pis: dict[str, np.ndarray]) -> dict:
    n = len(pis["n24"])
    if n < MIN_VALID:
        return {"n": n, "verdict": "nicht auswertbar"}
    d = {k: pis["n24"] - pis[c] for k, c in (("d2", "c2b"), ("d4", "c4b"), ("d8", "c8b"))}
    d["m4"] = pis["c4b"] - pis["c4"]
    ci = {k: boot_ci(v) for k, v in d.items()}
    inside = lambda c: -EQ <= c[0] and c[1] <= EQ   # noqa: E731
    if ci["d4"][0] > HI and ci["d8"][0] > HI and d["d8"].mean() > d["d4"].mean():
        v = "Auswertungen zaehlen"
    elif inside(ci["d4"]) and inside(ci["d8"]):
        v = "Fenster erklaeren"
    else:
        v = "teilweise"
    return {"n": n, "mean": {k: float(x.mean()) for k, x in d.items()}, "ci95": ci,
            "pos": {k: int((x > 0).sum()) for k, x in d.items()}, "verdict": v}


def main() -> None:
    rows = [E.seed_row(s) for s in D.SEEDS]
    ok = [r for r in rows if r["valid"]]
    col = lambda k: np.array([r[k] for r in ok])   # noqa: E731
    out: dict = {"n_valid": len(ok)}
    if ok:
        pis = {c: col(f"pi_{c}") for c in D.CELLS}
        out["primary"] = verdict(pis)
        f = {c: float(col(f"fsel_{c}").mean()) for c in D.CELLS}
        pm = {c: float(p.mean()) for c, p in pis.items()}
        out["secondary"] = {"pi_means": pm, "fsel_means": f, "dnorm_means": {c: float(col(f"dnorm_{c}").mean()) for c in D.CELLS},
                            "line_pred": {c: LINE[0] + LINE[1] * f[c] for c in D.CELLS},
                            "line_mae": float(np.mean([abs(LINE[0] + LINE[1] * f[c] - pm[c]) for c in D.CELLS]))}
    else:
        out["primary"] = {"verdict": "nicht auswertbar"}
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert len(D.jobs()) == len(D.SEEDS) * 12 and len(D.smoke()) == 3 and E.D is D
    assert all("--pre-switch-betas 0.2,0.84" in x and "--lr-scale 8" in x for x in D.smoke()[1:])
    for c, (cc, t, psb) in D.CELLS.items():
        assert cc * t == 24
        if psb:
            assert abs((1 - psb[0]) - cc * 0.1) < 1e-12 and abs((1 - psb[1]) - cc * 0.02) < 1e-12
    rng = np.random.default_rng(0)
    nz = lambda: rng.normal(0, 0.02, 16)   # noqa: E731
    base = 0.33 + nz()
    w = lambda d2, d4, d8: {"n24": base, "c4": base - 0.15 + nz(), "c2b": base - d2 + nz(), "c4b": base - d4 + nz(),   # noqa: E731
                            "c8b": base - d8 + nz()}
    assert verdict(w(0.02, 0.08, 0.15))["verdict"] == "Auswertungen zaehlen"
    assert verdict(w(0.0, 0.0, 0.0))["verdict"] == "Fenster erklaeren"
    assert verdict(w(0.0, 0.05, 0.0))["verdict"] == "teilweise"
    assert verdict({k: v[:9] for k, v in w(0, 0, 0).items()})["verdict"] == "nicht auswertbar"
    print("[exp094] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
