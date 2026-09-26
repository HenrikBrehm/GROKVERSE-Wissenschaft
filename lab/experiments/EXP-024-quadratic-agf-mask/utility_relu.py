"""EXP-024 arm R prediction (registered before any R run): same utility as utility_scan.py, activation ReLU.

U(u, v) = || P g ||, g_c = sum_a M(a, c-a) relu(u_a + v_{c-a}), single-frequency features, 16 x 16 phases.
Also recomputes the quadratic case on the same 19 units (12/G excluded) for side-by-side reporting.
"""
import json
import numpy as np
import utility_scan as us

ACTS = {"relu": lambda x: np.maximum(x, 0.0), "quad": lambda x: x * x}


def utility(M, k, act, n_phase=16):
    P = us.P
    a = np.arange(P)
    other = (a[None, :] - a[:, None]) % P
    Mac = M[a[:, None], other]
    best = 0.0
    for al in np.linspace(0, 2 * np.pi, n_phase, endpoint=False):
        u = np.cos(2 * np.pi * k * a / P + al)
        for be in np.linspace(0, 2 * np.pi, n_phase, endpoint=False):
            v = np.cos(2 * np.pi * k * a / P + be)
            g = (Mac * ACTS[act](u[:, None] + v[other])).sum(axis=0)
            best = max(best, float(np.linalg.norm(g - g.mean())))
    return best


res = {}
for act in ("relu",):
    rows = []
    for seed in range(10, 20):
        for arm, suf in (("F", ""), ("G", "_G")):
            if (seed, arm) == (12, "G"):
                continue
            M = us.mask_from_idx(np.load(us.S16 / f"split_seed{seed}_eps2.0{suf}.npy"))
            T = json.loads((us.S16 / f"split_seed{seed}_eps2.0{suf}.json").read_text())["targets"]
            H = {us.fold(57 * t) for t in T}
            U = np.array([utility(M, k, act) for k in range(1, us.K + 1)])
            top = set(int(k) for k in np.argsort(-U)[:5] + 1)
            rows.append({"seed": seed, "arm": arm, "top5": sorted(top), "ov_F": len(top & set(T)), "ov_H": len(top & H)})
            print(act, rows[-1], flush=True)
    res[act] = {"rows": rows, "ov_F_mean": float(np.mean([r["ov_F"] for r in rows])),
                "ov_H_mean": float(np.mean([r["ov_H"] for r in rows]))}
    print(act, res[act]["ov_F_mean"], res[act]["ov_H_mean"])
(us.HERE / "utility_relu.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
