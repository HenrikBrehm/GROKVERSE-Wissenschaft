"""EXP-108 (N54b, exploration; session 46, written before any EXP-108 run): how does the lock-in half-point t_half scale with
batch size? EXP-107 (B = 256): t_half ~ 133 steps; full batch (EXP-100 reference): ~ 31 steps. N = 3831 train pairs.
Switch F -> G and G -> F under i.i.d. minibatch AdamW (lr 1e-3, wd 1) at batch 64 and 1024, EXP-100 splits, seeds 3700-3707,
every run 5000 steps, pi at step 5000 against pure runs of the same batch size (B = 64: EXP-100 pilot iid64 runs, snapshot 5000;
B = 1024: new pure runs here). README.md holds the predictions and readings.
  python lab/experiments/EXP-108-lockin-batch-series/design.py --jobs > lab/experiments/EXP-108-lockin-batch-series/jobs.txt
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
SPL = "lab/experiments/EXP-100-set-vs-order/splits"
REL = "lab/experiments/EXP-108-lockin-batch-series"
SEEDS = tuple(range(3700, 3708))
SWITCH_T = {64: (100, 200, 300, 450, 700), 1024: (25, 50, 75, 100, 150)}
TOTAL = 5000


def base(s: int, split: str, bs: int) -> str:
    return (f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --test-file {SPL}/seed{s}_test.npy "
            f"--out-root {REL}/raw --split-file {SPL}/seed{s}_{split}.npy --steps {TOTAL} --stop-after-gen {TOTAL} "
            f"--batch-size {bs}")


def jobs() -> list[str]:
    out = [base(s, x, 1024) + f" --spectra-at 50,250,2000,2500,{TOTAL}" for s in SEEDS for x in "FG"]
    for bs, ts in SWITCH_T.items():
        for s in SEEDS:
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
