"""Post hoc (session 31), EXPLORATION: does the engineered-split speed-up also hold for mul 113 and add 97 (rule 15c)? Stored EXP-043 runs
(GPU): per seed 10 inits x arms F, G (eps 2) and R (eps 0, uniform), same init per seed. Test sets are complements of the train split
(confounded, as in EXP-016; a common test set exists only for add 113). Stated before looking: in both tasks the engineered arms (mean
bounded log2 time of F and G) generalise earlier than R in most seeds. Event = trainer first crossing (test >= 0.95); censored = budget.
  python lab/confirm/speed_posthoc_other_tasks.py
"""
import json
import math
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
RAW = LAB / "experiments" / "EXP-043-generalize-steering" / "raw"


def main() -> None:
    out = {}
    for task in ("add97", "mul113"):
        rows = []
        for d in sorted(RAW.glob(f"EXP-043_*_eps0.0_R_{task}_devcuda")):
            seed = d.name.split("_seed")[1].split("_")[0]
            t = {}
            for arm, eps in (("R", "0.0"), ("F", "2.0"), ("G", "2.0")):
                r = json.loads((RAW / d.name.replace("eps0.0_R", f"eps{eps}_{arm}") / "result.json").read_text(encoding="utf-8"))
                g = (r.get("events") or {}).get("generalization_step")
                t[arm] = (g if g is not None else r["max_steps"], g is not None)
            L = math.log2(t["R"][0]) - (math.log2(t["F"][0]) + math.log2(t["G"][0])) / 2
            rows.append({"seed": int(seed), **{a: list(v) for a, v in t.items()}, "L": L})
        Ls = np.array([r["L"] for r in rows])
        w, l = int((Ls > 0).sum()), int((Ls < 0).sum())
        out[task] = {"n": len(rows), "engineered_earlier": w, "R_earlier": l, "median_L": float(np.median(Ls)),
                     "R_observed": sum(r["R"][1] for r in rows), "FG_observed": sum(r["F"][1] + r["G"][1] for r in rows),
                     "p_sign_one_sided": sum(math.comb(w + l, k) for k in range(w, w + l + 1)) / 2 ** (w + l), "rows": rows}
        print(task, {k: v for k, v in out[task].items() if k != "rows"})
    (LAB / "confirm" / "speed_posthoc_other_tasks.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
