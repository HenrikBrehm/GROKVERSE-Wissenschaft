"""EXP-003c (EXPLORATORY, all data already seen): Spearman(F6 at checkpoint t, generalization step)
for every grid checkpoint t below the earliest generalization step of each group.

Not a confirmation: groups and feature were chosen after EXP-003/003b. Output: time_resolved.json.
"""
from __future__ import annotations

import json

import numpy as np

from early_predict import (GROUPS, HERE, N_PERM, PERM_SEED, ROOT, RUNS, TOP_K_FREQ,
                           embedding_matrix, fourier_top_k_concentration, load_ckpt,
                           perm_null, spearman)

EXT_RUNS = ROOT / "training" / "external" / "twohot10" / "runs"
ALL_GROUPS = {**{g: (RUNS, pat) for g, pat in GROUPS.items()},
              "confirm_b_m2h": (EXT_RUNS, "m2h_add_p113_wd1.0_frac0.3_seed{s}_arch25k")}
GRID = [0, 500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 12000]


def group_series(root, pattern) -> dict:
    runs = []
    for s in range(10):
        d = root / pattern.format(s=s)
        run = json.loads((d / "run.json").read_text(encoding="utf-8"))
        runs.append((d, run, run["transitions"]["primary"]["generalization"]["first_crossing_step"]))
    y = np.array([g for _, _, g in runs], dtype=float)
    steps = [t for t in GRID if t < y.min()]
    rng = np.random.default_rng(PERM_SEED)
    out = []
    for t in steps:
        x = np.array([fourier_top_k_concentration(
            embedding_matrix(load_ckpt(d, t), run.get("embedding_object")),
            run["config"]["p"], TOP_K_FREQ) for d, run, _ in runs])
        rho = spearman(x, y)   # t = 0 serves as a null check: init structure should not predict
        p = float((np.abs(perm_null(y, x, rng)) >= abs(rho) - 1e-12).mean())
        out.append({"step": t, "rho": rho, "p_two_sided": p, "f6_mean": float(x.mean()),
                    "f6_min": float(x.min()), "f6_max": float(x.max())})
    return {"gen_min": int(y.min()), "gen_max": int(y.max()), "series": out}


def main() -> int:
    res = {g: group_series(root, pat) for g, (root, pat) in ALL_GROUPS.items()}
    res["_note"] = "EXPLORATORY; t=0 is a null check (random init)"
    (HERE / "time_resolved.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    for g, r in res.items():
        if g.startswith("_"):
            continue
        print(g, f"gen {r['gen_min']}-{r['gen_max']}")
        for e in r["series"]:
            print(f"  t={e['step']:>5}  F6 mean {e['f6_mean']:.3f}  rho {e['rho']:+.2f}  p {e['p_two_sided']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
