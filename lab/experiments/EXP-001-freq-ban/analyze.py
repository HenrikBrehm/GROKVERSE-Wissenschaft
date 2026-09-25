#!/usr/bin/env python3
"""Evaluate EXP-001 against the decision rule fixed in README.md. Reads raw/*/result.json only.

    python lab/experiments/EXP-001-freq-ban/analyze.py [--raw DIR]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUPPORT_MARGIN, AGAINST_MARGIN = 1000, 500


CONDS = ("baseline", "ban_emerging", "ban_random", "shrink_matched")
SAME_ACROSS_ARMS = ("t0", "m", "max_steps", "stop_after_generalization", "split_hash", "amendment")


def load(raw: Path) -> dict:
    """Fail closed: duplicate (seed, condition) entries are an error, not a silent overwrite."""
    runs = {}
    for f in sorted(raw.glob("*/result.json")):
        r = json.loads(f.read_text())
        key = (r["seed"], r["condition"])
        if key in runs:
            raise SystemExit(f"duplicate run for {key}: {runs[key]['run_id']} and {r['run_id']}")
        runs[key] = r
    return runs


def gen_interval(r: dict) -> tuple[int, int | None] | None:
    """Crossing as an interval: observed g -> (g, g); censored at cap C -> (C, None = open).
    Incomplete runs -> None."""
    if r.get("status") != "completed":
        return None
    g = r["transitions"]["primary"]["generalization"]["first_crossing_step"]
    return (g, g) if g is not None else (r["steps_completed"], None)


def classify(e: tuple[int, int | None], r: tuple[int, int | None]) -> str:
    """Decision on gen(emerging) - gen(random) (the baseline cancels), with interval bounds."""
    lower = e[0] - (r[1] if r[1] is not None else float("inf"))
    upper = (e[1] if e[1] is not None else float("inf")) - r[0]
    if lower >= SUPPORT_MARGIN:
        return "support"
    if upper <= AGAINST_MARGIN:
        return "against"
    return "unclear"


def validate_seed(runs: dict, seed: int) -> str | None:
    """Reason why this seed cannot be evaluated, or None."""
    arms = [runs.get((seed, c)) for c in ("baseline", "ban_emerging", "ban_random")]
    if any(a is None for a in arms):
        return "missing arm"
    for field in SAME_ACROSS_ARMS:
        vals = {json.dumps(a.get(field)) for a in arms if field != "t0" or a["condition"] != "baseline"}
        if len(vals) > 1:
            return f"{field} differs across arms"
    if len({a["config"]["threads"] for a in arms}) > 1:
        return "threads differ across arms"
    return None


def banned_power_leak(r: dict, raw: Path) -> float | None:
    """Max share of W_E power in the banned frequencies after the ban step (should be ~0)."""
    if not r.get("banned_freqs"):
        return None
    import numpy as np
    d = raw / r["run_id"]
    spec, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy")
    after = spec[steps >= r["ban_from_step"]]
    if not len(after):
        return None
    idx = [k - 1 for k in r["banned_freqs"]]
    return float((after[:, idx].sum(axis=1) / after.sum(axis=1)).max())


def jaccard(a, b) -> float | None:
    if not a or not b:
        return None
    return len(set(a) & set(b)) / len(set(a) | set(b))


def evaluate_seed(runs: dict, seed: int, raw: Path) -> dict:
    row = {"seed": seed, "invalid_reason": validate_seed(runs, seed)}
    base = runs.get((seed, "baseline"))
    ib = gen_interval(base) if base else None
    row["baseline_gen"] = ib
    for cond in CONDS[1:]:
        r = runs.get((seed, cond))
        iv = gen_interval(r) if r else None
        row[f"{cond}_gen"] = iv
        row[f"{cond}_delay"] = (iv[0] - ib[0]) if (iv and ib and iv[1] is not None
                                                   and ib[1] is not None) else None
        if r:
            row[f"{cond}_banned"] = r.get("banned_freqs")
            row[f"{cond}_events"] = {k: v for k, v in r.get("events", {}).items() if k != "power_at_ban"}
            row[f"{cond}_final_top"] = r.get("final_top_m_freqs")
            row[f"{cond}_jaccard_vs_baseline_final"] = jaccard(
                r.get("final_top_m_freqs"), base.get("final_top_m_freqs") if base else None)
            row[f"{cond}_banned_power_leak"] = banned_power_leak(r, raw)
    ie, ir = row["ban_emerging_gen"], row["ban_random_gen"]
    if row["invalid_reason"] or not (ib and ie and ir) or ib[1] is None:
        row["verdict"] = "not_evaluable"
    else:
        row["verdict"] = classify(ie, ir)
    # secondary (amendment 2026-09-25b, not part of the decision): identity vs. energy
    isr = row["shrink_matched_gen"]
    row["secondary_emerging_vs_shrink"] = classify(ie, isr) if (ie and isr) else None
    row["delay_difference"] = (ie[0] - ir[0]) if (ie and ir and ie[1] is not None
                                                  and ir[1] is not None) else None
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(HERE / "raw"))
    a = ap.parse_args()
    runs = load(Path(a.raw))
    seeds = sorted({s for s, _ in runs})
    rows = [evaluate_seed(runs, s, Path(a.raw)) for s in seeds]
    n_sup = sum(r["verdict"] == "support" for r in rows)
    n_ag = sum(r["verdict"] == "against" for r in rows)
    n_eval = sum(r["verdict"] != "not_evaluable" for r in rows)
    overall = ("support" if n_sup >= 2 else "against" if n_ag >= 2
               else "unclear" if n_eval >= 3 else "incomplete")
    summary = {"exp_id": "EXP-001", "rule": f"support if lower bound of gen(emerging)-gen(random) >= {SUPPORT_MARGIN} in >= 2/3 "
               f"seeds; against if its upper bound <= {AGAINST_MARGIN} in >= 2/3 (interval censoring, "
               "amendment 2026-09-25b)",
               "overall": overall, "n_support": n_sup, "n_against": n_ag, "n_evaluable": n_eval,
               "per_seed": rows,
               "runs": {f"{s}/{c}": {"status": r.get("status"), "run_id": r.get("run_id"),
                                     "git_commit": r.get("git_commit"), "elapsed_s": r.get("elapsed_s"),
                                     "sec_per_step": r.get("sec_per_step"),
                                     "versions": r.get("versions"), "split_hash": r.get("split_hash")}
                        for (s, c), r in runs.items()}}
    (HERE / "summary.json").write_text(json.dumps(summary, indent=1))
    lines = ["# EXP-001 summary (generated by analyze.py — do not edit by hand)", "",
             f"Overall: **{overall}** ({n_sup} support / {n_ag} against / {n_eval} evaluable)", "",
             "| seed | baseline gen | ban_emerging gen (Δ) | ban_random gen (Δ) | Δe−Δr | banned (emerging) | banned (random) | verdict |",
             "|---|---|---|---|---|---|---|---|"]
    fmt = lambda iv: "—" if iv is None else (f">{iv[0]}" if iv[1] is None else str(iv[0]))  # noqa: E731
    for r in rows:
        lines.append(f"| {r['seed']} | {fmt(r['baseline_gen'])} | "
                     f"{fmt(r['ban_emerging_gen'])} ({r['ban_emerging_delay']}) | "
                     f"{fmt(r['ban_random_gen'])} ({r['ban_random_delay']}) | "
                     f"{r['delay_difference']} | {r.get('ban_emerging_banned')} | "
                     f"{r.get('ban_random_banned')} | {r['verdict']} |")
    (HERE / "SUMMARY.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
