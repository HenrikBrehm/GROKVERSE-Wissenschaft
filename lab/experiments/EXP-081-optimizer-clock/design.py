"""EXP-081 (pilot): splits and job list. Definition: README.md, Nachtrag a + d (fixed before any EXP-081 run).

Seeds 830-839 (fresh, checked sessions 27 and 40), omega = 0 split pairs A/B built exactly like EXP-056 (EXP-053
overlap_split.build, eps from its calibration.json). Pure numpy for the splits.

Cells (beta1, beta2); None = preset (no flag, reference run ids stay those of the plain trainer):
  ref (0.9, 0.98) | b1_08 (0.8, -) | b1_095 (0.95, -) | b2_095 (-, 0.95) | b2_0995 (-, 0.995)
Part A (beta1 cells ref/b1_08/b1_095): normal switch at t = 20, 25, 30 and m reset (--reset-optim-part m) at t = 25.
Part B (beta2 cells b2_095/b2_0995): normal switch at t = 25, 33, 45; reference cell additionally at t = 33, 45.
Every cell: pure A and pure B runs (2000 steps). Every switch run: A->B and B->A, then 2000 steps.

  python lab/experiments/EXP-081-optimizer-clock/design.py            # splits -> splits/, never overwrites
  python lab/experiments/EXP-081-optimizer-clock/design.py --jobs     # job lines for parallel_queue.py (GPU), pure runs first
  python lab/experiments/EXP-081-optimizer-clock/design.py --smoke    # the four non-reference pure A runs of seed 830
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-053-p3-overlap-design"))
import overlap_split as ov  # noqa: E402

SEEDS = tuple(range(830, 840))
BUDGET = 2000
CELLS = {"ref": (None, None), "b1_08": (0.8, None), "b1_095": (0.95, None), "b2_095": (None, 0.95), "b2_0995": (None, 0.995)}
PART_A_CELLS, PART_B_CELLS = ("ref", "b1_08", "b1_095"), ("b2_095", "b2_0995")
T_A, T_A_ROM, T_B = (20, 25, 30), (25,), (25, 33, 45)
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()     # absolute: CreateProcess (session 20)
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
REL = "lab/experiments/EXP-081-optimizer-clock"


def stem(s: int, arm: str) -> str:
    return f"seed{s}_w0_{arm}"


def switch_times(cell: str) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """(normal switch times, m-reset switch times) of a cell."""
    if cell in PART_A_CELLS:
        normal = tuple(sorted(set(T_A) | (set(T_B) if cell == "ref" else set())))
        return normal, T_A_ROM
    return T_B, ()


def beta_flags(cell: str) -> str:
    b1, b2 = CELLS[cell]
    return (f" --beta1 {b1}" if b1 is not None else "") + (f" --beta2 {b2}" if b2 is not None else "")


def write_splits() -> None:
    eps = json.loads((LAB / "experiments/EXP-053-p3-overlap-design/calibration.json").read_text(encoding="utf-8"))["levels"]["0.0"]["eps"]
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    for s in SEEDS:
        F, G = ov.targets(s)
        d = ov.build(s, 0.0, eps)
        assert not np.intersect1d(d["test"], np.union1d(d["A"], d["B"])).size
        assert len(d["A"]) == len(d["B"]) == ov.N_TRAIN and not len(np.intersect1d(d["A"], d["B"]))
        for arm in "AB":
            with open(out / f"{stem(s, arm)}.npy", "xb") as f:
                np.save(f, d[arm].astype(np.int64))
        with open(out / f"seed{s}_test.npy", "xb") as f:
            np.save(f, d["test"].astype(np.int64))
        meta = {"seed": s, "omega": 0.0, "eps": eps, "targets": {"A": F, "B": G},
                "share_A_F": ov.share(d["A"], F), "share_B_G": ov.share(d["B"], G),
                "share_A_G": ov.share(d["A"], G), "share_B_F": ov.share(d["B"], F)}
        (out / f"seed{s}_w0.json").open("x", encoding="utf-8").write(json.dumps(meta, indent=1))
    print(f"[exp081] wrote splits for {len(SEEDS)} seeds", flush=True)


def jobs() -> list[str]:
    pure, switch = [], []
    for s in SEEDS:
        test = f"{REL}/splits/seed{s}_test.npy"
        a, b = (f"{REL}/splits/{stem(s, x)}.npy" for x in "AB")
        for cell in CELLS:
            base = (f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --test-file {test} "
                    f"--out-root {REL}/raw{beta_flags(cell)}")
            for first in (a, b):
                pure.append(f"{base} --steps {BUDGET} --split-file {first} --spectra-at 50,250,{BUDGET}")
            normal, rom = switch_times(cell)
            for t, extra in [(t, "") for t in normal] + [(t, " --reset-optim-part m") for t in rom]:
                for first, second in ((a, b), (b, a)):
                    switch.append(f"{base} --steps {t + BUDGET} --split-file {first} --switch-split-file {second} "
                                  f"--switch-step {t} --spectra-at {t},{t + 250},{t + BUDGET}{extra}")
    return pure + switch


def smoke() -> list[str]:
    return [j for j in jobs() if "--seed 830 " in j and "w0_A.npy --spectra-at 50" in j and "--beta" in j]


if __name__ == "__main__":
    if sys.argv[1:] == ["--jobs"]:
        print("\n".join(jobs()))
    elif sys.argv[1:] == ["--smoke"]:
        print("\n".join(smoke()))
    elif not sys.argv[1:]:
        write_splits()
    else:
        raise SystemExit(__doc__)
