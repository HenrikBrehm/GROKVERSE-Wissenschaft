"""EXP-104 (exploration, N53): splits and job lines. numpy only, no training; run without the guard.

Per seed (3850, 3851): ten distinct target frequencies drawn from 1..56 (first five F, last five G), for each arm the flat split
S(1, D) of flat_marginal_split_s45.py, then m random swap moves (m = 0, 10, 500) that keep the counts of a, b and c exactly flat.
Test set = complement (freq_ban default). Writes splits/s{seed}_{arm}_m{m}.npy + .json and prints the job lines.
  python lab/experiments/EXP-104-flat-marginal-splits/design.py --splits
  python lab/experiments/EXP-104-flat-marginal-splits/design.py --jobs > lab/experiments/EXP-104-flat-marginal-splits/jobs.txt
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-102-lm-ladder-stage1"))
from flat_marginal_split_s45 import K, P, best_D, fold, mask_power, split_idx  # noqa: E402

SEEDS, MOVES, ARMS = (3850, 3851), (0, 10, 500), ("F", "G")
STEPS, SPECTRA_AT = 8000, "250,2000"
PY = "C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe"
SPL, RAW = HERE / "splits", HERE / "raw"


def targets(seed: int) -> dict[str, list[int]]:
    t = np.random.default_rng([104, seed]).choice(np.arange(1, K + 1), 10, replace=False).tolist()
    return {"F": sorted(t[:5]), "G": sorted(t[5:])}


def swap(M: np.ndarray, m: int, rng: np.random.Generator) -> np.ndarray:
    """m accepted moves (a1,b1),(a2,b2),(a3,b3) -> (a1,b2),(a2,b3),(a3,b1); counts of a, b, a+b stay exact (asserted)."""
    M = M.copy()
    done = 0
    while done < m:
        pairs = np.argwhere(M)
        (a1, b1), (a2, b2) = pairs[rng.choice(len(pairs), 2, replace=False)]
        a3, b3 = (a2 + b2 - b1) % P, (a1 + b1 - a2) % P
        rem, add = [(a1, b1), (a2, b2), (a3, b3)], [(a1, b2), (a2, b3), (a3, b1)]
        if len(set(map(tuple, rem + add))) < 6 or not M[a3, b3] or any(M[x, y] for x, y in add):
            continue
        for x, y in rem:
            M[x, y] = False
        for x, y in add:
            M[x, y] = True
        done += 1
    a, b = np.nonzero(M)
    assert all(np.ptp(np.bincount(v, minlength=P)) == 0 for v in (a, b, (a + b) % P))
    return M


def make_splits() -> None:
    SPL.mkdir(exist_ok=True)
    for seed in SEEDS:
        T = targets(seed)
        for arm in ARMS:
            rng = np.random.default_rng([104, seed, ARMS.index(arm)])
            D = best_D([fold(t * pow(2, -1, P)) for t in T[arm]], rng)
            M0 = np.zeros((P, P), bool)
            idx = split_idx(1, D)
            M0[idx // P, idx % P] = True
            for m in MOVES:
                M = swap(M0, m, np.random.default_rng([104, seed, ARMS.index(arm), m]))
                flat = np.flatnonzero(M.ravel()).astype(np.int64)
                out = SPL / f"s{seed}_{arm}_m{m}.npy"
                if out.exists():
                    raise SystemExit(f"{out} exists: never overwrite")
                np.save(out, flat)
                pw = mask_power(flat, "add", P)
                meta = {"seed": seed, "arm": arm, "moves": m, "targets": T[arm], "other_targets": T["G" if arm == "F" else "F"],
                        "lambda": 1, "D": D.tolist(), "n": int(len(flat)),
                        "m0_target_share": float(sum(pw[t - 1] for t in T[arm]) / pw.sum())}
                (SPL / f"s{seed}_{arm}_m{m}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
                print(out.name, len(flat), round(meta["m0_target_share"], 3))


def jobs() -> None:
    for seed in SEEDS:
        for m in MOVES:
            for arm in ARMS:
                split = (SPL / f"s{seed}_{arm}_m{m}.npy").relative_to(LAB.parent).as_posix()
                print(f"{PY} lab/experiments/EXP-001-freq-ban/freq_ban.py --seed {seed} --condition baseline --threads 1 "
                      f"--device cuda --out-root {RAW.relative_to(LAB.parent).as_posix()} --steps {STEPS} --split-file {split} "
                      f"--spectra-at {SPECTRA_AT}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--splits", action="store_true")
    g.add_argument("--jobs", action="store_true")
    a = ap.parse_args()
    make_splits() if a.splits else jobs()
