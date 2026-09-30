"""EXP-136 (session 65, pilot): K2 at larger moduli. Builds the engineered F/G splits (EXP-043 construction, eps 2) for
add p in {211, 307} at two train fractions - 0.3 (as everywhere) and 'lo' = 3831 / p^2 (the same number of pairs as add 113
at 30 %) - for seeds 13600-13602, and prints the job file for the GPU service (rule 21) on stdout.
Only the module constant TRAIN_FRAC of make_split.py is overridden; the construction itself is unchanged.
  python lab/experiments/EXP-136-large-modulus/make_jobs.py > lab/queue/staging/45zzz_exp136_modulus.jobs
  python lab/experiments/EXP-136-large-modulus/make_jobs.py --check      # rebuild and compare the saved splits
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

SEEDS = (13600, 13601, 13602)
PS = (211, 307)
N_LO = 3831                       # pairs of add 113 at 30 %
STEPS, EPS = 20_000, 2.0
SPECTRA = "50,250,500,1000,2000,5000,10000,20000"
GPY = "C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
HEADER = "#! workers=4 job_minutes=90 min_minutes=5 stall_minutes=0 crash_minutes=10 gpu_gb=1.5"


def fracs(p: int) -> dict[str, float]:
    return {"hi": 0.3, "lo": N_LO / p ** 2}


def stem(p: int, fr: str, s: int, arm: str) -> str:
    return f"split_add{p}_{fr}_seed{s}_{arm}"


def build(p: int, frac: float, s: int, arm: str) -> tuple[list[int], np.ndarray, np.ndarray]:
    ms.TRAIN_FRAC = frac
    T = ms.target_set(s, "add", p, arm)
    idx = ms.engineered_train_idx(s, "add", p, T, EPS, arm)
    return T, idx, ms.mask_power(idx, "add", p)


def main() -> None:
    check = sys.argv[1:] == ["--check"]
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    lines = [HEADER]
    for p in PS:
        for fr, frac in fracs(p).items():
            for s in SEEDS:
                for arm in "FG":
                    T, idx, pw = build(p, frac, s, arm)
                    assert len(idx) == int(round(frac * p * p)), (p, fr, len(idx))
                    assert sorted((np.argsort(-pw)[:5] + 1).tolist()) == T, (p, fr, s, arm)
                    st = stem(p, fr, s, arm)
                    if check:
                        assert np.array_equal(np.load(out / f"{st}.npy"), idx), st
                        continue
                    np.save(out / f"{st}.npy", idx)
                    (out / f"{st}.json").write_text(json.dumps(
                        {"seed": s, "p": p, "fraction": fr, "train_frac": frac, "arm": arm, "eps": EPS, "targets": T,
                         "n_train": int(len(idx)), "target_power_share": float(pw[[k - 1 for k in T]].sum() / pw.sum())},
                        indent=1), encoding="utf-8")
                    tf = [] if fr == "hi" else ["--train-frac", repr(frac)]
                    lines.append(" ".join([GPY, FB, "--seed", str(s), "--condition", "baseline", "--steps", str(STEPS),
                                           "--stop-after-gen", "2000", "--threads", "1", "--device", "cuda", "--p", str(p),
                                           "--task", "add", *tf, "--split-file", f"lab/experiments/EXP-136-large-modulus/splits/{st}.npy",
                                           "--spectra-at", SPECTRA, "--out-root", "lab/experiments/EXP-136-large-modulus/raw"]))
    if check:
        print("[exp136] splits ok", file=sys.stderr)
        return
    print("\n".join(lines))


if __name__ == "__main__":
    main()
