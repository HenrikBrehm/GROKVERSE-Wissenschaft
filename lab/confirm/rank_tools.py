"""Shared rank statistics for C1/C2 (session 28, after the Codex review of C1). Numpy only.

- spearman5 / cranks: exact ties raise TieError (the arm is then technical, never silently ranked).
- adjusted_coef: stacked within-arm centred ranks, OLS y ~ predictor + controls (no intercept: every block is centred);
  returns the predictor coefficient.
- seed_test: statistic = equal-weight mean of cell means of the seed values; one-sided sign-flip p with (exceed + 1) / (B + 1)
  (assumes symmetry about 0 under H0, stated in the registrations); bootstrap CIs resample seeds within cells (stratified).
"""
from __future__ import annotations

import numpy as np


class TieError(ValueError):
    pass


def cranks(x: np.ndarray) -> np.ndarray:
    """Centred ranks (mean 0) of a 1-d vector; exact ties are an error."""
    x = np.asarray(x, dtype=np.float64)
    if len(np.unique(x)) != len(x):
        raise TieError("tied values")
    return np.argsort(np.argsort(x)).astype(np.float64) - (len(x) - 1) / 2.0


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = cranks(x), cranks(y)
    return float((rx * ry).sum() / np.sqrt((rx ** 2).sum() * (ry ** 2).sum()))


def adjusted_coef(blocks: list[dict], pred: str, controls: list[str], y: str = "y") -> float:
    """blocks: one dict per arm with equal-length vectors for y, pred and every control."""
    Y = np.concatenate([cranks(b[y]) for b in blocks])
    X = np.column_stack([np.concatenate([cranks(b[k]) for b in blocks]) for k in [pred, *controls]])
    return float(np.linalg.lstsq(X, Y, rcond=None)[0][0])


def cell_mean(vals: dict[str, np.ndarray]) -> float:
    return float(np.mean([v.mean() for v in vals.values()]))


def sign_flip_p(vals: dict[str, np.ndarray], rng: np.random.Generator, n: int = 200_000) -> float:
    obs = cell_mean(vals)
    cells = list(vals)
    stat = np.zeros(n)
    for c in cells:
        v = vals[c]
        stat += (rng.choice((-1.0, 1.0), size=(n, len(v))) * v).mean(1)
    stat /= len(cells)
    return float(((stat >= obs).sum() + 1) / (n + 1))


def strat_boot(units: dict[str, list], stat, rng: np.random.Generator, n: int = 10_000) -> list[float]:
    """units: cell -> list of per-seed items; stat(dict cell -> list of items) -> float. Resamples seeds within cells."""
    out = np.empty(n)
    for i in range(n):
        out[i] = stat({c: [u[j] for j in rng.integers(0, len(u), len(u))] for c, u in units.items()})
    return [float(np.quantile(out, 0.025)), float(np.quantile(out, 0.975))]


def selftest() -> None:
    """Hand-calculated values, independent of the analysis code."""
    assert np.allclose(cranks(np.array([10.0, 30.0, 20.0, 50.0, 40.0])), [-2, 0, -1, 2, 1])
    assert abs(spearman(np.arange(5.0), np.arange(5.0)) - 1) < 1e-12
    assert abs(spearman(np.arange(5.0), np.array([1.0, 0.0, 2.0, 4.0, 3.0])) - 0.8) < 1e-12   # 1 - 6*4/120
    try:
        cranks(np.array([1.0, 1.0, 2.0, 3.0, 4.0]))
        raise AssertionError("ties must raise")
    except TieError:
        pass
    rng = np.random.default_rng(1)
    b = [{"y": 2 * x + c, "x": x, "c": c} for x, c in ((rng.permutation(5.0), rng.permutation(5.0)) for _ in range(50))]
    assert adjusted_coef(b, "x", ["c"]) > 0.3                       # y ranks driven by x and c jointly
    b0 = [{"y": c, "x": x, "c": c} for x, c in ((rng.permutation(5.0), rng.permutation(5.0)) for _ in range(200))]
    assert abs(adjusted_coef(b0, "x", ["c"])) < 1e-9                  # y = c exactly: x gets no weight
    v = {"a": np.array([0.5, 0.4, 0.6]), "b": np.array([0.1, 0.2, 0.3, 0.2])}
    assert abs(cell_mean(v) - (0.5 + 0.2) / 2) < 1e-12
    assert sign_flip_p(v, rng, 20_000) < 0.05                         # all positive: p = (1 + #flips reaching obs)/(B+1)
    assert abs(sign_flip_p({"a": np.array([1.0])}, rng, 20_000) - 0.5) < 0.02
    ci = strat_boot({"a": list(v["a"]), "b": list(v["b"])}, lambda u: cell_mean({c: np.array(x) for c, x in u.items()}), rng, 2000)
    assert ci[0] <= cell_mean(v) <= ci[1]
    print("rank_tools selftest ok")


if __name__ == "__main__":
    selftest()
