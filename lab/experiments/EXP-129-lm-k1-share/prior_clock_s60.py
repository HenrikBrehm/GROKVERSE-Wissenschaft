"""EXP-129 prior (session 60, post hoc on stored runs, descriptive; reading fixed before reading the EXP-113 curves):
answer-loss runs with K = 8 (EXP-113 raw_answer, seeds 3862/3863, 16 000 steps) vs K = 2 (EXP-116, seeds 3864/3865).
Per run: first step with held-out accuracy >= 0.5 and exposures per fact at that step (K * 32 * step / n_facts).
Reading (descriptive, different seeds/splits): 'eher Schritte' if the median onset STEP of K = 8 is within x1.5 of K = 2
while the median EXPOSURES differ by >= x2; 'eher Wiederholungen' if the median EXPOSURES are within x1.5 while the steps
differ by >= x2; otherwise 'unklar'. Runs that never reach 0.5 are reported and excluded from medians.
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-129-lm-k1-share/prior_clock_s60.py"""
import json
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[2]
SETS = {8: LAB / "experiments/EXP-113-lm-ladder-stage2b/raw_answer", 2: LAB / "experiments/EXP-116-lm-low-share/raw_answer"}
out = {}
for k, root in SETS.items():
    rows = []
    for d in sorted(root.iterdir()):
        f = d / "result.json"
        if not (d.is_dir() and f.exists()):
            continue
        res = json.loads(f.read_text(encoding="utf-8"))
        n = len(np.load(LAB.parent / res["config"]["split_file"])) if "split_file" in res["config"] else 3831
        t = next((int(r[0]) for r in res["curve"] if r[2] >= 0.5), None)
        rows.append({"run": d.name.split("_steps")[0], "n_facts": n, "onset_step": t,
                     "onset_exposures": None if t is None else k * 32 * t / n})
    out[k] = rows
med = {k: (float(np.median([r["onset_step"] for r in v if r["onset_step"]])),
           float(np.median([r["onset_exposures"] for r in v if r["onset_step"]]))) for k, v in out.items()}
rs, re_ = med[2][0] / med[8][0], med[8][1] / med[2][1]
reading = ("eher Schritte" if max(rs, 1 / rs) <= 1.5 and max(re_, 1 / re_) >= 2 else
           "eher Wiederholungen" if max(re_, 1 / re_) <= 1.5 and max(rs, 1 / rs) >= 2 else "unklar")
res = {"runs": out, "median_step_exposures": med, "ratio_steps_k2_over_k8": rs, "ratio_exposures_k8_over_k2": re_, "reading": reading}
(Path(__file__).with_suffix(".json")).write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps(res, indent=1))
