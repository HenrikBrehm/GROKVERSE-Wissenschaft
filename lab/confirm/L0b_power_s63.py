"""L0b registration helper (session 63, 2026-09-30, written before any L0b run; EXP-106 pilot values are SEEN data).
Sample size for the L0b family from the EXP-106 pilot spread (8 seeds), rule as L0 (L0_power_s46.py, memory note 'power from
small pilots'): normal model at HALF the pilot effect and 1.5x the pilot SD (pessimistic case), each test at alpha/k (k = 4,
conservative Holm bound), Monte Carlo 4000 repetitions per n, rng 63. Per-seed statistics (EXP-106 summary.json rows):
  H1  x = o(R, stride16w) - o(R, iid16w)                       one-sided t, H0 mean <= 0
  H2  x = mean_FG o(stride16w) - o(iid16w)                     TOST equivalence, margin DELTA = 0.05 (true mean taken as the
                                                               pilot mean 0.004, not halved: halving would favour H2)
  H3  x = dpow_end(stride16w)                                  one-sided t, H0 mean <= 1 (half effect = 1 + (mean - 1) / 2)
  H4  x = mean_FG log2 t_gen(stride16w) / t_gen(iid16w)         one-sided t, H0 mean <= 0
Recommendation: smallest n in 10..70 with pessimistic power >= 0.8 for every hypothesis; at most 70 (free seeds 3730-3799).
  python lab/confirm/L0b_power_s63.py
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("l0p", LAB / "confirm/L0_power_s46.py")
l0p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(l0p)
ALPHA, K, DELTA, REPS = 0.05, 4, 0.05, 4000


def pilot() -> dict:
    rows = json.loads((LAB / "experiments/EXP-106-l0-b16-long-epochs/summary.json").read_text(encoding="utf-8"))["rows"]
    lg = lambda r: np.mean([np.log2(a / b) for a, b in zip(r["tgen_stride16w"], r["tgen_iid16w"]) if a and b])   # noqa: E731
    return {"H1": np.array([r["R_o_stride16w"] - r["R_o_iid16w"] for r in rows]),
            "H2": np.array([r["o_stride16w"] - r["o_iid16w"] for r in rows]),
            "H3": np.array([r["dpow_end_stride16w"] for r in rows]),
            "H4": np.array([lg(r) for r in rows])}


def tcrit(df: int, a: float) -> float:
    lo, hi = 0.0, 20.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if l0p.t_sf(np.array([mid]), df)[0] > a else (lo, mid)
    return hi


def power(h: str, x: np.ndarray, n: int, rng: np.random.Generator) -> float:
    sd = 1.5 * x.std(ddof=1)
    mu = {"H1": x.mean() / 2, "H2": x.mean(), "H3": 1 + (x.mean() - 1) / 2, "H4": x.mean() / 2}[h]
    s = rng.normal(mu, sd, size=(REPS, n))
    m, se = s.mean(1), s.std(1, ddof=1) / np.sqrt(n)
    c = tcrit(n - 1, ALPHA / K)
    if h == "H2":
        return float(np.mean(((m + DELTA) / se > c) & ((DELTA - m) / se > c)))
    return float(np.mean((m - (1.0 if h == "H3" else 0.0)) / se > c))


def main() -> None:
    P, rng = pilot(), np.random.default_rng(63)
    out = {h: {"pilot_mean": float(x.mean()), "pilot_sd": float(x.std(ddof=1)), "n80": None} for h, x in P.items()}
    for h, x in P.items():
        for n in range(10, 71):
            if power(h, x, n, rng) >= 0.8:
                out[h]["n80"] = n
                break
    need = [v["n80"] for v in out.values()]
    rec = None if None in need else max(10, max(need))
    rec = rec + (rec % 2) if rec else None
    out["recommended_n"] = rec
    (LAB / "confirm/L0b_power_s63.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
