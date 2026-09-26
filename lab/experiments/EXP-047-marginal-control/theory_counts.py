"""EXP-047 Nachtrag a (session 13, pure numpy, no model): first-order prediction for the count (marginal) component.

Linearized first step at init (softmax ~ uniform u, common Jacobian W_U): grad at W_E row a is
g_a = W_U (n_a u - sum_b m(a,b) e_{a+b}) = -W_U P_perp sum_b m(a,b) e_{a+b}, because sum_c of the target part is n_a.
DFT over a: ||P_perp L_k||^2 = sum_c |L_k(c)|^2 - |n_k|^2 / p  ("centered M0"): the count spectrum is exactly the part
of M0 the first gradient does NOT see. Prints target ranks (0 = top, random 27.5) under raw M0, count spectrum,
centered M0, and the count share of M0, for the EXP-047 splits (seeds 150-159, arms F/G, kinds eng/shuf).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P, K = 113, 56


def spectra(idx: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    M = np.zeros((P, P))
    M[idx // P, idx % P] = 1
    t, c = np.arange(P), np.arange(P)
    other = (c[None, :] - t[:, None]) % P
    FL, FR = np.fft.fft(M[t[:, None], other], axis=0), np.fft.fft(M[other, t[:, None]], axis=0)
    raw = (abs(FL) ** 2 + abs(FR) ** 2).sum(1)
    cnt = abs(np.fft.fft(M.sum(1))) ** 2 + abs(np.fft.fft(M.sum(0))) ** 2
    assert np.allclose(FL.sum(1), np.fft.fft(M.sum(1))), "sum_c L_k(c) must equal the count DFT"
    comb = lambda x: x[1:K + 1] + x[P - K:][::-1]   # noqa: E731
    return comb(raw), comb(cnt), comb(raw - cnt / P)


def rank(pw: np.ndarray, T: list[int]) -> float:
    r = np.argsort(np.argsort(-pw, kind="stable"))
    return float(np.mean([r[k - 1] for k in T]))


def main() -> None:
    for kind in ("eng", "shuf"):
        rows = []
        for s in range(150, 160):
            for arm in "FG":
                stem = HERE / f"splits/split_add113_seed{s}_{kind}_{arm}"
                T = json.loads(stem.with_suffix(".json").read_text(encoding="utf-8"))["targets"]
                raw, cnt, cen = spectra(np.load(stem.with_suffix(".npy")))
                rows.append([rank(raw, T), rank(cnt, T), rank(cen, T), raw[[k - 1 for k in T]].sum() / raw.sum(),
                             cen[[k - 1 for k in T]].sum() / cen.sum(), (cnt / P).sum() / raw.sum()])
        m = np.mean(rows, 0)
        print(f"{kind}: target rank raw M0 {m[0]:.1f}, counts {m[1]:.1f}, centered M0 {m[2]:.1f} (random 27.5); "
              f"target share raw {m[3]:.3f}, centered {m[4]:.3f} (random 0.089); count part of M0 {m[5]:.4f}")


if __name__ == "__main__":
    main()
