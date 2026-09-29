"""N54b exploration (session 47; models and criteria fixed in JOURNAL 'Zyklus 3' before any N54b result was read; no verdict).
Fits three models of t_half(B, lr) to the six cell means of the frozen N54b summary (N54B_summary.json, written by --analyze):
  M_i   t = a * sqrt(x) / lam              x = N/B, lam = lr / 1e-3
  M_add t = a * sqrt(x) / lam + b * x
  M_pow t = a * x**alpha * lam**(-beta)
least squares in log t (M_add by a coarse-to-fine grid over a, b >= 0), RMS of log residuals and BIC = n log(RSS/n) + k log n.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/confirm/N54B_models_posthoc_s47.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
N = 3831


def cells() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    s = json.loads((HERE / "N54B_summary.json").read_text(encoding="utf-8"))["secondary"]
    x, lam, t = [], [], []
    for key, lr in (("lr0.001", 1.0), ("lr0.002", 2.0)):
        for b, v in s[key]["t_half_mean"].items():
            x.append(N / int(b)); lam.append(lr); t.append(v)
    return np.array(x), np.array(lam), np.array(t)


def score(pred: np.ndarray, t: np.ndarray, k: int) -> dict:
    r = np.log(t) - np.log(pred)
    rss = float((r ** 2).sum())
    n = len(t)
    return {"rms_log": float(np.sqrt(rss / n)), "bic": float(n * np.log(max(rss, 1e-12) / n) + k * np.log(n)),
            "residuals": [float(v) for v in r]}


def main() -> None:
    x, lam, t = cells()
    out = {}
    base = np.sqrt(x) / lam
    a = float(np.exp(np.mean(np.log(t) - np.log(base))))
    out["M_i"] = {"a": a, **score(a * base, t, 1)}
    best = None
    for lo_a, hi_a, lo_b, hi_b in ((1, 200, 0, 20),):
        for _ in range(4):
            A, B = np.linspace(lo_a, hi_a, 201), np.linspace(lo_b, hi_b, 201)
            for aa in A:
                pred = aa * base[None, :] + B[:, None] * x[None, :]
                rss = ((np.log(t)[None, :] - np.log(pred)) ** 2).sum(axis=1)
                j = int(np.argmin(rss))
                if best is None or rss[j] < best[0]:
                    best = (float(rss[j]), float(aa), float(B[j]))
            da, db = (hi_a - lo_a) / 20, (hi_b - lo_b) / 20
            lo_a, hi_a, lo_b, hi_b = max(1e-6, best[1] - da), best[1] + da, max(0.0, best[2] - db), best[2] + db
    out["M_add"] = {"a": best[1], "b": best[2], **score(best[1] * base + best[2] * x, t, 2)}
    X = np.column_stack([np.ones_like(x), np.log(x), -np.log(lam)])
    coef, *_ = np.linalg.lstsq(X, np.log(t), rcond=None)
    out["M_pow"] = {"a": float(np.exp(coef[0])), "alpha": float(coef[1]), "beta": float(coef[2]), **score(np.exp(X @ coef), t, 3)}
    out["cells"] = [{"x": float(a_), "lam": float(b_), "t_half": float(c_)} for a_, b_, c_ in zip(x, lam, t)]
    (HERE / "N54B_models_posthoc_s47.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "residuals"} if isinstance(v, dict) else v for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
