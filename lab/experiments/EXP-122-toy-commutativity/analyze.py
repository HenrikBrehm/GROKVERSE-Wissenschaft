"""EXP-122 (session 54): in the toy model, is the test accuracy on the grokking plateau of a random split carried by commutativity?
Exploration, written before any run. Models: lab/paper/repro/train.py (bit-identical to freq_ban in the R4 repro) on 4 R4 random
splits whose frozen runs generalized (seed/split/gen step below), trained to 50 % and 90 % of the frozen generalization step
(full batch, constant lr: a shorter run is the prefix of the longer one), --save-model. Test set = complement of the split.
Measure per model: test accuracy on held-out pairs whose swapped pair (b, a) is in the training split (acc_swap) and on the
others (acc_other). Reading at 90 % of the generalization step: 'Kommutativitaet zuerst' if acc_swap - acc_other >= 0.3 in >= 3/4
runs; 'gleichzeitig' if |acc_swap - acc_other| < 0.1 in >= 3/4; else 'teilweise'. 50 % is descriptive.
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-122-toy-commutativity/analyze.py
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

RUNS = [(2600, "r4_u0_s1", 5750), (2601, "r4_u0_s1", 5075), (2603, "r4_u1_s0", 5450), (2603, "r4_u1_s1", 3475)]
FRACS = (0.5, 0.9)
P = 113


def steps_for(gen: int, frac: float) -> int:
    return int(round(frac * gen / 25) * 25)


def main() -> None:
    rows = []
    for seed, split, gen in RUNS:
        cfg = get_config("arch25k", seed=seed, steps=gen, threads=1, p=P, task="add")
        data = make_dataset(cfg)
        tr = np.load(ROOT / "lab/confirm/r4_splits" / f"{split}.npy").astype(np.int64)
        te = np.setdiff1d(np.arange(P * P), tr)
        trs = set(tr.tolist())
        a, b = te // P, te % P
        swap = np.array([int(y) * P + int(x) in trs for x, y in zip(a, b)])
        X, Y = data["all_x"][te], data["all_y"][te]
        for frac in FRACS:
            st = steps_for(gen, frac)
            d = HERE / "raw" / f"seed{seed}_{split}_steps{st}"
            model = build_model(cfg)
            model.load_state_dict(torch.load(d / "model_final.pt", map_location="cpu"))
            model.eval()
            with torch.no_grad():
                pred = model.logits_last(X)[:, :P].argmax(-1)          # as train.py accuracy()
            ok = (pred == Y).numpy()
            logged = json.loads((d / "result.json").read_text(encoding="utf-8"))["final_acc"]["test"]
            r = {"seed": seed, "split": split, "gen_step": gen, "frac": frac, "steps": st, "acc": float(ok.mean()), "logged": logged,
                 "n_swap": int(swap.sum()), "acc_swap": float(ok[swap].mean()), "acc_other": float(ok[~swap].mean())}
            r["diff"] = r["acc_swap"] - r["acc_other"]
            rows.append(r)
            print(json.dumps(r), flush=True)
    at90 = [r for r in rows if r["frac"] == 0.9]
    ok_log = all(abs(r["acc"] - r["logged"]) * (P * P - 3831) <= 2.01 for r in rows)   # CPU eval vs GPU training: <= 2 flips
    if not ok_log:
        reading = "nicht auswertbar (Genauigkeit weicht vom Trainer ab)"
    elif sum(r["diff"] >= 0.3 for r in at90) >= 3:
        reading = "Kommutativitaet zuerst"
    elif sum(abs(r["diff"]) < 0.1 for r in at90) >= 3:
        reading = "gleichzeitig"
    else:
        reading = "teilweise"
    (HERE / "summary.json").write_text(json.dumps({"reading": reading, "rows": rows}, indent=1), encoding="utf-8")
    print(reading)


if __name__ == "__main__":
    main()
