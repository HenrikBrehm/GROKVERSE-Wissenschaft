"""P1 post hoc, EXPLORATION (session 28), new direction N40: does a trained embedding reveal WHICH of several equally built
training splits it saw? For each add-113 P1 arm: the true split and 9 decoys with the same targets and eps but other phase/key
streams (confirm_splits.draw with fresh generators). Score of a candidate = Spearman over the 5 targets between its M0c and the
learned W_E power at step 2000 (target order only; the target SET is identical for all candidates). Decision: highest score
(ties -> counted as miss). Chance 1/10. Fixed before looking. Also a pairwise version (true vs one decoy, chance 0.5).
Second measure, added after seeing the first result (5 ranks carry little information) but before computing it: the same
decision with the Pearson correlation of log power over the 51 NON-target frequencies (target set identical for all candidates,
so only the realized fluctuations of the split can discriminate)."""
import json, sys
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools")); sys.path.insert(0, str(LAB / "confirm"))
import confirm_p1 as c
import confirm_splits as cs
from P1_posthoc_within import m0c_add
from rank_tools import spearman
man = json.loads((LAB / "confirm/P1_manifest.json").read_text(encoding="utf-8"))
t = {"task": "add", "p": 113}
N_DECOY = 9
hits, pair, arms = 0, [], 0
hits_nt, pair_nt = 0, []
def nt_score(idx, pw_full, T):
    rest = [k - 1 for k in range(1, 57) if k not in T]
    return float(np.corrcoef(np.log(m0c_add(idx, 113)[rest]), np.log(pw_full[rest]))[0, 1])
for s in man["seeds"]:
    for a in "FG":
        st = c.stem(man, t, s, a)
        T = json.loads((c.SPLITS / f"{st}.json").read_text(encoding="utf-8"))["targets"]; sel = [k - 1 for k in T]
        pw_full = c.power_at(man, t, s, a)
        y = pw_full[sel]
        true = spearman(m0c_add(np.load(c.SPLITS / f"{st}.npy"), 113)[sel], y)
        true_nt = nt_score(np.load(c.SPLITS / f"{st}.npy"), pw_full, T)
        dec, dec_nt = [], []
        for j in range(N_DECOY):
            g = np.random.default_rng(np.random.SeedSequence([2809, s, cs.ARM[a], j]))
            idx = cs.draw("add", 113, T, 2.0, g, g)
            dec.append(spearman(m0c_add(idx, 113)[sel], y))
            dec_nt.append(nt_score(idx, pw_full, T))
        arms += 1
        hits += int(true > max(dec))
        pair.append(float(np.mean([1.0 if true > d else 0.5 if true == d else 0.0 for d in dec])))
        hits_nt += int(true_nt > max(dec_nt))
        pair_nt.append(float(np.mean([true_nt > d for d in dec_nt])))
out = {"arms": arms, "top1_of_10": hits / arms, "chance_top1": 0.1, "pairwise_true_beats_decoy": float(np.mean(pair)), "chance_pairwise": 0.5,
       "nontarget_top1_of_10": hits_nt / arms, "nontarget_pairwise": float(np.mean(pair_nt))}
print(json.dumps(out, indent=1))
(LAB / "confirm/P1_posthoc_split_id.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
