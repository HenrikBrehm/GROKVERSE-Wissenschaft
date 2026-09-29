"""EXP-113 (LM ladder stage 2b) job lines for the GPU daemon (rule 21). Session 49, written before any run.
Model seeds 3862/3863 <-> EXP-102 P1 splits of seeds 3802/3803 (F and G of one model seed share init, text, templates,
insert positions); common held-out test set = EXP-102 design.build(seed)["test"] (as the EXP-105 pilot). Two loss arms in
separate out-roots (the pilot analysis finds runs by run-id prefix): raw_all (--loss all) and raw_answer (--loss answer).
  python lab/experiments/EXP-113-lm-ladder-stage2b/make_jobs.py > lab/queue/inbox/40_exp113_stage2b.jobs
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
REL = "lab/experiments/EXP-113-lm-ladder-stage2b"
TRAINER = "lab/experiments/EXP-105-lm-ladder-stage2/lm_stage2.py"
P1 = "lab/experiments/EXP-102-lm-ladder-stage1/splits"
PAIRS = ((3862, 3802), (3863, 3803))
ARITH_FACTS, STEPS = 8, 16_000


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
    out = []
    for loss in ("answer", "all"):
        for m, s in PAIRS:
            for x in "FG":
                out.append(f"{PY} {TRAINER} --seed {m} --split-file {P1}/seed{s}_{x}.npy --test-file {REL}/tests/seed{s}_test.npy "
                           f"--steps {STEPS} --arith-facts {ARITH_FACTS} --loss {loss} --device cuda --out-root {REL}/raw_{loss}")
    return out


if __name__ == "__main__":
    write_tests()
    print("#! workers=8 job_minutes=600 min_minutes=5")
    print("\n".join(lines()))
