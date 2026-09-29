"""EXP-121 (session 54): random counterpart with exactly flat counts for the EXP-115 block (flat engineered splits in the LM).

Split Rf per EXP-104 seed s (3850, 3851): S(1, D) = {(a, b): a - b in D} with D a uniformly random 34-subset of Z_113
(numpy default_rng([121, s])), then 500 exact-count swap moves (EXP-104 swap(), rng [121, s, 500]) as for the m500 arms.
Every a, b and c = a + b occurs exactly 34 times, as in s{s}_F_m500 / s{s}_G_m500; no target emphasis in the pair structure.
Test set: the EXP-104 common test set s{s}_test.npy minus the Rf pairs (the trainer asserts disjointness).
  python lab/experiments/EXP-121-lm-flat-random-arm/design.py --splits      # never overwrites
  python lab/experiments/EXP-121-lm-flat-random-arm/design.py --jobs > lab/queue/inbox/37_exp121_flat_random.jobs
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-104-flat-marginal-splits"))
from design import SPL as SPL104, swap  # noqa: E402
from flat_marginal_split_s45 import P, SIZE_D, K, mask_power, split_idx  # noqa: E402

SEEDS = {3850: 3950, 3851: 3951}          # EXP-104 split seed -> EXP-115 model seed
MOVES, STEPS = 500, 4000
PY = "C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe"
SPL = HERE / "splits"


def spectrum_stats(flat: np.ndarray, targets: dict) -> dict:
    pw = mask_power(flat, "add", P)
    share = lambda T: float(sum(pw[t - 1] for t in T) / pw.sum())   # noqa: E731
    top5 = np.sort(pw)[::-1][:5].sum() / pw.sum()
    return {"share_F_targets": share(targets["F"]), "share_G_targets": share(targets["G"]), "top5_share": float(top5)}


def make_splits() -> None:
    SPL.mkdir(exist_ok=True)
    for s in SEEDS:
        D = np.sort(np.random.default_rng([121, s]).choice(P, SIZE_D, replace=False))
        M0 = np.zeros((P, P), bool)
        idx = split_idx(1, D)
        M0[idx // P, idx % P] = True
        M = swap(M0, MOVES, np.random.default_rng([121, s, MOVES]))
        flat = np.flatnonzero(M.ravel()).astype(np.int64)
        test = np.setdiff1d(np.load(SPL104 / f"s{s}_test.npy"), flat).astype(np.int64)
        out, tout = SPL / f"s{s}_Rf_m{MOVES}.npy", SPL / f"s{s}_Rf_test.npy"
        if out.exists() or tout.exists():
            raise SystemExit(f"{out} exists: never overwrite")
        np.save(out, flat)
        np.save(tout, test)
        ref = json.loads((SPL104 / f"s{s}_F_m500.json").read_text(encoding="utf-8"))
        targets = {"F": ref["targets"], "G": ref["other_targets"]}
        meta = {"seed": s, "arm": "Rf", "moves": MOVES, "D": D.tolist(), "n": int(len(flat)), "n_test": int(len(test)),
                "test_removed": int(len(np.load(SPL104 / f"s{s}_test.npy")) - len(test)), **spectrum_stats(flat, targets),
                "ref_F_m500": spectrum_stats(np.load(SPL104 / f"s{s}_F_m500.npy"), targets),
                "ref_G_m500": spectrum_stats(np.load(SPL104 / f"s{s}_G_m500.npy"), targets)}
        (SPL / f"s{s}_Rf_m{MOVES}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        print(json.dumps(meta))


def jobs() -> None:
    print("#! workers=2 job_minutes=240 min_minutes=5 crash_minutes=10 gpu_gb=3.5")
    for s, model_seed in SEEDS.items():
        split = (SPL / f"s{s}_Rf_m{MOVES}.npy").relative_to(LAB.parent).as_posix()
        test = (SPL / f"s{s}_Rf_test.npy").relative_to(LAB.parent).as_posix()
        print(f"{PY} lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py --seed {model_seed} --split-file {split} "
              f"--test-file {test} --steps {STEPS} --arith-facts 19 --loss answer --device cuda "
              f"--out-root lab/experiments/EXP-121-lm-flat-random-arm/raw")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--splits", action="store_true")
    g.add_argument("--jobs", action="store_true")
    a = ap.parse_args()
    make_splits() if a.splits else jobs()
