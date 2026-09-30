"""Session 56, post hoc descriptive (no reading): in the 10 frozen LM1 seed pairs, how far is Delta_pow at step 6000 below its
maximum over the snapshots? Context for LM3 (measured at the budget end), where EXP-116/113 showed a peak shortly after the fit
onset and a later fall. Uses the frozen LM1 loader (confirm_lm1 imports) read-only.
  python lab/tools/guarded_run.py -- python lab/confirm/LM1_peak_posthoc_s56.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import confirm_lm1 as C  # noqa: E402

rows = []
for s in C.SEEDS:
    rF = C.AP.load(C.RAW, s + C.MODEL_OFFSET, C.SPL / f"seed{s}_F.npy")
    rG = C.AP.load(C.RAW, s + C.MODEL_OFFSET, C.SPL / f"seed{s}_G.npy")
    TF, TG = C.AP.targets(C.SPL / f"seed{s}_F.npy"), C.AP.targets(C.SPL / f"seed{s}_G.npy")
    steps = [x for x in rF["steps"] if x in rG["P"]]
    dp = {x: C.A.delta_pow(rF["P"][x], rG["P"][x], TF, TG) for x in steps}
    peak = max((x for x in steps if dp[x] is not None), key=lambda x: dp[x])
    rows.append({"seed": s, "peak_step": peak, "dpow_peak": round(dp[peak], 3), "dpow_end": round(dp[steps[-1]], 3),
                 "end_over_peak": round(dp[steps[-1]] / dp[peak], 3)})
    print(json.dumps(rows[-1]))
Path(__file__).with_suffix(".json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
