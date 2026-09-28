"""R5 post hoc (session 45; EXPLORATION on the frozen R5 summary, no runs). Answers a simulated-review objection: the registered
contrasts are geometric means of time ratios bounded at 8000 steps, with censored arms (4 R, 6 and 9 D runs without an event).

Observation fixed before computing: every censored run is censored at the same administrative bound tau = 8000, so the
Kaplan-Meier restricted mean survival time up to tau equals the plain mean of the bounded times; the RMST ratio is therefore
a standard survival summary. Computed: per arm the KM curve (event = stable generalization), RMST(8000); ratios
RMST(R)/RMST(E2_0) and mean over both target sets of RMST(D_j)/RMST(E2_j); 95 % bootstrap CI over the 20 units (paired
resampling, 20 000 draws); also the KM median. Reading fixed before computing: "consistent with the registered result" if
both RMST-ratio CIs lie above 1; the geometric-mean ratios stay the registered estimand.
  python lab/confirm/R5_posthoc_rmst_s45.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
TAU = 8000
ARMS = ("E8_0", "E2_0", "E2_1", "E1_0", "R", "D_0", "D_1")


def km(times: np.ndarray, event: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Kaplan-Meier survival S(t) at the distinct event times (probability of no generalization yet)."""
    ts = np.unique(times[event])
    s, out = 1.0, []
    for t in ts:
        at_risk = (times >= t).sum()
        d = ((times == t) & event).sum()
        s *= 1 - d / at_risk
        out.append(s)
    return ts, np.array(out)


def rmst_km(times: np.ndarray, event: np.ndarray) -> float:
    ts, s = km(times, event)
    grid = np.concatenate([[0], ts, [TAU]])
    surv = np.concatenate([[1.0], s])
    return float(np.sum(surv * np.diff(grid)))


def km_median(times: np.ndarray, event: np.ndarray) -> float | None:
    ts, s = km(times, event)
    hit = np.nonzero(s <= 0.5)[0]
    return float(ts[hit[0]]) if len(hit) else None


def main() -> None:
    r5 = json.loads((LAB / "confirm/R5_summary.json").read_text(encoding="utf-8"))
    rows = [r for r in r5["rows"] if not r.get("technical")]
    assert len(rows) == 20
    T = {a: np.array([r["times"][a][0] for r in rows], float) for a in ARMS}
    E = {a: np.array([bool(r["times"][a][1]) for r in rows]) for a in ARMS}
    assert all((T[a][~E[a]] == TAU).all() for a in ARMS), "censoring not only at tau"
    out = {"note": "post hoc exploration on the frozen R5 summary; registered estimand remains the geometric-mean ratio", "arms": {}}
    for a in ARMS:
        rm = rmst_km(T[a], E[a])
        assert abs(rm - T[a].mean()) < 1e-6          # administrative censoring at tau: KM-RMST == mean bounded time
        out["arms"][a] = {"rmst": rm, "km_median": km_median(T[a], E[a]), "censored": int((~E[a]).sum())}
    rng = np.random.default_rng(45)
    idx = rng.integers(0, 20, (20000, 20))
    ratio_R = lambda i: T["R"][i].mean() / T["E2_0"][i].mean()   # noqa: E731
    ratio_D = lambda i: 0.5 * (T["D_0"][i].mean() / T["E2_0"][i].mean() + T["D_1"][i].mean() / T["E2_1"][i].mean())   # noqa: E731
    for name, f in (("RMST_R_over_E2A", ratio_R), ("RMST_D_over_E2", ratio_D)):
        full = f(np.arange(20))
        boot = np.array([f(i) for i in idx])
        out[name] = {"ratio": full, "ci95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))]}
    out["reading"] = ("consistent with the registered result" if min(out[k]["ci95"][0] for k in ("RMST_R_over_E2A", "RMST_D_over_E2")) > 1
                      else "not consistent")
    (LAB / "confirm/R5_posthoc_rmst_s45.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
