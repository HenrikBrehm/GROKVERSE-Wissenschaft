"""EXP-113 analysis (session 49, written before any run; readings in README "Vorab").
Per loss arm (raw_answer, raw_all): the EXP-105 pilot analysis (analyze_pilot.py: Delta_pow on the 113 number-token rows,
same readings 'K2 haelt im LM' / 'nur Repraesentation' / 'bricht' / 'unklar'), with one precedence rule fixed here:
  'nicht gelernt (Budget)' if the train-fact accuracy is < 0.1 in >= 3 of 4 runs (then no statement about K2).
Descriptive: per seed Delta_pow(answer) - Delta_pow(all) at the end, first step with held-out accuracy >= 0.5 per run.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-113-lm-ladder-stage2b/analyze.py
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
PAIRS = [f"3862:{SPL}/seed3802_F.npy,{SPL}/seed3802_G.npy", f"3863:{SPL}/seed3803_F.npy,{SPL}/seed3803_G.npy"]


def first_half(res: dict) -> int | None:
    return next((int(r[0]) for r in res["curve"] if r[2] >= 0.5), None)


def arm(loss: str) -> dict:
    root = HERE / f"raw_{loss}"
    argv, sys.argv = sys.argv, ["analyze_pilot.py", "--root", str(root), "--pairs", *PAIRS]
    try:
        AP.main()
    finally:
        sys.argv = argv
    out = json.loads((root / "pilot_summary.json").read_text(encoding="utf-8"))
    tr = [x for r in out["rows"] for x in r["train_acc"]]
    if sum(x < 0.1 for x in tr) >= len(tr) - 1:
        out["reading"] = "nicht gelernt (Budget)"
    half = {}
    for spec in PAIRS:
        seed, files = spec.split(":")
        for f in files.split(","):
            r = AP.load(root, int(seed), Path(f))["res"]
            half[f"{seed}_{Path(f).stem}"] = first_half(r)
    out["first_step_test_ge_0.5"] = half
    return out


def main() -> None:
    res = {loss: arm(loss) for loss in ("answer", "all")}
    diff = {str(ra["seed"]): ra["dpow_end"] - rb["dpow_end"] for ra, rb in zip(res["answer"]["rows"], res["all"]["rows"])}
    summary = {"readings": {k: v["reading"] for k, v in res.items()}, "dpow_answer_minus_all": diff,
               "first_step_test_ge_0.5": {k: v["first_step_test_ge_0.5"] for k, v in res.items()},
               "rows": {k: [{kk: vv for kk, vv in r.items() if kk != "dpow_traj"} for r in v["rows"]] for k, v in res.items()}}
    (HERE / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
