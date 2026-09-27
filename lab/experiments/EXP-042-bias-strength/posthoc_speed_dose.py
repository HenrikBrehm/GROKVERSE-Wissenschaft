"""Session 31 (2026-09-27), POST HOC exploration, reads saved result.json files only (no training).

Question: does grokking speed grow with the spectral concentration of the training split (dose-response)?
The only-G runs of EXP-020 (eps 2) and EXP-042 (eps 1, eps 8) share per seed the init (init_checksum_shared), the test set
(test_hash) and the train-set size (3831 pairs); only the concentration eps of the pair mask differs
(target share of M0: eps 1 ~ 0.115, eps 2 ~ 0.18, eps 8 ~ 0.36; random ~ 0.09). 2000 steps each, generalisation = first test >= 0.95.
Usage: python posthoc_speed_dose.py  -> prints a table and writes posthoc_speed_dose.json
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[0]
ROOTS = {"1": HERE / "eps1" / "raw", "2": LAB / "EXP-020-data-switch" / "raw", "8": HERE / "eps8" / "raw"}
SEEDS = (30, 31, 32, 34)


def load(eps: str, seed: int) -> dict:
    r = json.loads((ROOTS[eps] / f"EXP-018_baseline_seed{seed}_thr4_seed{seed}_train_G" / "result.json").read_text(encoding="utf-8"))
    assert r["status"] == "completed" and r["steps_completed"] == 2000, r["run_id"]
    return r


def main() -> None:
    rows = []
    for sd in SEEDS:
        runs = {e: load(e, sd) for e in ROOTS}
        inits = {r["init_checksum_shared"] for r in runs.values()}
        tests = {r["test_hash"] for r in runs.values()}
        assert len(inits) == 1 and len(tests) == 1, f"seed {sd}: init or test set differs"
        row = {"seed": sd}
        for e, r in runs.items():
            row[f"gen_eps{e}"] = r["events"].get("generalization_step")        # None = not within 2000 steps
            row[f"test_final_eps{e}"] = round(float(r["final_acc"]["test"]), 3)
            row[f"mem_eps{e}"] = r["transitions"]["primary"]["memorization"]["first_crossing_step"]
        g = [row["gen_eps8"], row["gen_eps2"], row["gen_eps1"] if row["gen_eps1"] is not None else float("inf")]
        row["strict_order_8_lt_2_lt_1"] = g[0] < g[1] < g[2]
        rows.append(row)
        print(row)
    n_ord = sum(r["strict_order_8_lt_2_lt_1"] for r in rows)
    out = {"note": "post hoc exploration, seeds 30-34 seen many times; no confirmation", "rows": rows,
           "strict_order_count": n_ord, "n": len(rows),
           "sign_test_one_sided_p": 0.5 ** len(rows) if n_ord == len(rows) else None}
    (HERE / "posthoc_speed_dose.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"strict order eps8 < eps2 < eps1: {n_ord}/{len(rows)}")


if __name__ == "__main__":
    main()
