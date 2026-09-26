"""Post hoc mechanism check (session 5): does the ACTUAL first gradient at W_E (G0, EXP-012) follow the coherent mask
spectrum M0c more closely than M0? H (stated before computing): Spearman(G0, M0c) > Spearman(G0, M0) in most seeds.
Seeds 0-17 (only init + one backward pass, no training). Also the same for the sign-flip-free check with a foreign mask.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import mask_spectrum as ms  # noqa: E402
from coherent_m0 import m0c  # noqa: E402

p12 = ms.p12


def rho(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1])


rows = []
for s in range(18):
    G0 = p12.init_predictors(s)[0]["G0"]
    M = ms.mask_matrix(s)
    Mf = ms.mask_matrix((s + 1) % 18)          # foreign mask as a floor
    rows.append({"seed": s, "rho_M0": rho(G0, ms.m0(M)), "rho_M0c": rho(G0, m0c(M)),
                 "rho_M0c_foreign": rho(G0, m0c(Mf))})
d = np.array([r["rho_M0c"] - r["rho_M0"] for r in rows])
out = {"n": len(rows), "mean_rho_M0": float(np.mean([r["rho_M0"] for r in rows])),
       "mean_rho_M0c": float(np.mean([r["rho_M0c"] for r in rows])),
       "mean_rho_M0c_foreign": float(np.mean([r["rho_M0c_foreign"] for r in rows])),
       "n_M0c_higher": int((d > 0).sum()), "p_signflip_M0c_higher": p12.sign_flip_p(d), "rows": rows}
(HERE / "coherent_vs_gradient.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
