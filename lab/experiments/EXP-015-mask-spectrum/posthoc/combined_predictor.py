"""Post hoc (session 5, exploratory): does log E0 + log M0c (init power + coherent mask spectrum) predict K better than
M0c alone? Seeds 0-9 (K = EXP-009 k_final) and 10-17 (EXP-003d baselines). Init + mask only, no training."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import mask_spectrum as ms  # noqa: E402
from coherent_m0 import k_of, m0c  # noqa: E402

p12 = ms.p12
k009 = {}
for r in json.loads(p12.EXP009.read_text(encoding="utf-8"))["runs"]:
    if r["run"].startswith("txf_add_p113_wd1.0_frac0.3_seed"):
        k009[int(r["run"].split("seed")[1].split("_")[0])] = r["k_final"]
rows = []
for s in range(18):
    K = k_of(s, k009)
    E0 = p12.init_predictors(s)[0]["E0"]
    c = m0c(ms.mask_matrix(s))
    rows.append({"seed": s, "M0c": p12.rbar(c, K), "E0": p12.rbar(E0, K), "sum": p12.rbar(np.log(E0) + np.log(c), K)})
out = {}
for g, sel in (("0_9", range(10)), ("10_17", range(10, 18))):
    R = [r for r in rows if r["seed"] in sel]
    d = np.array([r["M0c"] - r["sum"] for r in R])
    out[g] = {k: float(np.mean([r[k] for r in R])) for k in ("M0c", "E0", "sum")}
    out[g]["p_sum_better"] = p12.sign_flip_p(d)
print(json.dumps(out, indent=1))
(HERE / "combined_predictor.json").write_text(json.dumps({"summary": out, "rows": rows}, indent=1))
