"""EXP-129 (LM ladder, K = 1, ~4.5 % arithmetic tokens) job lines for the GPU daemon (rule 21). Session 60, written before any run;
copy of EXP-116/make_jobs.py with K = 1 and 14 000 steps (first text wrap at 14 477, wrap_budget.json).
Model seeds 3864/3865 (unused) <-> EXP-102 P1 splits of seeds 3804/3805; common held-out test set = EXP-102
design.build(seed)["test"] (as EXP-113). EXP-116 used K = 2 (~8.7 % arithmetic tokens, as the EXP-105
pilot); HERE K = 1 (~4.5 %), same model seeds, splits and tests as EXP-116. Unchanged trainer lm_stage2.py.
  python lab/experiments/EXP-129-lm-k1-share/make_jobs.py > <outside inbox>, then mv to lab/queue/inbox/47_exp129_k1.jobs
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
REL = "lab/experiments/EXP-129-lm-k1-share"
TRAINER = "lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py"
P1 = "lab/experiments/EXP-102-lm-ladder-stage1/splits"
PAIRS = ((3864, 3804), (3865, 3805))
ARITH_FACTS, STEPS = 1, 14_000


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
            f"--steps {STEPS} --arith-facts {ARITH_FACTS} --loss answer --device cuda --out-root {REL}/raw_answer"
            for m, s in PAIRS for x in "FG"]


if __name__ == "__main__":
    write_tests()
    print("#! workers=2 job_minutes=900 min_minutes=5 crash_minutes=10 gpu_gb=3.5")
    print("\n".join(lines()))
