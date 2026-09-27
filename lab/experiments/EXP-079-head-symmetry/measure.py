#!/usr/bin/env python3
"""EXP-079 (exploration for N36, session 26, UNTESTED): through which channels does position information reach the '=' position in
trained add-113 models? (Revised after a review: exchange-symmetric attention alone does NOT force symmetric outputs.)

For the 80 stored N29 final models (lab/confirm/n29_raw/*/model_final.pt) and all p*p inputs (a, b, '='):
  per head h
    swap_diff   = mean |alpha_a(a,b) - alpha_b(b,a)|                      (attention exchange symmetry; channel 1 = QK)
    share_a     = mean alpha_a / (alpha_a + alpha_b)
    qk_pos      = q_h . K_h (W_pos[0] - W_pos[1]) / sqrt(d_head)           (positional score offset, same for every input; QK channel)
    ov_tag_rel  = |W_O^h W_V^h (W_pos[0]-W_pos[1])| / mean_x |W_O^h W_V^h W_E[x]|   (position tag in the value path; VO channel)
  per model
    logit_swap_rel = mean |logits(a,b) - logits(b,a)| / mean |logits(a,b)|  (functional antisymmetry of the whole network)
The output difference under exchange is sum_h (alpha_a - alpha_b)(a,b) * W_O^h W_V^h (P0 - P1) when attention is exchange-symmetric,
so antisymmetry can come from the QK offset and/or the OV position tag (and W_pos). No training; forward passes of stored models only.

  python lab/tools/guarded_run.py -- python lab/experiments/EXP-079-head-symmetry/measure.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB.parent / "training"))
from grokverse.config import get_config  # noqa: E402
from grokverse.models import build_model  # noqa: E402

P = 113


@torch.no_grad()
def model_stats(run: Path) -> dict:
    cfg = get_config("arch25k", seed=0, steps=1, threads=1)
    model = build_model(cfg)
    model.load_state_dict(torch.load(run / "model_final.pt", map_location="cpu"))
    model.eval()
    a, b = np.meshgrid(np.arange(P), np.arange(P), indexing="ij")
    a, b = a.ravel(), b.ravel()
    x = torch.from_numpy(np.stack([a, b, np.full(len(a), P)], 1)).long()
    swap = b * P + a                                                        # flat index of (b, a)
    att = model.attention_pattern(x)[:, :, 2, :].double().numpy()          # [N, heads, 3]
    al_a, al_b = att[:, :, 0], att[:, :, 1]
    lg = model.logits_last(x)[:, :P].double().numpy()
    Wq, Wk, Wv, Wo = (getattr(model, n).double() for n in ("W_Q", "W_K", "W_V", "W_O"))
    E, pos = model.W_E.double(), model.W_pos.double()
    q = (E[P] + pos[2]) @ Wq                                               # [heads, d_head]: query at '=' (same for every input)
    dP = pos[0] - pos[1]
    qk_pos = ((q * (dP @ Wk)).sum(-1) / math.sqrt(cfg.d_head)).numpy()
    tag = torch.einsum("d,hde,hef->hf", dP, Wv, Wo).norm(dim=-1)
    content = torch.einsum("xd,hde,hef->hxf", E[:P], Wv, Wo).norm(dim=-1).mean(-1)
    return {"swap_diff": np.abs(al_a - al_b[swap]).mean(0).tolist(),
            "share_a": (al_a / np.maximum(al_a + al_b, 1e-12)).mean(0).tolist(),
            "qk_pos": qk_pos.tolist(), "ov_tag_rel": (tag / content).numpy().tolist(),
            "logit_swap_rel": float(np.abs(lg - lg[swap]).mean() / np.abs(lg).mean())}


def main() -> None:
    torch.set_num_threads(4)
    rows = [{"run": r.name, **model_stats(r)} for r in sorted((LAB / "confirm" / "n29_raw").iterdir()) if (r / "model_final.pt").exists()]
    sd = np.array([r["swap_diff"] for r in rows])
    out = {"n_models": len(rows),
           "swap_diff": {"mean": float(sd.mean()), "max": float(sd.max()), "frac_heads_gt_0.05": float((sd > 0.05).mean()),
                         "frac_heads_gt_0.2": float((sd > 0.2).mean())},
           "abs_share_a_minus_half_max": float(np.abs(np.array([r["share_a"] for r in rows]) - 0.5).max()),
           "qk_pos_abs_median": float(np.median(np.abs([r["qk_pos"] for r in rows]))),
           "ov_tag_rel_median": float(np.median([r["ov_tag_rel"] for r in rows])),
           "logit_swap_rel": {"median": float(np.median([r["logit_swap_rel"] for r in rows])), "max": float(max(r["logit_swap_rel"] for r in rows))},
           "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
