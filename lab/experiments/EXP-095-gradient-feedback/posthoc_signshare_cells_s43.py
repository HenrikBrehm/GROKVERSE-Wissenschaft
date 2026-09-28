"""EXP-095 post hoc (session 43, descriptive only, seen data, numpy on stored snapshots): how sign-quantised is the W_E
displacement at the switch in EVERY cell? Follow-up to posthoc_sign_s43.py, which covered n24/g24 only. Question: does the
sign-step confound of g24 also touch the primary contrast e8 (g8) and the large-step cell c8b?
Per cell: D = W_E(t) - (1 - c lr wd)^t W_E(0); unit = c lr sum_j (1 - c lr wd)^j (j < t); q = share of entries with |D| within
10 % of the unit (all steps full-size and same sign), a = mean |D| / unit. No readings (descriptive); writes the json below.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as X  # noqa: E402  (EXP-095 loader)

LR, WD = 1e-3, 1.0


def main() -> None:
    out = {}
    for cell, (c, t, _psb, _k) in X.D.CELLS.items():
        unit = c * LR * sum((1 - c * LR * WD) ** j for j in range(t))
        decay = (1 - c * LR * WD) ** t
        q, a = [], []
        for s in X.D.SEEDS:
            for kind in ("AB", "BA"):
                r = X.load(s, kind, cell)
                if isinstance(r, str):
                    raise SystemExit(r)
                D = r[1].astype(np.float64) - decay * r[2].astype(np.float64)
                q.append(float(np.mean(np.abs(np.abs(D) - unit) <= 0.1 * unit)))
                a.append(float(np.mean(np.abs(D)) / unit))
        out[cell] = {"unit": unit, "q_full_sign_share": float(np.mean(q)), "mean_abs_over_unit": float(np.mean(a)), "n": len(q)}
    (HERE / "posthoc_signshare_cells_s43.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
