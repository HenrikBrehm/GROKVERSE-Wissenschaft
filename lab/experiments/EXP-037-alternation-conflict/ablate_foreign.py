"""EXP-037 Nachtrag b (descriptive, fixed 2026-09-26 15:14 Berlin before any EXP-037 run): are "foreign" frequencies
functional? For every saved EXP-037 model (A = 5, A = 25, C_F100; seeds 30-32) whose K contains a foreign frequency
(summary.json of analyze.py), remove single frequencies from W_E[:p] (projection as in EXP-016 posthoc_overtone_test.py)
and measure the test loss on the EXP-020 test set.
  dloss(k) = loss(ablate k) - loss(base)
  functional   if dloss(foreign) >= 0.5 * median dloss(non-foreign K members)
  non-functional if dloss(foreign) <= 2 * max dloss(3 fixed random non-K frequencies, rng seed 0)
  else in-between. Only reported, no verdict on H37. Run through guarded_run.py (inference only).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB.parent / "training"))
sys.path.insert(0, str(LAB / "experiments/EXP-001-freq-ban"))
import freq_ban as fb  # noqa: E402
from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.train import evaluate  # noqa: E402

P = 113
B = fb.fourier_basis(P)
S20 = LAB / "experiments/EXP-020-data-switch/splits"
RUNS = {"A5": "_at200_alt5", "A25": "_at200_alt25", "C_F100": "_at100"}


def run_dir(s: int, suffix: str) -> Path:
    return HERE / f"raw/EXP-020_baseline_seed{s}_thr4_seed{s}_train_F_to_seed{s}_train_G{suffix}"


def ablation_row(s: int, arm: str, K: list[int], foreign: list[int]) -> dict:
    cfg = get_config("arch25k", seed=s)
    model = build_model(cfg)
    model.load_state_dict(torch.load(run_dir(s, RUNS[arm]) / "model_final.pt", map_location="cpu"))
    data = make_dataset(cfg)
    te = torch.from_numpy(np.sort(np.load(S20 / f"seed{s}_test.npy")).astype(np.int64))
    tx, ty = data["all_x"][te], data["all_y"][te]
    base = evaluate(model, tx, ty, P)

    def ablate(freq: int) -> float:
        proj = torch.tensor(fb.ban_projector(B, [freq]), dtype=model.W_E.dtype)
        w0 = model.W_E.detach().clone()
        with torch.no_grad():
            model.W_E[:P] = proj @ model.W_E[:P]
        loss = evaluate(model, tx, ty, P)[0]
        with torch.no_grad():
            model.W_E.copy_(w0)
        return loss - base[0]

    rnd = [int(x) for x in np.random.default_rng(0).choice([j for j in range(1, 57) if j not in K], 3, replace=False)]
    d_k = {k: ablate(k) for k in K}
    d_r = {k: ablate(k) for k in rnd}
    others = [d_k[k] for k in K if k not in foreign]
    labels = {}
    for f in foreign:
        if d_k[f] >= 0.5 * float(np.median(others)):
            labels[f] = "functional"
        elif d_k[f] <= 2 * max(d_r.values()):
            labels[f] = "non-functional"
        else:
            labels[f] = "in-between"
    return {"seed": s, "arm": arm, "base_loss": base[0], "base_acc": base[1], "dloss_K": d_k, "dloss_random": d_r,
            "labels": labels}


def main() -> None:
    summ = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
    rows = []
    for arm in RUNS:
        for r in summ[arm]["rows"]:
            if r.get("error") or not r["foreign"]:
                continue
            rows.append(ablation_row(r["seed"], arm, r["K"], r["foreign"]))
            print(rows[-1])
    (HERE / "ablate_foreign.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
