"""EXP-056 (P3 pilot): write the split pairs A/B with controlled overlap (EXP-053 overlap_split.build, eps from its calibration.json)
and the job list. Pure numpy for the splits. Seeds 400-409 (never used before, checked session 21), omega in {0, 0.2, 0.4}.

  python lab/experiments/EXP-056-overlap-persistence/make_splits.py            # splits -> splits/, never overwrites
  python lab/experiments/EXP-056-overlap-persistence/make_splits.py --jobs     # job lines for parallel_queue.py (GPU)
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

SEEDS = tuple(range(400, 410))
OMEGAS = ov.OMEGAS
T_SWITCH, BUDGET = 25, 2000
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()     # absolute: CreateProcess (session 20)
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
REL = "lab/experiments/EXP-056-overlap-persistence"


def lvl(omega: float) -> int:
    return int(round(omega * 1000))


def stem(s: int, omega: float, arm: str) -> str:
    return f"seed{s}_w{lvl(omega)}_{arm}"


def write_splits() -> None:
    cal = json.loads((LAB / "experiments/EXP-053-p3-overlap-design/calibration.json").read_text(encoding="utf-8"))["levels"]
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    for s in SEEDS:
        F, G = ov.targets(s)
        tests = []
        for om in OMEGAS:
            eps = cal[str(om)]["eps"]
            d = ov.build(s, om, eps)
            tests.append(d["test"])
            assert not np.intersect1d(d["test"], np.union1d(d["A"], d["B"])).size
            assert len(d["A"]) == len(d["B"]) == ov.N_TRAIN and len(np.intersect1d(d["A"], d["B"])) == len(d["S"])
            for arm in "AB":
                with open(out / f"{stem(s, om, arm)}.npy", "xb") as f:
                    np.save(f, d[arm].astype(np.int64))
            meta = {"seed": s, "omega": om, "eps": eps, "targets": {"A": F, "B": G}, "n_shared": int(len(d["S"])),
                    "share_A_F": ov.share(d["A"], F), "share_B_G": ov.share(d["B"], G),
                    "share_A_G": ov.share(d["A"], G), "share_B_F": ov.share(d["B"], F)}
            (out / f"seed{s}_w{lvl(om)}.json").open("x", encoding="utf-8").write(json.dumps(meta, indent=1))
        assert all(np.array_equal(tests[0], t) for t in tests)          # one test set per seed for every level
        with open(out / f"seed{s}_test.npy", "xb") as f:
            np.save(f, tests[0].astype(np.int64))
    print(f"[exp056] wrote splits for {len(SEEDS)} seeds x {len(OMEGAS)} levels", flush=True)


def jobs() -> list[str]:
    out = []
    for s in SEEDS:
        test = f"{REL}/splits/seed{s}_test.npy"
        base = f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --test-file {test} --out-root {REL}/raw"
        for om in OMEGAS:
            a, b = (f"{REL}/splits/{stem(s, om, x)}.npy" for x in "AB")
            for first in (a, b):
                out.append(f"{base} --steps {BUDGET} --split-file {first} --spectra-at 50,250,{BUDGET}")
            for first, second in ((a, b), (b, a)):
                out.append(f"{base} --steps {T_SWITCH + BUDGET} --split-file {first} --switch-split-file {second} "
                           f"--switch-step {T_SWITCH} --spectra-at {T_SWITCH},{T_SWITCH + 250},{T_SWITCH + BUDGET}")
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["--jobs"]:
        print("\n".join(jobs()))
    elif not sys.argv[1:]:
        write_splits()
    else:
        raise SystemExit(__doc__)
