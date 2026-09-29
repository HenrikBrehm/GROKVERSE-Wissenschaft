"""EXP-107 (N54, exploration; session 46, written before any EXP-107 run): does the early lock-in count in EPOCHS rather than in
optimizer steps? Under i.i.d. minibatch B = 256 (15 steps per epoch) the EXP-100 switch runs showed no lock-in at 25 or 50 steps
(pi ~ 0), while full batch (1 step = 1 epoch) locks in between 25 and 50. Here: switch F -> G and G -> F under iid256 at
t = 100, 200, 375, 750, 1500 steps (375 / 750 steps = 25 / 50 epochs), every run 5000 steps in total, EXP-100 splits and seeds
3700-3707, GPU. The pure iid256 runs of the EXP-100 pilot (raw, snapshot at 5000) are the endpoints. 80 runs.
  python lab/experiments/EXP-107-lockin-epochs/design.py --jobs > lab/experiments/EXP-107-lockin-epochs/jobs.txt
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
SPL = "lab/experiments/EXP-100-set-vs-order/splits"
REL = "lab/experiments/EXP-107-lockin-epochs"
SEEDS = tuple(range(3700, 3708))
SWITCH_T = (100, 200, 375, 750, 1500)
TOTAL = 5000


def line(s: int, first: str, second: str, t: int) -> str:
    spec = ",".join(str(x) for x in sorted({50, 250, t, 2000, 2500, TOTAL}))
    return (f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --test-file {SPL}/seed{s}_test.npy "
            f"--out-root {REL}/raw --split-file {SPL}/seed{s}_{first}.npy --steps {TOTAL} --stop-after-gen {TOTAL} "
            f"--spectra-at {spec} --batch-size 256 --switch-split-file {SPL}/seed{s}_{second}.npy --switch-step {t}")


def jobs() -> list[str]:
    return [line(s, a, b, t) for s in SEEDS for t in SWITCH_T for a, b in (("F", "G"), ("G", "F"))]


if __name__ == "__main__":
    if sys.argv[1:] == ["--jobs"]:
        print("\n".join(jobs()))
    else:
        raise SystemExit(__doc__)
