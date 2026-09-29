"""N54b post hoc, EXPLORATION (session 50; seeds already analyzed for N54b, so no confirmation).
Question: does minibatch training only rescale the lock-in time, or does it also change the shape of the lock-in curve?
Per seed, batch B and learning rate: least-squares fit of pi(t) = 1 / (1 + exp(-k (ln t - ln t0))) over the stored switch grid
(grid search, k in [0.5, 30], ln t0 in [ln 5, ln 1000]). k is the steepness in log time (larger = sharper transition).
Fixed before looking: if minibatch only rescales time, k is about equal across B (paired differences k(B) - k(1024) with
95 % bootstrap CI including 0); a clearly smaller k at small B would mean a broader, not only later, window.
Reads lab/confirm/N54B_summary.json only.
  python lab/tools/guarded_run.py -- python lab/confirm/N54B_shape_posthoc_s50.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
KS = np.linspace(0.5, 30, 296)
L0S = np.linspace(np.log(5), np.log(1000), 400)


def fit(ts: np.ndarray, pi: np.ndarray) -> tuple[float, float, float]:
    lt = np.log(ts)
    pred = 1 / (1 + np.exp(-KS[:, None, None] * (lt[None, None, :] - L0S[None, :, None])))
    sse = ((pred - pi[None, None, :]) ** 2).sum(-1)
    i, j = np.unravel_index(np.argmin(sse), sse.shape)
    return float(KS[i]), float(np.exp(L0S[j])), float(sse[i, j])


def boot(v: np.ndarray, rng: np.random.Generator) -> list[float]:
    m = rng.choice(v, (10000, len(v)), replace=True).mean(1)
    return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]


def main() -> None:
    nb = json.loads((HERE / "N54B_summary.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng(50)
    out: dict = {"note": "post hoc exploration on N54b seeds (already analyzed); logistic fit in log t per seed", "cells": {}}
    for lr, rows in nb["rows"].items():
        ks: dict[str, list[float]] = {}
        for r in rows:
            for b, curve in r["pi"].items():
                ts = np.array(sorted(curve, key=float), float)
                pi = np.array([curve[k] for k in sorted(curve, key=float)], float)
                k, t0, sse = fit(ts, np.clip(pi, -0.2, 1.2))
                ks.setdefault(b, []).append(k)
                out["cells"].setdefault(lr, {}).setdefault(b, []).append({"seed": r["seed"], "k": k, "t0": t0, "sse": sse})
        summ = {b: {"k_mean": float(np.mean(v)), "k_ci95": boot(np.array(v), rng)} for b, v in ks.items()}
        for b in ("256", "64"):
            d = np.array(ks[b]) - np.array(ks["1024"])
            summ[f"k{b}-k1024"] = {"mean": float(d.mean()), "ci95": boot(d, rng), "n_neg": int((d < 0).sum()), "n": len(d)}
        out[f"lr{lr}"] = summ
    (HERE / "N54B_shape_posthoc_s50.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k.startswith("lr")}, indent=1))


if __name__ == "__main__":
    main()
