"""Session 7, exploratory (no training): which part of the activation carries the F vs H preference of the AGF utility?

Same exact utility as utility_relu.py (U = ||P g||, g_c = sum_a M(a, c-a) act(r (u_a + v_{c-a}))), unit-amplitude
single-frequency features scaled by r, 16 x 16 phases, the 19 EXP-024 units. Activations: odd part x, even part |x|,
ReLU = (x + |x|)/2, and the family sigma_alpha(x) = alpha x + x^2 at r = 1 (only alpha / r matters for this family,
because sigma_alpha(r z) = r^2 (alpha/r z + z^2)). Reports mean top-5 overlap with F and H = fold(57 F).
"""
import json
import numpy as np
import utility_scan as us
from utility_relu import utility, ACTS

ALPHAS = (0.0, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0)
ACTS["lin"] = lambda x: x
ACTS["abs"] = np.abs
for al in ALPHAS:
    ACTS[f"sig{al}"] = (lambda A: (lambda x: A * x + x * x))(al)


def units():
    for seed in range(10, 20):
        for arm, suf in (("F", ""), ("G", "_G")):
            if (seed, arm) == (12, "G"):
                continue
            M = us.mask_from_idx(np.load(us.S16 / f"split_seed{seed}_eps2.0{suf}.npy"))
            T = set(json.loads((us.S16 / f"split_seed{seed}_eps2.0{suf}.json").read_text())["targets"])
            yield seed, arm, M, T, {us.fold(57 * t) for t in T}


def main():
    acts = ["lin", "abs", "relu"] + [f"sig{al}" for al in ALPHAS]
    res = {a: {"ov_F": [], "ov_H": []} for a in acts}
    for seed, arm, M, T, H in units():
        for act in acts:
            U = np.array([utility(M, k, act, n_phase=8) for k in range(1, us.K + 1)])
            top = set(int(k) for k in np.argsort(-U)[:5] + 1)
            res[act]["ov_F"].append(len(top & T))
            res[act]["ov_H"].append(len(top & H))
        print(seed, arm, {a: (res[a]["ov_F"][-1], res[a]["ov_H"][-1]) for a in acts}, flush=True)
    summ = {a: {"ov_F_mean": float(np.mean(v["ov_F"])), "ov_H_mean": float(np.mean(v["ov_H"])), **v}
            for a, v in res.items()}
    for a in acts:
        print(a, "ov_F %.2f ov_H %.2f" % (summ[a]["ov_F_mean"], summ[a]["ov_H_mean"]))
    (us.HERE / "utility_parity.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
