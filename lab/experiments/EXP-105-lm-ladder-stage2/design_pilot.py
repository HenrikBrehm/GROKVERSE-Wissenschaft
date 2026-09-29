"""EXP-105 pilot job lines (session 48). Split choice fixed in README 'Pilotplan' point 3 (depends on EXP-104):
  flat: EXP-104 seeds 3850/3851, m = 10, shared test s{seed}_test.npy      p1: EXP-102 seeds 3800/3801, tests/seed{seed}_test.npy
Model seeds 3860/3861 (F and G of one model seed share init, text and template streams).
  python lab/experiments/EXP-105-lm-ladder-stage2/design_pilot.py --splits flat|p1 --steps N > .../jobs_pilot.txt
"""
from __future__ import annotations

import argparse
from pathlib import Path

LAB = Path(__file__).resolve().parents[2]
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
REL = "lab/experiments/EXP-105-lm-ladder-stage2"
FLAT, P1 = "lab/experiments/EXP-104-flat-marginal-splits/splits", "lab/experiments/EXP-102-lm-ladder-stage1/splits"


def pairs(kind: str) -> list[tuple[int, str, str]]:
    if kind == "flat":
        return [(m, f"{FLAT}/s{s}_{x}_m10.npy", f"{FLAT}/s{s}_test.npy") for m, s in ((3860, 3850), (3861, 3851)) for x in "FG"]
    return [(m, f"{P1}/seed{s}_{x}.npy", f"{REL}/tests/seed{s}_test.npy") for m, s in ((3860, 3800), (3861, 3801)) for x in "FG"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits", choices=("flat", "p1"), required=True)
    ap.add_argument("--steps", type=int, required=True)
    a = ap.parse_args()
    for m, sp, te in pairs(a.splits):
        print(f"{PY} {REL}/lm_stage2.py --seed {m} --split-file {sp} --test-file {te} --steps {a.steps} --device cuda "
              f"--out-root {REL}/raw_pilot")
