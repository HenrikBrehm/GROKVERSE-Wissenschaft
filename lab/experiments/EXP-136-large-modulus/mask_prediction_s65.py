"""EXP-136, first-order prediction fixed BEFORE any block run (session 65, 2026-10-01, ~02:05 Berlin).
Mask analogue of the primary measure: Delta_mask = log[M_F(F)/M_F(G)] + log[M_G(G)/M_G(F)], with M = the EXP-015 mask power
of the train split (make_split.mask_power) instead of the W_E group power. Pure numpy, no training.
Prediction (descriptive check after the block, not a verdict): (1) Delta_mask is lower in 'lo' than in 'hi' for each p;
(2) across the 12 seed-cells the Spearman correlation of Delta_mask with Delta_pow(2000) is positive.
  python lab/experiments/EXP-136-large-modulus/mask_prediction_s65.py   -> mask_prediction_s65.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_jobs as mj  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp136_analyze", HERE / "analyze.py")   # by path: EXP-043 also has analyze.py
_an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_an)
delta_pow = _an.delta_pow


def main() -> None:
    rows = []
    for p in mj.PS:
        for fr, frac in mj.fracs(p).items():
            for s in mj.SEEDS:
                (F, iF, mF), (G, iG, mG) = mj.build(p, frac, s, "F"), mj.build(p, frac, s, "G")
                assert np.array_equal(iF, np.load(HERE / "splits" / f"{mj.stem(p, fr, s, 'F')}.npy"))
                rows.append({"p": p, "fraction": fr, "seed": s, "delta_mask": delta_pow(mF, mG, F, G)})
    (HERE / "mask_prediction_s65.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    for r in rows:
        print(r["p"], r["fraction"], r["seed"], round(r["delta_mask"], 3))


if __name__ == "__main__":
    main()
