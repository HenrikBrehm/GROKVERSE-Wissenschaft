"""EXP-119 (LM ladder, R5 in a language model; pilot = exploration). Session 52, written before any run.
Model seeds 3866/3867 (unused; checked by file search in session 52) <-> EXP-102 splits of seeds 3806/3807: arms F, G (P1
construction, target share of the mask 0.18 ~ R5's E2) and R (uniform random, same size, same pool). Common held-out test =
EXP-102 design.build(seed)["test"] (disjoint from F, G and R; checked). Trainer lm_stage2.py unchanged (hash in LM1), K = 19,
--loss answer, 6000 steps (as LM1). All arms of one model seed share init, text, templates and insert positions.
  python lab/experiments/EXP-119-lm-speed-r5/make_jobs.py > lab/queue/inbox/36_exp119_lm_r5.jobs
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-102-lm-ladder-stage1"))
import design  # noqa: E402

PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
REL = "lab/experiments/EXP-119-lm-speed-r5"
TRAINER = "lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py"
SPL = "lab/experiments/EXP-102-lm-ladder-stage1/splits"
PAIRS = ((3866, 3806), (3867, 3807))
ARMS = ("F", "G", "R")
ARITH_FACTS, STEPS = 19, 6000


def write_tests() -> None:
    (HERE / "tests").mkdir(exist_ok=True)
    for _, s in PAIRS:
        d = design.build(s)
        t = d["test"].astype(np.int64)
        for x in ARMS:
            assert not np.intersect1d(np.load(LAB.parent / SPL / f"seed{s}_{x}.npy"), t).size, (s, x)
        f = HERE / "tests" / f"seed{s}_test.npy"
        if f.exists():
            assert np.array_equal(np.load(f), t), f
        else:
            np.save(f, t)


def lines() -> list[str]:
    return [f"{PY} {TRAINER} --seed {m} --split-file {SPL}/seed{s}_{x}.npy --test-file {REL}/tests/seed{s}_test.npy "
            f"--steps {STEPS} --arith-facts {ARITH_FACTS} --loss answer --device cuda --out-root {REL}/raw"
            for m, s in PAIRS for x in ARMS]


if __name__ == "__main__":
    write_tests()
    print("#! workers=2 job_minutes=240 min_minutes=5 gpu_gb=3.5")
    print("\n".join(lines()))
