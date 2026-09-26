"""Post hoc architecture contrast (session 5). Prediction stated BEFORE computing: in the shared-embedding MLP the left
and right operand go through DIFFERENT halves of W_in (independent random matrices), so the positional cross-term of the
first W_E gradient should NOT follow the mask cross-term (rho ~ 0), and M0 should describe the gradient power at least
as well as M0c; in the transformer (shared value path) the cross-term follows the mask (rho 0.50, positional_gradient.py).
Also: rbar(M0) vs rbar(M0c) for the final W_E top-5 of the study MLP runs (seeds 0-9, arch25k).
Init + one backward pass and stored final models; no training. Run through guarded_run.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import positional_gradient as pg  # noqa: E402

ROOT = HERE.parents[3]
P = 113


def per_seed(s: int) -> dict:
    cfg = pg.get_config("arch25k", seed=s, threads=4, arch="mlp")
    torch.set_num_threads(4)
    pg.set_seed(cfg.seed)
    data = pg.make_dataset(cfg)
    model = pg.build_model(cfg)
    x, y = data["train_x"], data["train_y"]
    F.cross_entropy(model.logits_last(x)[:, :P], y).backward()
    g_ref = model.W_E.grad[:P].detach().clone()
    model.zero_grad(set_to_none=True)
    ea = model.W_E[x[:, 0]].detach().requires_grad_(True)
    eb = model.W_E[x[:, 1]].detach().requires_grad_(True)
    h = torch.relu(torch.cat([ea, eb], dim=-1) @ model.W_in + model.b_in)
    F.cross_entropy((h @ model.W_out + model.b_out)[:, :P], y).backward()
    d = model.W_E.shape[1]
    GL = torch.zeros(P, d).index_add_(0, x[:, 0], ea.grad)
    GR = torch.zeros(P, d).index_add_(0, x[:, 1], eb.grad)
    err = float((GL + GR - g_ref).abs().max() / g_ref.abs().max())
    PL, PR, PS = (pg.fb.freq_power(G.numpy().astype(np.float64), pg.fb.fourier_basis(P)) for G in (GL, GR, GL + GR))
    cross = PS - PL - PR
    Mk = pg.ms.mask_matrix(s)
    a, c = pg.ms.m0(Mk), pg.m0c(Mk)
    sd = torch.load(ROOT / f"training/runs/mlp_add_p113_wd1.0_frac0.3_seed{s}_arch25k/model_final.pt", map_location="cpu")
    pw = pg.fb.freq_power(sd["W_E"].numpy().astype(np.float64)[:P], pg.fb.fourier_basis(P))
    K = sorted(int(k) + 1 for k in np.argsort(-pw)[:5])
    return {"seed": s, "sanity_rel_err": err, "rho_cross_vs_maskcross": pg.rho(cross, c - a),
            "rho_PS_M0": pg.rho(PS, a), "rho_PS_M0c": pg.rho(PS, c), "K_final": K,
            "rbar_M0": pg.ms.p12.rbar(a, K), "rbar_M0c": pg.ms.p12.rbar(c, K)}


rows = [per_seed(s) for s in range(10)]
summ = {k: float(np.mean([r[k] for r in rows])) for k in rows[0] if k not in ("seed", "K_final")}
summ["n_cross_positive"] = sum(r["rho_cross_vs_maskcross"] > 0 for r in rows)
for r in rows:
    print({k: round(v, 3) if isinstance(v, float) else v for k, v in r.items()})
print(json.dumps(summ, indent=1))
(HERE / "mlp_contrast.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1))
