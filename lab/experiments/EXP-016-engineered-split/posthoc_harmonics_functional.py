"""Post hoc (session 5): (k, fold(2k)) pairs among the FUNCTIONAL (ablation-based, 'nanda') key frequencies of the study
(seeds 0-9, step 25000). If 2k were only waveform distortion in W_E, functional keys should not be enriched.
Null: random sets of the same size from 1..56."""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
P = 113


def fold(x):
    x %= P
    return min(x, P - x)


def pairs(S):
    S = set(S)
    return sum(fold(2 * k) in S for k in S)


rows = []
for s in range(10):
    f = ROOT / f"training/runs/txf_add_p113_wd1.0_frac0.3_seed{s}_arch25k/analysis/key_frequencies/step025000.json"
    res = json.loads(f.read_text(encoding="utf-8"))["results"]
    res = res if isinstance(res, dict) else eval(res, {"__builtins__": {}})   # stored as repr string (as EXP-015)
    K = sorted(res["primary_key_frequencies"])
    rows.append({"seed": s, "K": K, "pairs": pairs(K), "which": [(k, fold(2 * k)) for k in K if fold(2 * k) in K]})
rng = np.random.default_rng(0)
nulls = np.array([np.mean([pairs(rng.choice(np.arange(1, 57), len(r["K"]), replace=False)) for r in rows])
                  for _ in range(20000)])
obs = float(np.mean([r["pairs"] for r in rows]))
out = {"mean_pairs": obs, "null_mean": float(nulls.mean()), "p_ge": float((nulls >= obs - 1e-12).mean()), "rows": rows}
for r in rows:
    print(r)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}))
(Path(__file__).resolve().parent / "posthoc_harmonics_functional.json").write_text(json.dumps(out, indent=1))
