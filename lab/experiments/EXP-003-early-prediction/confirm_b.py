"""EXP-003b: confirm F6 (fixed candidate) on the untouched external two-hot runs. See CONFIRM_b.md."""
from __future__ import annotations

import json
import subprocess
import sys

import numpy as np

from early_predict import (ALPHA, FEATURES, HERE, N_PERM, PERM_SEED, ROOT, features_for,
                           perm_null, spearman)

EXT_RUNS = ROOT / "training" / "external" / "twohot10" / "runs"
PATTERN = "m2h_add_p113_wd1.0_frac0.3_seed{s}_arch25k"
CANDIDATE = "F6_WE_top8_conc"


def main() -> int:
    rows = [features_for(PATTERN.format(s=s), EXT_RUNS) for s in range(10)]
    y = np.array([r["generalization_step"] for r in rows], dtype=float)
    rng = np.random.default_rng(PERM_SEED)
    stats = {}
    for f in FEATURES:
        x = np.array([r[f] for r in rows])
        rho, null = spearman(x, y), perm_null(y, x, rng)
        stats[f] = {"rho": rho, "p_less": float((null <= rho + 1e-12).mean()),
                    "p_two_sided": float((np.abs(null) >= abs(rho) - 1e-12).mean())}
    c = stats[CANDIDATE]
    if c["rho"] >= 0:
        verdict = "widerspricht"
    elif c["p_less"] < ALPHA:
        verdict = "bestätigt"
    else:
        verdict = "richtungsgleich, nicht signifikant"
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()
    out = {"experiment": "EXP-003b", "code_commit": commit, "candidate": CANDIDATE,
           "verdict": verdict, "stats": stats, "rows": rows, "n_perm": N_PERM,
           "env": {"python": sys.version.split()[0], "numpy": np.__version__}}
    (HERE / "summary_b.json").write_text(json.dumps(out, indent=2, ensure_ascii=False),
                                         encoding="utf-8")
    print(verdict, {f: (round(v["rho"], 3), round(v["p_two_sided"], 3)) for f, v in stats.items()})
    print("gen steps:", y.astype(int).tolist())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
