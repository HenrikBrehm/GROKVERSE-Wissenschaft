"""Checks after the Codex conclusion review (2026-09-26):
(a) exact permutation p (all n! mask assignments, ties counted as >= extreme) for phase 2 (seeds 10-17);
(b) matched vs foreign M0 against the study's functional 'nanda' key frequencies at 25k (seeds 0-9),
    instead of the W_E top-5. No training; run through guarded_run.py."""
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mask_spectrum as ms  # noqa: E402
import predict as p12  # noqa: E402

ROOT = HERE.parents[2]


def exact_p(R: np.ndarray) -> tuple[float, float]:
    n = len(R)
    obs = np.trace(R) / n
    vals = np.array([R[np.arange(n), list(pi)].mean() for pi in itertools.permutations(range(n))])
    return float(obs), float(np.mean(vals <= obs + 1e-12))


out = {}
ph2 = json.loads((HERE / "summary_phase2.json").read_text(encoding="utf-8"))
valid = [r for r in ph2["rows"] if r["valid"]]
seeds = [r["seed"] for r in valid]
masks = {s: ms.m0(ms.mask_matrix(s)) for s in seeds}
R = np.array([[p12.rbar(masks[m], r["K"]) for m in seeds] for r in valid])
obs, p = exact_p(R)
out["phase2_exact"] = {"n": len(seeds), "rbar_matched": obs, "p_exact_ties_inclusive": p}

K = {}
for s in range(10):
    f = ROOT / f"training/runs/txf_add_p113_wd1.0_frac0.3_seed{s}_arch25k/analysis/key_frequencies/step025000.json"
    res = json.loads(f.read_text(encoding="utf-8"))["results"]
    res = res if isinstance(res, dict) else eval(res, {"__builtins__": {}})   # stored as repr string
    K[s] = res["primary_key_frequencies"]
masks0 = {s: ms.m0(ms.mask_matrix(s)) for s in range(10)}
R0 = np.array([[p12.rbar(masks0[m], K[s]) for m in range(10)] for s in range(10)])
obs0, p0 = exact_p(R0)
out["nanda_keys_seeds0_9"] = {"K_sizes": {s: len(K[s]) for s in K}, "rbar_matched": obs0,
                              "rbar_foreign": float((R0.sum() - np.trace(R0)) / 90), "p_exact_ties_inclusive": p0}
(HERE / "exact_and_keyfreq_check.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
