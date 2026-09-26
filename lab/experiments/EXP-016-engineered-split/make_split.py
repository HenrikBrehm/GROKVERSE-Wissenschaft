"""EXP-016: build a training split whose mask spectrum M0 favours a target frequency set F*.

Pair (a, b) enters the training set with weight
    q(a, b) = 1 + eps * mean_{k in F*} cos(2 pi k a / p + phi_{k, a+b})
(random phase per target frequency and anti-diagonal c = a+b; floored at 0.05), sampled without replacement
to exactly the size of the standard 30 % split. Along each anti-diagonal, membership then
oscillates at frequency k in a (and in b = c - a), which is what M0 measures.
Pure numpy, deterministic in --seed. Writes train_idx (flat index a*p + b) as .npy + meta json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-015-mask-spectrum"))

P, TRAIN_FRAC, N_FREQ, M = 113, 0.3, 56, 5
TARGET_SALT = 30_011


ARM_SALT = {"F": 0, "G": 7}      # Nachtrag a: second arm G with a disjoint target set


def target_set(seed: int, arm: str = "F") -> list[int]:
    F = sorted(int(k) for k in np.random.default_rng(seed + TARGET_SALT).choice(
        np.arange(1, N_FREQ + 1), size=M, replace=False))
    if arm == "F":
        return F
    pool = np.setdiff1d(np.arange(1, N_FREQ + 1), F)
    return sorted(int(k) for k in np.random.default_rng(seed + TARGET_SALT + ARM_SALT[arm]).choice(
        pool, size=M, replace=False))


def engineered_train_idx(seed: int, targets: list[int], eps: float, arm: str = "F") -> np.ndarray:
    rng = np.random.default_rng(seed + TARGET_SALT + 1 + ARM_SALT[arm])
    a = np.arange(P).repeat(P)
    b = np.tile(np.arange(P), P)
    phi = rng.uniform(0, 2 * np.pi, size=(len(targets), P))          # per (k, c)
    wave = np.mean([np.cos(2 * np.pi * k * a / P + phi[i, (a + b) % P])
                    for i, k in enumerate(targets)], axis=0)
    q = np.clip(1.0 + eps * wave, 0.05, None)      # eps > 1 needs a floor to stay positive
    n_train = int(round(TRAIN_FRAC * P * P))
    # weighted sampling without replacement via Efraimidis-Spirakis keys
    keys = rng.random(P * P) ** (1.0 / q)
    return np.sort(np.argsort(-keys)[:n_train])


def mask_from_idx(idx: np.ndarray) -> np.ndarray:
    Mk = np.zeros((P, P))
    Mk[idx // P, idx % P] = 1.0
    return Mk


def main() -> None:
    import mask_spectrum as ms
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--eps", type=float, default=1.0)
    ap.add_argument("--arm", choices=tuple(ARM_SALT), default="F")
    ap.add_argument("--out", default=str(HERE / "splits"))
    a = ap.parse_args()
    F = target_set(a.seed, a.arm)
    idx = engineered_train_idx(a.seed, F, a.eps, a.arm)
    pw = ms.m0(mask_from_idx(idx))
    order = np.argsort(-pw, kind="stable")
    top = sorted((order[:M] + 1).tolist())
    rank = np.argsort(order)
    meta = {"seed": a.seed, "eps": a.eps, "arm": a.arm, "targets": F, "M0_top5": top,
            "target_ranks": [int(rank[k - 1]) for k in F], "n_train": int(len(idx)),
            "target_power_share": float(pw[[k - 1 for k in F]].sum() / pw.sum())}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"split_seed{a.seed}_eps{a.eps}" + ("" if a.arm == "F" else f"_{a.arm}")
    np.save(out / f"{stem}.npy", idx)
    (out / f"{stem}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
