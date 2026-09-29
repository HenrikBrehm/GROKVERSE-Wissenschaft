"""Session 52, post hoc exploration: decompose the Delta_pow decline of EXP-115 (peak ~2500 -> 4000) into own-target vs
foreign-target energy shares (relative to total number-row energy); compare EXP-114 (P1 splits, no decline).
Reading fixed before computing (JOURNAL S52 cycle 3): per run, (a) "own targets fade" if |d ln share(own)| > |d ln share(foreign)|
between 2500 and the end, else (b) "foreign targets grow". Descriptive only.
"""
import json, sys
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / "experiments" / "EXP-102-lm-ladder-stage1"))
sys.path.insert(0, str(LAB / "experiments" / "EXP-105-lm-ladder-stage2"))
import analyze as A  # noqa: E402
from analyze_pilot import targets  # noqa: E402
E104 = LAB / "experiments" / "EXP-104-flat-marginal-splits" / "splits"
E102 = LAB / "experiments" / "EXP-102-lm-ladder-stage1" / "splits"
SETS = {"EXP-115 flat": (LAB / "experiments" / "EXP-115-lm-flat-marginals" / "raw",
                         [(3950, E104 / "s3850_F_m500.npy", E104 / "s3850_G_m500.npy"),
                          (3951, E104 / "s3851_F_m500.npy", E104 / "s3851_G_m500.npy")]),
        "EXP-114 P1": (LAB / "experiments" / "EXP-114-lm-dilution-pilot" / "raw_k19",
                       [(3862, E102 / "seed3802_F.npy", E102 / "seed3802_G.npy")])}
out = []
for name, (root, pairs) in SETS.items():
    for seed, fF, fG in pairs:
        TF, TG = targets(fF), targets(fG)
        for arm, f, own, foreign in (("F", fF, TF, TG), ("G", fG, TG, TF)):
            d = [x for x in root.iterdir() if x.name.startswith(f"lm2_seed{seed}_{f.stem}_steps")][0]
            W = np.load(d / "we_snapshots.npy"); S = [int(x) for x in np.load(d / "we_snapshot_steps.npy")]
            row = {"set": name, "seed": seed, "arm": arm, "shares": {}}
            for i, s in enumerate(S):
                if s in (1500, 2000, 2500, 3000, 3500, S[-1]):
                    p = A.power(W[i]); tot = p.sum()
                    top = [int(k) + 1 for k in np.argsort(p)[::-1][:5]]
                    row["shares"][s] = {"own": round(float(p[[k - 1 for k in own]].sum() / tot), 4),
                                        "foreign": round(float(p[[k - 1 for k in foreign]].sum() / tot), 4),
                                        "total": round(float(tot), 1), "top5": top}
            a, b = row["shares"][2500], row["shares"][S[-1]]
            do, df = np.log(b["own"] / a["own"]), np.log(b["foreign"] / a["foreign"])
            row.update({"own_targets": own, "foreign_targets": foreign, "dln_own": round(float(do), 3),
                        "dln_foreign": round(float(df), 3),
                        "reading": "own targets fade" if abs(do) > abs(df) else "foreign targets grow"})
            out.append(row); print(json.dumps(row))
Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1), encoding="utf-8")
