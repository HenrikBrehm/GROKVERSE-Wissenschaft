"""EXP-015 post hoc (exploratory, not pre-registered): does the mask spectrum M0 of split s also
predict the final top-5 frequencies of the stored MLP runs with the same seed (same split)?
Compares with the EXP-009 init-spectrum r-bar per group. Run through guarded_run.py."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mask_spectrum as ms  # noqa: E402
import predict as p12  # noqa: E402  (path set by mask_spectrum)

runs = json.loads(p12.EXP009.read_text(encoding="utf-8"))["runs"]
cache = {}
out = {}
for r in runs:
    grp, seed = r["run"].split("_seed")[0], int(r["run"].split("_seed")[1].split("_")[0])
    if seed not in cache:
        cache[seed] = ms.m0(ms.mask_matrix(seed))
    out.setdefault(grp, []).append(p12.rbar(cache[seed], r["k_final"]))
res = {}
for g, v in out.items():
    rb = float(np.mean(v))
    res[g] = {"n": len(v), "rbar_M0": rb, "p_M0": p12.mc_null_p(rb, len(v))}
(HERE / "arch_posthoc.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
