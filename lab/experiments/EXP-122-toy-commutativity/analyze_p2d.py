"""EXP-122 Nachtrag 1 (session 54, written before any run): do engineered splits (P2d, add 113, P1 construction) also pass a
commutativity-first stage? Same measure as analyze.py on 4 frozen P2d runs (seeds 2230/2231, arms F/G), retrained with
lab/paper/repro/train.py to 50 % and 90 % of their frozen generalization step; test set = complement of the split.
Reading at 50 %: 'auch Kommutativitaet zuerst' if acc_other <= 0.1 and acc_swap - acc_other >= 0.3 in >= 3/4 runs;
'ohne Kommutativitaetsphase' if |acc_swap - acc_other| < 0.1 in >= 3/4; else 'teilweise'. 90 % descriptive.
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-122-toy-commutativity/analyze_p2d.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "training"))
from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402
from grokverse.models import build_model  # noqa: E402

RUNS = [(2230, "F", 575), (2230, "G", 1125), (2231, "F", 800), (2231, "G", 1475)]
FRACS, P = (0.5, 0.9), 113


def steps_for(gen: int, frac: float) -> int:
    return int(round(frac * gen / 25) * 25)


def main() -> None:
    rows = []
    for seed, arm, gen in RUNS:
        cfg = get_config("arch25k", seed=seed, steps=gen, threads=1, p=P, task="add")
        data = make_dataset(cfg)
        tr = np.load(ROOT / "lab/confirm/p2d_splits" / f"p2d_seed{seed}_{arm}.npy").astype(np.int64)
        te = np.setdiff1d(np.arange(P * P), tr)
        trs = set(tr.tolist())
        swap = np.array([int(t % P) * P + int(t // P) in trs for t in te])
        X, Y = data["all_x"][te], data["all_y"][te]
        for frac in FRACS:
            st = steps_for(gen, frac)
            d = HERE / "raw_p2d" / f"seed{seed}_{arm}_steps{st}"
            model = build_model(cfg)
            model.load_state_dict(torch.load(d / "model_final.pt", map_location="cpu"))
            model.eval()
            with torch.no_grad():
                pred = model.logits_last(X)[:, :P].argmax(-1)
            ok = (pred == Y).numpy()
            logged = json.loads((d / "result.json").read_text(encoding="utf-8"))["final_acc"]["test"]
            r = {"seed": seed, "arm": arm, "gen_step": gen, "frac": frac, "steps": st, "acc": float(ok.mean()), "logged": logged,
                 "n_swap": int(swap.sum()), "n_test": int(len(te)), "acc_swap": float(ok[swap].mean()), "acc_other": float(ok[~swap].mean())}
            r["diff"] = r["acc_swap"] - r["acc_other"]
            rows.append(r)
            print(json.dumps(r), flush=True)
    at50 = [r for r in rows if r["frac"] == 0.5]
    if not all(abs(r["acc"] - r["logged"]) * r["n_test"] <= 2.01 for r in rows):
        reading = "nicht auswertbar (Genauigkeit weicht vom Trainer ab)"
    elif sum(r["acc_other"] <= 0.1 and r["diff"] >= 0.3 for r in at50) >= 3:
        reading = "auch Kommutativitaet zuerst"
    elif sum(abs(r["diff"]) < 0.1 for r in at50) >= 3:
        reading = "ohne Kommutativitaetsphase"
    else:
        reading = "teilweise"
    (HERE / "summary_p2d.json").write_text(json.dumps({"reading": reading, "rows": rows}, indent=1), encoding="utf-8")
    print(reading)


if __name__ == "__main__":
    main()
