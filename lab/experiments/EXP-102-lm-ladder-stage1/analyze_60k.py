"""EXP-102 follow-up 'all 60k' (session 48; written before any of these runs started; readings also in README).
Question: once the rung 'all' (loss on all positions) has grokked, is the steering back at r0 size, or does it stay reduced?
Rung all, seeds 3800-3809, F/G, 60 000 steps, raw_long60k (20 runs). W_E snapshots every 1000 steps.
Per seed: evaluable if F and G both generalized (events.generalization_step). Post-grok step
t_post = ceil((max(gen_F, gen_G) + 2000) / 1000) * 1000 (first snapshot >= 2000 steps after the later of the two), capped
at 60 000; Delta_pow(t_post) as analyze.py (same power, same bootstrap size, rng seed 1026).
Readings (evaluable seeds only, R0 = mean Delta_pow of r0 at 2000 in the pilot, R0_HALF = R0 / 2):
  'grokkt nicht'        < 5/10 seeds evaluable
  'erholt'              >= 8/10 evaluable and CI lower bound of mean Delta_pow(t_post) > R0_HALF
  'bleibt reduziert'    >= 8/10 evaluable and CI upper bound < R0_HALF
  else 'unklar'
Descriptive: paired difference Delta_pow(t_post) - Delta_pow_r0(2000) per evaluable seed (mean, bootstrap CI);
Delta_pow at 10 000 / 30 000 / 60 000 for all seeds; generalization steps; Spearman(later gen step, Delta_pow(t_post)).
Note: r0 at 2000 is on average ~1200 steps after its own grokking (pilot median 763), so the comparison is 'shortly after
grokking' on both sides, not at equal step counts.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-102-lm-ladder-stage1/analyze_60k.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import analyze as A

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw_long60k"
STEPS = 60000
TAG = "fs1_tie0_lossall"


def dpow_at(runs: dict, T: dict, t: int) -> float:
    pF, pG = runs["F"]["P"][t], runs["G"]["P"][t]
    f, g = [k - 1 for k in T["F"]], [k - 1 for k in T["G"]]
    return float(np.log(pF[f].sum() / pF[g].sum()) + np.log(pG[g].sum() / pG[f].sum()))


def load(d: Path) -> dict:
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    assert res["status"] == "completed" and res["steps_completed"] == STEPS, d
    W, S = np.load(d / "we_snapshots.npy"), [int(x) for x in np.load(d / "we_snapshot_steps.npy")]
    assert np.isfinite(W).all(), d
    return {"P": {s: A.power(W[i]) for i, s in enumerate(S)}, "gen": res["events"].get("generalization_step")}


def boot_ci(v: np.ndarray, rng: np.random.Generator) -> list[float]:
    m = v[rng.integers(0, len(v), (A.BOOT, len(v)))].mean(1)
    return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def main() -> None:
    r0 = json.loads((HERE / "pilot_summary.json").read_text(encoding="utf-8"))["rungs"]["r0"]["mean"]
    rng = np.random.default_rng(1026)
    rows = []
    for s in A.design.SEEDS:
        T = json.loads((HERE / f"splits/seed{s}.json").read_text(encoding="utf-8"))["targets"]
        runs = {x: load(RAW / f"lad_seed{s}_seed{s}_{x}_op0_{TAG}_B0_steps{STEPS}_thr1_cuda") for x in "FG"}
        r0runs = {x: {"P": {2000: A.load_power(s, x, "r0")}} for x in "FG"}
        assert all(isinstance(r0runs[x]["P"][2000], np.ndarray) for x in "FG"), (s, "r0 run missing/defect")
        row = {"seed": s, "gen_F": runs["F"]["gen"], "gen_G": runs["G"]["gen"],
               "dpow": {t: dpow_at(runs, T, t) for t in (10000, 30000, 60000)}, "dpow_r0_2000": dpow_at(r0runs, T, 2000)}
        if row["gen_F"] is not None and row["gen_G"] is not None:
            tp = min(STEPS, int(math.ceil((max(row["gen_F"], row["gen_G"]) + 2000) / 1000) * 1000))
            row["t_post"], row["dpow_post"] = tp, dpow_at(runs, T, tp)
        rows.append(row)
    ev = [r for r in rows if "dpow_post" in r]
    out: dict = {"r0_mean": r0, "r0_half": r0 / 2, "n_evaluable": len(ev), "rows": rows}
    if ev:
        v = np.array([r["dpow_post"] for r in ev])
        d = np.array([r["dpow_post"] - r["dpow_r0_2000"] for r in ev])
        out["post"] = {"mean": float(v.mean()), "ci95": boot_ci(v, rng), "n_pos": int((v > 0).sum())}
        out["paired_minus_r0"] = {"mean": float(d.mean()), "ci95": boot_ci(d, rng), "n_neg": int((d < 0).sum())}
        if len(ev) >= 4:
            out["spearman_gen_vs_post"] = spearman(np.array([max(r["gen_F"], r["gen_G"]) for r in ev], float), v)
    for t in (10000, 30000, 60000):
        v = np.array([r["dpow"][t] for r in rows])
        out[f"dpow_{t}"] = {"mean": float(v.mean()), "ci95": boot_ci(v, rng), "n_pos": int((v > 0).sum())}
    ci = out.get("post", {}).get("ci95")
    n = len(ev)
    out["reading"] = ("grokkt nicht" if n < 5 else "erholt" if n >= 8 and ci[0] > r0 / 2
                      else "bleibt reduziert" if n >= 8 and ci[1] < r0 / 2 else "unklar")
    (HERE / "long60k_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r["seed"], r["gen_F"], r["gen_G"], r.get("t_post"), round(r.get("dpow_post", float("nan")), 2),
              round(r["dpow_r0_2000"], 2), {k: round(x, 2) for k, x in r["dpow"].items()})


if __name__ == "__main__":
    main()
