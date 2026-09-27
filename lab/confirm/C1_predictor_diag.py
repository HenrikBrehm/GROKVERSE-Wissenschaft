"""C1 predictor-only diagnostics (session 28, Codex review of C1, MAJOR 1): computed on the R1 splits BEFORE any R1 run,
from the deterministic R1 split construction (confirm_r1.build, nothing written). Per arm: Spearman of M0c(target) with the
target index k (targets are stored sorted, so list position has the same ranks); ties in M0c; M0c spread. Numpy only.
Also the adjusted P1 exploration (seen data): coefficient of M0c ranks controlling for k and step-0 ranks."""
import json, sys
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools")); sys.path.insert(0, str(LAB / "confirm"))
import confirm_r1 as r1
import confirm_splits as cs
from P1_posthoc_within import m0c_add
from rank_tools import TieError, adjusted_coef, spearman

man = json.loads((LAB / "confirm/R1_manifest_DRAFT.json").read_text(encoding="utf-8"))
rho_k, ties, spread = [], 0, []
for c in r1.CELLS:
    for s in man["seeds"][c]:
        T = cs.target_sets(man["experiment"], "add", r1.P, s)
        for a in "FG":
            idx, targ = r1.build(man["experiment"], s, a, man["eps"][c], r1.frac_of(c))
            assert targ == T[a] and targ == sorted(targ)
            m = m0c_add(idx, r1.P)[[k - 1 for k in targ]]
            try:
                rho_k.append(spearman(m, np.array(targ, float)))
            except TieError:
                ties += 1
            spread.append(m.max() / m.min())
out = {"r1_arms": len(rho_k) + ties, "mean_rho_M0c_k": float(np.mean(rho_k)), "sd_rho_M0c_k": float(np.std(rho_k, ddof=1)),
       "ties": ties, "median_M0c_max_over_min": float(np.median(spread))}

import confirm_p1 as c1
from P1_posthoc_share import power0
pman = json.loads((LAB / "confirm/P1_manifest.json").read_text(encoding="utf-8"))
t = {"task": "add", "p": 113}
blocks = []
for s in pman["seeds"]:
    for a in "FG":
        st = c1.stem(pman, t, s, a); T = json.loads((c1.SPLITS / f"{st}.json").read_text())["targets"]; sel = [k - 1 for k in T]
        blocks.append({"y": c1.power_at(pman, t, s, a)[sel], "m0c": m0c_add(np.load(c1.SPLITS / f"{st}.npy"), 113)[sel],
                       "k": np.array(T, float), "init": power0(pman, t, s, a)[sel]})
out["p1_add113_adjusted_coef_M0c_given_k_init"] = adjusted_coef(blocks, "m0c", ["k", "init"])
out["p1_add113_unadjusted_mean_rho"] = float(np.mean([spearman(b["m0c"], b["y"]) for b in blocks]))
print(json.dumps(out, indent=1))
(LAB / "confirm/C1_predictor_diag.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
