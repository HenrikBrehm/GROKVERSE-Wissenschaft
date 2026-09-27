"""Session 32 (2026-09-27, window closed), POST HOC exploration on the stored N28 block (30 seeds, GPU), no training.

Motivation: in EXP-020 (5 seeds) switches at 10/25/50 steps often failed to grok by ~2000 steps, a switch at 150 did not slow
grokking (speed_switch_cost_s32.py). N28 has, per seed, A-only, B-only and switches A->B / B->A at 25 and 50 (common test set).
Its generalisation steps were never looked at. Stated before looking:
  Q-a  a switch at 25 delays grokking against the destination-only run (A->B@25 vs B-only, B->A@25 vs A-only), pooled over
       both directions: exact one-sided sign test over pairs whose order is determined under censoring.
  Q-b  @25 is slower than @50 (same direction, same seed), pooled, sign test.
Descriptive: share of runs with an event per arm, median gen (inf = none), and the same for @50 vs destination-only.
gen = trainer event (first test >= 0.95), counted from step 0; horizon = steps_completed.
  python lab/confirm/speed_switch_cost_n28_s32.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
RAW = LAB / "confirm/n28_raw"
PAT = re.compile(r"seed(\d+)_thr1_n28_seed\d+_w0_(A|B)(?:_to_n28_seed\d+_w0_(A|B)_at(\d+)(_rom)?)?_devcuda$")


def load() -> dict:
    runs = {}
    for d in RAW.iterdir():
        m = PAT.search(d.name)
        if not m or m.group(5):                      # skip the _rom (optimizer-moment) variants
            continue
        s, a, b, t = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        arm = a if b is None else f"{a}{b}@{t}"
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        assert r["status"] == "completed", d.name
        runs.setdefault(s, {})[arm] = {"gen": (r.get("events") or {}).get("generalization_step"), "h": r["steps_completed"],
                                        "test": float(r["final_acc"]["test"]), "th": r["test_hash"]}
    return runs


def later(a: dict, b: dict) -> int:
    """+1 if a strictly later than b, -1 if earlier, 0 if tie/undetermined."""
    ga = a["gen"] if a["gen"] is not None else math.inf
    gb = b["gen"] if b["gen"] is not None else math.inf
    if ga == gb:
        return 0
    if ga > gb:
        return 1 if gb <= a["h"] else 0
    return -1 if ga <= b["h"] else 0


def sign_p(k: int, n: int) -> float:
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0


def test(pairs: list[int]) -> dict:
    d = [x for x in pairs if x]
    k = sum(x > 0 for x in d)
    return {"later": k, "earlier": len(d) - k, "undetermined_or_tie": len(pairs) - len(d), "p_one_sided": sign_p(k, len(d))}


def main() -> None:
    runs = load()
    for s, r in runs.items():
        assert len({v["th"] for v in r.values()}) == 1, s
    arms = ["A", "B", "AB@25", "BA@25", "AB@50", "BA@50"]
    per_arm = {a: {"n": sum(a in r for r in runs.values()),
                   "with_event": sum(1 for r in runs.values() if a in r and r[a]["gen"] is not None),
                   "median_gen": float(np.median([r[a]["gen"] if r[a]["gen"] is not None else math.inf for r in runs.values() if a in r]))}
               for a in arms}
    qa = [later(r["AB@25"], r["B"]) for r in runs.values()] + [later(r["BA@25"], r["A"]) for r in runs.values()]
    q50 = [later(r["AB@50"], r["B"]) for r in runs.values()] + [later(r["BA@50"], r["A"]) for r in runs.values()]
    qb = [later(r["AB@25"], r["AB@50"]) for r in runs.values()] + [later(r["BA@25"], r["BA@50"]) for r in runs.values()]
    out = {"note": "post hoc exploration on the N28 block (seeds seen for the frequency analysis, gen never looked at)",
           "n_seeds": len(runs), "per_arm": per_arm, "Q_a_at25_vs_destination": test(qa),
           "descr_at50_vs_destination": test(q50), "Q_b_at25_vs_at50": test(qb)}
    (LAB / "confirm/speed_switch_cost_n28_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
