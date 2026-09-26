"""Post hoc mechanism test (session 5, after Codex review of the conclusions): decompose the first W_E gradient into
the left-position (token at pos 0) and right-position (pos 1) contributions and MEASURE the spectral cross-term.
coherence C = sum_k [P(G_L + G_R) - P(G_L) - P(G_R)] / sum_k [P(G_L) + P(G_R)]  (1 = in phase, 0 = incoherent, as M0 assumes)
Also: per-frequency cross share, Spearman of P(G_L+G_R) with M0 / M0c, sanity check G_L + G_R == W_E.grad[:p].
Init + one backward pass per seed (seeds 0-17), no training. Run through guarded_run.py."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
sys.path.insert(0, str(LAB.parent / "training"))
sys.path.insert(0, str(LAB / "experiments/EXP-001-freq-ban"))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import freq_ban as fb  # noqa: E402
import mask_spectrum as ms  # noqa: E402
from coherent_m0 import m0c  # noqa: E402
from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402


def forward_from_e(model, e: torch.Tensor) -> torch.Tensor:
    """Transformer.forward with the token embeddings e = W_E[tokens] supplied (copied from models/transformer.py)."""
    cfg = model.cfg
    T = e.shape[1]
    x = e + model.W_pos[None, :T, :]
    q = torch.einsum("btd,hde->bhte", x, model.W_Q)
    k = torch.einsum("btd,hde->bhte", x, model.W_K)
    v = torch.einsum("btd,hde->bhte", x, model.W_V)
    scores = torch.einsum("bhte,bhse->bhts", q, k) / math.sqrt(cfg.d_head)
    mask = torch.triu(torch.ones(T, T, dtype=torch.bool), diagonal=1)
    attn = scores.masked_fill(mask, float("-inf")).softmax(dim=-1)
    z = torch.einsum("bhts,bhse->bhte", attn, v)
    x = x + torch.einsum("bhte,hed->btd", z, model.W_O)
    x = x + torch.einsum("btf,fd->btd", torch.relu(torch.einsum("btd,df->btf", x, model.W_in)), model.W_out)
    return torch.einsum("btd,dv->btv", x, model.W_U)


def rho(x, y) -> float:
    return float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1])


def per_seed(seed: int, drop_diag: bool = False) -> dict:
    cfg = get_config("arch25k", seed=seed, threads=4)
    torch.set_num_threads(cfg.threads)
    set_seed(cfg.seed)
    data = make_dataset(cfg)
    model = build_model(cfg)
    p = cfg.p
    x, y = data["train_x"], data["train_y"]
    if drop_diag:
        keep = x[:, 0] != x[:, 1]
        x, y = x[keep], y[keep]
    # reference: ordinary gradient
    F.cross_entropy(model.logits_last(x)[:, :p], y).backward()
    g_ref = model.W_E.grad[:p].detach().clone()
    model.zero_grad(set_to_none=True)
    e = model.W_E[x].detach().requires_grad_(True)
    F.cross_entropy(forward_from_e(model, e)[:, -1, :p], y).backward()
    d = model.W_E.shape[1]
    GL = torch.zeros(p, d, dtype=e.dtype).index_add_(0, x[:, 0], e.grad[:, 0])
    GR = torch.zeros(p, d, dtype=e.dtype).index_add_(0, x[:, 1], e.grad[:, 1])
    err = float((GL + GR - g_ref).abs().max() / g_ref.abs().max())
    B = fb.fourier_basis(p)
    PL, PR, PS = (fb.freq_power(G.numpy().astype(np.float64), B) for G in (GL, GR, GL + GR))
    cross = PS - PL - PR
    Mk = ms.mask_matrix(seed)
    return {"seed": seed, "sanity_rel_err": err, "coherence": float(cross.sum() / (PL + PR).sum()),
            "share_freqs_positive_cross": float((cross > 0).mean()),
            "rho_PS_M0": rho(PS, ms.m0(Mk)), "rho_PS_M0c": rho(PS, m0c(Mk)),
            "rho_PL_PR": rho(PL, PR),
            # per-frequency test (added after the aggregate result): measured cross-term vs mask cross-term M0c - M0
            "rho_cross_vs_maskcross": rho(cross, m0c(Mk) - ms.m0(Mk)),
            "pearson_cross_vs_maskcross": float(np.corrcoef(cross, m0c(Mk) - ms.m0(Mk))[0, 1])}


def main() -> None:
    rows = [per_seed(s) for s in range(18)]
    rows_nd = [per_seed(s, drop_diag=True) for s in range(6)]
    summ = {k: float(np.mean([r[k] for r in rows])) for k in rows[0] if k != "seed"}
    summ["max_sanity_rel_err"] = max(r["sanity_rel_err"] for r in rows)
    summ_nd = {k: float(np.mean([r[k] for r in rows_nd])) for k in ("coherence", "rho_PS_M0", "rho_PS_M0c",
                                                                    "rho_cross_vs_maskcross")}
    out = {"summary_seeds0_17": summ, "summary_no_diagonal_seeds0_5": summ_nd, "rows": rows, "rows_no_diag": rows_nd}
    (HERE / "positional_gradient.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for r in rows:
        print({k: round(v, 3) if isinstance(v, float) else v for k, v in r.items()})
    print(json.dumps({"all": summ, "no_diag": summ_nd}, indent=1))


if __name__ == "__main__":
    main()
