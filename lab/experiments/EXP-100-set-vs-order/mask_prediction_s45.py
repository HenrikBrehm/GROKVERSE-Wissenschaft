"""EXP-100 add-on (session 45, written BEFORE any EXP-100 run; exploration, no GPU cost): an out-of-sample test of the R4 post hoc
finding (lab/confirm/R4_posthoc_mask_s45.py: on uniform random splits the network's top-5 W_E frequencies sit on average at the
78th percentile of its own split's coherent mask spectrum M0c, full batch, add 113).

Data: the feasibility runs of EXP-100 (raw_feas; random split R of seeds 3700-3702; B = 256, 64, 16; order iid or stride;
30 000 steps, W_E snapshot at the final step, read exactly like feas_read.py). These splits and seeds are untouched.
Measure per run: mean percentile (rank / 55, 0 = lowest) of the run's top-5 W_E frequencies (group power, k = 1..56) in M0c of its
own split R; chance 0.5. Also the share of those top-5 that lie in the stride-order set O = {11, 12, 22, 23, 34, 45}.
Predictions fixed here, before the runs:
  P-iid     i.i.d. arms (9 runs): mean percentile >= 0.65 in every batch size's mean (3 runs each) -> "the mask prediction transfers
            to minibatch training"; mean over all 9 <= 0.55 -> "does not transfer"; else "unclear".
  P-order   descriptive, compared with feas_read.py's order effect: at a batch size where the order acts, the stride runs' mean
            percentile is lower than the i.i.d. runs' (the order pulls the choice away from the set's mask).
3 runs per cell: an exploration; the reading only says whether the R4 pattern appears at all under minibatch training.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-100-set-vs-order/mask_prediction_s45.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(LAB / "confirm"))
from feas_read import O, P, SEEDS, end_power  # noqa: E402
from R4_posthoc_mask_s45 import m0c  # noqa: E402


def percentile_top5(pw: np.ndarray, mask_spec: np.ndarray) -> tuple[float, float]:
    pct = np.argsort(np.argsort(mask_spec)) / (len(mask_spec) - 1)
    top = np.argsort(-pw)[:5]
    return float(pct[top].mean()), float(np.mean([k + 1 in O for k in top]))


def main() -> None:
    out: dict = {"note": "exploration; predictions fixed in the docstring before any EXP-100 run", "cells": {}}
    iid_means = []
    for B in (256, 64, 16):
        for stride in (False, True):
            rows = []
            for s in SEEDS:
                pw = end_power(s, B, stride)
                if isinstance(pw, str):
                    rows.append({"seed": s, "status": pw})
                    continue
                spec = m0c(np.load(HERE / f"splits/seed{s}_R.npy"))
                pctl, o_share = percentile_top5(pw, spec)
                rows.append({"seed": s, "status": "ok", "top5_percentile": pctl, "top5_in_O": o_share})
            ok = [r["top5_percentile"] for r in rows if r["status"] == "ok"]
            cell = {"rows": rows, "mean_percentile": float(np.mean(ok)) if len(ok) == len(SEEDS) else None}
            out["cells"][f"B{B}_{'stride' if stride else 'iid'}"] = cell
            if not stride:
                iid_means.append(cell["mean_percentile"])
    if any(m is None for m in iid_means):
        out["P_iid"] = "not evaluable (missing or broken runs)"
    else:
        allm = float(np.mean(iid_means))
        out["P_iid"] = ("transfers" if all(m >= 0.65 for m in iid_means) else "does not transfer" if allm <= 0.55 else "unclear")
        out["iid_mean_all"] = allm
    (HERE / "mask_prediction_s45.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
