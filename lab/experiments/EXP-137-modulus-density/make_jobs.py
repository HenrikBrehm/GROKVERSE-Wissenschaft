"""EXP-137 (session 67, pilot): does the split composition still steer the frequencies at larger moduli when the data are
sparser but the network still generalizes? Follow-up of EXP-136, where 3831 pairs (8.6 % / 4.1 %) never generalized.
Builds the engineered F/G splits (EXP-043 construction, eps 2) for add p in {211, 307} at train fractions 0.10, 0.15, 0.20
for seeds 13700-13702 and prints the job file for the GPU service (rule 21) on stdout. Only the module constant
TRAIN_FRAC of make_split.py is overridden; the construction itself is unchanged (as in EXP-136).
  python lab/experiments/EXP-137-modulus-density/make_jobs.py > lab/queue/staging/48_exp137_density.jobs
  python lab/experiments/EXP-137-modulus-density/make_jobs.py --check   # rebuild and compare the saved splits
  python lab/experiments/EXP-137-modulus-density/make_jobs.py --mask    # first-order prediction (mask Delta), no run
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
import make_split as ms  # noqa: E402

SEEDS = (13700, 13701, 13702)
PS = (211, 307)
FRACS = {"f10": 0.10, "f15": 0.15, "f20": 0.20}
STEPS, EPS = 30_000, 2.0
SPECTRA = ",".join(str(x) for x in [50, 250, 500, *range(1000, STEPS + 1, 1000)])
GPY = "C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
HEADER = "#! workers=5 job_minutes=120 min_minutes=5 stall_minutes=0 crash_minutes=10 gpu_gb=1.5"


def stem(p: int, fr: str, s: int, arm: str) -> str:
    return f"split_add{p}_{fr}_seed{s}_{arm}"


def build(p: int, frac: float, s: int, arm: str) -> tuple[list[int], np.ndarray, np.ndarray]:
    ms.TRAIN_FRAC = frac
    T = ms.target_set(s, "add", p, arm)
    idx = ms.engineered_train_idx(s, "add", p, T, EPS, arm)
    return T, idx, ms.mask_power(idx, "add", p)


def mask_delta(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float:
    s = lambda pw, S: float(pw[[k - 1 for k in S]].sum())   # noqa: E731
    return float(np.log(s(pF, F) / s(pF, G)) + np.log(s(pG, G) / s(pG, F)))


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    lines, masks = [HEADER], []
    for p in PS:
        for fr, frac in FRACS.items():
            for s in SEEDS:
                pw = {}
                for arm in "FG":
                    T, idx, pw[arm] = build(p, frac, s, arm)
                    assert len(idx) == int(round(frac * p * p)), (p, fr, len(idx))
                    assert sorted((np.argsort(-pw[arm])[:5] + 1).tolist()) == T, (p, fr, s, arm)
                    pw[arm + "T"] = T
                    st = stem(p, fr, s, arm)
                    if mode == "--check":
                        assert np.array_equal(np.load(out / f"{st}.npy"), idx), st
                        continue
                    if mode == "--mask":
                        continue
                    np.save(out / f"{st}.npy", idx)
                    (out / f"{st}.json").write_text(json.dumps(
                        {"seed": s, "p": p, "fraction": fr, "train_frac": frac, "arm": arm, "eps": EPS, "targets": T,
                         "n_train": int(len(idx)), "target_power_share": float(pw[arm][[k - 1 for k in T]].sum() / pw[arm].sum())},
                        indent=1), encoding="utf-8")
                    lines.append(" ".join([GPY, FB, "--seed", str(s), "--condition", "baseline", "--steps", str(STEPS),
                                           "--stop-after-gen", "2000", "--threads", "1", "--device", "cuda", "--p", str(p),
                                           "--task", "add", "--train-frac", repr(frac),
                                           "--split-file", f"lab/experiments/EXP-137-modulus-density/splits/{st}.npy",
                                           "--spectra-at", SPECTRA, "--out-root", "lab/experiments/EXP-137-modulus-density/raw"]))
                masks.append({"p": p, "fraction": fr, "seed": s,
                              "delta_mask": mask_delta(pw["F"], pw["G"], pw["FT"], pw["GT"])})
    if mode == "--check":
        print("[exp137] splits ok", file=sys.stderr)
    elif mode == "--mask":
        (HERE / "mask_prediction_s67.json").write_text(json.dumps(masks, indent=1), encoding="utf-8")
        for m in masks:
            print(m["p"], m["fraction"], m["seed"], round(m["delta_mask"], 3))
    else:
        print("\n".join(lines))


if __name__ == "__main__":
    main()
