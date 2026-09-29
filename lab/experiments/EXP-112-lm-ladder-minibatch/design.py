"""EXP-112 (rule 20e, LM ladder stage 1, last rung): steering K2 when the LM format and i.i.d. minibatches are combined.
Uses the EXP-102 trainer (lm_ladder.py, unchanged) and the EXP-102 splits (seeds 3800-3809, F/G).
Rungs (all with --batch-size 256):
  r0B    everything off (freq_ban setup, minibatch)
  lmB    --op-token --full-softmax --tie (answer loss): the format rungs of EXP-102 together
  lmnbB  like lmB with --loss all_but_b (next-token loss on every position except the one predicting b)
  python lab/experiments/EXP-112-lm-ladder-minibatch/design.py --jobs  > lab/experiments/EXP-112-lm-ladder-minibatch/jobs.txt
  python lab/experiments/EXP-112-lm-ladder-minibatch/design.py --smoke
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
SRC = "lab/experiments/EXP-102-lm-ladder-stage1"
REL = "lab/experiments/EXP-112-lm-ladder-minibatch"
SEEDS = tuple(range(3800, 3810))
STEPS, BATCH = 5000, 256
RUNGS = {"r0B": "", "lmB": "--op-token --full-softmax --tie", "lmnbB": "--op-token --full-softmax --tie --loss all_but_b"}


def line(s: int, split: str, rung: str, steps: int = STEPS, root: str = "raw") -> str:
    flags = RUNGS[rung]
    return (f"{PY} {SRC}/lm_ladder.py --seed {s} --split-file {SRC}/splits/seed{s}_{split}.npy --steps {steps} "
            f"--device cuda --threads 1 --batch-size {BATCH} --out-root {REL}/{root}" + (f" {flags}" if flags else ""))


if __name__ == "__main__":
    arg = sys.argv[1:]
    if arg == ["--jobs"]:
        print("\n".join(line(s, x, r) for s in SEEDS for r in RUNGS for x in "FG"))
    elif arg == ["--smoke"]:
        print("\n".join(line(SEEDS[0], "F", r, steps=50, root="raw_smoke") for r in RUNGS))
    else:
        raise SystemExit(__doc__)
