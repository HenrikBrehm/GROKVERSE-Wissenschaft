"""R6 post hoc (session 37, exploration, AFTER the frozen analysis; not a confirmation): across seeds, is the switch cost C(t) related
to the persistence pi(t) of the same seed? Spearman over seeds with a defined pi, per t, exact permutation-free normal approx not used:
p from 20 000 permutations. C uses generalization times, pi the final W_E of the switch runs (no shared term).
  python lab/confirm/R6_posthoc_pi_cost_s37.py
"""
import json
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]


def rank(x: np.ndarray) -> np.ndarray:
    o = np.argsort(x, kind="stable")
    r = np.empty(len(x))
    r[o] = np.arange(len(x))
    for v in np.unique(x):                      # average ties
        m = x == v
        r[m] = r[m].mean()
    return r


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    a, b = rank(x), rank(y)
    return float(np.corrcoef(a, b)[0, 1])


d = json.loads((LAB / "confirm/R6_summary.json").read_text(encoding="utf-8"))
rows = [r for r in d["rows"] if r["valid"] and "pi" in r]
rng = np.random.default_rng(37)
out = {"n": len(rows)}
for t in sorted(rows[0]["pi"], key=int):
    x = np.array([r["pi"][t] for r in rows])
    y = np.array([r["C"][t] for r in rows])
    rho = spearman(x, y)
    perm = np.array([spearman(x, rng.permutation(y)) for _ in range(20000)])
    out[t] = {"rho": round(rho, 3), "p_two_sided": float((np.abs(perm) >= abs(rho) - 1e-12).mean())}
print(json.dumps(out, indent=1))
