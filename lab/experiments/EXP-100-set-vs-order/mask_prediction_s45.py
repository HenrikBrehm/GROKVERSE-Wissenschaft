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
  P-pred    (added session 45 after the R4 calibration lab/confirm/R4_posthoc_predictor_s45.py, still before any EXP-100 run):
            predictor S_k = a * pct_mask(k) + (1 - a) * pct_init(k) with a FROZEN at 0.7 (fit on seen R4 runs: overlap 0.385 at
            full batch, mask only 0.338, init only 0.194, chance 0.089); pct_init from the run's W_E power at step 0 (spectra.npy).
            Overlap of the predicted and the learned top 5 at the final step, i.i.d. runs: mean over all 9 >= 0.25 -> 'predicts
            under minibatch'; <= 0.15 -> 'does not'; else 'unclear'. Also reported per batch size and for the stride runs.
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

A_FROZEN = 0.7   # from lab/confirm/R4_posthoc_predictor_s45.json (session 45); never refit on EXP-100 data


def percentile_top5(pw: np.ndarray, mask_spec: np.ndarray) -> tuple[float, float]:
    pct = np.argsort(np.argsort(mask_spec)) / (len(mask_spec) - 1)
    top = np.argsort(-pw)[:5]
    return float(pct[top].mean()), float(np.mean([k + 1 in O for k in top]))


def init_power(seed: int, B: int, stride: bool) -> np.ndarray | None:
    """W_E power at step 0 from spectra.npy of the same run directory feas_read.end_power uses (None if missing)."""
    cands = [d for d in (HERE / "raw_feas").glob(f"*seed{seed}_*seed{seed}_R*") if f"_bs{B}_" in d.name + "_"
             and ("_ordstride" in d.name) == stride]
    if len(cands) != 1 or not (cands[0] / "spectra.npy").exists():
        return None
    steps = list(np.load(cands[0] / "spectra_steps.npy"))
    return np.load(cands[0] / "spectra.npy")[steps.index(0)] if 0 in steps else None


def pred_overlap(pw: np.ndarray, mask_spec: np.ndarray, init_pw: np.ndarray | None) -> float | None:
    if init_pw is None:
        return None
    pc = lambda x: np.argsort(np.argsort(x)) / (len(x) - 1)   # noqa: E731
    score = A_FROZEN * pc(mask_spec) + (1 - A_FROZEN) * pc(init_pw)
    return len(set(np.argsort(-score)[:5]) & set(np.argsort(-pw)[:5])) / 5


def main() -> None:
    out: dict = {"note": "exploration; predictions fixed in the docstring before any EXP-100 run", "cells": {}}
    iid_means, iid_ov = [], []
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
                ov = pred_overlap(pw, spec, init_power(s, B, stride))
                rows.append({"seed": s, "status": "ok", "top5_percentile": pctl, "top5_in_O": o_share, "pred_overlap": ov})
            ok = [r["top5_percentile"] for r in rows if r["status"] == "ok"]
            ovs = [r["pred_overlap"] for r in rows if r.get("pred_overlap") is not None]
            cell = {"rows": rows, "mean_percentile": float(np.mean(ok)) if len(ok) == len(SEEDS) else None,
                    "mean_pred_overlap": float(np.mean(ovs)) if len(ovs) == len(SEEDS) else None}
            out["cells"][f"B{B}_{'stride' if stride else 'iid'}"] = cell
            if not stride:
                iid_means.append(cell["mean_percentile"])
                iid_ov.append(cell["mean_pred_overlap"])
    if any(m is None for m in iid_means):
        out["P_iid"] = "not evaluable (missing or broken runs)"
    else:
        allm = float(np.mean(iid_means))
        out["P_iid"] = ("transfers" if all(m >= 0.65 for m in iid_means) else "does not transfer" if allm <= 0.55 else "unclear")
        out["iid_mean_all"] = allm
    if any(m is None for m in iid_ov):
        out["P_pred"] = "not evaluable (missing runs or step-0 spectra)"
    else:
        mo = float(np.mean(iid_ov))
        out["P_pred"] = "predicts under minibatch" if mo >= 0.25 else "does not" if mo <= 0.15 else "unclear"
        out["iid_pred_overlap_all"] = mo
    (HERE / "mask_prediction_s45.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
