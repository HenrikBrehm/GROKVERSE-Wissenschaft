"""Session 45 follow-up to flat_marginal_split_s45.py (numpy only, exploration, readings fixed before computing).

Risk found after the first computation: S(lambda, D) is invariant under the translations (a, b) -> (a + lambda*s, b + s), a
subgroup of order p. Tomas Bernal, Mallinar, Belkin 2026 (arXiv 2604.00316) report that RFM fails to generalize on train/test
partitions invariant under a non-singleton subgroup. Symmetry-broken variant: S = S(l1, D1) u S(l2, D2), |D1| = |D2| = 17.
Measured: (1) marginal flatness of a, b, c (min/max counts), (2) M0 target share, (3) the number of translations (u, v) != 0 that
map S onto itself (1 = only the identity, i.e. no translation symmetry left), (4) |S|.
Readings: "symmetry broken, usable" if (3) == 1, share >= 0.171 and counts within +-20 % of the mean; otherwise report as is.
  python lab/experiments/EXP-102-lm-ladder-stage1/flat_marginal_mix_s45.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from flat_marginal_split_s45 import P, K, best_D, fold, mask_power, split_idx  # noqa: E402


def n_translations(idx: np.ndarray) -> int:
    M = np.zeros((P, P), bool)
    M[idx // P, idx % P] = True
    count = 0
    for u in range(P):
        Mu = np.roll(M, u, axis=0)
        for v in range(P):
            if np.array_equal(np.roll(Mu, v, axis=1), M):
                count += 1
    return count


def main() -> None:
    rng = np.random.default_rng(4545)
    print("targets            l1,l2  share   count a/b/c min-max        |S|  translations")
    for _ in range(4):
        T = sorted(rng.choice(np.arange(1, K + 1), 5, replace=False).tolist())
        for l1, l2 in ((1, 2), (1, 5)):
            parts = []
            for lam in (l1, l2):
                inv = pow(1 + lam, -1, P)
                D = best_D([fold(t * inv) for t in T], rng, size=17)
                parts.append(split_idx(lam, D))
            idx = np.unique(np.concatenate(parts))
            m0 = mask_power(idx, "add", P)
            share = sum(m0[t - 1] for t in T) / m0.sum()
            a, b = idx // P, idx % P
            mm = [(int(c.min()), int(c.max())) for c in (np.bincount(v, minlength=P) for v in (a, b, (a + b) % P))]
            print(f"{str(T):<18} {l1},{l2}   {share:.3f}  {mm}  {len(idx)}  {n_translations(idx)}")
    single = split_idx(1, best_D([fold(t * pow(2, -1, P)) for t in T], rng))
    print("reference single family, translations:", n_translations(single))


if __name__ == "__main__":
    main()
