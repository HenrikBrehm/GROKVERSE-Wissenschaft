"""Post hoc (exploratory, session 5): does the natural M0 top-5 share of a RANDOM split go with grokking time?
H (stated before computing): higher share -> earlier generalization (Spearman < 0). Existing runs only, no training.
Study arch25k runs (seeds 0-9, 4 architectures, 1 thread) and EXP-003d baselines (seeds 10-17, transformer, 4 threads).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[2]
sys.path.insert(0, str(LAB / "experiments/EXP-015-mask-spectrum"))
import mask_spectrum as ms  # noqa: E402

man = json.loads((LAB.parent / "training/results/run_manifest.json").read_text(encoding="utf-8"))
runs = man["runs"] if isinstance(man, dict) and "runs" in man else man


def spearmanr(x: list, y: list, n_perm: int = 100_000) -> tuple[float, float]:
    """Spearman rho (average ranks) and two-sided permutation p (seeded)."""
    def rank(v):
        v = np.asarray(v, float)
        o = np.argsort(v, kind="stable")
        r = np.empty(len(v))
        r[o] = np.arange(len(v))
        for u in np.unique(v):
            r[v == u] = r[v == u].mean()
        return r
    rx, ry = rank(x), rank(y)
    rho = float(np.corrcoef(rx, ry)[0, 1])
    rng = np.random.default_rng(0)
    null = np.array([np.corrcoef(rx, rng.permutation(ry))[0, 1] for _ in range(n_perm)])
    return rho, float((np.abs(null) >= abs(rho) - 1e-12).mean())


def share(seed: int) -> float:
    pw = ms.m0(ms.mask_matrix(seed))
    return float(np.sort(pw)[-5:].sum() / pw.sum())


def gen_of(r: dict) -> int | None:
    ck = r.get("checkpoints")
    ck = json.loads(ck) if isinstance(ck, str) else ck
    for c in ck or []:
        if "generalization" in c["kind"]:
            return int(c["step"])
    return None


shares = {s: share(s) for s in range(0, 18)}
out = {"shares": shares, "by_arch": {}}
for arch in ("txf", "mlp", "m2h"):
    rows = []
    for r in runs:
        rid = r.get("run_id", "")
        for s in range(10):
            if rid == f"{arch}_add_p113_wd1.0_frac0.3_seed{s}_arch25k" and r.get("status") == "completed":
                g = gen_of(r)
                if g is not None:
                    rows.append((s, shares[s], g))
    if len(rows) >= 5:
        rho, p = spearmanr([x[1] for x in rows], [x[2] for x in rows])
        out["by_arch"][arch] = {"n": len(rows), "rho": float(rho), "p_two_sided": float(p), "rows": rows}
base = []
for s in range(10, 18):
    f = LAB / f"experiments/EXP-003-early-prediction/raw_d/EXP-001_baseline_t2000_m5_seed{s}_thr4/result.json"
    res = json.loads(f.read_text(encoding="utf-8"))
    g = res["events"].get("generalization_step")
    if res["status"] == "completed" and g is not None:
        base.append((s, shares[s], int(g)))
rho, p = spearmanr([x[1] for x in base], [x[2] for x in base])
out["txf_thr4_seeds10_17"] = {"n": len(base), "rho": float(rho), "p_two_sided": float(p), "rows": base}
(HERE / "natural_concentration.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps({k: ({kk: (vv["n"], round(vv["rho"], 3), round(vv["p_two_sided"], 3)) for kk, vv in v.items()}
                      if k == "by_arch" else v) for k, v in out.items() if k != "shares"}, indent=1))
print("share range", round(min(shares.values()), 4), round(max(shares.values()), 4))
