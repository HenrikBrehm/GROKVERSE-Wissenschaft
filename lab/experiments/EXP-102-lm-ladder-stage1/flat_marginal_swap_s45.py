"""Session 45, second follow-up to flat_marginal_split_s45.py (numpy only, exploration; readings fixed before computing).

Goal: exactly flat counts of a, b, c AND no translation symmetry. Move (derived before computing): remove (a1,b1), (a2,b2), (a3,b3)
from S and add (a1,b2), (a2,b3), (a3,b1). Rows and columns keep their counts; the sums keep their multiset iff
b3 = a1 + b1 - a2 and b2 = a3 + b1 - a2 (mod p) (then a1+b2 = a3+b3, a2+b3 = a1+b1, a3+b1 = a2+b2). A move is valid if the three
removed pairs are in S, the three added ones are not, and all six are distinct. Start: S(1, D), |D| = 34.
Measured after m accepted moves (m = 0, 10, 50, 200, 500): exact flatness (asserted), M0 target share, top-5 of M0 vs targets,
number of translations mapping S onto itself.
Readings: "flat and symmetry-free, usable" at the smallest m with translations == 1, if the share there is >= 0.171 (P1 level);
otherwise "symmetry breaking costs the steering". Also reported: the share at m = 500 (how fast the steering decays).
  python lab/experiments/EXP-102-lm-ladder-stage1/flat_marginal_swap_s45.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from flat_marginal_mix_s45 import n_translations  # noqa: E402
from flat_marginal_split_s45 import K, P, best_D, fold, mask_power, split_idx  # noqa: E402

CHECKPOINTS = (0, 10, 50, 200, 500)


def counts_flat(M: np.ndarray) -> bool:
    a, b = np.nonzero(M)
    cs = [np.bincount(v, minlength=P) for v in (a, b, (a + b) % P)]
    return all(c.min() == c.max() for c in cs)


def run(T: list[int], rng: np.random.Generator) -> None:
    D = best_D([fold(t * pow(2, -1, P)) for t in T], rng)
    M = np.zeros((P, P), bool)
    idx = split_idx(1, D)
    M[idx // P, idx % P] = True
    pairs = np.argwhere(M)
    accepted, tries = 0, 0
    for target_m in CHECKPOINTS:
        while accepted < target_m:
            tries += 1
            i, j = rng.choice(len(pairs), 2, replace=False)
            (a1, b1), (a2, b2) = pairs[i], pairs[j]
            a3 = (a2 + b2 - b1) % P          # from b2 = a3 + b1 - a2
            b3 = (a1 + b1 - a2) % P
            rem = [(a1, b1), (a2, b2), (a3, b3)]
            add = [(a1, b2), (a2, b3), (a3, b1)]
            if len(set(rem + add)) < 6 or not M[a3, b3] or any(M[x, y] for x, y in add):
                continue
            for x, y in rem:
                M[x, y] = False
            for x, y in add:
                M[x, y] = True
            pairs = np.argwhere(M)
            accepted += 1
        assert counts_flat(M), "flatness broken"
        cur = np.flatnonzero(M.ravel())
        m0 = mask_power(cur, "add", P)
        share = sum(m0[t - 1] for t in T) / m0.sum()
        top = sorted((np.argsort(-m0)[:5] + 1).tolist())
        print(f"{str(T):<18} m={target_m:>3}  share={share:.3f}  top5=targets:{top == T}  translations={n_translations(cur)}"
              f"  |S|={len(cur)}  tries={tries}")


def main() -> None:
    rng = np.random.default_rng(4546)
    for _ in range(3):
        run(sorted(rng.choice(np.arange(1, K + 1), 5, replace=False).tolist()), rng)


if __name__ == "__main__":
    main()
