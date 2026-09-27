"""Post hoc (session 30), EXPLORATION: generalization event (trainer: first test >= 0.95) of stored runs with engineered vs random
splits. Test sets are complements of the training split in all groups here (confounded; see EXP041_posthoc_speed.py for a common
test set and EXP-018 for the pre-registered test). Groups: EXP-016 pilot engineered (CPU), EXP-003d random baselines (CPU),
P1 add 113 F/G (GPU, 2000 steps), EXP-047 engineered vs shuffled pair structure with identical token frequencies (GPU, 2000 steps).

  python lab/confirm/speed_posthoc_gen_steps.py
"""
import json
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
GROUPS = {"EXP-016 engineered (CPU)": "experiments/EXP-016-engineered-split/raw/EXP-016_*",
          "EXP-003d random (CPU)": "experiments/EXP-003-early-prediction/raw_d/EXP-001_baseline_t2000_m5_seed*_thr4",
          "P1 add113 F/G (GPU)": "confirm/raw/EXP-016_*add113_seed*_[FG]_devcuda",
          "EXP-047 engineered (GPU)": "experiments/EXP-047-marginal-control/raw/*_eng_[FG]_devcuda",
          "EXP-047 shuffled (GPU)": "experiments/EXP-047-marginal-control/raw/*_shuf_[FG]_devcuda"}


def main() -> None:
    out = {}
    for name, pat in GROUPS.items():
        g, acc, steps = [], [], []
        for d in sorted(LAB.glob(pat)):
            r = json.loads((d / "result.json").read_text(encoding="utf-8"))
            g.append((r.get("events") or {}).get("generalization_step"))
            acc.append(r["final_acc"]["test"])
            steps.append(r["steps_completed"])
        ok = [x for x in g if x is not None]
        out[name] = {"runs": len(g), "generalized": len(ok), "median_gen": float(np.median(ok)) if ok else None,
                     "range_gen": [min(ok), max(ok)] if ok else None, "max_steps_completed": max(steps),
                     "final_test_range": [round(min(acc), 3), round(max(acc), 3)]}
        print(name, out[name])
    (LAB / "confirm/speed_posthoc_gen_steps.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
