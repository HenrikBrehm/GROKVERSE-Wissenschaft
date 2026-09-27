"""Session 34, post hoc on N29 trajectories (N29_posthoc_decay_s34.json, seeds 2250-2269). Fixed before computing:
If the W_E log power ratio at the switch, D(0) = (L_AB - L_BA)/2 at tau = 0, were the state that decides the outcome, the D(0) values
of t = 25 (all 20 seeds end with the NEW targets, D(+2000) < 0) and t = 50 (all 20 end with the OLD, D(+2000) > 0) would be separable
by one threshold: max D(0)@25 < min D(0)@50. Overlap (some seed at t = 25 has a larger D(0) than some seed at t = 50) means W_E's
spectral lead alone does not decide it (as EXP-060 on seen seeds). Reports: ranges, number of overlapping cross pairs (of 400),
and the best single-threshold accuracy. Descriptive, no training.   python lab/confirm/N29_state_overlap_s34.py"""
import json
from pathlib import Path
import numpy as np
d = json.loads(Path("lab/confirm/N29_posthoc_decay_s34.json").read_text(encoding="utf-8"))["per_seed"]
x25 = np.array([v["0"] for k, v in d.items() if k.endswith("@25")]); x50 = np.array([v["0"] for k, v in d.items() if k.endswith("@50")])
e25 = np.array([v["2000"] for k, v in d.items() if k.endswith("@25")]); e50 = np.array([v["2000"] for k, v in d.items() if k.endswith("@50")])
assert (e25 < 0).all() and (e50 > 0).all()
over = int(sum((a >= b) for a in x25 for b in x50))
allv = np.concatenate([x25, x50]); lab = np.r_[np.zeros(20), np.ones(20)]
best = max(((allv > th) == lab).mean() for th in np.r_[allv, allv.min() - 1])
print(f"D(0)@25 range {x25.min():+.3f}..{x25.max():+.3f} mean {x25.mean():+.3f}; D(0)@50 range {x50.min():+.3f}..{x50.max():+.3f} mean {x50.mean():+.3f}")
print(f"cross pairs with D(0)@25 >= D(0)@50: {over}/400; best single-threshold accuracy {best:.3f}")
