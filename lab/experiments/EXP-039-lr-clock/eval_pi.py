"""EXP-039, descriptive (session 14, written before any run; UNTESTED): pi per seed and cell against predictions_pi.json.

pi = (D - D_onlyG) / (D_onlyF - D_onlyG) with D = beta_F - beta_G (EXP-020 posthoc_beta_persistence.D), normalised by the pure
EXP-018 runs of the seed (EXP-020 raw, no lr scaling), exactly as in the frozen predictions. Runs: EXP-039 raw, name of the
EXP-020 switch run + "_lrs{c}" (analyze.load_mod). A run counts only if result.json is 'completed' with the expected lr_scale.
RMSE of the three frozen clock models over all available (seed, cell) values. No verdict (analyze.py decides EXP-039).
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
E20 = HERE.parent / "EXP-020-data-switch"
sys.path.insert(0, str(E20))
from posthoc_beta_persistence import D  # noqa: E402

SEEDS = (30, 31, 32, 34)
GRID = {2.0: (10, 25, 50), 0.5: (50, 100, 150)}


def main() -> None:
    pred = json.loads((HERE / "predictions_pi.json").read_text(encoding="utf-8"))["predictions"]
    rows = []
    for s in SEEDS:
        dF = D(E20 / "raw" / f"EXP-018_baseline_seed{s}_thr4_seed{s}_train_F", s, 2000)
        dG = D(E20 / "raw" / f"EXP-018_baseline_seed{s}_thr4_seed{s}_train_G", s, 2000)
        for c, ts in GRID.items():
            for t in ts:
                r = HERE / "raw" / f"EXP-020_baseline_seed{s}_thr4_seed{s}_train_F_to_seed{s}_train_G_at{t}_lrs{c:g}"
                if not (r / "result.json").exists():
                    continue
                res = json.loads((r / "result.json").read_text(encoding="utf-8"))
                if res.get("status") != "completed" or float(res.get("lr_scale", 1.0)) != c:
                    continue
                rows.append({"seed": s, "cell": f"c{c:g}_t{t}", "pi": (D(r, s, None) - dG) / (dF - dG)})
    out = {"rows": rows, "n": len(rows), "rmse": {m: float(np.sqrt(np.mean([(r["pi"] - p[r["cell"]]) ** 2 for r in rows])))
                                                  for m, p in pred.items()} if rows else None}
    (HERE / "eval_pi.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
