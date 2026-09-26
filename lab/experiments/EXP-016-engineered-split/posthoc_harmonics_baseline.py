"""Post hoc (session 5): do networks on RANDOM splits also learn pairs (k, fold(2k)) within K?
Count ordered pairs k, fold(2k) both in K per run; null = random 5-sets from 1..56 (MC). Seeds 0-9 (EXP-009 k_final,
study arch25k) and 10-17 (EXP-003d baselines, final_top_m_freqs). Also EXP-016 runs for comparison."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
P = 113


def fold(x: int) -> int:
    x %= P
    return min(x, P - x)


def pairs(K: list[int]) -> int:
    S = set(K)
    return sum(fold(2 * k) in S and fold(2 * k) != k for k in S)


k009 = {}
for r in json.loads((LAB / "experiments/EXP-009-freq-commitment/summary.json").read_text(encoding="utf-8"))["runs"]:
    if r["run"].startswith("txf_add_p113_wd1.0_frac0.3_seed") and r["run"].endswith("arch25k"):
        k009[int(r["run"].split("seed")[1].split("_")[0])] = r["k_final"]
base = dict(k009)
for s in range(10, 18):
    f = LAB / f"experiments/EXP-003-early-prediction/raw_d/EXP-001_baseline_t2000_m5_seed{s}_thr4/result.json"
    base[s] = json.loads(f.read_text(encoding="utf-8"))["final_top_m_freqs"]
eng = [r["K"] for r in json.loads((HERE / "posthoc_m0c.json").read_text(encoding="utf-8"))]
rng = np.random.default_rng(0)
null = np.array([pairs(list(rng.choice(np.arange(1, 57), 5, replace=False))) for _ in range(100_000)])
obs_b = [pairs(K) for K in base.values()]
obs_e = [pairs(K) for K in eng]
out = {"null_mean_pairs_per_set": float(null.mean()),
       "baseline": {"n": len(obs_b), "mean": float(np.mean(obs_b)), "per_seed": dict(zip(map(str, base), obs_b)),
                    "p_mean_ge": float((np.array([rng.choice(null, len(obs_b)).mean() for _ in range(20_000)])
                                        >= np.mean(obs_b)).mean())},
       "engineered_EXP016": {"n": len(obs_e), "mean": float(np.mean(obs_e))}}
print(json.dumps(out, indent=1))
print({s: K for s, K in base.items()})
(HERE / "posthoc_harmonics_baseline.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
