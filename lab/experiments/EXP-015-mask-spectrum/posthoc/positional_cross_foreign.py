"""Control for positional_gradient.py: measured cross-term of seed s vs the mask cross-term of a FOREIGN split (s+1)."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import positional_gradient as pg  # noqa: E402
import torch  # noqa: E402
import torch.nn.functional as F  # noqa: E402

out = []
for s in range(10):
    cfg = pg.get_config("arch25k", seed=s, threads=4)
    torch.set_num_threads(4)
    pg.set_seed(s)
    data = pg.make_dataset(cfg)
    model = pg.build_model(cfg)
    p = cfg.p
    x, y = data["train_x"], data["train_y"]
    e = model.W_E[x].detach().requires_grad_(True)
    F.cross_entropy(pg.forward_from_e(model, e)[:, -1, :p], y).backward()
    GL = torch.zeros(p, e.shape[2]).index_add_(0, x[:, 0], e.grad[:, 0])
    GR = torch.zeros(p, e.shape[2]).index_add_(0, x[:, 1], e.grad[:, 1])
    B = pg.fb.fourier_basis(p)
    PL, PR, PS = (pg.fb.freq_power(G.numpy().astype(np.float64), B) for G in (GL, GR, GL + GR))
    cross = PS - PL - PR
    own, other = pg.ms.mask_matrix(s), pg.ms.mask_matrix((s + 1) % 10)
    out.append({"seed": s, "own": pg.rho(cross, pg.m0c(own) - pg.ms.m0(own)),
                "foreign": pg.rho(cross, pg.m0c(other) - pg.ms.m0(other))})
print(out)
print("mean own %.3f foreign %.3f" % (np.mean([o["own"] for o in out]), np.mean([o["foreign"] for o in out])))
(HERE / "positional_cross_foreign.json").write_text(json.dumps(out, indent=1))
