"""R4 design check (session 30, before any R4 run; numpy only, no training): how different are the centred coherent mask spectra (M0c)
of the uniform random splits R4 will use, and how large is their natural contrast compared with an engineered P1 split?
Reads nothing from any run. Prints: max/min of M0c over k per split, Spearman between the two splits of a unit (expected ~0),
and the ratio of the top-5 mean to the mean of the other 51 frequencies. For comparison (session 28, quoted, not recomputed): natural
max/min WITHIN the five P1 targets 1.30, strong EXP-082 grading 3.8.

  python lab/confirm/R4_design_lever.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
from confirm_r4 import MAX_UNITS, P, spearman, split_indices  # noqa: E402
from P1_posthoc_within import m0c_add  # noqa: E402


def main() -> None:
    mm, rho, top = [], [], []
    for u in range(MAX_UNITS):
        a, b = m0c_add(split_indices(u, 0), P), m0c_add(split_indices(u, 1), P)
        mm += [a.max() / a.min(), b.max() / b.min()]
        rho.append(spearman(a, b))
        top.append(len(set(np.argsort(a)[-5:]) & set(np.argsort(b)[-5:])))
    mm, rho = np.array(mm), np.array(rho)
    print(f"M0c max/min per split: median {np.median(mm):.2f} (range {mm.min():.2f}-{mm.max():.2f})")
    print(f"Spearman M0c(s1) vs M0c(s2) within a unit: mean {rho.mean():+.3f}, sd {rho.std(ddof=1):.3f} (independent splits -> ~0)")
    print(f"top-5 overlap of M0c between the two splits: mean {np.mean(top):.2f} (chance 25/56 = 0.45)")
    r = []
    for u in range(MAX_UNITS):
        a = m0c_add(split_indices(u, 0), P)
        s = np.sort(a)
        r.append(s[-5:].mean() / s[:-5].mean())
    print(f"mean M0c of the top-5 frequencies / mean of the other 51: median {np.median(r):.2f}")


if __name__ == "__main__":
    main()
