"""EXP-116 analysis (session 51, written before any run; readings in README "Vorab"): the EXP-113 rules for one arm.
EXP-105 pilot analysis (analyze_pilot.py: Delta_pow on the 113 number-token rows; 'K2 haelt im LM' / 'nur Repraesentation' /
'bricht' / 'unklar') with the precedence rule 'nicht gelernt (Budget)' if train-fact accuracy < 0.1 in >= 3 of 4 runs.
Descriptive: first step with held-out accuracy >= 0.5 per run; text wraps per run (expected ~1 at 16 000 steps).
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-116-lm-low-share/analyze.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-105-lm-ladder-stage2"))
import analyze_pilot as AP  # noqa: E402

SPL = "lab/experiments/EXP-102-lm-ladder-stage1/splits"
PAIRS = [f"3864:{SPL}/seed3804_F.npy,{SPL}/seed3804_G.npy", f"3865:{SPL}/seed3805_F.npy,{SPL}/seed3805_G.npy"]


def main() -> None:
    root = HERE / "raw_answer"
    argv, sys.argv = sys.argv, ["analyze_pilot.py", "--root", str(root), "--pairs", *PAIRS]
    try:
        AP.main()
    finally:
        sys.argv = argv
    out = json.loads((root / "pilot_summary.json").read_text(encoding="utf-8"))
    tr = [x for r in out["rows"] for x in r["train_acc"]]
    if sum(x < 0.1 for x in tr) >= len(tr) - 1:
        out["reading"] = "nicht gelernt (Budget)"
    half, wraps = {}, {}
    for d in sorted(root.iterdir()):
        f = d / "result.json"
        if d.is_dir() and f.exists():
            res = json.loads(f.read_text(encoding="utf-8"))
            half[d.name] = next((int(r[0]) for r in res["curve"] if r[2] >= 0.5), None)
            wraps[d.name] = res.get("text_wraps")
    out["first_step_heldout_ge_0.5"], out["text_wraps"] = half, wraps
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
