"""Session 50, post hoc EXPLORATION on seen data (EXP-103 part A: P1 preset add 113, seeds 1000-1049, spectra at 10, 25, 50,
..., 250 steps, dense train accuracy every 10 steps). Question: is the LM pattern 'steering arrives with fact learning'
(EXP-113 peek, EXP-114) really different from the toy model, if 'learning' means TRAINING accuracy (memorization), as in the LM
definition (s_learn = first snapshot with train accuracy >= 0.1 in F and G; s_steer = first snapshot with Delta_pow > 1)?
Written before looking at the toy train-accuracy / Delta_pow ordering (one seed's dense train curve was seen: 0.1 at ~step 55).
Expectation stated before the run: if toy steering is driven by the mask before any memorization, s_steer < s_learn in most seeds;
if steering needs the model to fit the training pairs first (as in the LM), s_steer >= s_learn in most seeds.
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-114-lm-dilution-pilot/toy_order_s50.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
RAW = LAB / "experiments/EXP-103-early-steering-curve/raw"


def delta(pF, pG, F, G):
    s = lambda pw, S: pw[..., [k - 1 for k in S]].sum(-1)   # noqa: E731  (as EXP-103 analyze.delta)
    return float(np.log(s(pF, F) / s(pF, G)) + np.log(s(pG, G) / s(pG, F)))


def main() -> None:
    rows = []
    for s in range(1000, 1050):
        T = {a: json.loads((LAB / f"confirm/splits/confirm_exp1_eps2.0_add113_seed{s}_{a}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
        d = {a: RAW / f"EXP-016_baseline_seed{s}_thr1_confirm_exp1_eps2.0_add113_seed{s}_{a}_devcuda" for a in "FG"}
        st = [int(x) for x in np.load(d["F"] / "spectra_steps.npy")]
        assert st == [int(x) for x in np.load(d["G"] / "spectra_steps.npy")]
        sp = {a: np.load(d[a] / "spectra.npy") for a in "FG"}
        dense = {a: json.loads((d[a] / "result.json").read_text(encoding="utf-8"))["dense"] for a in "FG"}
        tr = {a: dict(zip(dense[a]["train_steps"], dense[a]["train_acc"])) for a in "FG"}
        dp = {t: delta(sp["F"][i], sp["G"][i], T["F"], T["G"]) for i, t in enumerate(st)}
        s_learn = next((t for t in st if tr["F"].get(t, 0) >= 0.1 and tr["G"].get(t, 0) >= 0.1), None)
        s_steer = next((t for t in st if dp[t] > 1), None)
        rows.append({"seed": s, "s_learn": s_learn, "s_steer": s_steer, "dpow_at_learn": dp.get(s_learn),
                     "train_at_steer": [tr["F"].get(s_steer), tr["G"].get(s_steer)] if s_steer else None})
    before = sum(r["s_steer"] is not None and r["s_learn"] is not None and r["s_steer"] < r["s_learn"] for r in rows)
    out = {"n": len(rows), "n_steer_before_learn": before, "steps": st,
           "median_s_learn": float(np.median([r["s_learn"] for r in rows if r["s_learn"] is not None])),
           "median_s_steer": float(np.median([r["s_steer"] for r in rows if r["s_steer"] is not None])),
           "median_dpow_at_learn": float(np.median([r["dpow_at_learn"] for r in rows if r["dpow_at_learn"] is not None])),
           "rows": rows}
    (HERE / "toy_order_s50.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
