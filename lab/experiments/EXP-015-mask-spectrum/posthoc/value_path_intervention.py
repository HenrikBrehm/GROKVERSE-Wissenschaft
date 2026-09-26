"""Post hoc in-silico intervention (session 5). Prediction BEFORE computing: if the shared attention value path
(W_V, W_O) makes the left/right gradient contributions interfere, then giving position 1 its OWN independent value matrix
W_V' (same init distribution) in the first-gradient computation removes the interference: rho(cross, mask cross) -> ~0
(unmodified transformer 0.50). Also a second control: independent W_O' for position 1 instead. Init + one backward pass;
no training. Run through guarded_run.py."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import positional_gradient as pg  # noqa: E402

P = 113


def forward_split_value(model, e: torch.Tensor, WV1: torch.Tensor | None, WO1: torch.Tensor | None) -> torch.Tensor:
    """Transformer forward where position 1 (token b) uses its own value matrix WV1 and/or output matrix WO1."""
    cfg = model.cfg
    T = e.shape[1]
    x = e + model.W_pos[None, :T, :]
    q = torch.einsum("btd,hde->bhte", x, model.W_Q)
    k = torch.einsum("btd,hde->bhte", x, model.W_K)
    v = torch.einsum("btd,hde->bhte", x, model.W_V)
    if WV1 is not None:
        v1 = torch.einsum("bd,hde->bhe", x[:, 1], WV1)
        v = torch.cat([v[:, :, :1], v1[:, :, None], v[:, :, 2:]], dim=2)
    scores = torch.einsum("bhte,bhse->bhts", q, k) / math.sqrt(cfg.d_head)
    mask = torch.triu(torch.ones(T, T, dtype=torch.bool), diagonal=1)
    attn = scores.masked_fill(mask, float("-inf")).softmax(dim=-1)
    if WO1 is None:
        z = torch.einsum("bhts,bhse->bhte", attn, v)
        x = x + torch.einsum("bhte,hed->btd", z, model.W_O)
    else:   # position-1 contribution through WO1, the rest through W_O
        a_not1 = attn.clone()
        a_not1[..., 1] = 0
        a_1 = attn - a_not1
        x = x + torch.einsum("bhte,hed->btd", torch.einsum("bhts,bhse->bhte", a_not1, v), model.W_O) \
              + torch.einsum("bhte,hed->btd", torch.einsum("bhts,bhse->bhte", a_1, v), WO1)
    x = x + torch.einsum("btf,fd->btd", torch.relu(torch.einsum("btd,df->btf", x, model.W_in)), model.W_out)
    return torch.einsum("btd,dv->btv", x, model.W_U)


def cross_rho(s: int, mode: str) -> float:
    cfg = pg.get_config("arch25k", seed=s, threads=4)
    torch.set_num_threads(4)
    pg.set_seed(cfg.seed)
    data = pg.make_dataset(cfg)
    model = pg.build_model(cfg)
    g = torch.Generator().manual_seed(10_000 + s)
    WV1 = torch.randn(model.W_V.shape, generator=g) * model.W_V.detach().std() if mode == "own_WV" else None
    WO1 = torch.randn(model.W_O.shape, generator=g) * model.W_O.detach().std() if mode == "own_WO" else None
    x, y = data["train_x"], data["train_y"]
    e = model.W_E[x].detach().requires_grad_(True)
    F.cross_entropy(forward_split_value(model, e, WV1, WO1)[:, -1, :P], y).backward()
    d = model.W_E.shape[1]
    GL = torch.zeros(P, d).index_add_(0, x[:, 0], e.grad[:, 0])
    GR = torch.zeros(P, d).index_add_(0, x[:, 1], e.grad[:, 1])
    B = pg.fb.fourier_basis(P)
    PL, PR, PS = (pg.fb.freq_power(G.numpy().astype(np.float64), B) for G in (GL, GR, GL + GR))
    Mk = pg.ms.mask_matrix(s)
    return pg.rho(PS - PL - PR, pg.m0c(Mk) - pg.ms.m0(Mk))


def main() -> None:
    out = {mode: [cross_rho(s, mode) for s in range(10)] for mode in ("unmodified", "own_WV", "own_WO")}
    summ = {m: {"mean": float(np.mean(v)), "n_positive": int(sum(x > 0 for x in v))} for m, v in out.items()}
    print(json.dumps(summ, indent=1))
    (HERE / "value_path_intervention.json").write_text(json.dumps({"summary": summ, "per_seed": out}, indent=1))


if __name__ == "__main__":
    main()
