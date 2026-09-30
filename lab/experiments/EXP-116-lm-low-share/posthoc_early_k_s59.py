"""Post hoc, session 59 (written and committed before reading any value computed here). Motivation: at the LM1 random init the first
answer-loss gradient of the number rows carries the mask targets with ONE fact per sequence but not with 16 (context mixing,
EXP-127/first_gradient_shuffled*.json). Prediction: stored LM runs with few facts per sequence (K = 2: EXP-105 pilot 'all' loss,
EXP-116 'answer' loss) show number-row steering BEFORE fact learning, runs with K >= 8 (EXP-113 'all'/'answer' K = 8, EXP-114 K = 19,
LM1 K = 19, answer loss) do not. All runs: lm_stage2.py, lr 6e-4, same model; they differ in K, arithmetic token share and loss mode
(confounded, descriptive only, exploration).
Measure: Delta_pow of the raw number-token W_E rows (EXP-127 analyze.power / delta_pow, same as the LM analyses) per stored snapshot.
'Early' = snapshot steps at which the training-fact accuracy of BOTH arms is < 0.1 (curve column train accuracy; snapshot steps and
curve steps coincide, every 250). Per F/G pair: Delta_pow at step 1000 and at the last early step.
Reading (fixed before reading): 'K-abhaengig frueh' if every K = 2 pair has Delta_pow > 0.5 at its last early step and every K >= 8 pair
has <= 0.2 there; 'kein Hinweis' if the K = 2 pairs are all <= 0.2; else 'unklar'.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-116-lm-low-share/posthoc_early_k_s59.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-127-pretrained-lm"))
import analyze as A  # noqa: E402

GROUPS = {  # name: (run root, split dir)
    "EXP-105 K2 all": ("experiments/EXP-105-lm-ladder-stage2/raw_pilot", "experiments/EXP-102-lm-ladder-stage1/splits"),
    "EXP-116 K2 answer": ("experiments/EXP-116-lm-low-share/raw_answer", "experiments/EXP-102-lm-ladder-stage1/splits"),
    "EXP-113 K8 all": ("experiments/EXP-113-lm-ladder-stage2b/raw_all", "experiments/EXP-102-lm-ladder-stage1/splits"),
    "EXP-113 K8 answer": ("experiments/EXP-113-lm-ladder-stage2b/raw_answer", "experiments/EXP-102-lm-ladder-stage1/splits"),
    "EXP-114 K19 answer": ("experiments/EXP-114-lm-dilution-pilot/raw_k19", "experiments/EXP-102-lm-ladder-stage1/splits"),
    "LM1 K19 answer": ("confirm/lm1_raw", "confirm/lm1_splits"),
}


def load(d: Path) -> dict:
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    cols = r["curve_cols"]
    i_s, i_t = cols.index("step"), cols.index("train_fact_acc")      # rows can differ in length (fix before reading any value)
    tr = {int(row[i_s]): float(row[i_t]) for row in r["curve"]}
    W, st = np.load(d / "we_snapshots.npy"), np.load(d / "we_snapshot_steps.npy").astype(int)
    return {"k": r["config"]["arith_facts"], "tr": tr, "W": {int(s): W[i] for i, s in enumerate(st)}}


def main() -> None:
    out, rows = {}, []
    for name, (root, spl) in GROUPS.items():
        runs = {}
        for d in sorted((LAB / root).glob("lm2_seed*_seed*_[FG]_steps*")):
            if not (d / "result.json").exists() or not (d / "we_snapshots.npy").exists():
                continue
            m = re.match(r"lm2_seed(\d+)_seed(\d+)_([FG])_steps", d.name)
            runs.setdefault(int(m.group(2)), {})[m.group(3)] = load(d)
        for s, pr in sorted(runs.items()):
            if set(pr) != {"F", "G"}:
                continue
            tg = json.loads((LAB / spl / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
            F, G = pr["F"], pr["G"]
            common = sorted(set(F["W"]) & set(G["W"]) & set(F["tr"]) & set(G["tr"]))
            dp = {t: A.delta_pow(A.power(F["W"][t]), A.power(G["W"][t]), tg["F"], tg["G"]) for t in common}
            early = [t for t in common if F["tr"][t] < 0.1 and G["tr"][t] < 0.1]
            last = max(early) if early else None
            rows.append({"group": name, "k": F["k"], "split_seed": s, "dpow_1000": dp.get(1000), "last_early_step": last,
                         "dpow_last_early": dp.get(last) if last is not None else None,
                         "first_learn_step": min((t for t in common if t not in early), default=None),
                         "dpow_curve": {t: dp[t] for t in common if t <= 4000 or t % 1000 == 0}})
    k2 = [r["dpow_last_early"] for r in rows if r["k"] == 2]
    k8 = [r["dpow_last_early"] for r in rows if r["k"] >= 8]
    ok = lambda v: v is not None  # noqa: E731
    reading = ("K-abhaengig frueh" if k2 and all(ok(v) and v > 0.5 for v in k2) and all(ok(v) and v <= 0.2 for v in k8)
               else "kein Hinweis" if k2 and all(ok(v) and v <= 0.2 for v in k2) else "unklar")
    out = {"reading": reading, "rows": rows}
    (HERE / "posthoc_early_k_s59.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for r in rows:
        print(r["group"], r["split_seed"], "K", r["k"], "d@1000", r["dpow_1000"], "last early", r["last_early_step"],
              r["dpow_last_early"], "learn from", r["first_learn_step"])
    print(reading)


if __name__ == "__main__":
    main()
