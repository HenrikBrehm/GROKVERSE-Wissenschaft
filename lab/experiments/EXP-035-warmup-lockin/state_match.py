"""EXP-035 Nachtrag c (descriptive, fixed 2026-09-26 18:20 before any seed-32 warmup run): do end states (top-5 of W_E)
of warmup and no-warmup switch runs agree better when matched by accumulated learning rate than by step?
Lambda-matched pairs (warmup t', no-warmup t): (50, 10) Lambda 6.4/10, (100, 25) 25.2/25, (150, 50) 56.6/50.
Step-matched pairs: (10, 10), (25, 25), (50, 50). Overlap = |K_wu(t') n K_nowu(t)|.
P35d (seed 32 only; seeds 30, 31 were seen): mean overlap Lambda-matched > step-matched -> erfuellt, else nicht erfuellt.
Seeds 30, 31 are reported as exploration. Usage: python state_match.py"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
E20 = HERE.parent / "EXP-020-data-switch" / "raw"
LAM = ((50, 10), (100, 25), (150, 50))
STEP = ((10, 10), (25, 25), (50, 50))


def K(root: Path, s: int, t: int, wu: bool) -> set[int] | None:
    name = f"EXP-020_baseline_seed{s}_thr4_seed{s}_train_F_to_seed{s}_train_G_at{t}" + ("_wu200" if wu else "")
    try:
        r = json.loads((root / name / "result.json").read_text(encoding="utf-8"))
    except OSError:
        return None
    return set(r["final_top_m_freqs"]) if r.get("status") == "completed" else None


def overlaps(s: int, pairs) -> list[int] | None:
    out = []
    for tw, tn in pairs:
        a, b = K(HERE / "raw", s, tw, True), K(E20, s, tn, False)
        if a is None or b is None:
            return None
        out.append(len(a & b))
    return out


def main() -> None:
    res = {}
    for s in (30, 31, 32):
        lam, step = overlaps(s, LAM), overlaps(s, STEP)
        row = {"lambda_matched": lam, "step_matched": step}
        if lam and step:
            row["mean_lambda"], row["mean_step"] = sum(lam) / 3, sum(step) / 3
            if s == 32:
                row["P35d"] = "erfuellt" if row["mean_lambda"] > row["mean_step"] else "nicht erfuellt"
            else:
                row["role"] = "exploration (seen before the rule)"
        res[s] = row
        print(s, row)
    (HERE / "state_match.json").write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
