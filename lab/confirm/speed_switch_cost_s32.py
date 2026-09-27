"""Session 32 (2026-09-27, window closed), POST HOC exploration on stored EXP-020 runs, no training.

Question ("lock-in cost"): EXP-041 showed R->E@150 mostly failing to grok by 2150 although it saw the same pairs as the fast
E->R@150. Hypothesis: grokking is slow when the frequencies fixed in the first ~50-150 steps (K4) do not match the spectrum of
the data trained on afterwards. EXP-020 (engineered F -> engineered G, other targets, common test set, seeds 30-34) tests this:
Stated before looking at any generalisation step of the switched runs:
  H-a  gen(F->G@150) > gen(G-only) in most seeds (locked to F, trained on G).
  H-b  median gen rises from switches before the lock-in (@10, @25) to after it (@50, @150).
Descriptive: @400, @1000 (F has partly or fully grokked by then), F-only. gen = trainer event (first test >= 0.95), counted
from step 0; horizon = steps_completed.
  python lab/confirm/speed_switch_cost_s32.py
"""
import json
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
RAW = LAB / "experiments/EXP-020-data-switch/raw"
SEEDS = (30, 31, 32, 33, 34)
ARMS = ["G", "F"] + [f"@{t}" for t in (10, 25, 50, 150, 400, 1000)]


def name(arm: str, s: int) -> str:
    if arm in ("F", "G"):
        return f"EXP-018_baseline_seed{s}_thr4_seed{s}_train_{arm}"
    return f"EXP-020_baseline_seed{s}_thr4_seed{s}_train_F_to_seed{s}_train_G_at{arm[1:]}"


def main() -> None:
    rows = []
    for s in SEEDS:
        row = {"seed": s}
        tests = set()
        for a in ARMS:
            r = json.loads((RAW / name(a, s) / "result.json").read_text(encoding="utf-8"))
            assert r["status"] == "completed", r["run_id"]
            tests.add(r["test_hash"])
            row[a] = [(r.get("events") or {}).get("generalization_step"), r["steps_completed"], round(float(r["final_acc"]["test"]), 3)]
        assert len(tests) == 1, s
        rows.append(row)
        print(row)
    inf = lambda v: v[0] if v[0] is not None else float("inf")
    later = sum(inf(r["@150"]) > inf(r["G"]) for r in rows)
    med = {a: float(np.median([inf(r[a]) for r in rows])) for a in ARMS}
    out = {"note": "post hoc exploration, seen seeds 30-34", "rows": rows, "H_a_at150_later_than_G": f"{later}/{len(rows)}",
           "median_gen": med}
    (LAB / "confirm/speed_switch_cost_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(out["H_a_at150_later_than_G"], med)


if __name__ == "__main__":
    main()
