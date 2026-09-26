"""Post hoc (exploratory): do final top-5 sets of DIFFERENT architectures overlap more when they share
the seed (= same train split, different weights) than when they do not? Pure read of EXP-009 summary."""
import itertools
import json
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[2]
runs = json.loads((LAB / "experiments/EXP-009-freq-commitment/summary.json").read_text(encoding="utf-8"))["runs"]
K = {}
for r in runs:
    K[(r["run"].split("_seed")[0], int(r["run"].split("_seed")[1].split("_")[0]))] = set(r["k_final"])
groups = sorted({g for g, _ in K})
res = {}
for g1, g2 in itertools.combinations(groups, 2):
    same = [len(K[(g1, s)] & K[(g2, s)]) for s in range(10)]
    diff = [len(K[(g1, s)] & K[(g2, t)]) for s in range(10) for t in range(10) if s != t]
    # permutation p: shuffle seed labels of g2
    rng = np.random.default_rng(0)
    null = [np.mean([len(K[(g1, s)] & K[(g2, int(pi))]) for s, pi in enumerate(rng.permutation(10))])
            for _ in range(20000)]
    p = float((np.sum(np.array(null) >= np.mean(same)) + 1) / (len(null) + 1))
    res[f"{g1} | {g2}"] = {"same_seed": float(np.mean(same)), "other_seed": float(np.mean(diff)), "p_perm": p,
                           "per_seed": same}
(Path(__file__).with_suffix(".json")).write_text(json.dumps(res, indent=1), encoding="utf-8")
for k, v in res.items():
    print(k, {x: (round(y, 3) if isinstance(y, float) else y) for x, y in v.items()})
