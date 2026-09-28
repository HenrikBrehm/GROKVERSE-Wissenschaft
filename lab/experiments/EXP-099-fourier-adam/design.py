"""EXP-099 (pilot, exploration; NOVEL_DIRECTIONS N49): does Adam's COORDINATE BASIS for the embedding shape which frequencies the
early motion selects? Token-basis AdamW (default) against AdamW on the real-DFT coordinates C = B^T W_E[:p] (--we-fourier-adam,
session 43, shipped as trainer_wef.patch ON TOP OF EXP-097's trainer_psu.patch; applied only after R10/R11 are analysed and the
EXP-096/098 blocks are done). Same init, same data; only the optimizer coordinates of W_E[:p] differ.
Definition and competing predictions (V1 scatter vs V2 equalisation): README.md (fixed before any EXP-099 run).

Seeds 3680-3695 (fresh, file search session 43), omega = 0 split pairs A/B built like EXP-094/095 (EXP-053 overlap_split.build).
Pure A and B runs in BOTH parametrisations (tok, four); cells (switch at t = 24, gradient every k, Fourier-Adam):
  n24 (1, no) | g24 (24, no) | n24F (1, yes) | g24F (24, yes). Every switch run: A->B and B->A, then 2000 steps (same optimizer).

  python lab/experiments/EXP-099-fourier-adam/design.py            # splits -> splits/, never overwrites
  python lab/experiments/EXP-099-fourier-adam/design.py --jobs     # job lines for parallel_queue.py (GPU), pure runs first
  python lab/experiments/EXP-099-fourier-adam/design.py --smoke    # seed 3680: pure A (Fourier) and the two n24F switch runs
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

SEEDS = tuple(range(3680, 3696))
BUDGET = 2000
T_SW = 24
CELLS = {"n24": (1, False), "g24": (24, False), "n24F": (1, True), "g24F": (24, True)}   # name -> (gradient every k, Fourier-Adam)
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()     # absolute: CreateProcess (session 20)
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
REL = "lab/experiments/EXP-099-fourier-adam"


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
    print(f"[exp099] wrote splits for {len(SEEDS)} seeds", flush=True)


def flags(cell: str) -> str:
    k, four = CELLS[cell]
    return (f" --pre-switch-grad-every {k}" if k != 1 else "") + (" --we-fourier-adam" if four else "")


def jobs() -> list[str]:
    pure, switch = [], []
    for s in SEEDS:
        test = f"{REL}/splits/seed{s}_test.npy"
        a, b = (f"{REL}/splits/{stem(s, x)}.npy" for x in "AB")
        base = f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --test-file {test} --out-root {REL}/raw"
        for four in (False, True):
            for first in (a, b):
                pure.append(f"{base} --steps {BUDGET} --split-file {first} --spectra-at 50,250,{BUDGET}" + (" --we-fourier-adam" if four else ""))
        for cell in CELLS:
            for first, second in ((a, b), (b, a)):
                switch.append(f"{base} --steps {T_SW + BUDGET} --split-file {first} --switch-split-file {second} "
                              f"--switch-step {T_SW} --spectra-at {T_SW},{T_SW + 250},{T_SW + BUDGET}{flags(cell)}")
    return pure + switch


def smoke() -> list[str]:
    j = [x for x in jobs() if "--seed 3680 " in x]
    return ([x for x in j if "w0_A.npy --spectra-at 50,250,2000 --we-fourier-adam" in x]
            + [x for x in j if "--switch-step" in x and x.endswith("--we-fourier-adam") and "--pre-switch-grad-every" not in x])


if __name__ == "__main__":
    if sys.argv[1:] == ["--jobs"]:
        print("\n".join(jobs()))
    elif sys.argv[1:] == ["--smoke"]:
        print("\n".join(smoke()))
    elif not sys.argv[1:]:
        write_splits()
    else:
        raise SystemExit(__doc__)
