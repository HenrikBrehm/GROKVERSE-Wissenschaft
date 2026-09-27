"""P1 post hoc, exploration (session 28): k-index control and mismatched-arm control for the within-arm target order (add 113,
M0c). Run from the repo root. Numpy only, stored P1 runs through the frozen P1 loader."""
import json, sys, numpy as np
from pathlib import Path
sys.path.insert(0, "lab/tools"); sys.path.insert(0, "lab/confirm")
import confirm_p1 as c
from P1_posthoc_within import m0c_add, mean_rho
man = json.loads(Path("lab/confirm/P1_manifest.json").read_text())
t = {"task": "add", "p": 113}
Y, M, K = [], [], []
for s in man["seeds"]:
    for a in "FG":
        st = c.stem(man, t, s, a); T = json.loads((c.SPLITS / f"{st}.json").read_text())["targets"]; sel = [k-1 for k in T]
        Y.append(c.power_at(man, t, s, a)[sel]); M.append(m0c_add(np.load(c.SPLITS / f"{st}.npy"), 113)[sel]); K.append(np.array(T, float))
Y, M, K = map(np.array, (Y, M, K))
out = {"rho_learned_k": mean_rho(K, Y), "rho_M0c_k": mean_rho(K, M), "rho_M0c_learned": mean_rho(M, Y), "mismatched_roll7": mean_rho(M, np.roll(Y, 7, axis=0))}
print("rho(learned,k) %.3f  rho(M0c,k) %.3f  rho(M0c,learned) %.3f" % (mean_rho(K, Y), mean_rho(K, M), mean_rho(M, Y)))
# control: pair each arm's M0c ranking with a DIFFERENT arm's learned ranking (targets differ, so rank-by-position only)
print("mismatched arms (roll 7):", round(mean_rho(M, np.roll(Y, 7, axis=0)), 3))
# residual: rank learned by M0c within arm after removing k-rank partial
print("M0c relative spread within arm (max/min):", np.round(np.median(M.max(1)/M.min(1)), 3))
(Path("lab/confirm") / "P1_posthoc_kcontrol.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
