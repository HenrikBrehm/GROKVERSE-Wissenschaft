"""R4 post hoc (session 45; EXPLORATION on the stored R4 runs, no training). Written before computing.

Question (simulated review of the short paper, item 7): does an ordinary random split's own mask spectrum predict which
frequencies the network learns, beyond the initialization? EXP-015 found an association but with split and init drawn from
the same seed. R4 crosses two inits with two independent uniform 30 % splits per unit (60 units, 240 runs), so the split's
contribution can be separated: for every run (init i, split s) compare
    rho_own   = Spearman over k = 1..56 between M(s) and the run's W_E power spectrum at step t,
    rho_other = the same with the OTHER split s' of the unit (same init, same run),
contrast c = rho_own - rho_other; unit value = mean of its 4 runs. M = M0 (make_split.mask_power) and M0c (centred coherent
mask spectrum, P1_posthoc_m0_strength.py). Steps t = 2000 (primary) and 8000.
Reading fixed before computing: "the random split's mask spectrum predicts its learned frequencies beyond the init" if the
95 % bootstrap CI (units, 20 000 draws) of the mean contrast at t = 2000 lies above 0 for M0c; also reported: M0, t = 8000,
units with contrast > 0, mean rho_own. The R4 units were seen for the registered similarity measure (Delta_split), not for
this association; exploration, not a confirmation.
  python lab/confirm/R4_posthoc_mask_s45.py
  python lab/confirm/R4_posthoc_mask_s45.py --top5     # secondary (after main)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
from make_split import mask_power  # noqa: E402

P, K, UNITS, STEPS = 113, 56, 60, (2000, 8000)
RAW, SPL = LAB / "confirm/r4_raw", LAB / "confirm/r4_splits"


def m0c(idx: np.ndarray) -> np.ndarray:
    m = np.zeros((P, P))
    m[idx // P, idx % P] = 1
    t, c = np.arange(P)[:, None], np.arange(P)[None, :]
    X = np.fft.fft(m[t, (c - t) % P] + m[(c - t) % P, t], axis=0)
    X = X - X.mean(1, keepdims=True)
    s = (np.abs(X) ** 2).sum(1)
    return s[1:K + 1] + s[P - K:][::-1]


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def spectrum(u: int, init: int, s: int, step: int) -> np.ndarray:
    d = RAW / f"EXP-016_baseline_seed{init}_thr1_r4_u{u}_s{s}_devcuda"
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    assert r["status"] == "completed", d
    steps = list(np.load(d / "spectra_steps.npy"))
    v = np.load(d / "spectra.npy")[steps.index(step)]
    assert np.isfinite(v).all()
    return v


def main() -> None:
    masks = {name: {} for name in ("M0", "M0c")}
    for u in range(UNITS):
        for s in (0, 1):
            idx = np.load(SPL / f"r4_u{u}_s{s}.npy")
            masks["M0"][u, s], masks["M0c"][u, s] = mask_power(idx, "add", P), m0c(idx)
    rng = np.random.default_rng(45)
    boot = rng.integers(0, UNITS, (20000, UNITS))
    out = {"note": "post hoc exploration on stored R4 runs (units seen for Delta_split only)"}
    for name in ("M0c", "M0"):
        for step in STEPS:
            unit_c, unit_own = [], []
            for u in range(UNITS):
                cs, owns = [], []
                for init in (2600 + 2 * u, 2601 + 2 * u):
                    for s in (0, 1):
                        pw = spectrum(u, init, s, step)
                        own, other = spearman(masks[name][u, s], pw), spearman(masks[name][u, 1 - s], pw)
                        cs.append(own - other)
                        owns.append(own)
                unit_c.append(np.mean(cs))
                unit_own.append(np.mean(owns))
            c = np.array(unit_c)
            bm = c[boot].mean(1)
            out[f"{name}_t{step}"] = {"mean_contrast": float(c.mean()), "ci95": [float(np.quantile(bm, 0.025)), float(np.quantile(bm, 0.975))],
                                      "units_positive": int((c > 0).sum()), "mean_rho_own": float(np.mean(unit_own))}
    prim = out["M0c_t2000"]
    out["reading"] = ("the random split's mask spectrum predicts its learned frequencies beyond the init" if prim["ci95"][0] > 0
                      else "no evidence beyond the init at step 2000")
    (LAB / "confirm/R4_posthoc_mask_s45.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__" and "--top5" not in sys.argv:
    main()


# Secondary, fixed after the primary result and BEFORE computing it (session 45): the Spearman over all 56 frequencies may be
# carried by the bulk of weak frequencies. Descriptive check on the frequencies the network actually uses: mean percentile
# (0 = lowest, 1 = highest) of the run's top-5 W_E frequencies in M0c of the own vs the other split, unit means, same bootstrap.
# Chance: 0.5 for both. Reading: "the top frequencies follow the own mask" if the CI of own - other lies above 0.
def top5_percentile() -> dict:
    res = {}
    rng = np.random.default_rng(46)
    boot = rng.integers(0, UNITS, (20000, UNITS))
    for step in STEPS:
        diff, own_m = [], []
        for u in range(UNITS):
            ids = [np.load(SPL / f"r4_u{u}_s{s}.npy") for s in (0, 1)]
            pct = [np.argsort(np.argsort(m0c(i))) / (K - 1) for i in ids]
            d, o = [], []
            for init in (2600 + 2 * u, 2601 + 2 * u):
                for s in (0, 1):
                    top = np.argsort(-spectrum(u, init, s, step))[:5]
                    d.append(pct[s][top].mean() - pct[1 - s][top].mean())
                    o.append(pct[s][top].mean())
            diff.append(np.mean(d))
            own_m.append(np.mean(o))
        dd = np.array(diff)
        res[f"top5_pct_t{step}"] = {"mean_own": float(np.mean(own_m)), "mean_own_minus_other": float(dd.mean()),
                                    "ci95": [float(np.quantile(dd[boot].mean(1), 0.025)), float(np.quantile(dd[boot].mean(1), 0.975))],
                                    "units_positive": int((dd > 0).sum())}
    return res


if __name__ == "__main__" and "--top5" in sys.argv:
    r = top5_percentile()
    p = LAB / "confirm/R4_posthoc_mask_s45.json"
    out = json.loads(p.read_text(encoding="utf-8"))
    out["secondary_top5"] = r
    p.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(r, indent=1))
