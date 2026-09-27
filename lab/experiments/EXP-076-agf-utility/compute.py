"""EXP-076 (theory computation, no training): AGF first-step utility per frequency with a pair mask vs the mask spectrum M0.
Definition: README.md (fixed before the first computation). Pure numpy.

Model: f(a, b) = w . (u_a + v_b)^2, one-hot inputs over Z_p, centred target e_(a+b), data = pairs in S. Utility of one neuron at vanishing init:
U(u, v, w) = sum_{(a,b) in S} w_(a+b) (u_a + v_b)^2. Single-frequency ansatz at k: u, v, w in span{cos, sin}(2 pi k . / p).
U_k = 2/(3 sqrt 3) * max_phi lambda_max(cos phi M1 + sin phi M2), M_j = sum_S B_j(a+b) z z^T, z = [B(a); B(b)].
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
from make_split import mask_power  # noqa: E402  (EXP-015 M0 in group coordinates)

P = 113
K = (P - 1) // 2
PHI = np.linspace(0.0, 2 * np.pi, 721)[:-1]
CONST = 2.0 / (3.0 * np.sqrt(3.0))


def basis(k: int) -> np.ndarray:
    x = np.arange(P)
    B = np.stack([np.cos(2 * np.pi * k * x / P), np.sin(2 * np.pi * k * x / P)], 1)
    return B / np.linalg.norm(B, axis=0)


def utility(idx: np.ndarray) -> np.ndarray:
    a, b = idx // P, idx % P
    out = np.empty(K)
    for k in range(1, K + 1):
        B = basis(k)
        Z = np.concatenate([B[a], B[b]], 1)                     # [n, 4]
        W = B[(a + b) % P]                                      # [n, 2]
        M = [Z.T @ (Z * W[:, j:j + 1]) for j in range(2)]       # two 4x4 symmetric matrices
        stack = np.cos(PHI)[:, None, None] * M[0][None] + np.sin(PHI)[:, None, None] * M[1][None]
        out[k - 1] = CONST * float(np.linalg.eigvalsh(stack)[:, -1].max())
    return out


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    def rank(v: np.ndarray) -> np.ndarray:
        o = np.argsort(v, kind="stable")
        r = np.empty(len(v))
        r[o] = np.arange(len(v))
        for u in np.unique(v):
            r[v == u] = r[v == u].mean()
        return r
    return float(np.corrcoef(rank(x), rank(y))[0, 1])


def top5(v: np.ndarray) -> set[int]:
    return set((np.argsort(-v, kind="stable")[:5] + 1).tolist())


def selftest() -> None:
    U = utility(np.arange(P * P))                               # all pairs: every frequency ties (one-hot, uniform data)
    assert np.allclose(U, U[0], rtol=1e-9), (U.min(), U.max())
    print(f"[exp076] selftest ok: uniform data -> all U_k equal ({U[0]:.4f})", flush=True)


def main() -> None:
    selftest()
    rows = []
    spl = LAB / "experiments/EXP-016-engineered-split/splits"
    for s in range(10, 20):
        for arm, suf in (("F", ""), ("G", "_G")):
            idx = np.load(spl / f"split_seed{s}_eps2.0{suf}.npy")
            T = set(json.loads((spl / f"split_seed{s}_eps2.0{suf}.json").read_text(encoding="utf-8"))["targets"])
            U, M0 = utility(idx), mask_power(idx, "add", P)
            rows.append({"split": f"{s}{arm}", "rho": spearman(U, M0), "hits_U": len(top5(U) & T), "hits_M0": len(top5(M0) & T),
                         "top5_U": sorted(top5(U)), "targets": sorted(T)})
            print(rows[-1], flush=True)
    rng = np.random.default_rng(76)
    rnd = []
    for i in range(10):
        idx = np.sort(rng.choice(P * P, int(round(0.3 * P * P)), replace=False))
        rnd.append({"split": f"random{i}", "rho": spearman(utility(idx), mask_power(idx, "add", P))})
    rho = np.array([r["rho"] for r in rows])
    hu, hm = np.mean([r["hits_U"] for r in rows]), np.mean([r["hits_M0"] for r in rows])
    if np.median(rho) >= 0.8 and hu >= hm - 0.5:
        verdict = "Brücke gestützt"
    elif np.median(rho) < 0.4:
        verdict = "keine Brücke"
    else:
        verdict = "unklar"
    out = {"median_rho_engineered": float(np.median(rho)), "min_rho_engineered": float(rho.min()), "mean_hits_U": float(hu), "mean_hits_M0": float(hm),
           "median_rho_random": float(np.median([r["rho"] for r in rnd])), "verdict": verdict, "rows": rows, "random": rnd}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("rows", "random")}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
