"""EXP-113 Nachtrag 1, H-folgt (session 50, written before any run finished; exploration, 2 seeds).
Per loss arm and seed (F/G pair) that learns training facts: s_learn = first snapshot at which BOTH runs have train-fact accuracy
>= 0.1; s_steer = first snapshot with Delta_pow > 1. The pair supports H-folgt if s_steer is None or s_steer >= s_learn.
Reading: 'H-folgt widerlegt' if s_steer < s_learn in at least half of the counted pairs; 'H-folgt haelt' otherwise;
'nicht pruefbar' if no pair learns facts. Pairs without fact learning are listed but not counted.
Snapshots and curve rows share the evaluation steps (every 250 steps, lm_stage2.py EVAL_EVERY).
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-113-lm-ladder-stage2b/analyze_folgt.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-105-lm-ladder-stage2"))
import analyze_pilot as AP  # noqa: E402
sys.path.insert(0, str(LAB / "experiments/EXP-102-lm-ladder-stage1"))
import analyze as A  # noqa: E402

SPL = LAB / "experiments/EXP-102-lm-ladder-stage1/splits"
PAIRS = {3862: ("seed3802_F.npy", "seed3802_G.npy"), 3863: ("seed3803_F.npy", "seed3803_G.npy")}
LEARN, STEER = 0.1, 1.0


def pair(root: Path, seed: int, fF: str, fG: str) -> dict:
    rF, rG = AP.load(root, seed, SPL / fF), AP.load(root, seed, SPL / fG)
    TF, TG = AP.targets(SPL / fF), AP.targets(SPL / fG)
    trF = {int(r[0]): r[1] for r in rF["res"]["curve"]}
    trG = {int(r[0]): r[1] for r in rG["res"]["curve"]}
    steps = [s for s in rF["steps"] if s in rG["P"]]
    dp = {s: A.delta_pow(rF["P"][s], rG["P"][s], TF, TG) for s in steps}
    s_learn = next((s for s in steps if trF.get(s, 0) >= LEARN and trG.get(s, 0) >= LEARN), None)
    s_steer = next((s for s in steps if dp[s] > STEER), None)
    counted = s_learn is not None
    supports = None if not counted else (s_steer is None or s_steer >= s_learn)
    return {"seed": seed, "s_learn": s_learn, "s_steer": s_steer, "counted": counted, "supports": supports,
            "dpow_at_learn": dp.get(s_learn) if counted else None, "dpow_end": dp[steps[-1]], "end_step": steps[-1]}


def main() -> None:
    out = {}
    for loss in ("answer", "all"):
        rows = [pair(HERE / f"raw_{loss}", s, *f) for s, f in PAIRS.items()]
        out[loss] = rows
    rows = [r for v in out.values() for r in v if r["counted"]]
    reading = ("nicht pruefbar" if not rows else
               "H-folgt widerlegt" if sum(not r["supports"] for r in rows) * 2 >= len(rows) else "H-folgt haelt")
    summary = {"reading": reading, "n_counted": len(rows), "pairs": out}
    (HERE / "folgt_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
