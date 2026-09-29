"""Session 52, post hoc: do the non-target frequencies that grow after learning (top-5 at the last snapshot) follow the split's
mask spectrum beyond the five declared targets? Reading fixed before computing (JOURNAL S52 cycle 3): per run, all non-target
top-5 frequencies within the mask's top-10 -> "follows the mask beyond the targets"; none -> "not mask-driven"; else "mixed".
"""
import json, sys
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / "experiments" / "EXP-043-generalize-steering"))
from make_split import mask_power  # noqa: E402
rows = json.loads((Path(__file__).parent / "decline_decomp_s52.json").read_text(encoding="utf-8"))
E104 = LAB / "experiments" / "EXP-104-flat-marginal-splits" / "splits"
E102 = LAB / "experiments" / "EXP-102-lm-ladder-stage1" / "splits"
SPL = {(3950, "F"): E104 / "s3850_F_m500.npy", (3950, "G"): E104 / "s3850_G_m500.npy",
       (3951, "F"): E104 / "s3851_F_m500.npy", (3951, "G"): E104 / "s3851_G_m500.npy",
       (3862, "F"): E102 / "seed3802_F.npy", (3862, "G"): E102 / "seed3802_G.npy"}
out = []
for r in rows:
    m0 = mask_power(np.load(SPL[(r["seed"], r["arm"])]), "add", 113)
    rank = {int(k) + 1: i + 1 for i, k in enumerate(np.argsort(m0)[::-1])}
    last = max(int(s) for s in r["shares"])
    top = r["shares"][str(last)]["top5"]
    nt = [k for k in top if k not in r["own_targets"]]
    inside = [k for k in nt if rank[k] <= 10]
    reading = ("no non-target in top5" if not nt else "follows the mask beyond the targets" if len(inside) == len(nt)
               else "not mask-driven" if not inside else "mixed")
    row = {"set": r["set"], "seed": r["seed"], "arm": r["arm"], "top5_last": top, "non_targets": nt,
           "mask_rank_of_non_targets": {k: rank[k] for k in nt}, "mask_rank_of_own": {k: rank[k] for k in r["own_targets"]},
           "mask_top10": [int(k) + 1 for k in np.argsort(m0)[::-1][:10]], "reading": reading}
    out.append(row); print(json.dumps(row))
Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1), encoding="utf-8")
