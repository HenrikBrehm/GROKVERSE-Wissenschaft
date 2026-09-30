"""Session 56, post hoc exploration: decompose the Delta_pow decline after the fit onset in EXP-116 (K = 2) and EXP-113 arm
'all' (K = 8) into own-target vs foreign-target energy shares of the number-token rows, as EXP-115 decline_decomp_s52.py.
Reading fixed before computing (JOURNAL S56 cycle 11): per run, between the seed's Delta_pow peak snapshot and the end (EXP-116:
step 15 000, before the text wrap; EXP-113: 16 000), "own targets fade" if |d ln share(own)| > |d ln share(foreign)|, else
"foreign targets grow". Descriptive only.
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-116-lm-low-share/decline_decomp_s56.py
"""
import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB / "experiments" / "EXP-102-lm-ladder-stage1"))
sys.path.insert(0, str(LAB / "experiments" / "EXP-105-lm-ladder-stage2"))
import analyze as A  # noqa: E402
from analyze_pilot import targets  # noqa: E402

E102 = LAB / "experiments" / "EXP-102-lm-ladder-stage1" / "splits"
SETS = {"EXP-116 K2 answer": (LAB / "experiments" / "EXP-116-lm-low-share" / "raw_answer", 15000,
                              [(3864, E102 / "seed3804_F.npy", E102 / "seed3804_G.npy"),
                               (3865, E102 / "seed3805_F.npy", E102 / "seed3805_G.npy")]),
        "EXP-113 K8 all": (LAB / "experiments" / "EXP-113-lm-ladder-stage2b" / "raw_all", 16000,
                           [(3862, E102 / "seed3802_F.npy", E102 / "seed3802_G.npy"),
                            (3863, E102 / "seed3803_F.npy", E102 / "seed3803_G.npy")])}
out = []
for name, (root, end, pairs) in SETS.items():
    for seed, fF, fG in pairs:
        TF, TG = targets(fF), targets(fG)
        load = {}
        for arm, f in (("F", fF), ("G", fG)):
            d = [x for x in root.iterdir() if x.name.startswith(f"lm2_seed{seed}_{f.stem}_steps")]
            assert len(d) == 1, d
            W = np.load(d[0] / "we_snapshots.npy")
            S = [int(x) for x in np.load(d[0] / "we_snapshot_steps.npy")]
            load[arm] = {s: A.power(W[i]) for i, s in enumerate(S) if s <= end}
        steps = sorted(set(load["F"]) & set(load["G"]))
        dp = {s: A.delta_pow(load["F"][s], load["G"][s], TF, TG) for s in steps}
        peak = max((s for s in steps if dp[s] is not None), key=lambda s: dp[s])
        for arm, own, foreign in (("F", TF, TG), ("G", TG, TF)):
            sh = {}
            for s in (peak, end):
                p = load[arm][s]
                tot = p.sum()
                sh[s] = {"own": float(p[[k - 1 for k in own]].sum() / tot), "foreign": float(p[[k - 1 for k in foreign]].sum() / tot),
                         "total": float(tot)}
            do = np.log(sh[end]["own"] / sh[peak]["own"])
            df = np.log(sh[end]["foreign"] / sh[peak]["foreign"])
            row = {"set": name, "seed": seed, "arm": arm, "peak_step": peak, "dpow_peak": round(dp[peak], 3),
                   "dpow_end": round(dp[end], 3), "end_step": end,
                   "share_own": [round(sh[peak]["own"], 4), round(sh[end]["own"], 4)],
                   "share_foreign": [round(sh[peak]["foreign"], 4), round(sh[end]["foreign"], 4)],
                   "total": [round(sh[peak]["total"], 1), round(sh[end]["total"], 1)],
                   "dln_own": round(float(do), 3), "dln_foreign": round(float(df), 3),
                   "reading": "own targets fade" if abs(do) > abs(df) else "foreign targets grow"}
            out.append(row)
            print(json.dumps(row))
Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=1), encoding="utf-8")
