"""EXP-033 Nachtrag b (prediction before any EXP-033 run): in the sigma_3 phase from small init the net is ~linear,
f(a,b) = 3 W_out^T (W_in[a] + W_in[P+b]). Under gradient flow the product grows along the top singular vectors of the
initial residual correlation J = X^T (Y - 1/P) (X: two-hot inputs [n, 2P], Y: one-hot labels [n, P]), each mode at a rate
proportional to its singular value (rich get richer). Sign steps move every coordinate by the same amount instead.
Computes, per EXP-016 split 10-19: singular values of J, the Fourier content of the top left singular vectors folded to
k = 1..56 (u = first P rows, v = last P rows), and ds = share(F) - share(H) of (a) the top-5 modes weighted by s^2 and
(b) the sign pattern sign(J) (proxy for Adam's first step on W_in, since dL/dW_in ~ J W_out at init)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
S16 = HERE.parents[0] / "EXP-016-engineered-split" / "splits"
P, K = 113, 56


def fold_pw(x: np.ndarray) -> np.ndarray:        # x [P, m] -> folded power [56]
    pw = (np.abs(np.fft.fft(x, axis=0)) ** 2).sum(1)
    return pw[1:K + 1] + pw[P - K:][::-1]


def ds_of(pw: np.ndarray, T: set[int]) -> float:
    H = {min(57 * t % P, P - 57 * t % P) for t in T}
    w = pw / pw.sum()
    return float(w[[k - 1 for k in T]].sum() - w[[k - 1 for k in H]].sum())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split-dir", default=str(S16))
    ap.add_argument("--seeds", default="10-19")
    ap.add_argument("--out", default=str(HERE / "linear_modes.json"))
    args = ap.parse_args()
    lo, hi = (int(x) for x in args.seeds.split("-"))
    sd = Path(args.split_dir)
    rows = []
    for s in range(lo, hi + 1):
        idx = np.load(sd / f"split_seed{s}_eps2.0.npy")
        T = set(json.loads((sd / f"split_seed{s}_eps2.0.json").read_text())["targets"])
        a, b = idx // P, idx % P
        y = (a + b) % P
        X = np.zeros((len(idx), 2 * P)); X[np.arange(len(idx)), a] = 1; X[np.arange(len(idx)), P + b] = 1
        Y = np.zeros((len(idx), P)); Y[np.arange(len(idx)), y] = 1
        J = X.T @ (Y - 1.0 / P)                                   # [2P, P]
        U, S, Vt = np.linalg.svd(J, full_matrices=False)
        top = U[:, :5] * S[:5]
        pw_top = fold_pw(top[:P]) + fold_pw(top[P:])
        sg = np.sign(J)
        pw_sign = fold_pw(sg[:P]) + fold_pw(sg[P:])
        pw_J = fold_pw(J[:P]) + fold_pw(J[P:])
        top_k = [sorted(int(k) for k in np.argsort(-(fold_pw(U[:P, [i]]) + fold_pw(U[P:, [i]])))[:1] + 1) for i in range(10)]
        rows.append({"seed": s, "targets": sorted(T), "sv_top10": S[:10].round(2).tolist(), "top_mode_freq": top_k,
                     "ds_top5_modes": ds_of(pw_top, T), "ds_J": ds_of(pw_J, T), "ds_signJ": ds_of(pw_sign, T)})
    out = {"rows": rows, "mean": {k: float(np.mean([r[k] for r in rows])) for k in ("ds_top5_modes", "ds_J", "ds_signJ")}}
    Path(args.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    for r in rows:
        print(r["seed"], r["targets"], r["sv_top10"][:7], [x[0] for x in r["top_mode_freq"]],
              round(r["ds_top5_modes"], 3), round(r["ds_J"], 3), round(r["ds_signJ"], 3))
    print(out["mean"])


if __name__ == "__main__":
    main()
