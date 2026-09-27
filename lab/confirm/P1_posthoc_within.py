"""P1 post hoc, EXPLORATION (session 28; not registered, no Holm, the P1 seeds are already seen; no confirmation).

Observation that motivates it (P1_posthoc_share.py): on average ~80 % of the W_E group power sits on the 5 steered targets at
step 2000 (add 113), yet only ~3.9 of the 5 targets are among the 5 strongest components. Which target falls behind?
Written before looking at any within-arm ranking; two competing predictors, both measurable without training:
  M0   : the target's power in the split's mask spectrum (first-order theory, draft section 5; for add 113 also centred M0c),
  init : the target's power in W_E at step 0 (initialization lottery; same init for F and G of a seed).
Measure per arm: Spearman over the 5 targets between the predictor and the W_E power at step 2000; mean over the 100 arms of a
task; null by permuting the predictor within every arm (20 000 draws), two-sided. Also: how often the weakest learned target is
the one with the lowest predictor (chance 0.2). Reading: a predictor with a clearly positive mean rho (p < 0.01) explains which
target lags; if both are, the larger mean rho is reported, not tested against each other. Numpy only, stored runs only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "confirm"))
import confirm_p1 as c  # noqa: E402
import confirm_splits as cs  # noqa: E402
from P1_posthoc_share import power0  # noqa: E402

N_PERM = 20_000


def m0c_add(idx: np.ndarray, p: int) -> np.ndarray:
    """Centred coherent mask spectrum (shared path), as in P1_posthoc_m0_strength.py."""
    K = (p - 1) // 2
    m = np.zeros((p, p))
    m[idx // p, idx % p] = 1
    t, col = np.arange(p)[:, None], np.arange(p)[None, :]
    X = np.fft.fft(m[t, (col - t) % p] + m[(col - t) % p, t], axis=0)
    X = X - X.mean(1, keepdims=True)
    s = (np.abs(X) ** 2).sum(1)
    return s[1:K + 1] + s[p - K:][::-1]


def ranks(x: np.ndarray) -> np.ndarray:
    return np.argsort(np.argsort(x, axis=-1), axis=-1).astype(float)


def mean_rho(P: np.ndarray, Y: np.ndarray) -> float:
    """P, Y: [arms, 5]; mean over arms of the Spearman correlation (ranks, no ties expected in continuous values)."""
    rp, ry = ranks(P) - 2.0, ranks(Y) - 2.0
    return float(((rp * ry).sum(1) / 10.0).mean())


def main() -> None:
    man = json.loads((LAB / "confirm/P1_manifest.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng(2026_09_28_2)
    out = {"note": "post hoc exploration; P1 seeds already seen", "tasks": {}}
    for t in man["tasks"]:
        name = f"{t['task']}{t['p']}"
        Y, pred = [], {"M0": [], "init": []} | ({"M0c": []} if name == "add113" else {})
        for s in man["seeds"]:
            for arm in "FG":
                st = c.stem(man, t, s, arm)
                T = json.loads((c.SPLITS / f"{st}.json").read_text(encoding="utf-8"))["targets"]
                pw, p0 = c.power_at(man, t, s, arm), power0(man, t, s, arm)
                if isinstance(pw, str) or p0 is None:
                    continue
                idx = np.load(c.SPLITS / f"{st}.npy")
                sel = [k - 1 for k in T]
                Y.append(pw[sel])
                pred["M0"].append(cs.m0(idx, t["task"], t["p"])[sel])
                pred["init"].append(p0[sel])
                if "M0c" in pred:
                    pred["M0c"].append(m0c_add(idx, t["p"])[sel])
        Y = np.array(Y)
        res = {"arms": len(Y)}
        for k, P in pred.items():
            P = np.array(P)
            obs = mean_rho(P, Y)
            null = np.array([mean_rho(rng.permuted(P, axis=1), Y) for _ in range(N_PERM)])
            weakest_match = float((np.argmin(P, 1) == np.argmin(Y, 1)).mean())
            res[k] = {"mean_rho": obs, "p_two": float((np.abs(null) >= abs(obs)).mean()), "weakest_is_lowest": weakest_match,
                      "pred_cv_within_arm": float((P.std(1) / P.mean(1)).mean())}
        out["tasks"][name] = res
        print(name, json.dumps(res), flush=True)
    (LAB / "confirm/P1_posthoc_within.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
