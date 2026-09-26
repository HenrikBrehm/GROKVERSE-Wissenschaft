"""Post hoc (session 5): which targets are displaced between step 250 (overlap 5/5 everywhere) and step 2000?
H (before computing): dropped targets are more often than chance the target with the lowest mask power M0 (rank 5 of 5
among the targets) or the lowest init power E0. Also: power rank among targets at step 250.
Reads EXP-016 spectra (seeds 10-15) and the split files; E0 from the step-0 spectrum. No training."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-015-mask-spectrum"))
import mask_spectrum as ms  # noqa: E402
from make_split import mask_from_idx  # noqa: E402

rows = []
for s in range(10, 16):
    for suf, arm in (("", "F"), ("_G", "G")):
        stem = f"split_seed{s}_eps2.0{suf}"
        T = sorted(json.loads((HERE / f"splits/{stem}.json").read_text())["targets"])
        d = HERE / f"raw/EXP-016_baseline_seed{s}_thr4_{stem}"
        sp, st = np.load(d / "spectra.npy"), list(np.load(d / "spectra_steps.npy"))
        top = lambda x: {int(k) + 1 for k in np.argsort(-sp[st.index(x)])[:5]}
        dropped = sorted(set(T) - top(2000))
        m0 = ms.m0(mask_from_idx(np.load(HERE / f"splits/{stem}.npy")))
        rank_among = lambda pw: {k: sorted(T, key=lambda j: -pw[j - 1]).index(k) + 1 for k in T}  # 1 = strongest
        rM, rE, r250 = rank_among(m0), rank_among(sp[0]), rank_among(sp[st.index(250)])
        rows.append({"seed": s, "arm": arm, "dropped": dropped, "M0_rank": [rM[k] for k in dropped],
                     "E0_rank": [rE[k] for k in dropped], "rank_at_250": [r250[k] for k in dropped]})
for r in rows:
    print(r)
n = sum(len(r["dropped"]) for r in rows)
summ = {"n_dropped": n, "chance_rank5": n / 5}
for key in ("M0_rank", "E0_rank", "rank_at_250"):
    ranks = [x for r in rows for x in r[key]]
    summ[key] = {"mean": float(np.mean(ranks)) if ranks else None, "n_lowest(5)": sum(x == 5 for x in ranks),
                 "n_bottom2": sum(x >= 4 for x in ranks)}
print(json.dumps(summ, indent=1))
(HERE / "posthoc_dropped_targets.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1))
