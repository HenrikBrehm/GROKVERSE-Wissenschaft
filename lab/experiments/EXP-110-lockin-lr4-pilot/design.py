"""EXP-110 (N54c, pilot/exploration; session 47, written before any EXP-110 run): lock-in half-point t_half against batch size at
lr 4e-3 (wd 1): stability and grid before an N54c registration (model predictions in JOURNAL session 47, 05:00).
EXP-100 splits, seeds 3700-3701 (already seen in EXP-100/107/108), i.i.d. minibatch AdamW, B in {1024, 256, 64},
pure F/G and switches F->G, G->F at GRID[B]; every run 5000 steps, pi at step 5000 as EXP-108.
  python lab/experiments/EXP-110-lockin-lr4-pilot/design.py --jobs > lab/experiments/EXP-110-lockin-lr4-pilot/jobs.txt
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
SPL = "lab/experiments/EXP-100-set-vs-order/splits"
REL = "lab/experiments/EXP-110-lockin-lr4-pilot"
SEEDS = (3700, 3701)
LR = 4e-3
GRID = {1024: (8, 12, 16, 20, 30, 40), 256: (20, 30, 40, 55, 75, 120),
        64: (50, 75, 100, 150, 200, 300)}
TOTAL = 5000
EXT = {64: (400, 600, 900, 1400)}   # s47, 05:44: after the first grid showed no crossing at B 64 by 300 (README)


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


def ext_jobs() -> list[str]:
    out = []
    for bs, ts in EXT.items():
        for s in SEEDS:
            for t in ts:
                for a, b in (("F", "G"), ("G", "F")):
                    spec = ",".join(str(x) for x in sorted({50, 250, t, 2000, 2500, TOTAL}))
                    out.append(base(s, a, bs) + f" --spectra-at {spec} --switch-split-file {SPL}/seed{s}_{b}.npy --switch-step {t}")
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["--ext"]:
        print("\n".join(ext_jobs()))
    elif sys.argv[1:] == ["--jobs"]:
        print("\n".join(jobs()))
    else:
        raise SystemExit(__doc__)
