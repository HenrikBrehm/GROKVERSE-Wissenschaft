"""EXP-043: engineered splits (EXP-016 construction) for other tasks: add mod 97 and mul mod 113.

The construction lives on the cyclic group on which the task is addition:
  add p : group Z_p, coordinates u = a, v = b (all p*p pairs)
  mul p : group Z_{p-1} via the discrete log to the primitive root g (u = log a, v = log b) for a, b != 0;
          the 2p - 1 pairs with a zero get the neutral weight 1
Pair weight q = max(0.05, 1 + eps * mean_{k in T} cos(2 pi k u / n + phi_{k, (u+v) mod n})), n = group order,
sampled without replacement (Efraimidis-Spirakis) to round(0.3 p^2) pairs, as in EXP-016.
Targets: 5 of k = 1..K (K = (n-1)//2, i.e. the Nyquist mode n/2 of even n is never a target); arm G disjoint.
Separate RNG streams per task and arm (ARM_SALT > seed span; EXP-016 Nachtrag c). Pure numpy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TRAIN_FRAC, M = 0.3, 5
TARGET_SALT = 43_001
ARM_SALT = {"F": 0, "G": 1_000, "R": 2_000}   # R: random reference split (use --eps 0)
TASK_SALT = {"add": 0, "mul": 500_000}
PRIMITIVE_ROOT = {113: 3, 97: 5}


def group(task: str, p: int) -> tuple[int, np.ndarray | None]:
    """Group order n and, for mul, elem[i] = g^i mod p (i = 0..p-2)."""
    if task == "add":
        return p, None
    g = PRIMITIVE_ROOT[p]
    elem = np.array([pow(g, i, p) for i in range(p - 1)])
    if len(set(elem.tolist())) != p - 1:
        raise SystemExit(f"{g} is not a primitive root mod {p}")
    return p - 1, elem


def n_freq(n: int) -> int:
    return (n - 1) // 2


def target_set(seed: int, task: str, p: int, arm: str = "F") -> list[int]:
    K = n_freq(group(task, p)[0])
    base = seed + TARGET_SALT + TASK_SALT[task]
    F = sorted(int(k) for k in np.random.default_rng(base).choice(np.arange(1, K + 1), size=M, replace=False))
    if arm in ("F", "R"):             # R (eps 0) ignores its targets; recorded only for bookkeeping
        return F
    pool = np.setdiff1d(np.arange(1, K + 1), F)
    return sorted(int(k) for k in np.random.default_rng(base + ARM_SALT[arm]).choice(pool, size=M, replace=False))


def group_coords(task: str, p: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """For every flat pair a*p+b: (u, v, valid) in group coordinates; valid = False for mul pairs with a zero."""
    n, elem = group(task, p)
    a, b = np.arange(p).repeat(p), np.tile(np.arange(p), p)
    if elem is None:
        return a, b, np.ones(p * p, bool), n
    log = np.full(p, -1)
    log[elem] = np.arange(n)
    valid = (a != 0) & (b != 0)
    return np.where(valid, log[a], 0), np.where(valid, log[b], 0), valid, n


def engineered_train_idx(seed: int, task: str, p: int, targets: list[int], eps: float, arm: str) -> np.ndarray:
    rng = np.random.default_rng(seed + TARGET_SALT + TASK_SALT[task] + 1 + ARM_SALT[arm])
    u, v, valid, n = group_coords(task, p)
    phi = rng.uniform(0, 2 * np.pi, size=(len(targets), n))
    wave = np.mean([np.cos(2 * np.pi * k * u / n + phi[i, (u + v) % n]) for i, k in enumerate(targets)], axis=0)
    q = np.where(valid, np.clip(1.0 + eps * wave, 0.05, None), 1.0)
    keys = rng.random(p * p) ** (1.0 / q)
    return np.sort(np.argsort(-keys)[:int(round(TRAIN_FRAC * p * p))])


def mask_power(idx: np.ndarray, task: str, p: int) -> np.ndarray:
    """EXP-015 M0 in group coordinates (mul: only pairs without a zero), k = 1..(n-1)//2."""
    u, v, valid, n = group_coords(task, p)
    Mk = np.zeros((n, n))
    sel = np.zeros(p * p, bool)
    sel[idx] = True
    sel &= valid
    Mk[u[sel], v[sel]] = 1.0
    t, c = np.arange(n), np.arange(n)
    other = (c[None, :] - t[:, None]) % n
    left, right = Mk[t[:, None], other], Mk[other, t[:, None]]
    pw = (np.abs(np.fft.fft(left, axis=0)) ** 2 + np.abs(np.fft.fft(right, axis=0)) ** 2).sum(axis=1)
    K = n_freq(n)
    return pw[1:K + 1] + pw[n - K:][::-1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--task", choices=("add", "mul"), required=True)
    ap.add_argument("--p", type=int, required=True)
    ap.add_argument("--eps", type=float, default=2.0)
    ap.add_argument("--arm", choices=tuple(ARM_SALT), default="F")
    ap.add_argument("--out", default=str(HERE / "splits"))
    a = ap.parse_args()
    T = target_set(a.seed, a.task, a.p, a.arm)
    idx = engineered_train_idx(a.seed, a.task, a.p, T, a.eps, a.arm)
    pw = mask_power(idx, a.task, a.p)
    order = np.argsort(-pw, kind="stable")
    rank = np.argsort(order)
    meta = {"seed": a.seed, "task": a.task, "p": a.p, "eps": a.eps, "arm": a.arm, "targets": T,
            "M0_top5": sorted((order[:M] + 1).tolist()), "target_ranks": [int(rank[k - 1]) for k in T],
            "n_train": int(len(idx)), "target_power_share": float(pw[[k - 1 for k in T]].sum() / pw.sum()),
            "n_zero_pairs_in_train": int(np.sum((idx // a.p == 0) | (idx % a.p == 0)))}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"split_{a.task}{a.p}_seed{a.seed}_eps{a.eps}_{a.arm}"
    np.save(out / f"{stem}.npy", idx)
    (out / f"{stem}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
