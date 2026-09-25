#!/usr/bin/env python3
"""Evaluate EXP-002 (destined-frequency ban from step 1) against README.md. UNTESTED.

Baselines come from EXP-001 raw/, treatment arms from EXP-002 raw/. Uses EXP-001's interval
censoring and fail-closed loading (amendment 2026-09-25b applies here too).

    python lab/experiments/EXP-002-destined-ban/analyze.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP001 = HERE.parent / "EXP-001-freq-ban"
sys.path.insert(0, str(EXP001))

from analyze import gen_interval, load  # noqa: E402

SEEDS = (0, 1, 2)
PRIVILEGED_MARGIN, SAME_MARGIN = 1000, 500
SAME_ACROSS_ARMS = ("m", "max_steps", "stop_after_generalization", "split_hash", "amendment")


def diff_bounds(d: tuple, r: tuple) -> tuple[float, float]:
    """Bounds of gen(destined) - gen(random_t1) from crossing intervals (None = open)."""
    inf = float("inf")
    lower = d[0] - (r[1] if r[1] is not None else inf)
    upper = (d[1] if d[1] is not None else inf) - r[0]
    return lower, upper


def evaluate_seed(base: dict | None, dest: dict | None, rand: dict | None, seed: int) -> dict:
    row: dict = {"seed": seed}
    arms = {"baseline": base, "ban_destined": dest, "ban_random_t1": rand}
    missing = [k for k, v in arms.items() if v is None]
    if missing:
        return {**row, "verdict": "not_evaluable", "reason": f"missing {missing}"}
    if rand.get("t0") != 1 or rand.get("ban_from_step") != 1:
        return {**row, "verdict": "not_evaluable", "reason": "random arm is not t0 = 1"}
    for f in SAME_ACROSS_ARMS:
        if len({json.dumps(a.get(f)) for a in arms.values()}) > 1:
            return {**row, "verdict": "not_evaluable", "reason": f"{f} differs across arms"}
    # validity: local baseline must reproduce the stored model's top-5 (= destined set)
    row["destined"] = dest.get("banned_freqs")
    row["baseline_final_top"] = base.get("final_top_m_freqs")
    if set(row["destined"] or []) != set(row["baseline_final_top"] or []):
        return {**row, "verdict": "not_evaluable",
                "reason": "local baseline top-5 != stored top-5 (destined not reproduced locally)"}
    ib, idst, irnd = (gen_interval(a) for a in (base, dest, rand))
    if None in (ib, idst, irnd):
        return {**row, "verdict": "not_evaluable", "reason": "incomplete run"}
    if ib[1] is None:
        return {**row, "verdict": "not_evaluable", "reason": "baseline censored"}
    lower, upper = diff_bounds(idst, irnd)
    row.update({"gen": {"baseline": ib, "ban_destined": idst, "ban_random_t1": irnd},
                "diff_bounds": [lower, upper],
                "destined_final_top": dest.get("final_top_m_freqs"),
                "random_final_top": rand.get("final_top_m_freqs")})
    if lower >= PRIVILEGED_MARGIN:
        row["verdict"] = "privileged"
    elif lower > -SAME_MARGIN and upper < SAME_MARGIN:
        row["verdict"] = "not_privileged"
    else:
        row["verdict"] = "unclear"
    return row


def main() -> None:
    base_runs, runs = load(EXP001 / "raw"), load(HERE / "raw")
    rows = [evaluate_seed(base_runs.get((s, "baseline")), runs.get((s, "ban_destined")),
                          runs.get((s, "ban_random")), s) for s in SEEDS]
    valid = [r for r in rows if r["verdict"] != "not_evaluable"]
    n_priv = sum(r["verdict"] == "privileged" for r in valid)
    n_same = sum(r["verdict"] == "not_privileged" for r in valid)
    overall = ("nicht auswertbar" if len(valid) < 2 else "privilegiert" if n_priv >= 2
               else "nicht privilegiert" if n_same >= 2 else "unklar")
    out = {"exp_id": "EXP-002", "overall": overall, "n_valid": len(valid), "per_seed": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
