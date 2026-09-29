"""EXP-102 check 'r0 long' (session 48, written before the runs): does the steering of r0 (answer loss, full batch) change
with long training, i.e. is the all-60k gap a training-length artefact? r0, seeds 3800-3809, F/G, 30 000 steps
(raw_r0long30k), snapshots every 1000. Compared with rung 'all' (raw_long60k) at equal step counts 10 000 and 30 000.
Readings (bootstrap 10 000, rng 1027):
  r0 drift:  CI of r0(30k) - r0(2000, same runs) excludes 0 -> 'r0 driftet' (sign reported), else 'r0 stabil'
  gap:       CI upper bound of all(30k) - r0(30k) < 0 -> 'Abstand bleibt bei gleicher Schrittzahl'; CI contains 0 -> 'kein Abstand'
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-102-lm-ladder-stage1/analyze_r0long.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import analyze as A

HERE = Path(__file__).resolve().parent


def snaps(root: str, s: int, x: str, tag: str, steps: int) -> dict:
    d = HERE / root / f"lad_seed{s}_seed{s}_{x}_op0_{tag}_B0_steps{steps}_thr1_cuda"
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    assert r["status"] == "completed" and r["steps_completed"] == steps, d
    W, S = np.load(d / "we_snapshots.npy"), [int(v) for v in np.load(d / "we_snapshot_steps.npy")]
    assert np.isfinite(W).all(), d
    return {t: A.power(W[i]) for i, t in enumerate(S)}


def dp(PF: dict, PG: dict, T: dict, t: int) -> float:
    return A.delta_pow(PF[t], PG[t], T["F"], T["G"])


def ci(v: np.ndarray, rng) -> list[float]:
    m = v[rng.integers(0, len(v), (A.BOOT, len(v)))].mean(1)
    return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]


def main() -> None:
    rng, rows = np.random.default_rng(1027), []
    for s in A.design.SEEDS:
        T = json.loads((HERE / f"splits/seed{s}.json").read_text(encoding="utf-8"))["targets"]
        r0 = {x: snaps("raw_r0long30k", s, x, "fs0_tie0_lossanswer", 30000) for x in "FG"}
        al = {x: snaps("raw_long60k", s, x, "fs1_tie0_lossall", 60000) for x in "FG"}
        rows.append({"seed": s, **{f"r0_{t}": dp(r0["F"], r0["G"], T, t) for t in (2000, 10000, 30000)},
                     **{f"all_{t}": dp(al["F"], al["G"], T, t) for t in (10000, 30000)}})
    g = lambda k: np.array([r[k] for r in rows])   # noqa: E731
    drift, gap30, gap10 = g("r0_30000") - g("r0_2000"), g("all_30000") - g("r0_30000"), g("all_10000") - g("r0_10000")
    out = {"means": {k: float(g(k).mean()) for k in rows[0] if k != "seed"},
           "r0_drift_30k_minus_2k": {"mean": float(drift.mean()), "ci95": ci(drift, rng)},
           "all_minus_r0_30k": {"mean": float(gap30.mean()), "ci95": ci(gap30, rng), "n_neg": int((gap30 < 0).sum())},
           "all_minus_r0_10k": {"mean": float(gap10.mean()), "ci95": ci(gap10, rng), "n_neg": int((gap10 < 0).sum())}, "rows": rows}
    c = out["r0_drift_30k_minus_2k"]["ci95"]
    out["reading_drift"] = "r0 stabil" if c[0] <= 0 <= c[1] else f"r0 driftet ({'hoch' if c[0] > 0 else 'runter'})"
    c = out["all_minus_r0_30k"]["ci95"]
    out["reading_gap"] = "Abstand bleibt bei gleicher Schrittzahl" if c[1] < 0 else "kein Abstand" if c[0] <= 0 <= c[1] else "all groesser"
    (HERE / "r0long_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
