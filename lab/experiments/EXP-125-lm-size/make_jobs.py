"""EXP-125 (LM ladder: model size) job lines for the GPU daemon (rule 21). Session 57, written before any run.
Model seeds 3868/3869 (unused; seeds 3860-3867 are taken) <-> EXP-102 P1 splits of seeds 3808/3809; common held-out test set =
EXP-102 design.build(seed)["test"] (as EXP-113/116). LM1 setting (K = 19 arithmetic sentences per sequence, loss only on the answer,
6000 steps) with a larger model: d 512, 8 layers, 8 heads (~2.2x the parameters of the default d 384 / 6 layers). Unchanged trainer
lm_stage2.py (its run id hashes d/layers/heads, so no collision with default-size runs; own out-root anyway).
  python lab/experiments/EXP-125-lm-size/make_jobs.py > lab/queue/staging/45_exp125_lm_size.jobs   (then mv into lab/queue/inbox)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-102-lm-ladder-stage1"))
import design  # noqa: E402  (EXP-102 split and test construction)

PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
REL = "lab/experiments/EXP-125-lm-size"
TRAINER = "lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py"
P1 = "lab/experiments/EXP-102-lm-ladder-stage1/splits"
PAIRS = ((3868, 3808), (3869, 3809))
ARITH_FACTS, STEPS, D, LAYERS, HEADS = 19, 6000, 512, 8, 8


def write_tests() -> None:
    (HERE / "tests").mkdir(exist_ok=True)
    for _, s in PAIRS:
        f = HERE / "tests" / f"seed{s}_test.npy"
        t = design.build(s)["test"].astype(np.int64)
        if f.exists():
            assert np.array_equal(np.load(f), t), f
        else:
            np.save(f, t)


def lines() -> list[str]:
    return [f"{PY} {TRAINER} --seed {m} --split-file {P1}/seed{s}_{x}.npy --test-file {REL}/tests/seed{s}_test.npy "
            f"--steps {STEPS} --arith-facts {ARITH_FACTS} --loss answer --d {D} --layers {LAYERS} --heads {HEADS} --device cuda "
            f"--out-root {REL}/raw_d512"
            for m, s in PAIRS for x in "FG"]


if __name__ == "__main__":
    write_tests()
    print("#! workers=2 job_minutes=600 min_minutes=5 crash_minutes=10 gpu_gb=7")
    print("\n".join(lines()))
