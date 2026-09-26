"""EXP-047: engineered splits (EXP-016 construction, add mod 113) and their marginal-matched shuffles.

eng  : q(a, b) = max(0.05, 1 + eps * mean_{k in T} cos(2 pi k a / p + phi_{k, (a+b) mod p})), eps = 2, 3831 pairs
       without replacement (Efraimidis-Spirakis), exactly as EXP-016/043.
shuf : the same a-list with a random permutation of the b-values, duplicate pairs repaired by random swaps of b between
       pairs. Keeps the token counts of a and of b exactly (so their spectra too), destroys the pair structure.
Targets 5 of k = 1..56; arm G disjoint. Every random stream comes from SeedSequence([SALT, seed, arm, purpose]), so no two
seeds, arms or purposes share a stream (the seed+salt scheme of EXP-016/043 lets seed s's pair stream equal seed s+1's
target stream). Pure numpy.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-043-generalize-steering"))
from make_split import mask_power  # noqa: E402

P, TRAIN_FRAC, M, EPS = 113, 0.3, 5, 2.0
SALT = 47_001
ARM_ID = {"F": 0, "G": 1}
PURPOSE = {"targets": 0, "pairs": 1, "shuffle": 2}


def rng_for(seed: int, arm: str, purpose: str) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([SALT, seed, ARM_ID[arm], PURPOSE[purpose]]))


def target_sets(seed: int) -> dict[str, list[int]]:
    K = (P - 1) // 2
    F = sorted(int(k) for k in rng_for(seed, "F", "targets").choice(np.arange(1, K + 1), size=M, replace=False))
    pool = np.setdiff1d(np.arange(1, K + 1), F)
    G = sorted(int(k) for k in rng_for(seed, "G", "targets").choice(pool, size=M, replace=False))
    return {"F": F, "G": G}


def engineered(seed: int, arm: str, targets: list[int]) -> np.ndarray:
    rng = rng_for(seed, arm, "pairs")
    a, b = np.arange(P).repeat(P), np.tile(np.arange(P), P)
    phi = rng.uniform(0, 2 * np.pi, size=(len(targets), P))
    wave = np.mean([np.cos(2 * np.pi * k * a / P + phi[i, (a + b) % P]) for i, k in enumerate(targets)], axis=0)
    q = np.clip(1.0 + EPS * wave, 0.05, None)
    keys = rng.random(P * P) ** (1.0 / q)
    return np.sort(np.argsort(-keys)[:int(round(TRAIN_FRAC * P * P))])


def shuffled(idx: np.ndarray, seed: int, arm: str, max_iter: int = 200_000) -> np.ndarray:
    rng = rng_for(seed, arm, "shuffle")
    a, b = idx // P, rng.permutation(idx % P)
    for _ in range(max_iter):
        flat = a * P + b
        _, inv, cnt = np.unique(flat, return_inverse=True, return_counts=True)
        dup = np.flatnonzero(cnt[inv] > 1)
        if not len(dup):
            out = np.sort(flat)
            for part in (lambda x: x // P, lambda x: x % P):   # fail closed: both marginals exactly preserved
                if not np.array_equal(np.bincount(part(out), minlength=P), np.bincount(part(idx), minlength=P)):
                    raise SystemExit("marginal changed")
            return out
        i, j = rng.choice(dup), rng.integers(len(b))
        b[i], b[j] = b[j], b[i]
    raise SystemExit("duplicate repair did not converge")


def count_rank(idx: np.ndarray, T: list[int]) -> float:
    """Mean rank (0 = strongest) of the targets in the DFT power of the a- and b-token counts."""
    cnt = np.stack([np.bincount(idx // P, minlength=P), np.bincount(idx % P, minlength=P)], 1).astype(float)
    pw = (np.abs(np.fft.fft(cnt - cnt.mean(0), axis=0)) ** 2).sum(1)[1:(P - 1) // 2 + 1]
    r = np.argsort(np.argsort(-pw, kind="stable"))
    return float(np.mean([r[k - 1] for k in T]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", default=str(HERE / "splits"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    T = target_sets(a.seed)
    for arm in "FG":
        eng = engineered(a.seed, arm, T[arm])
        for kind, idx in (("eng", eng), ("shuf", shuffled(eng, a.seed, arm))):
            pw = mask_power(idx, "add", P)
            r = np.argsort(np.argsort(-pw, kind="stable"))
            meta = {"seed": a.seed, "arm": arm, "kind": kind, "targets": T[arm], "n_train": int(len(idx)),
                    "M0_target_rank_mean": float(np.mean([r[k - 1] for k in T[arm]])),
                    "M0_target_share": float(pw[[k - 1 for k in T[arm]]].sum() / pw.sum()),
                    "count_target_rank_mean": count_rank(idx, T[arm])}
            stem = f"split_add113_seed{a.seed}_{kind}_{arm}"
            np.save(out / f"{stem}.npy", idx)
            (out / f"{stem}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
            print(json.dumps(meta))


if __name__ == "__main__":
    main()
