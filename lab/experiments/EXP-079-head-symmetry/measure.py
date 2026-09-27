#!/usr/bin/env python3
"""EXP-079 (exploration for N36, session 26, UNTESTED): are the attention heads of trained add-113 models position-symmetric?

Reads the 80 stored N29 final models (lab/confirm/n29_raw/*/model_final.pt; 4000+ steps, add 113, generalised in 19/20 seeds) and, for all
p*p inputs (a, b, '='), the attention of the '=' position to position 0 (a) and 1 (b) per head. Per model and head:
  share_a   = mean over inputs of alpha_a / (alpha_a + alpha_b)          (0.5 = no position preference on average)
  swap_diff = mean |alpha_a(a,b) - alpha_b(b,a)|                          (0 = exchange-symmetric pattern)
No training, no gradient; a forward pass of stored models only. Output: summary.json next to this file.

  python lab/tools/guarded_run.py -- python lab/experiments/EXP-079-head-symmetry/measure.py
"""
from __future__ import annotations

import json
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
def head_stats(run: Path) -> dict:
    model = build_model(get_config("arch25k", seed=0, steps=1, threads=1))
    model.load_state_dict(torch.load(run / "model_final.pt", map_location="cpu"))
    model.eval()
    a, b = np.meshgrid(np.arange(P), np.arange(P), indexing="ij")
    a, b = a.ravel(), b.ravel()
    x = torch.from_numpy(np.stack([a, b, np.full(len(a), P)], 1)).long()
    att = model.attention_pattern(x)[:, :, 2, :].double().numpy()          # [N, heads, 3]: '=' attends to a, b, '='
    al_a, al_b = att[:, :, 0], att[:, :, 1]
    share_a = (al_a / np.maximum(al_a + al_b, 1e-12)).mean(0)
    swap = (b * P + a)                                                      # index of (b, a)
    swap_diff = np.abs(al_a - al_b[swap]).mean(0)
    return {"share_a": share_a.tolist(), "swap_diff": swap_diff.tolist(), "self": att[:, :, 2].mean(0).tolist()}


def main() -> None:
    torch.set_num_threads(4)
    rows = []
    for run in sorted((LAB / "confirm" / "n29_raw").iterdir()):
        if (run / "model_final.pt").exists():
            rows.append({"run": run.name, **head_stats(run)})
    sa = np.array([r["share_a"] for r in rows])
    sd = np.array([r["swap_diff"] for r in rows])
    out = {"n_models": len(rows),
           "share_a_mean_per_head": sa.mean(0).tolist(),
           "frac_heads_strong_preference": float((np.abs(sa - 0.5) > 0.2).mean()),     # a head with > 70 % on one operand
           "max_abs_share_dev": float(np.abs(sa - 0.5).max()),
           "swap_diff_mean": float(sd.mean()), "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
