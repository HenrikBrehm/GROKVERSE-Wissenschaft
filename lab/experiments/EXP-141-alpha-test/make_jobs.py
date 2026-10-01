"""EXP-141 (session 68, pilot; cloned from EXP-139 make_jobs.py, only seeds/cells/paths/header changed). Question: at add 503,
do N = 16100 / 18100 pairs (N/p 32 / 36; N/p^(5/3) 0.51 / 0.57) generalize? alpha = 1 (data per number row) predicts yes,
alpha = 5/3 (margin theory) predicts no (EXP-139 amendments b/c). Original EXP-139 text follows.
 is it the pair count rather than the data fraction that decides whether the network
generalizes at larger moduli, and does the split composition still steer the frequencies there? Follow-up of EXP-137
(add 307 with 10 % = 9425 pairs generalized 6/6 and steered; add 211 with 10 % = 4452 pairs never generalized) and R14.
Builds the engineered F/G splits (EXP-043 construction, eps 2) for add p in {401, 503, 613} with a FIXED pair count
N in {9425, 14000} (fractions 1.5-8.7 %) for seeds 13900-13902 and prints the job file for the GPU service (rule 21) on
stdout. Only the module constant TRAIN_FRAC of make_split.py is overridden (to N / p^2), as in EXP-136/137.
  python lab/experiments/EXP-141-alpha-test/make_jobs.py > lab/queue/staging/52bzz_exp141_alpha.jobs
  python lab/experiments/EXP-141-alpha-test/make_jobs.py --check   # rebuild and compare the saved splits
  python lab/experiments/EXP-141-alpha-test/make_jobs.py --mask    # first-order prediction (mask Delta), no run
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

SEEDS = (13910, 13911, 13912)
PS = (503,)
NS = {"n16100": 16100, "n18100": 18100}
STEPS, EPS = 30_000, 2.0
SPECTRA = ",".join(str(x) for x in [50, 250, 500, *range(1000, STEPS + 1, 1000)])
GPY = "C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
HEADER = "#! workers=2 job_minutes=150 min_minutes=5 stall_minutes=0 crash_minutes=10 gpu_gb=7.0"


def frac(p: int, cell: str) -> float:
    return NS[cell] / (p * p)


def stem(p: int, cell: str, s: int, arm: str) -> str:
    return f"split_add{p}_{cell}_seed{s}_{arm}"


def build(p: int, f: float, s: int, arm: str) -> tuple[list[int], np.ndarray, np.ndarray]:
    old = ms.TRAIN_FRAC
    try:
        ms.TRAIN_FRAC = f
        T = ms.target_set(s, "add", p, arm)
        idx = ms.engineered_train_idx(s, "add", p, T, EPS, arm)
    finally:
        ms.TRAIN_FRAC = old
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
        for cell in NS:
            f = frac(p, cell)
            for s in SEEDS:
                pw = {}
                for arm in "FG":
                    T, idx, pw[arm] = build(p, f, s, arm)
                    assert len(idx) == NS[cell], (p, cell, len(idx))
                    top = sorted((np.argsort(-pw[arm])[:5] + 1).tolist())
                    pw[arm + "T"], pw[arm + "top"] = T, top
                    st = stem(p, cell, s, arm)
                    if mode == "--check":
                        assert np.array_equal(np.load(out / f"{st}.npy"), idx), st
                        continue
                    if mode == "--mask":
                        continue
                    assert top == T, (p, cell, s, arm, top, T)
                    np.save(out / f"{st}.npy", idx)
                    (out / f"{st}.json").write_text(json.dumps(
                        {"seed": s, "p": p, "cell": cell, "n_pairs": NS[cell], "train_frac": f, "arm": arm, "eps": EPS,
                         "targets": T, "n_train": int(len(idx)),
                         "target_power_share": float(pw[arm][[k - 1 for k in T]].sum() / pw[arm].sum())},
                        indent=1), encoding="utf-8")
                    lines.append(" ".join([GPY, FB, "--seed", str(s), "--condition", "baseline", "--steps", str(STEPS),
                                           "--stop-after-gen", "2000", "--threads", "1", "--device", "cuda", "--p", str(p),
                                           "--task", "add", "--train-frac", repr(f),
                                           "--split-file", f"lab/experiments/EXP-141-alpha-test/splits/{st}.npy",
                                           "--spectra-at", SPECTRA, "--out-root", "lab/experiments/EXP-141-alpha-test/raw"]))
                masks.append({"p": p, "cell": cell, "seed": s, "train_frac": f,
                              "delta_mask": mask_delta(pw["F"], pw["G"], pw["FT"], pw["GT"]),
                              "top5_is_target": [pw["Ftop"] == pw["FT"], pw["Gtop"] == pw["GT"]]})
    if mode == "--check":
        print("[exp139] splits ok", file=sys.stderr)
    elif mode == "--mask":
        (HERE / "mask_prediction_s68_141.json").write_text(json.dumps(masks, indent=1), encoding="utf-8")
        for m in masks:
            print(m["p"], m["cell"], m["seed"], round(m["train_frac"], 4), round(m["delta_mask"], 3), m["top5_is_target"])
    else:
        print("\n".join(lines))


if __name__ == "__main__":
    main()
