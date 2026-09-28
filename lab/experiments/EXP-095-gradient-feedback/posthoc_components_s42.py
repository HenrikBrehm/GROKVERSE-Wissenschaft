"""EXP-095 post hoc (session 42, after the result, seen data, exploration): WHY is the early W_E motion less target-selective
when the gradient is evaluated less often? Split the group power of the displacement W_E(t) - W_E(0) into target power T
(the first split's five targets) and non-target power R (all other frequencies), per cell, averaged over both directions.

Readings fixed here BEFORE computing (ratios of cell means against n24; 'similar' = within 0.8-1.25):
  'Selbstverstaerkung fehlt'  T(g24)/T(n24) < 0.8 and R(g24)/R(n24) similar   (targets grow less without fresh gradients)
  'Korrektur fehlt'           T(g24)/T(n24) similar and R(g24)/R(n24) > 1.25  (non-targets grow more: stale, sign-like Adam steps)
  'beides'                    T ratio < 0.8 and R ratio > 1.25
  else 'unklar'. Same ratios reported for g8, g4 and c8b (descriptive). Paired per-seed log ratios with bootstrap CIs (rng 42).
Expectation (stated before computing): 'Korrektur fehlt' (g24 moved further, N 2.87 vs 2.36, with a lower target share).
Reads only stored snapshots through the EXP-095 loader; writes posthoc_components_s42.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as X  # noqa: E402  (EXP-095 loader, E = EXP-092 helpers)

LO, HI = 0.8, 1.25


def components(W_t: np.ndarray, W_0: np.ndarray, F: list[int]) -> tuple[float, float]:
    pw = X.E.A._a43.group_power(W_t - W_0, "add", 113)[0]
    T = float(pw[[k - 1 for k in F]].sum())
    return T, float(pw.sum() - T)


def boot(x: np.ndarray, rng: np.random.Generator) -> list[float]:
    m = x[rng.integers(0, len(x), size=(10_000, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def main() -> None:
    rows = []
    for s in X.D.SEEDS:
        meta = json.loads((X.E.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        r = {"seed": s}
        for cell in X.D.CELLS:
            ab, ba = X.load(s, "AB", cell), X.load(s, "BA", cell)
            if isinstance(ab, str) or isinstance(ba, str):
                raise SystemExit(f"seed {s} {cell}: {ab if isinstance(ab, str) else ba}")
            (ta, ra), (tb, rb) = components(ab[1], ab[2], F), components(ba[1], ba[2], G)
            r[f"T_{cell}"], r[f"R_{cell}"] = (ta + tb) / 2, (ra + rb) / 2
        rows.append(r)
    col = lambda k: np.array([r[k] for r in rows])   # noqa: E731
    rng = np.random.default_rng(42)
    out: dict = {"n": len(rows), "cells": {}}
    for cell in X.D.CELLS:
        if cell == "n24":
            continue
        lt, lr = np.log(col(f"T_{cell}") / col("T_n24")), np.log(col(f"R_{cell}") / col("R_n24"))
        out["cells"][cell] = {"T_ratio_of_means": float(col(f"T_{cell}").mean() / col("T_n24").mean()),
                              "R_ratio_of_means": float(col(f"R_{cell}").mean() / col("R_n24").mean()),
                              "T_ratio_geo": float(np.exp(lt.mean())), "T_ratio_geo_ci": [float(np.exp(v)) for v in boot(lt, rng)],
                              "R_ratio_geo": float(np.exp(lr.mean())), "R_ratio_geo_ci": [float(np.exp(v)) for v in boot(lr, rng)]}
    out["means"] = {f"{k}_{c}": float(col(f"{k}_{c}").mean()) for k in "TR" for c in X.D.CELLS}
    t, r = out["cells"]["g24"]["T_ratio_of_means"], out["cells"]["g24"]["R_ratio_of_means"]
    sim = lambda v: LO <= v <= HI   # noqa: E731
    out["reading_g24"] = ("Selbstverstaerkung fehlt" if t < LO and sim(r) else "Korrektur fehlt" if sim(t) and r > HI
                          else "beides" if t < LO and r > HI else "unklar")
    out["rows"] = rows
    (HERE / "posthoc_components_s42.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
