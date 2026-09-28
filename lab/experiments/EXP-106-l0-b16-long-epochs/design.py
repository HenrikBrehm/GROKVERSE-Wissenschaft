"""EXP-106 (L0 follow-up, exploration; session 46): set composition vs a fixed data order in the LONG-EPOCH regime, batch 16
(240 steps per epoch at 30 % of p^2 = 3831 pairs), weight decay 0.1 (the EXP-100 B16 probe v3 was the only tested setting in
which B = 16 learns within 30 000 steps). README.md. Splits: EXP-100's (seeds 3700-3707; F/G engineered, R random, O = stride
frequencies). Written before any EXP-106 run.

Arms (all AdamW lr 1e-3, weight decay 0.1, 30 000 steps, --stop-after-gen 30 000 so every run has the full budget):
  fbw        full batch                 on F and G  (K2 reference at the same weight decay)
  iid16w     batch 16, i.i.d. order     on F, G and R
  stride16w  batch 16, stride order     on F, G and R
8 seeds x (3 arms x F/G + 2 R) = 64 runs, one out-root (run ids differ: _bs16 / _ordstride / _wd0.1).
  python lab/experiments/EXP-106-l0-b16-long-epochs/design.py --jobs > lab/experiments/EXP-106-l0-b16-long-epochs/jobs.txt
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
SPL = "lab/experiments/EXP-100-set-vs-order/splits"
REL = "lab/experiments/EXP-106-l0-b16-long-epochs"
SEEDS = tuple(range(3700, 3708))
BUDGET, WD = 30_000, 0.1
ARMS = {"fbw": (0, "iid"), "iid16w": (16, "iid"), "stride16w": (16, "stride")}
R_ARMS = ("iid16w", "stride16w")
O = (11, 12, 22, 23, 34, 45)     # stride-order frequencies (EXP-100 design.O)


def line(s: int, split: str, arm: str) -> str:
    bs, order = ARMS[arm]
    spec = ",".join(str(x) for x in sorted({50, 250, 2000, BUDGET} | set(range(2500, BUDGET + 1, 2500))))
    cmd = (f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --test-file {SPL}/seed{s}_test.npy "
           f"--out-root {REL}/raw --split-file {SPL}/seed{s}_{split}.npy --steps {BUDGET} --stop-after-gen {BUDGET} "
           f"--spectra-at {spec} --weight-decay {WD}")
    if bs:
        cmd += f" --batch-size {bs}" + (f" --order {order}" if order != "iid" else "")
    return cmd


def jobs() -> list[str]:
    out = [line(s, x, arm) for s in SEEDS for arm in ARMS for x in "FG"]
    return out + [line(s, "R", arm) for s in SEEDS for arm in R_ARMS]


if __name__ == "__main__":
    if sys.argv[1:] == ["--jobs"]:
        print("\n".join(jobs()))
    else:
        raise SystemExit(__doc__)
