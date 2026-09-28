"""EXP-093 (pilot, exploration): range of the momentum-lag clock. Definition, predictions and readings: README.md (fixed before any
EXP-093 run). Run under guarded_run.py with the global python.

pi, validity, loading and displacement selectivity exactly as EXP-092 (functions imported from its analyze.py, pointed at this
experiment's design). Per seed s and cell c: residual r_c = pi(c) - [pi(n25) + (pi(n30) - pi(n25)) (x_c - x25) / (x30 - x25)],
x = lag clock Lambda_eff (EXP-092). 95 % percentile bootstrap over seeds (10 000, rng 93).
Per cell: 'trifft' if the CI of r_c lies inside [-0.03, +0.03]; 'verfehlt' if the CI upper bound < -0.03 (or lower bound > +0.03);
else 'offen'. Cells in order c2, c3, c4, c6, c8.
Reading: 'Grenze zwischen c_a und c_b' if the cells split into a leading run of 'trifft' followed only by 'verfehlt' (both
non-empty); 'keine Grenze bis c = 8' if all 'trifft'; 'Uhr verfehlt schon bei c = 2' if all 'verfehlt'; else 'gemischt'.
Fewer than 10 valid seeds -> 'nicht auswertbar'.
Secondary (descriptive): residual means, Spearman of residual means with c and with 2/t (share of Lambda in the first two
Adam steps), cell means of pi, displacement selectivity and norm, n20 residual (calibration check).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(HERE))
import design as D  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp092", LAB / "experiments/EXP-092-momentum-lag-clock/analyze.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)
E.D, E.SPL, E.RAW = D, HERE / "splits", HERE / "raw"      # reuse EXP-092 loading on this experiment's design and files

MIN_VALID, N_BOOT, EQ = 10, 10_000, 0.03
CELLS = ("c2", "c3", "c4", "c6", "c8")


def x_lag(cell: str) -> float:
    c, t, psb = D.CELLS[cell]
    return c * t - c * E.lag(psb[0] if psb else 0.9, t)


def residuals(pis: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    x25, x30 = x_lag("n25"), x_lag("n30")
    return {c: pis[c] - (pis["n25"] + (pis["n30"] - pis["n25"]) * (x_lag(c) - x25) / (x30 - x25)) for c in CELLS + ("n20",)}


def boot_ci(x: np.ndarray, seed: int = 93) -> list[float]:
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), size=(N_BOOT, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def cell_call(ci: list[float]) -> str:
    if -EQ <= ci[0] and ci[1] <= EQ:
        return "trifft"
    if ci[1] < -EQ or ci[0] > EQ:
        return "verfehlt"
    return "offen"


def reading(calls: list[str]) -> str:
    if all(c == "trifft" for c in calls):
        return "keine Grenze bis c = 8"
    if all(c == "verfehlt" for c in calls):
        return "Uhr verfehlt schon bei c = 2"
    k = 0
    while k < len(calls) and calls[k] == "trifft":
        k += 1
    if 0 < k < len(calls) and all(c == "verfehlt" for c in calls[k:]):
        return f"Grenze zwischen {CELLS[k - 1]} und {CELLS[k]}"
    return "gemischt"


def verdict(pis: dict[str, np.ndarray]) -> dict:
    n = len(pis["n25"])
    if n < MIN_VALID:
        return {"n": n, "verdict": "nicht auswertbar"}
    res = residuals(pis)
    cis = {c: boot_ci(res[c]) for c in CELLS + ("n20",)}
    calls = [cell_call(cis[c]) for c in CELLS]
    return {"n": n, "residual_mean": {c: float(res[c].mean()) for c in res}, "residual_ci95": cis,
            "calls": dict(zip(CELLS, calls)), "verdict": reading(calls)}


def spearman(x: list[float], y: list[float]) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def main() -> None:
    rows = [E.seed_row(s) for s in D.SEEDS]
    ok = [r for r in rows if r["valid"]]
    col = lambda k: np.array([r[k] for r in ok])   # noqa: E731
    out: dict = {"n_valid": len(ok)}
    if ok:
        pis = {c: col(f"pi_{c}") for c in D.CELLS}
        out["primary"] = v = verdict(pis)
        if "residual_mean" in v:
            rm = [v["residual_mean"][c] for c in CELLS]
            out["secondary"] = {"pi_means": {c: float(p.mean()) for c, p in pis.items()},
                                "x_lag": {c: x_lag(c) for c in D.CELLS},
                                "spearman_resid_c": spearman([D.CELLS[c][0] for c in CELLS], rm),
                                "spearman_resid_2_over_t": spearman([2 / D.CELLS[c][1] for c in CELLS], rm),
                                "fsel_means": {c: float(col(f"fsel_{c}").mean()) for c in D.CELLS},
                                "dnorm_means": {c: float(col(f"dnorm_{c}").mean()) for c in D.CELLS}}
    else:
        out["primary"] = {"verdict": "nicht auswertbar"}
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert len(D.jobs()) == len(D.SEEDS) * 18 and len(D.smoke()) == 3
    assert all("--lr-scale 8" in x for x in D.smoke()[1:]) and E.D is D
    assert abs(x_lag("c4") - 15.2209) < 1e-3
    rng = np.random.default_rng(0)
    base = lambda: 0.36 + rng.normal(0, 0.02, 16)   # noqa: E731
    slope = 0.1 / (x_lag("n30") - x_lag("n25"))
    def world(defect: dict[str, float]) -> dict[str, np.ndarray]:
        b = base()
        return {c: b + slope * (x_lag(c) - x_lag("n25")) + defect.get(c, 0.0) + rng.normal(0, 0.01, 16) for c in D.CELLS}
    assert verdict(world({}))["verdict"] == "keine Grenze bis c = 8", verdict(world({}))
    v = verdict(world({"c4": -0.1, "c6": -0.15, "c8": -0.2}))
    assert v["verdict"] == "Grenze zwischen c3 und c4", v
    assert verdict(world({c: -0.2 for c in CELLS}))["verdict"] == "Uhr verfehlt schon bei c = 2"
    assert verdict(world({"c3": -0.2}))["verdict"] == "gemischt"
    assert verdict({c: p[:9] for c, p in world({}).items()})["verdict"] == "nicht auswertbar"
    print("[exp093] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
