"""Frozen, descriptive pi predictions for EXP-039 (session 14, before any EXP-039 run). Pure numpy on stored post hoc results.

Phenomenological clock: effective time tau(t) = sum_{s=1..t} (lr_s / lr_0)^gamma of the F phase; pi(t) = P(tau(t)), where P is the
EXP-020 persistence curve (constant lr, tau = t), piecewise linear through (0, 0) and the EXP-020 means at 10, 25, 50, 150
(pi = 1 beyond 150). Models: step clock gamma = 0, Lambda clock gamma = 1, and gamma fitted (least squares, grid) on the stored
EXP-035 warmup runs (linear warmup over 200 steps: lr_s / lr_0 = s / 200 for s <= 200).
EXP-039 arms: lr scale c constant in steps 1..min(t, 250), so tau = t * c^gamma. Predictions per (c, t) for all three models.
Writes predictions_pi.json once (frozen); the evaluation after the runs uses ../EXP-020-data-switch/posthoc_beta_persistence.py.
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
E20 = HERE.parent / "EXP-020-data-switch"
OUT = HERE / "predictions_pi.json"
WARMUP = 200
GRID = (("c2", 2.0, (10, 25, 50)), ("c0.5", 0.5, (50, 100, 150)))


def curve() -> tuple[np.ndarray, np.ndarray]:
    sw = json.loads((E20 / "posthoc_beta_persistence.json").read_text(encoding="utf-8"))["switch"]
    ts = [10, 25, 50, 150]
    return np.array([0.0] + ts), np.array([0.0] + [min(1.0, sw[str(t)]["pi_mean"]) for t in ts])


def P(tau: float, x: np.ndarray, y: np.ndarray) -> float:
    return float(np.interp(tau, x, y, right=1.0))


def tau_warmup(t: int, gamma: float) -> float:
    s = np.arange(1, t + 1)
    return float(((np.minimum(s, WARMUP) / WARMUP) ** gamma).sum())


def main() -> None:
    if OUT.exists():
        raise SystemExit(f"{OUT.name} exists: predictions are frozen")
    x, y = curve()
    obs = json.loads((E20 / "posthoc_pi_other.json").read_text(encoding="utf-8"))["EXP-035"]
    pts = [(int(k.split("_t")[1]), v["pi"]) for k, v in obs.items()]
    gammas = np.round(np.arange(0.0, 1.51, 0.01), 2)
    sse = [sum((P(tau_warmup(t, g), x, y) - p) ** 2 for t, p in pts) for g in gammas]
    g_fit = float(gammas[int(np.argmin(sse))])
    models = {"step_gamma0": 0.0, "lambda_gamma1": 1.0, f"fit_gamma{g_fit}": g_fit}
    pred = {m: {f"{name}_t{t}": P(t * c ** g, x, y) for name, c, ts in GRID for t in ts} for m, g in models.items()}
    fit_quality = {m: float(np.sqrt(np.mean([(P(tau_warmup(t, g), x, y) - p) ** 2 for t, p in pts]))) for m, g in models.items()}
    out = {"frozen": "session 14, 2026-09-26, before any EXP-039 run", "curve_tau": x.tolist(), "curve_pi": y.tolist(),
           "fit_points_EXP035": pts, "gamma_fit": g_fit, "rmse_on_EXP035": fit_quality, "predictions": pred,
           "evaluation": "after the runs: pi per seed with posthoc_beta_persistence.D (normalised by the EXP-018 pure runs of the "
                         "seed), compare RMSE of the three models over all (c, t) cells; descriptive, no verdict"}
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("gamma_fit", "rmse_on_EXP035", "predictions")}, indent=1))


if __name__ == "__main__":
    main()
