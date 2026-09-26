"""EXP-017: Recursive Feature Machine (Gaussian Mahalanobis kernel, AGOP) on modular addition.

No random initialization (M0 = I): any frequency preference must come from the train split.
Definition: README.md. Run only through lab/tools/guarded_run.py.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB.parent / "training"))
sys.path.insert(0, str(LAB / "experiments/EXP-015-mask-spectrum"))

import mask_spectrum as ms  # noqa: E402
import predict as p12  # noqa: E402  (path set by mask_spectrum)
from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402

P, L2, LAM, BATCH = 113, 1.0, 1e-3, 32
K_HALF = (P - 1) // 2


def onehot_pairs(x: np.ndarray) -> np.ndarray:
    X = np.zeros((len(x), 2 * P))
    X[np.arange(len(x)), x[:, 0]] = 1.0
    X[np.arange(len(x)), P + x[:, 1]] = 1.0
    return X


def kernel(A: np.ndarray, B: np.ndarray, M: np.ndarray) -> np.ndarray:
    AM, BM = A @ M, B @ M
    d2 = (AM * A).sum(1)[:, None] + (BM * B).sum(1)[None, :] - 2 * AM @ B.T
    return np.exp(-np.maximum(d2, 0.0) / (2 * L2))


def agop(X: np.ndarray, alpha: np.ndarray, M: np.ndarray) -> np.ndarray:
    """mean_x J(x)^T J(x), J(x) = d f(x)/dx = -(1/L2) sum_i k(x,x_i) alpha_i (M (x - x_i))^T."""
    G = np.zeros((X.shape[1], X.shape[1]))
    XM = X @ M
    for s in range(0, len(X), BATCH):
        xb = X[s:s + BATCH]
        Kb = kernel(xb, X, M)                               # [b, n]
        Ka = Kb @ alpha                                     # [b, out]
        # J_b = -(1/L2) [ Ka^T (x M)  -  sum_i Kb_i alpha_i (x_i M) ]  per sample
        term1 = Ka[:, :, None] * (xb @ M)[:, None, :]       # [b, out, d]
        term2 = np.tensordot(Kb[:, :, None] * alpha[None], XM, axes=([1], [0]))   # [b, out, d]
        J = -(term1 - term2) / L2
        G += np.einsum("bod,boe->de", J, J, optimize=True)
    G /= len(X)
    return G * (2 * P / np.trace(G))


def freq_power_block(Mb: np.ndarray) -> np.ndarray:
    Fm = np.exp(-2j * np.pi * np.outer(np.arange(P), np.arange(P)) / P) / np.sqrt(P)
    d = np.real(np.diag(Fm.conj().T @ Mb @ Fm))
    return d[1:K_HALF + 1] + d[P - K_HALF:][::-1]


def run_split(seed: int, iters: int) -> dict:
    data = make_dataset(get_config("arch25k", seed=seed))
    Xtr, Xte = onehot_pairs(data["train_x"].numpy()), onehot_pairs(data["test_x"].numpy())
    ytr, yte = data["train_y"].numpy(), data["test_y"].numpy()
    Y = np.eye(P)[ytr] - 1.0 / P
    M = np.eye(2 * P)
    hist = []
    for t in range(iters + 1):
        K = kernel(Xtr, Xtr, M)
        alpha = np.linalg.solve(K + LAM * np.eye(len(K)), Y)
        test_acc = float((kernel(Xte, Xtr, M) @ alpha).argmax(1).__eq__(yte).mean())
        train_acc = float((K @ alpha).argmax(1).__eq__(ytr).mean())
        pw = freq_power_block(M[:P, :P]) + freq_power_block(M[P:, P:])
        top = sorted((np.argsort(-pw, kind="stable")[:5] + 1).tolist())
        hist.append({"iter": t, "train_acc": train_acc, "test_acc": test_acc, "top5": top,
                     "top5_share": float(np.sort(pw)[::-1][:5].sum() / pw.sum()), "power": pw.tolist()})
        print(f"seed {seed} iter {t}: train {train_acc:.3f} test {test_acc:.3f} top5 {top} "
              f"share {hist[-1]['top5_share']:.3f}", flush=True)
        if t < iters:
            M = agop(Xtr, alpha, M)
    return {"seed": seed, "hist": hist}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="0-9")
    ap.add_argument("--iters", type=int, default=15)
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.seeds.split("-"))
    seeds = list(range(lo, hi + 1))
    runs = [run_split(s, a.iters) for s in seeds]
    (HERE / "raw").mkdir(exist_ok=True)
    (HERE / "raw/rfm_runs.json").write_text(json.dumps(runs), encoding="utf-8")
    k009 = {}
    for r in json.loads(p12.EXP009.read_text(encoding="utf-8"))["runs"]:
        if r["run"].startswith("txf_add_p113_wd1.0_frac0.3_seed"):
            k009[int(r["run"].split("seed")[1].split("_")[0])] = r["k_final"]
    final = {r["seed"]: r["hist"][-1] for r in runs}
    ok = [s for s in seeds if final[s]["test_acc"] >= 0.9 and final[s]["top5_share"] >= 2 * 5 / K_HALF]
    out: dict = {"n_ok": len(ok), "final": {s: {k: v for k, v in final[s].items() if k != "power"} for s in seeds}}
    if len(ok) < 8:
        out["verdict"] = "nicht auswertbar (Vorbedingung)"
    else:
        masks = {m: ms.m0(ms.mask_matrix(m)) for m in ok}
        R = np.array([[p12.rbar(masks[m], final[s]["top5"]) for m in ok] for s in ok])
        rng = np.random.default_rng(0)
        null = np.array([R[np.arange(len(ok)), rng.permutation(len(ok))].mean() for _ in range(20000)])
        matched = float(np.trace(R) / len(ok))
        p = float((np.sum(null <= matched - 1e-12) + 1) / (len(null) + 1))
        out.update({"rbar_matched": matched, "rbar_foreign": float((R.sum() - np.trace(R)) / (len(ok) * (len(ok) - 1))),
                    "p_perm": p, "verdict": "bestätigt" if p < 0.05 else "nicht bestätigt"})
        same = [len(set(final[s]["top5"]) & set(k009[s])) for s in ok if s in k009]
        other = [len(set(final[s]["top5"]) & set(k009[t])) for s in ok for t in k009 if t != s]
        out["secondary_txf_overlap"] = {"same_split": float(np.mean(same)) if same else None,
                                        "other_split": float(np.mean(other)) if other else None}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "final"}, indent=1))


if __name__ == "__main__":
    main()
