"""Progress view of running EXP-105 pilot runs from their checkpoints (descriptive monitoring only, rule 14; not a reading).
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-105-lm-ladder-stage2/peek_progress.py
"""
import json
import sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-102-lm-ladder-stage1"))
import analyze as A  # noqa: E402

S = HERE.parent / "EXP-102-lm-ladder-stage1/splits"
for m, s in ((3860, 3800), (3861, 3801)):
    T = json.loads((S / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
    ck = {}
    for x in "FG":
        d = [p for p in (HERE / "raw_pilot").iterdir() if p.name.startswith(f"lm2_seed{m}_seed{s}_{x}_")]
        if d and (d[0] / "checkpoint.pt").exists():
            ck[x] = torch.load(d[0] / "checkpoint.pt", map_location="cpu", weights_only=False)
    if len(ck) < 2:
        print(m, "checkpoints missing")
        continue
    steps = [t for t in ck["F"]["snap_steps"] if t in ck["G"]["snap_steps"]]
    for t in steps[::4] + ([steps[-1]] if steps[-1] not in steps[::4] else []):
        pF = A.power(ck["F"]["snaps"][ck["F"]["snap_steps"].index(t)])
        pG = A.power(ck["G"]["snaps"][ck["G"]["snap_steps"].index(t)])
        print(m, t, round(A.delta_pow(pF, pG, T["F"], T["G"]), 3))
    print(m, "last curve F", ck["F"]["curve"][-1][:4], "G", ck["G"]["curve"][-1][:4])
