"""EXP-096 (pilot, exploration; rule 15c generalization of EXP-095): does lock-in at Lambda = 24 also need re-evaluated gradients
in add mod 97 and mul mod 113? Cells n24 / g8 / g24 as EXP-095 (24 default Adam steps, gradient every k steps before the switch).
Splits: EXP-044 construction (F and G engineered for disjoint target sets, independent keys, ~37 % shared pairs, common test set),
one direction F -> G. Definition and predictions: README.md (fixed before any EXP-096 run). Session 42, UNTESTED.

  python lab/experiments/EXP-096-gradient-feedback-tasks/design.py            # splits -> splits/, never overwrites
  python lab/experiments/EXP-096-gradient-feedback-tasks/design.py --jobs     # job lines for parallel_queue.py (GPU), pure runs first
  python lab/experiments/EXP-096-gradient-feedback-tasks/design.py --smoke    # seed 3560: pure F add 97 and the g24 switch run of each task
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-044-generalize-lockin"))
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
import make_splits as ms  # noqa: E402  (EXP-044 build)
from make_split import target_set  # noqa: E402

SEEDS = tuple(range(3560, 3576))
TASKS = (("add", 97), ("mul", 113))
BUDGET, T_SWITCH = 2000, 24
CELLS = {"n24": 1, "g8": 8, "g24": 24}          # name -> gradient every k steps before the switch
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
REL = "lab/experiments/EXP-096-gradient-feedback-tasks"


def stem(task: str, p: int, s: int) -> str:
    return f"{task}{p}_seed{s}"


def write_splits() -> None:
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    for task, p in TASKS:
        for s in SEEDS:
            sets = ms.build(s, task, p)
            assert not np.intersect1d(sets["test"], np.union1d(sets["F"], sets["G"])).size
            T = {arm: target_set(s, task, p, arm) for arm in "FG"}
            assert not set(T["F"]) & set(T["G"])
            for name, idx in sets.items():
                with open(out / f"{stem(task, p, s)}_{'test' if name == 'test' else 'train_' + name}.npy", "xb") as f:
                    np.save(f, idx.astype(np.int64))
            meta = {"seed": s, "task": task, "p": p, "targets": T, "overlap_FG_train": int(np.intersect1d(sets["F"], sets["G"]).size)}
            with (out / f"{stem(task, p, s)}.json").open("x", encoding="utf-8") as f:
                f.write(json.dumps(meta, indent=1))
    print(f"[exp096] wrote splits for {len(SEEDS)} seeds x {len(TASKS)} tasks", flush=True)


def jobs() -> list[str]:
    pure, switch = [], []
    for task, p in TASKS:
        for s in SEEDS:
            st = f"{REL}/splits/{stem(task, p, s)}"
            base = (f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --p {p} --task {task} "
                    f"--test-file {st}_test.npy --out-root {REL}/raw")
            for arm in "FG":
                pure.append(f"{base} --steps {BUDGET} --split-file {st}_train_{arm}.npy --spectra-at 50,250,{BUDGET}")
            for k in CELLS.values():
                switch.append(f"{base} --steps {T_SWITCH + BUDGET} --split-file {st}_train_F.npy --switch-split-file {st}_train_G.npy "
                              f"--switch-step {T_SWITCH} --spectra-at {T_SWITCH},{T_SWITCH + 250},{T_SWITCH + BUDGET}"
                              + (f" --pre-switch-grad-every {k}" if k != 1 else ""))
    return pure + switch


def smoke() -> list[str]:
    j = jobs()
    return ([x for x in j if "--seed 3560 " in x and "add97_seed3560_train_F.npy --spectra-at" in x]
            + [x for x in j if "--seed 3560 " in x and "--pre-switch-grad-every 24" in x])


if __name__ == "__main__":
    if sys.argv[1:] == ["--jobs"]:
        print("\n".join(jobs()))
    elif sys.argv[1:] == ["--smoke"]:
        print("\n".join(smoke()))
    elif not sys.argv[1:]:
        write_splits()
    else:
        raise SystemExit(__doc__)
