"""EXP-125 analysis (session 57, written before any run; readings in README "Vorab"): the EXP-113/116 rules for one arm, applied to the
larger model (d 512, 8 layers). EXP-105 pilot analysis (analyze_pilot.py: Delta_pow on the 113 number-token rows; 'K2 haelt im LM' /
'nur Repraesentation' / 'bricht' / 'unklar') with the precedence rule 'nicht gelernt (Budget)' if train-fact accuracy < 0.1 in >= 3 of 4
runs. Checks that every run really has d 512 / 8 layers / 8 heads. Descriptive: first step with held-out accuracy >= 0.5, n_params.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-125-lm-size/analyze.py
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
PAIRS = [f"3868:{SPL}/seed3808_F.npy,{SPL}/seed3808_G.npy", f"3869:{SPL}/seed3809_F.npy,{SPL}/seed3809_G.npy"]


def main() -> None:
    root = HERE / "raw_d512"
    runs = [d for d in sorted(root.iterdir()) if d.is_dir() and (d / "result.json").exists()]
    if len(runs) != 4:
        raise SystemExit(f"EXP-125: expected 4 runs, found {len(runs)} (nicht auswertbar)")
    info = {}
    for d in runs:
        res = json.loads((d / "result.json").read_text(encoding="utf-8"))
        c = res["config"]
        if (c["d"], c["layers"], c["heads"], c["arith_facts"], c.get("loss"), c["steps"]) != (512, 8, 8, 19, "answer", 6000):
            raise SystemExit(f"EXP-125: {d.name} has the wrong configuration")
        info[d.name] = {"n_params": res.get("n_params"), "text_wraps": res.get("text_wraps"),
                        "first_step_heldout_ge_0.5": next((int(r[0]) for r in res["curve"] if r[2] >= 0.5), None)}
    argv, sys.argv = sys.argv, ["analyze_pilot.py", "--root", str(root), "--pairs", *PAIRS]
    try:
        AP.main()
    finally:
        sys.argv = argv
    out = json.loads((root / "pilot_summary.json").read_text(encoding="utf-8"))
    tr = [x for r in out["rows"] for x in r["train_acc"]]
    if sum(x < 0.1 for x in tr) >= len(tr) - 1:
        out["reading"] = "nicht gelernt (Budget)"
    out["runs"] = info
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
