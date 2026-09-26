"""EXP-048: engineered splits for NON-modular integer addition a + b (a, b in 0..112, label c = a + b in 0..224).

Same construction as EXP-016/047 with the integer sum instead of the residue:
q(a, b) = max(0.05, 1 + eps * mean_{k in T} cos(2 pi k a / 113 + phi_{k, a+b})), 3831 pairs without replacement
(Efraimidis-Spirakis), test = complement. Targets: 5 of k = 6..56 (k <= 5 excluded: a number line, the known
solution for integer addition (Liu et al. 2022), puts most of its DFT power there); arm G disjoint from F; arm R: eps 0.
Random streams from SeedSequence([SALT, seed, arm, purpose]). M0 (EXP-015 definition, integer version): for every
output c, N_L(t) = [(t, c-t) in train], N_R(t) = [(c-t, t) in train] over t in 0..112 (0 where c-t is out of range),
DFT over t. Pure numpy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P, TRAIN_FRAC, M = 113, 0.3, 5
NC = 2 * P - 1                     # outputs 0..224
KMIN, KMAX = 6, (P - 1) // 2
SALT = 48_001
ARM_ID = {"F": 0, "G": 1, "R": 2}
PURPOSE = {"targets": 0, "pairs": 1}


def rng_for(seed: int, arm: str, purpose: str) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([SALT, seed, ARM_ID[arm], PURPOSE[purpose]]))


def target_sets(seed: int) -> dict[str, list[int]]:
    ks = np.arange(KMIN, KMAX + 1)
    F = sorted(int(k) for k in rng_for(seed, "F", "targets").choice(ks, size=M, replace=False))
    G = sorted(int(k) for k in rng_for(seed, "G", "targets").choice(np.setdiff1d(ks, F), size=M, replace=False))
    return {"F": F, "G": G}


def engineered(seed: int, arm: str, targets: list[int], eps: float) -> np.ndarray:
    rng = rng_for(seed, arm, "pairs")
    a, b = np.arange(P).repeat(P), np.tile(np.arange(P), P)
    phi = rng.uniform(0, 2 * np.pi, size=(len(targets), NC))
    wave = np.mean([np.cos(2 * np.pi * k * a / P + phi[i, a + b]) for i, k in enumerate(targets)], axis=0)
    q = np.clip(1.0 + eps * wave, 0.05, None)
    keys = rng.random(P * P) ** (1.0 / q)
    return np.sort(np.argsort(-keys)[:int(round(TRAIN_FRAC * P * P))])


def mask_power(idx: np.ndarray) -> np.ndarray:
    """Integer-addition M0, k = 1..56 (k and P-k combined)."""
    Mk = np.zeros((P, P))
    Mk[idx // P, idx % P] = 1.0
    t, c = np.arange(P)[:, None], np.arange(NC)[None, :]
    o = c - t
    ok = (o >= 0) & (o < P)
    oc = np.clip(o, 0, P - 1)
    left, right = np.where(ok, Mk[t, oc], 0.0), np.where(ok, Mk[oc, t], 0.0)
    pw = (np.abs(np.fft.fft(left, axis=0)) ** 2 + np.abs(np.fft.fft(right, axis=0)) ** 2).sum(axis=1)
    return pw[1:KMAX + 1] + pw[P - KMAX:][::-1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--arm", choices=tuple(ARM_ID), required=True)
    ap.add_argument("--out", default=str(HERE / "splits"))
    a = ap.parse_args()
    ts = target_sets(a.seed)
    eps = 0.0 if a.arm == "R" else 2.0
    T = ts["F"] if a.arm == "R" else ts[a.arm]          # R: no steering; F targets only for reporting
    idx = engineered(a.seed, a.arm, T, eps)
    if len(idx) != int(round(TRAIN_FRAC * P * P)) or len(np.unique(idx)) != len(idx):
        raise SystemExit("bad split size")
    pw = mask_power(idx)
    rank = np.argsort(np.argsort(-pw, kind="stable"))
    meta = {"seed": a.seed, "arm": a.arm, "eps": eps, "targets": T, "targets_F": ts["F"], "targets_G": ts["G"],
            "n_train": int(len(idx)), "M0_top5": sorted((np.argsort(-pw, kind="stable")[:M] + 1).tolist()),
            "target_ranks": [int(rank[k - 1]) for k in T],
            "target_power_share": float(pw[[k - 1 for k in T]].sum() / pw.sum())}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"split_intadd113_seed{a.seed}_eps{eps}_{a.arm}"      # no Path.with_suffix: '.0_F' would be the suffix
    np.save(out / f"{stem}.npy", idx)
    (out / f"{stem}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(stem, meta["M0_top5"], "targets", T, "ranks", meta["target_ranks"],
          f"share {meta['target_power_share']:.3f}")


if __name__ == "__main__":
    main()
