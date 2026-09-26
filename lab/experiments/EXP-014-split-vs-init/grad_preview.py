"""EXP-014 preview (exploratory, no training): is the first-gradient frequency spectrum G0
driven by the init or by the train split?

For init seeds i and split seeds j in 0..9, G0(i, j) = power spectrum of dL/dW_E[:p] at step 0.
Compares corr(G0(i,j), G0(i,i)) [same init] with corr(G0(i,j), G0(j,j)) [same split], i != j,
using Spearman correlation over the 56 frequencies. Also: overlap of top-5 sets.
Run through lab/tools/guarded_run.py (one forward/backward per (i, j), 100 total).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB.parent / "training"))
sys.path.insert(0, str(LAB / "experiments/EXP-001-freq-ban"))

import freq_ban as fb  # noqa: E402
from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402

SEEDS = range(10)


def g0(init: int, split: int) -> np.ndarray:
    cfg = get_config("arch25k", seed=init, threads=4)
    torch.set_num_threads(cfg.threads)
    set_seed(init)
    data = make_dataset(get_config("arch25k", seed=split, threads=4))
    model = build_model(cfg)
    p = cfg.p
    F.cross_entropy(model.logits_last(data["train_x"])[:, :p], data["train_y"]).backward()
    return fb.freq_power(model.W_E.grad.numpy().astype(np.float64)[:p], fb.fourier_basis(p))


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def main() -> None:
    G = {(i, j): g0(i, j) for i in SEEDS for j in SEEDS}
    rows = []
    for i in SEEDS:
        for j in SEEDS:
            if i == j:
                continue
            c = G[(i, j)]
            ti, tj, tc = (set(fb.top_frequencies(G[k], 5)) for k in ((i, i), (j, j), (i, j)))
            rows.append({"init": i, "split": j,
                         "rho_same_init": spearman(c, G[(i, i)]), "rho_same_split": spearman(c, G[(j, j)]),
                         "ov_same_init": len(tc & ti), "ov_same_split": len(tc & tj)})
    summ = {k: float(np.mean([r[k] for r in rows])) for k in
            ("rho_same_init", "rho_same_split", "ov_same_init", "ov_same_split")}
    summ["frac_split_closer"] = float(np.mean([r["rho_same_split"] > r["rho_same_init"] for r in rows]))
    (HERE / "grad_preview.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1),
                                            encoding="utf-8")
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
