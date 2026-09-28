#!/usr/bin/env python3
"""Table of the confirmation blocks behind the paper's claims, generated from the frozen manifests and job lists (no hand-typed numbers).

Reads lab/confirm/<block>_manifest.json (commit, seeds) and lab/confirm/<block>_jobs.txt (number of runs); writes table_registrations.md.
Session 26. Pure file reading, no training.

  python lab/paper/figures/table_registrations.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONF = HERE.parents[1] / "confirm"
BLOCKS = [("P1", "K2 (steering; add 113, mul 113, add 97, D59)"), ("P2d", "K2-function (add 113)"), ("P2e", "K2-function (mul 113, add 97)"),
          ("P3", "K4 (trace after 25 steps)"), ("N28", "K4b (Adam first moment)"), ("N29", "K4c (ablation contrast 25 vs 50)"),
          ("N29b", "K4d (attention vs MLP reset)"), ("N29c", "K4e (value path vs query/key reset)"),
          # session 45 (simulated review: readers need one table from block ids to hypotheses); descriptions only, numbers from files
          ("P2f", "K2-function (D59, after grokking)"), ("P4", "K2 in an MLP, at 4x width, integer addition"),
          ("R1", "K2 robustness (learning rate, weight decay, train fraction)"), ("R2", "K4c at lr 2e-3 and weight decay 0.3"),
          ("R3", "lock-in clock: steps vs summed learning rate"), ("R4", "a uniform random split shapes the choice"),
          ("R5", "engineered splits generalize earlier"), ("R6", "switch cost C(t), t = 10-75"),
          ("R7", "K2 in a two-layer transformer"), ("R8", "only a change of targets costs"), ("R9", "lock-in window rule (K5)")]


def flat(x) -> list:
    if isinstance(x, dict):
        return [v for vv in x.values() for v in flat(vv)]
    if isinstance(x, list):
        return [v for vv in x for v in flat(vv)]
    return [x]


def main() -> None:
    lines = ["| Block | Claim | Manifest commit | Fresh seeds | n seeds | Runs | Registration |", "|---|---|---|---|---|---|---|"]
    for b, claim in BLOCKS:
        m = json.loads((CONF / f"{b}_manifest.json").read_text(encoding="utf-8"))
        jobs = [ln for ln in (CONF / f"{b}_jobs.txt").read_text(encoding="utf-8").splitlines() if ln.strip()]
        if "seeds" in m:
            seeds = sorted({int(s) for s in flat(m["seeds"])})
        else:   # R4/R5 (session 45): the manifest holds a unit count; the seeds are the --seed values of the frozen job list
            seeds = sorted({int(ln.split("--seed ")[1].split()[0]) for ln in jobs})
        runs = len(jobs)
        reg = m["registration"][0] if isinstance(m.get("registration"), list) else m.get("registration", "")
        lines.append(f"| {b} | {claim} | {m['commit']} | {seeds[0]}–{seeds[-1]} | {len(seeds)} | {runs} | `{reg}` |")
    out = "\n".join(lines) + "\n"
    (HERE / "table_registrations.md").write_text(out, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
