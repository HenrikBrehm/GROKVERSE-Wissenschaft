"""EXP-114 analysis (session 50, written before any run; readings in README 'Vorab'). Exploration, 1 seed.
K19 = this experiment (raw_k19), K8 = EXP-113 raw_answer, both seed 3862 with the P1 splits of seed 3802.
Per pair: Delta_pow per snapshot, s_learn = first snapshot with train-fact accuracy >= 0.1 in F and G, s_steer = first snapshot with
Delta_pow > 1. Facts seen at step s = batch * K * s (every sequence carries K arithmetic sentences).
  'Verduennung gestuetzt'      K19: s_steer < s_learn (or s_steer set and no s_learn), and at equal facts seen Delta_pow(K19) >
                               Delta_pow(K8, interpolated) at every K19 snapshot up to the facts seen at K8's s_learn (or K8's end)
  'Verduennung nicht gestuetzt' K19: Delta_pow <= 1 at every snapshot before s_learn (' (Budget)' if K19 learns no facts)
  else 'unklar'
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-114-lm-dilution-pilot/analyze.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-105-lm-ladder-stage2"))
import analyze_pilot as AP  # noqa: E402
sys.path.insert(0, str(LAB / "experiments/EXP-102-lm-ladder-stage1"))
import analyze as A  # noqa: E402

SPL = LAB / "experiments/EXP-102-lm-ladder-stage1/splits"
SEED, FF, FG = 3862, SPL / "seed3802_F.npy", SPL / "seed3802_G.npy"
LEARN, STEER = 0.1, 1.0


def trace(root: Path) -> dict:
    rF, rG = AP.load(root, SEED, FF), AP.load(root, SEED, FG)
    cfg = rF["res"]["config"]
    per_step = cfg["batch"] * cfg["arith_facts"]
    TF, TG = AP.targets(FF), AP.targets(FG)
    trF = {int(r[0]): r[1] for r in rF["res"]["curve"]}
    trG = {int(r[0]): r[1] for r in rG["res"]["curve"]}
    steps = [s for s in rF["steps"] if s in rG["P"]]
    dp = [A.delta_pow(rF["P"][s], rG["P"][s], TF, TG) for s in steps]
    s_learn = next((s for s in steps if trF.get(s, 0) >= LEARN and trG.get(s, 0) >= LEARN), None)
    s_steer = next((s for s, d in zip(steps, dp) if d > STEER), None)
    return {"K": cfg["arith_facts"], "per_step": per_step, "steps": steps, "facts": [s * per_step for s in steps], "dpow": dp,
            "s_learn": s_learn, "s_steer": s_steer, "train_end": [trF[steps[-1]], trG[steps[-1]]]}


def main() -> None:
    k19 = trace(HERE / "raw_k19")
    k8 = trace(LAB / "experiments/EXP-113-lm-ladder-stage2b/raw_answer")
    assert k19["K"] == 19 and k8["K"] == 8, (k19["K"], k8["K"])
    lim = (k8["s_learn"] if k8["s_learn"] is not None else k8["steps"][-1]) * k8["per_step"]
    pts = [(f, d) for f, d in zip(k19["facts"], k19["dpow"]) if 0 < f <= lim]
    comp = [{"facts": f, "k19": d, "k8": float(np.interp(f, k8["facts"], k8["dpow"]))} for f, d in pts]
    above = bool(comp) and all(c["k19"] > c["k8"] for c in comp)
    sl, ss = k19["s_learn"], k19["s_steer"]
    early = ss is not None and (sl is None or ss < sl)
    before = [d for s, d in zip(k19["steps"], k19["dpow"]) if sl is None or s < sl]
    if early and above:
        reading = "Verdünnung gestützt"
    elif all(d <= STEER for d in before):
        reading = "Verdünnung nicht gestützt" + (" (Budget)" if sl is None else "")
    else:
        reading = "unklar"
    out = {"reading": reading, "k19": k19, "k8": k8, "equal_facts": comp, "k19_above_k8_all": above, "k19_steer_before_learn": early}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("k19", "k8")}, indent=1, ensure_ascii=False))
    print("K19 s_learn/s_steer", sl, ss, "| K8 s_learn/s_steer", k8["s_learn"], k8["s_steer"])


if __name__ == "__main__":
    main()
