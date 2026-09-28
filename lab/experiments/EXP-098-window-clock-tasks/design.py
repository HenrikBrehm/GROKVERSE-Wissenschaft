"""EXP-098 (pilot, exploration; rule 15c generalization of K5 / R9): does lock-in tick in summed learning rate Lambda once Adam's
windows are measured in Lambda, also in add mod 97 and mul mod 113? Cells at Lambda = 25 as R9: n25 (25 default steps),
l100 (100 steps at lr x 0.25, default betas), l100b (same, betas 0.975/0.995 before the switch = 1 - c (1 - beta)).
Splits: EXP-044 construction (F and G engineered for disjoint target sets, independent keys, ~37 % shared pairs, common test set),
one direction F -> G. Definition and predictions: README.md (fixed before any EXP-098 run). Session 43, UNTESTED.

  python lab/experiments/EXP-098-window-clock-tasks/design.py            # splits -> splits/, never overwrites
  python lab/experiments/EXP-098-window-clock-tasks/design.py --jobs     # job lines for parallel_queue.py (GPU), pure runs first
  python lab/experiments/EXP-098-window-clock-tasks/design.py --smoke    # seed 3660: pure F add 97 and the l100b switch run of each task
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

SEEDS = tuple(range(3660, 3676))
TASKS = (("add", 97), ("mul", 113))
BUDGET = 2000
CELLS = {"n25": (1.0, 25, None), "l100": (0.25, 100, None), "l100b": (0.25, 100, (0.975, 0.995))}   # name -> (c, t, pre-switch betas)
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
REL = "lab/experiments/EXP-098-window-clock-tasks"


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
    print(f"[exp098] wrote splits for {len(SEEDS)} seeds x {len(TASKS)} tasks", flush=True)


def jobs() -> list[str]:
    pure, switch = [], []
    for task, p in TASKS:
        for s in SEEDS:
            st = f"{REL}/splits/{stem(task, p, s)}"
            base = (f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --p {p} --task {task} "
                    f"--test-file {st}_test.npy --out-root {REL}/raw")
            for arm in "FG":
                pure.append(f"{base} --steps {BUDGET} --split-file {st}_train_{arm}.npy --spectra-at 50,250,{BUDGET}")
            for c, t, psb in CELLS.values():
                switch.append(f"{base} --steps {t + BUDGET} --split-file {st}_train_F.npy --switch-split-file {st}_train_G.npy "
                              f"--switch-step {t} --spectra-at {t},{t + 250},{t + BUDGET}"
                              + (f" --lr-scale {c:g}" if c != 1.0 else "") + (f" --pre-switch-betas {psb[0]},{psb[1]}" if psb else ""))
    return pure + switch


def smoke() -> list[str]:
    j = jobs()
    return ([x for x in j if "--seed 3660 " in x and "add97_seed3660_train_F.npy --spectra-at" in x]
            + [x for x in j if "--seed 3660 " in x and "--pre-switch-betas" in x])


if __name__ == "__main__":
    if sys.argv[1:] == ["--jobs"]:
        print("\n".join(jobs()))
    elif sys.argv[1:] == ["--smoke"]:
        print("\n".join(smoke()))
    elif not sys.argv[1:]:
        write_splits()
    else:
        raise SystemExit(__doc__)
