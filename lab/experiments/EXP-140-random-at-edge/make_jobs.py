"""EXP-140 (session 68, pilot): at the data edge of EXP-139, does an engineered split generalize where a random split of
the same size does not? Random reference arm R (EXP-043 construction with eps 0, i.e. a uniform random subset of exactly
N pairs) for the EXP-139 cells, same seeds 13900-13902 (same initialization as the engineered arms F/G).
Cell selection rule (fixed before any EXP-139 result, session 68): every EXP-139 cell with p <= 503 whose engineered arms
generalized (>= 2 seeds with both arms generalized, EXP-139 analyze.py 'generalises'); p = 613 is left out (9 GB per run,
one at a time). The rule needs EXP-139/summary.json; without it the script stops.
  python lab/experiments/EXP-140-random-at-edge/make_jobs.py > lab/queue/staging/53_exp140_random.jobs
  python lab/experiments/EXP-140-random-at-edge/make_jobs.py --check   # rebuild and compare the saved splits
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
E139 = LAB / "experiments/EXP-139-pair-count"
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
import make_split as ms  # noqa: E402

SEEDS = (13900, 13901, 13902)
NS = {"n9425": 9425, "n14000": 14000}
P_MAX = 503
STEPS = 30_000
SPECTRA = ",".join(str(x) for x in [50, 250, 500, *range(1000, STEPS + 1, 1000)])
GPY = "C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
GPU_GB = {401: 4.0, 503: 6.0}
WORKERS = {401: 3, 503: 2}


def frac(p: int, cell: str) -> float:
    return NS[cell] / (p * p)


def stem(p: int, cell: str, s: int) -> str:
    return f"split_add{p}_{cell}_seed{s}_R"


def build(p: int, f: float, s: int) -> np.ndarray:
    old = ms.TRAIN_FRAC
    try:
        ms.TRAIN_FRAC = f
        T = ms.target_set(s, "add", p, "R")      # ignored at eps 0 (bookkeeping only)
        return ms.engineered_train_idx(s, "add", p, T, 0.0, "R")
    finally:
        ms.TRAIN_FRAC = old


def selected_cells() -> list[tuple[int, str]]:
    f = E139 / "summary.json"
    if not f.exists():
        raise SystemExit("EXP-139 summary.json missing: the cell selection rule needs the EXP-139 result")
    return [(c["p"], c["cell"]) for c in json.loads(f.read_text(encoding="utf-8"))["cells"]
            if c["p"] <= P_MAX and c["generalises"]]


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    cells = selected_cells()
    by_p: dict[int, list[str]] = {}
    for p, cell in cells:
        f = frac(p, cell)
        for s in SEEDS:
            idx = build(p, f, s)
            assert len(idx) == NS[cell], (p, cell, len(idx))
            st = stem(p, cell, s)
            if mode == "--check":
                assert np.array_equal(np.load(out / f"{st}.npy"), idx), st
                continue
            np.save(out / f"{st}.npy", idx)
            (out / f"{st}.json").write_text(json.dumps(
                {"seed": s, "p": p, "cell": cell, "n_pairs": NS[cell], "train_frac": f, "arm": "R", "eps": 0.0,
                 "n_train": int(len(idx))}, indent=1), encoding="utf-8")
            by_p.setdefault(p, []).append(" ".join([
                GPY, FB, "--seed", str(s), "--condition", "baseline", "--steps", str(STEPS), "--stop-after-gen", "2000",
                "--threads", "1", "--device", "cuda", "--p", str(p), "--task", "add", "--train-frac", repr(f),
                "--split-file", f"lab/experiments/EXP-140-random-at-edge/splits/{st}.npy",
                "--spectra-at", SPECTRA, "--out-root", "lab/experiments/EXP-140-random-at-edge/raw"]))
    if mode == "--check":
        print("[exp140] splits ok", cells, file=sys.stderr)
        return
    for p, lines in by_p.items():
        hdr = f"#! workers={WORKERS[p]} job_minutes=150 min_minutes=5 stall_minutes=0 crash_minutes=10 gpu_gb={GPU_GB[p]}"
        print(f"=== 53_exp140_p{p}.jobs")
        print("\n".join([hdr] + lines))
    print(f"[exp140] cells {cells}", file=sys.stderr)


if __name__ == "__main__":
    main()
