"""EXP-102 follow-up 'all lang' (session 47; written while the runs were going, before any result was read; readings in README).
Rungs all and tieall, seeds 3800-3809, F/G, 10 000 steps, raw_long. Delta_pow as analyze.py (same power, same bootstrap) at
steps 2000, 5000, 10 000; generalization per run from events.generalization_step.
  'verzoegert, Steuerung erholt'  >= 8/10 seeds generalized in F and G and CI lower bound of Delta_pow(10 000) > R0_HALF
  'Steuerung blockiert'            >= 8/10 generalized and CI upper bound < R0_HALF
  'grokkt nicht'                   < 5/10 generalized
  else 'unklar'
R0_HALF = 0.5 * mean Delta_pow of r0 in the pilot (pilot_summary.json).
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-102-lm-ladder-stage1/analyze_long.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import analyze as A

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw_long"
RUNGS = {"all": "fs1_tie0_lossall", "tieall": "fs1_tie1_lossall"}


def main() -> None:
    r0_half = 0.5 * json.loads((HERE / "pilot_summary.json").read_text(encoding="utf-8"))["rungs"]["r0"]["mean"]
    out: dict = {"r0_half": r0_half}
    for rung, tag in RUNGS.items():
        rows = []
        for s in A.design.SEEDS:
            T = json.loads((HERE / f"splits/seed{s}.json").read_text(encoding="utf-8"))["targets"]
            runs = {}
            for x in "FG":
                d = HERE / "raw_long" / f"lad_seed{s}_seed{s}_{x}_op0_{tag}_B0_steps10000_thr1_cuda"
                res = json.loads((d / "result.json").read_text(encoding="utf-8"))
                assert res["status"] == "completed" and res["steps_completed"] == 10000, d
                W, S = np.load(d / "we_snapshots.npy"), list(np.load(d / "we_snapshot_steps.npy"))
                runs[x] = ({t: A.power(W[S.index(t)]) for t in (2000, 5000, 10000)}, res["events"].get("generalization_step"))
            dp = {t: float(np.log(runs["F"][0][t][[k - 1 for k in T["F"]]].sum() / runs["F"][0][t][[k - 1 for k in T["G"]]].sum())
                           + np.log(runs["G"][0][t][[k - 1 for k in T["G"]]].sum() / runs["G"][0][t][[k - 1 for k in T["F"]]].sum()))
                  for t in (2000, 5000, 10000)}
            rows.append({"seed": s, "dpow": dp, "gen_F": runs["F"][1], "gen_G": runs["G"][1]})
        rng = np.random.default_rng(102)
        n_gen = sum(r["gen_F"] is not None and r["gen_G"] is not None for r in rows)
        stats = {}
        for t in (2000, 5000, 10000):
            v = np.array([r["dpow"][t] for r in rows])
            m = v[rng.integers(0, len(v), (A.BOOT, len(v)))].mean(1)
            stats[t] = {"mean": float(v.mean()), "ci95": [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))], "n_pos": int((v > 0).sum())}
        ci = stats[10000]["ci95"]
        rd = ("grokkt nicht" if n_gen < 5 else "verzoegert, Steuerung erholt" if n_gen >= 8 and ci[0] > r0_half
              else "Steuerung blockiert" if n_gen >= 8 and ci[1] < r0_half else "unklar")
        gens = [g for r in rows for g in (r["gen_F"], r["gen_G"]) if g is not None]
        out[rung] = {"reading": rd, "n_seeds_generalized_both": n_gen, "gen_median": float(np.median(gens)) if gens else None,
                     "dpow": stats, "rows": rows}
    (HERE / "long_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk != "rows"} if isinstance(v, dict) else v) for k, v in out.items()}, indent=1))


if __name__ == "__main__":
    main()
