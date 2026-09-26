"""EXP-046: engineered splits (EXP-016 construction) for composition in the dihedral group D_n (default n = 59).

Pair (a, b), c = a*b. Weight q = max(0.05, 1 + eps * mean_{k in T} tr(A_{k,c} rho_k(a))), A_{k,c} iid Gaussian 2x2,
scaled to unit Frobenius norm, so that tr(A rho_k(a)) has RMS 1/sqrt(2) over a (like cos in EXP-016) and, for each
output c, lies in irrep k as a function of a. Sampled without replacement (Efraimidis-Spirakis) to round(0.3 |G|^2)
pairs. Targets: 5 of the (n-1)/2 two-dim irreps; arm G disjoint; arm R = random reference (--eps 0). Pure numpy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from dihedral import check_group, compose_table, mask_power, n_irrep2, rho

HERE = Path(__file__).resolve().parent
TRAIN_FRAC, M = 0.3, 5
TARGET_SALT = 46_001
ARM_SALT = {"F": 0, "G": 1_000, "R": 2_000}


def target_set(seed: int, n: int, arm: str = "F") -> list[int]:
    K = n_irrep2(n)
    base = seed + TARGET_SALT
    F = sorted(int(k) for k in np.random.default_rng(base).choice(np.arange(1, K + 1), size=M, replace=False))
    if arm in ("F", "R"):
        return F
    pool = np.setdiff1d(np.arange(1, K + 1), F)
    return sorted(int(k) for k in np.random.default_rng(base + ARM_SALT[arm]).choice(pool, size=M, replace=False))


def engineered_train_idx(seed: int, n: int, targets: list[int], eps: float, arm: str) -> np.ndarray:
    check_group(n)
    G = 2 * n
    rng = np.random.default_rng(seed + TARGET_SALT + 1 + ARM_SALT[arm])
    A = rng.standard_normal((len(targets), G, 2, 2))
    A /= np.linalg.norm(A, axis=(2, 3), keepdims=True)
    T = compose_table(n)
    a = np.arange(G).repeat(G)
    c = T.reshape(-1)                                      # flat index a*G+b -> c = a*b
    wave = np.mean([np.einsum("pij,pji->p", A[i, c], rho(n, k)[a]) for i, k in enumerate(targets)], axis=0)
    q = np.clip(1.0 + eps * wave, 0.05, None)
    keys = rng.random(G * G) ** (1.0 / q)
    return np.sort(np.argsort(-keys)[:int(round(TRAIN_FRAC * G * G))])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--n", type=int, default=59)
    ap.add_argument("--eps", type=float, default=2.0)
    ap.add_argument("--arm", choices=tuple(ARM_SALT), default="F")
    ap.add_argument("--out", default=str(HERE / "splits"))
    a = ap.parse_args()
    T = target_set(a.seed, a.n, a.arm)
    idx = engineered_train_idx(a.seed, a.n, T, a.eps, a.arm)
    pw = mask_power(idx, a.n)
    order = np.argsort(-pw, kind="stable")
    rank = np.argsort(order)
    meta = {"seed": a.seed, "group": f"D{a.n}", "n": a.n, "order": 2 * a.n, "eps": a.eps, "arm": a.arm, "targets": T,
            "M0_top5": sorted((order[:M] + 1).tolist()), "target_ranks": [int(rank[k - 1]) for k in T],
            "n_train": int(len(idx)), "target_power_share": float(pw[[k - 1 for k in T]].sum() / pw.sum())}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"split_D{a.n}_seed{a.seed}_eps{a.eps}_{a.arm}"
    np.save(out / f"{stem}.npy", idx)
    (out / f"{stem}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
