"""R4 power report (R4_REGISTRATION_DRAFT.md, session 30, written before the EXP-014 pilot ran). DESCRIPTIVE ONLY: n = 60 units is fixed
in the registration (60 units since the Codex revision); this script changes nothing, it only reports the power R4 is expected to have. UNTESTED.

EXP-014 gives, per disjoint seed pair (a, b), the full 2x2 init x split table: (a, split a) and (b, split b) are the EXP-003d baselines,
(a, split b) and (b, split a) the crossed runs. From the W_E spectra at step 2000: delta_split = S_split - S_none per unit, as in
confirm_r4.py (H1a: Spearman at step 2000). Report: pilot SD of delta_split and the normal-approximation power for a true delta_split
of 0.10 (MDE 0.05, one-sided alpha 0.025, Holm worst case) at n = 60. Only reads stored runs; writes R4_pilot_n.json next to this file.

  python lab/confirm/R4_pilot_n.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
sys.path.insert(0, str(LAB / "tools"))
from confirm_r4 import PAIRS, PRIMARY, spearman  # noqa: E402

MEASURE, PRIMARY_STEP, MDE = PRIMARY["H1a"]         # the pilot runs stop near grokking (~4000 steps): only H1a is estimable

BASE = LAB / "experiments/EXP-003-early-prediction/raw_d/EXP-001_baseline_t2000_m5_seed{s}_thr4"
CROSS = LAB / "experiments/EXP-014-split-vs-init/raw/EXP-014_baseline_t2000_m5_seed{i}_thr4_split{j}"
UNITS = ((10, 11), (12, 13), (14, 15), (16, 17), (18, 19))
TRUE_DELTA, Z_ALPHA, N_UNITS = 0.10, 1.959964, 60


def spectrum_at(d: Path, step: int) -> np.ndarray | None:
    try:
        res = json.loads((d / "result.json").read_text(encoding="utf-8"))
        spec, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
    except (OSError, ValueError):
        return None
    if res.get("status") != "completed" or step not in steps:
        return None
    v = np.asarray(spec[steps.index(step)], dtype=np.float64)
    return v if np.isfinite(v).all() else None


def unit_delta(a: int, b: int) -> float | None:
    runs = {(0, 0): Path(str(BASE).format(s=a)), (1, 1): Path(str(BASE).format(s=b)),
            (0, 1): Path(str(CROSS).format(i=a, j=b)), (1, 0): Path(str(CROSS).format(i=b, j=a))}   # (init index, split index)
    spec = {k: spectrum_at(d, PRIMARY_STEP) for k, d in runs.items()}
    if any(v is None for v in spec.values()):
        return None
    s = {name: float(np.mean([spearman(spec[x], spec[y]) for x, y in pp])) for name, pp in PAIRS.items()}
    return s["split"] - s["none"]


def power(sd: float, n: int) -> float:
    z = (TRUE_DELTA - MDE) / (sd / math.sqrt(n)) - Z_ALPHA
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def main() -> None:
    d = [unit_delta(a, b) for a, b in UNITS]
    if any(x is None for x in d):
        out = {"deltas": d, "sd": None, "power_60": None, "note": "pilot spectrum at step 2000 missing; power not estimable"}
    else:
        sd = float(np.std(d, ddof=1))
        out = {"deltas": d, "sd": sd, "power_60": power(sd, N_UNITS) if sd > 0 else 1.0,
               "note": "descriptive; below 0.8 -> report R4 as underpowered for delta 0.10, n stays 60"}
    (HERE / "R4_pilot_n.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
