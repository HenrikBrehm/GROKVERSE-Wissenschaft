"""EXP-089 (pilot): at a fixed summed learning rate Lambda = 25 (units of 1e-3 steps), does lock-in grow with the number of
pre-switch steps? Definition: README.md (fixed before any EXP-089 run).

Seeds 3260-3269 (fresh, checked session 40), omega = 0 split pairs A/B built like EXP-056/EXP-081 (EXP-053
overlap_split.build, eps from its calibration.json). Cells (lr scale c on the first split for steps 1..t, standard lr after
the switch; --lr-scale of EXP-039/R3): standard curve c = 1 at t = 25, 33, 45; Lambda = 25 cells (0.5, 50) and (0.25, 100).
Pure A and B runs (standard lr, 2000 steps) for pi. Every switch run: A->B and B->A, then 2000 steps.

  python lab/experiments/EXP-089-lambda-fixed-steps/design.py            # splits -> splits/, never overwrites
  python lab/experiments/EXP-089-lambda-fixed-steps/design.py --jobs     # job lines for parallel_queue.py (GPU), pure runs first
  python lab/experiments/EXP-089-lambda-fixed-steps/design.py --smoke    # seed 3260: pure A and both (0.25, 100) switch runs
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

SEEDS = tuple(range(3260, 3270))
BUDGET = 2000
CELLS = {"n25": (1.0, 25), "n33": (1.0, 33), "n45": (1.0, 45), "l50": (0.5, 50), "l100": (0.25, 100)}   # name -> (c, t)
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()     # absolute: CreateProcess (session 20)
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
REL = "lab/experiments/EXP-089-lambda-fixed-steps"


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
    print(f"[exp089] wrote splits for {len(SEEDS)} seeds", flush=True)


def jobs() -> list[str]:
    pure, switch = [], []
    for s in SEEDS:
        test = f"{REL}/splits/seed{s}_test.npy"
        a, b = (f"{REL}/splits/{stem(s, x)}.npy" for x in "AB")
        base = f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --test-file {test} --out-root {REL}/raw"
        for first in (a, b):
            pure.append(f"{base} --steps {BUDGET} --split-file {first} --spectra-at 50,250,{BUDGET}")
        for c, t in CELLS.values():
            flag = f" --lr-scale {c:g}" if c != 1.0 else ""
            for first, second in ((a, b), (b, a)):
                switch.append(f"{base} --steps {t + BUDGET} --split-file {first} --switch-split-file {second} "
                              f"--switch-step {t} --spectra-at {t},{t + 250},{t + BUDGET}{flag}")
    return pure + switch


def smoke() -> list[str]:
    j = [x for x in jobs() if "--seed 3260 " in x]
    return [x for x in j if "w0_A.npy --spectra-at 50" in x] + [x for x in j if "--lr-scale 0.25" in x]


if __name__ == "__main__":
    if sys.argv[1:] == ["--jobs"]:
        print("\n".join(jobs()))
    elif sys.argv[1:] == ["--smoke"]:
        print("\n".join(smoke()))
    elif not sys.argv[1:]:
        write_splits()
    else:
        raise SystemExit(__doc__)
