"""Check after Codex review (exploratory, seeds 0-9, all 4 architectures of EXP-009):
does the MATCHED mask spectrum predict K better than FOREIGN masks (split of another seed)?
If foreign masks predict equally well, M0 only captures a generic frequency preference.
Permutation p: fraction of random seed->mask permutations whose mean r-bar <= matched."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mask_spectrum as ms  # noqa: E402
import predict as p12  # noqa: E402

runs = json.loads(p12.EXP009.read_text(encoding="utf-8"))["runs"]
M0 = {s: ms.m0(ms.mask_matrix(s)) for s in range(10)}
res = {}
rng = np.random.default_rng(0)
for g in sorted({r["run"].split("_seed")[0] for r in runs}):
    K = {int(r["run"].split("_seed")[1].split("_")[0]): r["k_final"] for r in runs if r["run"].startswith(g + "_seed")}
    R = np.array([[p12.rbar(M0[m], K[s]) for m in range(10)] for s in range(10)])   # [run seed, mask seed]
    matched = float(np.trace(R) / 10)
    foreign = float((R.sum() - np.trace(R)) / 90)
    perms = [rng.permutation(10) for _ in range(20000)]
    null = np.array([R[np.arange(10), pi].mean() for pi in perms])
    res[g] = {"matched": matched, "foreign_mean": foreign,
              "p_perm": float((np.sum(null <= matched - 1e-12) + 1) / (len(null) + 1))}
(HERE / "foreign_mask_check.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
