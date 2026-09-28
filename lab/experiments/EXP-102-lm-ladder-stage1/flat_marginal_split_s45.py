"""Session 45 (numpy only, no training; EXPLORATION of a split construction, written before any run).

Question: can an engineered split for (a + b) mod p concentrate its mask spectrum M0 on five target frequencies while the token
counts of a, b AND c = a + b are exactly flat? Motivation: in a language model (EXP-102 stage 1 tie/all arms, stage 2) the
unigram counts of the number tokens could imprint the targets on W_E without any computation; the EXP-016/P1 splits carry the
targets also in their marginals (count(b) target share 0.225, count(a) 0.165, pba_spectrum_s44.py).

Construction: S(lambda, D) = {(a, b) : a - lambda*b mod p in D}, lambda not in {0, -1}. Every a, every b and every c has exactly |D|
partners (lambda and 1 + lambda invertible mod p). Along an anti-diagonal c the mask is the indicator of D mapped by
a -> (1 + lambda)a - lambda*c, so M0(k) is proportional to |D^(k / (1 + lambda))|^2 (both operand terms). Choose D (|D| = 34, so
|S| = 3842, near the 3831 of P1) as the top-34 residues of a sum of cosines on T' = T / (1 + lambda), phases by random search.

Readings fixed before computing: "usable" if the target share of M0 is at least that of the P1-type engineered split of the same
seed (EXP-102 design, F arm 0.171-0.192) AND all three marginals are exactly flat; "weaker" if flat but the share is lower than
0.171 and above 2x chance (0.089); "not usable" otherwise.
  python lab/experiments/EXP-102-lm-ladder-stage1/flat_marginal_split_s45.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
from make_split import mask_power  # noqa: E402

P, SIZE_D, K = 113, 34, 56


def split_idx(lam: int, D: np.ndarray) -> np.ndarray:
    a, b = np.meshgrid(np.arange(P), np.arange(P), indexing="ij")
    keep = np.isin((a - lam * b) % P, D)
    return (a * P + b)[keep]


def best_D(Tp: list[int], rng: np.random.Generator, tries: int = 400, size: int = SIZE_D) -> np.ndarray:
    x = np.arange(P)
    best, best_val = None, -1.0
    for _ in range(tries):
        ph = rng.uniform(0, 2 * np.pi, len(Tp))
        g = sum(np.cos(2 * np.pi * t * x / P + f) for t, f in zip(Tp, ph))
        D = np.argsort(-g)[:size]
        ind = np.zeros(P)
        ind[D] = 1
        pw = np.abs(np.fft.fft(ind)) ** 2
        val = sum(pw[t] for t in Tp) / pw[1:].sum() * 2
        if val > best_val:
            best, best_val = D, val
    return np.sort(best)


def fold(k: int) -> int:
    k %= P
    return min(k, P - k)


def main() -> None:
    rng = np.random.default_rng(45)
    print("lam  targets            M0 share  count(a,b,c) min/max        n")
    for seed_T in range(5):
        T = sorted(rng.choice(np.arange(1, K + 1), 5, replace=False).tolist())
        for lam in (1, 2, 5):
            inv = pow(1 + lam, -1, P)
            Tp = [fold(t * inv) for t in T]
            D = best_D(Tp, rng)
            idx = split_idx(lam, D)
            m0 = mask_power(idx, "add", P)
            share = sum(m0[t - 1] for t in T) / m0.sum()
            a, b = idx // P, idx % P
            cnt = [np.bincount(v, minlength=P) for v in (a, b, (a + b) % P)]
            mm = [(int(c.min()), int(c.max())) for c in cnt]
            top5 = sorted((np.argsort(-m0)[:5] + 1).tolist())
            print(f"{lam:>3}  {str(T):<18} {share:8.3f}  {mm}  {len(idx)}  top5={top5}")


if __name__ == "__main__":
    main()
