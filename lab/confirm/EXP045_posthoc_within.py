"""EXP-045 post hoc, EXPLORATION (session 28; pilot seeds 90-99, already seen for K2 but never for the target order).
Architecture contrast of the first-order theory (draft section 5, prediction 2) at the level of the fine order:
the transformer's first W_E gradient follows the COHERENT spectrum M0c, the shared-embedding MLP's the uncentred per-operand M0.
Prediction fixed before looking: in the MLP, the within-arm Spearman of the target power with M0 exceeds that with M0c
(transformer, P1 add 113: M0c 0.44 > M0 0.32). Measure: mean over the 20 arms of rho_M0 - rho_M0c at steps 2000 and 10000;
within-arm permutation p for each predictor; paired sign-flip p for the difference (seed unit). Pilot, n = 10 seeds."""
import json, sys
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools")); sys.path.insert(0, str(LAB / "confirm")); sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
import confirm_splits as cs
from analyze import group_power
from P1_posthoc_within import m0c_add, mean_rho
from rank_tools import spearman
HERE = next((LAB / "experiments").glob("EXP-045*"))
rng = np.random.default_rng(45)
out = {}
for step in (2000, 10000):
    Y, M0, MC, seeds = [], [], [], []
    for d in sorted((HERE / "raw").glob("*_mlp_devcuda")):
        s, arm = int(d.name.split("_seed")[1].split("_")[0]), d.name.split("_eps2.0_")[1][0]
        stem = f"split_add113_seed{s}_eps2.0_{arm}"
        T = json.loads((HERE / f"splits/{stem}.json").read_text(encoding="utf-8"))["targets"]; sel = [k - 1 for k in T]
        idx = np.load(HERE / f"splits/{stem}.npy")
        st = list(np.load(d / "we_snapshot_steps.npy")); W = np.load(d / "we_snapshots.npy").astype(np.float64)
        Y.append(group_power(W[st.index(step)], "add", 113)[0][sel]); M0.append(cs.m0(idx, "add", 113)[sel]); MC.append(m0c_add(idx, 113)[sel]); seeds.append(s)
    Y, M0, MC = map(np.array, (Y, M0, MC))
    res = {"arms": len(Y)}
    for name, X in (("M0", M0), ("M0c", MC)):
        obs = mean_rho(X, Y); null = np.array([mean_rho(rng.permuted(X, axis=1), Y) for _ in range(20000)])
        res[name] = {"mean_rho": round(obs, 3), "p_two": float((np.abs(null) >= abs(obs)).mean())}
    diff = np.array([spearman(M0[i], Y[i]) - spearman(MC[i], Y[i]) for i in range(len(Y))])
    by = {}
    for s, v in zip(seeds, diff): by.setdefault(s, []).append(v)
    u = np.array([np.mean(v) for v in by.values()])
    flips = rng.choice((-1.0, 1.0), size=(200000, len(u)))
    res["diff_M0_minus_M0c"] = {"mean": round(float(u.mean()), 3), "seeds": len(u), "n_pos": int((u > 0).sum()),
                                "p_one_sided": float((((flips * u).mean(1) >= u.mean()).sum() + 1) / 200001)}
    out[str(step)] = res
    print(step, json.dumps(res))
(LAB / "confirm/EXP045_posthoc_within.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
