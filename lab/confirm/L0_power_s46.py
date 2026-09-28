"""L0 registration helper (session 46, written BEFORE the EXP-100 pilot result was read): sample size n for the L0 confirmation
from the pilot spread. Reads lab/experiments/EXP-100-set-vs-order/summary.json (rows written by analyze.py).

Per hypothesis a per-seed statistic x from the pilot rows:
  H1  dpow_end_iid256        (steering under i.i.d. minibatch, B = 256)
  H2  dpow_end_iid64         (B = 64)
  H3c dpow_end_stride64 - dpow_end_iid64   (candidate conflict contrast; only reported, its form is set after the pilot)
Power model (memory note 'power from small pilots': a bootstrap of ~10 pilot values flatters; use a normal model at HALF the
pilot effect, and a 1.5x pilot SD as the pessimistic case): x ~ N(d, s^2), one-sided t-test at Holm level alpha/k for the
smallest p (conservative: every test at alpha/k, k = family size), plus the CI rule (95 % CI lower bound > 0, which for a
one-sided t-test at alpha/k <= 0.025 is implied). Monte Carlo 4000 repetitions per n, rng 46.
Output: for each hypothesis and n in 6..60 the power at (half effect, pilot SD) and (half effect, 1.5 SD); the smallest n with
power >= 0.8 in the pessimistic case is the recommendation. Decision rule for the registration: n = max over H1/H2 of that n,
at least 10, rounded up to a multiple of 2.
  python lab/confirm/L0_power_s46.py [--k 3]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
SUMMARY = LAB / "experiments/EXP-100-set-vs-order/summary.json"
N_GRID = range(6, 61)
REPS, ALPHA = 4000, 0.05


def t_sf(t: np.ndarray, df: int) -> np.ndarray:
    """Upper tail of Student's t via the regularized incomplete beta (continued fraction), vectorised over t."""
    x = df / (df + t * t)
    out = 0.5 * np.array([_ibeta(df / 2.0, 0.5, xi) for xi in x])
    return np.where(t > 0, out, 1.0 - out)


def _ibeta(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x > (a + 1) / (a + b + 2):
        return 1.0 - _ibeta(b, a, 1 - x)
    f, c, d = 1.0, 1.0, 0.0
    for i in range(200):
        m = i // 2
        if i == 0:
            num = 1.0
        elif i % 2 == 0:
            num = (m * (b - m) * x) / ((a + 2 * m - 1) * (a + 2 * m))
        else:
            num = -((a + m) * (a + b + m) * x) / ((a + 2 * m) * (a + 2 * m + 1))
        d = 1.0 + num * d
        d = 1.0 / (d if abs(d) > 1e-30 else 1e-30)
        c = 1.0 + num / c if abs(c) > 1e-30 else 1e-30
        f *= c * d
        if abs(c * d - 1.0) < 1e-12:
            break
    return math.exp(lbeta) * (f - 1.0) / a


def power(d: float, s: float, n: int, level: float, rng: np.random.Generator) -> float:
    x = rng.normal(d, s, size=(REPS, n))
    t = x.mean(1) / (x.std(1, ddof=1) / math.sqrt(n))
    return float(np.mean(t_sf(t, n - 1) < level))


def main() -> None:
    k = int(sys.argv[sys.argv.index("--k") + 1]) if "--k" in sys.argv else 3
    rows = [r for r in json.loads(SUMMARY.read_text(encoding="utf-8"))["rows"] if r.get("valid")]
    stats = {"H1": [r["dpow_end_iid256"] for r in rows],
             "H2": [r["dpow_end_iid64"] for r in rows],
             "H3c": [r["dpow_end_stride64"] - r["dpow_end_iid64"] for r in rows
                     if "dpow_end_stride64" in r and "dpow_end_iid64" in r]}
    rng = np.random.default_rng(46)
    out = {"k": k, "n_pilot": len(rows), "hyp": {}}
    for h, xs in stats.items():
        xs = np.asarray(xs, dtype=float)
        if len(xs) < 3:
            out["hyp"][h] = {"n": len(xs), "reading": "zu wenig Pilotwerte"}
            continue
        d, s = abs(float(xs.mean())) / 2, float(xs.std(ddof=1))
        curve = {n: (power(d, s, n, ALPHA / k, rng), power(d, 1.5 * s, n, ALPHA / k, rng)) for n in N_GRID}
        rec = next((n for n, (_, pp) in curve.items() if pp >= 0.8), None)
        out["hyp"][h] = {"pilot_mean": float(xs.mean()), "pilot_sd": s, "n_pilot": len(xs), "half_effect": d,
                         "n_recommended_pessimistic": rec,
                         "power_at": {str(n): [round(a, 3), round(b, 3)] for n, (a, b) in curve.items() if n in (8, 10, 12, 16, 20, 24, 30, 40)}}
    ns = [out["hyp"][h].get("n_recommended_pessimistic") for h in ("H1", "H2") if isinstance(out["hyp"].get(h), dict)]
    ns = [n for n in ns if n is not None]
    out["n_rule"] = (max(10, max(ns)) + 1) // 2 * 2 if ns else None
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
