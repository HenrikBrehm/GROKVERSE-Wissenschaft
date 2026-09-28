"""EXP-097 (pilot, exploration): is the weak lock-in with only the initial gradient (EXP-095 g24) a staleness effect, or an
artefact of Adam turning a frozen gradient into elementwise SIGN steps? 2 x 2 before the switch: {Adam, linear normalised
steps} x {fresh gradient every step, initial gradient only}. The linear arms move the weights by lr * g / rms(g) per tensor
while AdamW's moments and step counter are updated from the same gradients (trainer option --pre-switch-update normgd,
session 43, shipped as trainer_psu.patch; applied only after the R10 block is analysed, R10 binds the trainer hash).
Definition and predictions: README.md (fixed before any EXP-097 run).

Seeds 3600-3615 (fresh, file search session 43), omega = 0 split pairs A/B built like EXP-094/095 (EXP-053 overlap_split.build).
Cells (switch step t = 24, gradient every k, pre-switch weight update):
  n24 (24, 1, adam; reference) | g24 (24, 24, adam; replication of EXP-095) | L1 (24, 1, normgd) | L24 (24, 24, normgd)
Pure A and B runs (standard, 2000 steps). Every switch run: A->B and B->A, then 2000 standard steps.

  python lab/experiments/EXP-097-sign-vs-staleness/design.py            # splits -> splits/, never overwrites
  python lab/experiments/EXP-097-sign-vs-staleness/design.py --jobs     # job lines for parallel_queue.py (GPU), pure runs first
  python lab/experiments/EXP-097-sign-vs-staleness/design.py --smoke    # seed 3600: pure A and the two L24 switch runs
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

SEEDS = tuple(range(3600, 3616))
BUDGET = 2000
T_SW = 24
CELLS = {"n24": (1, "adam"), "g24": (24, "adam"), "L1": (1, "normgd"), "L24": (24, "normgd")}   # name -> (gradient every k, update)
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()     # absolute: CreateProcess (session 20)
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
REL = "lab/experiments/EXP-097-sign-vs-staleness"


def stem(s: int, arm: str) -> str:
    return f"seed{s}_w0_{arm}"


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
                "share_A_F": ov.share(d["A"], F), "share_B_G": ov.share(d["B"], G)}
        (out / f"seed{s}_w0.json").open("x", encoding="utf-8").write(json.dumps(meta, indent=1))
    print(f"[exp097] wrote splits for {len(SEEDS)} seeds", flush=True)


def flags(cell: str) -> str:
    k, upd = CELLS[cell]
    return (f" --pre-switch-grad-every {k}" if k != 1 else "") + (f" --pre-switch-update {upd}" if upd != "adam" else "")


def jobs() -> list[str]:
    pure, switch = [], []
    for s in SEEDS:
        test = f"{REL}/splits/seed{s}_test.npy"
        a, b = (f"{REL}/splits/{stem(s, x)}.npy" for x in "AB")
        base = f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --test-file {test} --out-root {REL}/raw"
        for first in (a, b):
            pure.append(f"{base} --steps {BUDGET} --split-file {first} --spectra-at 50,250,{BUDGET}")
        for cell in CELLS:
            for first, second in ((a, b), (b, a)):
                switch.append(f"{base} --steps {T_SW + BUDGET} --split-file {first} --switch-split-file {second} "
                              f"--switch-step {T_SW} --spectra-at {T_SW},{T_SW + 250},{T_SW + BUDGET}{flags(cell)}")
    return pure + switch


def smoke() -> list[str]:
    j = [x for x in jobs() if "--seed 3600 " in x]
    return [x for x in j if "w0_A.npy --spectra-at 50" in x] + [x for x in j if x.endswith("--pre-switch-grad-every 24 --pre-switch-update normgd")]


if __name__ == "__main__":
    if sys.argv[1:] == ["--jobs"]:
        print("\n".join(jobs()))
    elif sys.argv[1:] == ["--smoke"]:
        print("\n".join(smoke()))
    elif not sys.argv[1:]:
        write_splits()
    else:
        raise SystemExit(__doc__)
