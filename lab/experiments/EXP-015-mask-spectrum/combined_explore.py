"""Exploration (seeds 0-9 only): is a combination of init spectrum E0 and mask spectrum M0 a better
predictor than either? Score = mean of the two rank positions (rank-average), and log-product
log(E0) + log(M0). Run through guarded_run.py."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mask_spectrum as ms  # noqa: E402
import predict as p12  # noqa: E402

k009 = {}
for r in json.loads(p12.EXP009.read_text(encoding="utf-8"))["runs"]:
    if r["run"].startswith("txf_add_p113_wd1.0_frac0.3_seed"):
        k009[int(r["run"].split("seed")[1].split("_")[0])] = r["k_final"]
rows = []
for s in range(10):
    preds, _ = p12.init_predictors(s)
    E0, M0 = preds["E0"], ms.m0(ms.mask_matrix(s))
    rk = lambda x: np.argsort(np.argsort(-x))          # noqa: E731
    rankavg = -(rk(E0) + rk(M0)).astype(float)
    logprod = np.log(E0) + np.log(M0)
    rows.append({"seed": s, "E0": p12.rbar(E0, k009[s]), "M0": p12.rbar(M0, k009[s]),
                 "G0": p12.rbar(preds["G0"], k009[s]), "rankavg": p12.rbar(rankavg, k009[s]),
                 "logprod": p12.rbar(logprod, k009[s])})
mean = {k: float(np.mean([r[k] for r in rows])) for k in ("E0", "M0", "G0", "rankavg", "logprod")}
(HERE / "combined_explore.json").write_text(json.dumps({"mean": mean, "rows": rows}, indent=1), encoding="utf-8")
print(json.dumps(mean, indent=1))
