"""EXP-109 (N54b, pilot/exploration; session 47, written before any EXP-109 run): lock-in half-point t_half against batch size at
a second learning rate (lr 2e-3, wd 1), to fix the switch grid and check stability before the N54b confirmation (fresh seeds 3900+).
EXP-100 splits, seeds 3700-3701 (already seen in EXP-100/107/108), i.i.d. minibatch AdamW, B in {full, 1024, 256, 64},
pure F/G and switches F->G, G->F at GRID[B]; every run 5000 steps, pi at step 5000 as EXP-108.
  python lab/experiments/EXP-109-lockin-lr-pilot/design.py --jobs > lab/experiments/EXP-109-lockin-lr-pilot/jobs.txt
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
SPL = "lab/experiments/EXP-100-set-vs-order/splits"
REL = "lab/experiments/EXP-109-lockin-lr-pilot"
SEEDS = (3700, 3701)
LR = 2e-3
GRID = {0: (8, 16, 25, 35, 50, 75), 1024: (15, 30, 50, 75, 100, 150), 256: (30, 60, 100, 150, 200, 300),
        64: (75, 150, 225, 300, 450, 700)}
TOTAL = 5000


def base(s: int, split: str, bs: int) -> str:
    return (f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --test-file {SPL}/seed{s}_test.npy "
            f"--out-root {REL}/raw --split-file {SPL}/seed{s}_{split}.npy --steps {TOTAL} --stop-after-gen {TOTAL} --lr {LR!r}"
            + (f" --batch-size {bs}" if bs else ""))


def jobs() -> list[str]:
    out = []
    for bs, ts in GRID.items():
        for s in SEEDS:
            out += [base(s, x, bs) + f" --spectra-at 50,250,2000,2500,{TOTAL}" for x in "FG"]
            for t in ts:
                for a, b in (("F", "G"), ("G", "F")):
                    spec = ",".join(str(x) for x in sorted({50, 250, t, 2000, 2500, TOTAL}))
                    out.append(base(s, a, bs) + f" --spectra-at {spec} --switch-split-file {SPL}/seed{s}_{b}.npy --switch-step {t}")
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["--jobs"]:
        print("\n".join(jobs()))
    else:
        raise SystemExit(__doc__)
