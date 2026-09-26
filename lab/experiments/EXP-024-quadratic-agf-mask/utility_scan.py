"""EXP-024 (theory check, no training): AGF utility of a single quadratic neuron under a masked loss.

Model (Kunin et al. 2025, one-hot inputs): f(a,b) = sum_n w_n (u_n[a] + v_n[b])^2, MSE on training pairs S.
At small init the residual is the (centred) target, so a neuron's utility with w optimised is
    U(u, v) = || P g ||,   g_c = sum_a M(a, c-a) (u_a + v_{c-a})^2,   P = centring over c.
For a single-frequency feature u_a = cos(w k a + al), v_b = cos(w k b + be) we maximise U over (al, be) and
compare the utility ranking over k with the mask spectrum M0 at k and at fold(2k).
Pure numpy, seconds. Run through guarded_run.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-015-mask-spectrum"))
from mask_spectrum import m0  # noqa: E402

P, K = 113, 56
S16 = LAB / "experiments/EXP-016-engineered-split/splits"


def fold(k: int) -> int:
    k %= P
    return min(k, P - k)


def mask_from_idx(idx: np.ndarray) -> np.ndarray:
    M = np.zeros((P, P))
    M.flat[idx] = 1.0
    return M


def utility(M: np.ndarray, k: int, n_phase: int = 16) -> float:
    a = np.arange(P)
    c = np.arange(P)
    other = (c[None, :] - a[:, None]) % P            # [a, c] -> c - a
    Mac = M[a[:, None], other]                        # M(a, c-a)
    best = 0.0
    for al in np.linspace(0, 2 * np.pi, n_phase, endpoint=False):
        u = np.cos(2 * np.pi * k * a / P + al)
        for be in np.linspace(0, 2 * np.pi, n_phase, endpoint=False):
            v = np.cos(2 * np.pi * k * a / P + be)
            s = (u[:, None] + v[other]) ** 2          # [a, c]
            g = (Mac * s).sum(axis=0)
            g = g - g.mean()
            best = max(best, float(np.linalg.norm(g)))
    return best


def spearman(x, y) -> float:
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def main() -> None:
    out = []
    for seed in range(10, 20):
        for arm, suf in (("F", ""), ("G", "_G")):
            f = S16 / f"split_seed{seed}_eps2.0{suf}.npy"
            meta = json.loads((S16 / f"split_seed{seed}_eps2.0{suf}.json").read_text())
            M = mask_from_idx(np.load(f))
            U = np.array([utility(M, k) for k in range(1, K + 1)])
            spec = m0(M)                                        # index k-1
            spec2 = np.array([spec[fold(2 * k) - 1] for k in range(1, K + 1)])
            top = [int(k) for k in np.argsort(-U)[:5] + 1]
            T = meta["targets"]
            half = sorted(fold(t * 57) for t in T)              # 57 = 2^{-1} mod 113
            row = {"seed": seed, "arm": arm, "targets": T, "half_targets": half, "U_top5": top,
                   "top5_in_targets": len(set(top) & set(T)), "top5_in_half": len(set(top) & set(half)),
                   "rho_U_M0k": spearman(U, spec), "rho_U_M0_2k": spearman(U, spec2),
                   "U_rel_spread": float(U.std() / U.mean())}
            print(json.dumps(row))
            out.append(row)
    (HERE / "utility_scan.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for key in ("top5_in_targets", "top5_in_half", "rho_U_M0k", "rho_U_M0_2k"):
        print(key, float(np.mean([r[key] for r in out])))


if __name__ == "__main__":
    main()
