"""Session 59, comparison value for the first-gradient tests (written before running; descriptive). The LM tests used the LM1 splits
(seeds 4000/4001, add mod 113, 3831 facts); the notes lacked the toy-model value on the same facts ("so klar wie das Spielzeugmodell"
was struck for that reason). Here: the study's one-layer transformer (get_config("arch25k"), build_model; the trainer freq_ban.py
builds the model the same way), init seeds 4100/4101 (grokverse set_seed), full-batch cross-entropy on the split's pairs at init
(model.logits_last(x)[:, :p], as freq_ban.py), gradient w.r.t. the number rows W_E[:p]; Delta_pow and top-5 with EXP-127 analyze.power /
delta_pow (same definition as the LM tests). Reading for symmetry (fixed before running): 'gestuetzt' if > 1 in both seeds,
'nicht gestuetzt' if <= 0 in both, else 'unklar'. CPU, 2 threads.
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-127-pretrained-lm/first_gradient_toy.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "training"))
import analyze as A  # noqa: E402
from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402

SPL = ROOT / "lab/confirm/lm1_splits"
P = 113


def main() -> None:
    torch.set_num_threads(2)
    out = {"model": "arch25k one-layer transformer (study)", "rows": []}
    for s in (4000, 4001):
        tg = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        g = {}
        for arm in "FG":
            cfg = get_config("arch25k", seed=s + 100, steps=1, threads=2, p=P)
            set_seed(cfg.seed)
            data = make_dataset(cfg)
            model = build_model(cfg)
            idx = torch.from_numpy(np.load(SPL / f"seed{s}_{arm}.npy").astype(np.int64))
            x, y = data["all_x"][idx], data["all_y"][idx]
            assert bool(((x[:, 0] + x[:, 1]) % P == y).all()), "labels are not (a + b) mod p"
            model.zero_grad(set_to_none=True)
            F.cross_entropy(model.logits_last(x)[:, :P], y).backward()
            g[arm] = model.W_E.grad[:P].double().numpy()
        pF, pG = A.power(g["F"]), A.power(g["G"])
        r = {"seed": s, "targets": tg, "dpow_grad_in": A.delta_pow(pF, pG, tg["F"], tg["G"]),
             "top5_F_in": (np.argsort(pF)[::-1][:5] + 1).tolist(), "top5_G_in": (np.argsort(pG)[::-1][:5] + 1).tolist()}
        out["rows"].append(r)
        print(json.dumps(r), flush=True)
    d = [r["dpow_grad_in"] for r in out["rows"]]
    out["reading"] = ("gestuetzt" if all(v is not None and v > 1 for v in d) else
                      "nicht gestuetzt" if all(v is not None and v <= 0 for v in d) else "unklar")
    (HERE / "first_gradient_toy.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(out["reading"])


if __name__ == "__main__":
    main()
