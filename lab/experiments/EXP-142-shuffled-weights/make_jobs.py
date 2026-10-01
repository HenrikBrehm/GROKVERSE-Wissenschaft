"""EXP-142 (session 69, pilot): does ANY equally strong non-uniform pair weighting replace density at the data edge, or only the
frequency-aligned one? Arm U = the pair weights q of the engineered F split (EXP-043 construction, eps 2, same seed and targets
as EXP-139 F at add 401 / 14 000 pairs) randomly permuted over the p^2 pairs (same weight distribution, no frequency structure),
then the same weighted key draw with an independent stream. Seeds 13900-13902 (same init as EXP-139 F/G and EXP-140 R).
  python lab/experiments/EXP-142-shuffled-weights/make_jobs.py > lab/queue/staging/52a57_exp142_shuf.jobs
  python lab/experiments/EXP-142-shuffled-weights/make_jobs.py --check   # rebuild and compare; prints coverage/mask stats
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

P, N, EPS, U_SALT = 401, 14000, 2.0, 3_000
SEEDS = (13900, 13901, 13902)
STEPS = 30_000
SPECTRA = ",".join(str(x) for x in [50, 250, 500, *range(1000, STEPS + 1, 1000)])
GPY = "C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
E139 = LAB / "experiments/EXP-139-pair-count/splits"


def weights_f(s: int) -> np.ndarray:
    """q of the F arm exactly as ms.engineered_train_idx(s, 'add', P, T_F, EPS, 'F') computes it (same stream order)."""
    T = ms.target_set(s, "add", P, "F")
    rng = np.random.default_rng(s + ms.TARGET_SALT + ms.TASK_SALT["add"] + 1 + ms.ARM_SALT["F"])
    u, v, valid, n = ms.group_coords("add", P)
    phi = rng.uniform(0, 2 * np.pi, size=(len(T), n))
    wave = np.mean([np.cos(2 * np.pi * k * u / n + phi[i, (u + v) % n]) for i, k in enumerate(T)], axis=0)
    return np.where(valid, np.clip(1.0 + EPS * wave, 0.05, None), 1.0)


def build_u(s: int) -> np.ndarray:
    q = weights_f(s)
    rng = np.random.default_rng(s + ms.TARGET_SALT + ms.TASK_SALT["add"] + 1 + U_SALT)
    qu = q[rng.permutation(P * P)]
    keys = rng.random(P * P) ** (1.0 / qu)
    return np.sort(np.argsort(-keys)[:N])


def stem(s: int) -> str:
    return f"split_add{P}_n{N}_seed{s}_U"


def coverage(idx: np.ndarray) -> dict:
    a, b = idx // P, idx % P
    out = np.bincount((a + b) % P, minlength=P)
    return {"sd_per_output": float(out.std()), "sd_per_a": float(np.bincount(a, minlength=P).std()),
            "min_per_output": int(out.min())}


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    old = ms.TRAIN_FRAC
    ms.TRAIN_FRAC = N / (P * P)
    lines = []
    try:
        for s in SEEDS:
            T = ms.target_set(s, "add", P, "F")
            f_idx = ms.engineered_train_idx(s, "add", P, T, EPS, "F")
            assert np.array_equal(f_idx, np.load(E139 / f"split_add{P}_n{N}_seed{s}_F.npy")), "F weights reproduction differs"
            idx = build_u(s)
            assert len(idx) == N == len(np.unique(idx))
            mp = ms.mask_power(idx, "add", P)
            top5 = sorted(int(k) + 1 for k in np.argsort(-mp)[:5])
            stats = {"seed": s, "p": P, "n_pairs": N, "arm": "U", "eps": EPS, "targets_F": T, "mask_top5": top5,
                     "mask_top5_overlap_F": len(set(top5) & set(T)), "coverage_U": coverage(idx), "coverage_F": coverage(f_idx)}
            if mode == "--check":
                assert np.array_equal(np.load(out / f"{stem(s)}.npy"), idx), s
                print(json.dumps(stats), file=sys.stderr)
                continue
            np.save(out / f"{stem(s)}.npy", idx)
            (out / f"{stem(s)}.json").write_text(json.dumps(stats, indent=1), encoding="utf-8")
            lines.append(" ".join([
                GPY, FB, "--seed", str(s), "--condition", "baseline", "--steps", str(STEPS), "--stop-after-gen", "2000",
                "--threads", "1", "--device", "cuda", "--p", str(P), "--task", "add", "--train-frac", repr(N / (P * P)),
                "--split-file", f"lab/experiments/EXP-142-shuffled-weights/splits/{stem(s)}.npy",
                "--spectra-at", SPECTRA, "--out-root", "lab/experiments/EXP-142-shuffled-weights/raw"]))
    finally:
        ms.TRAIN_FRAC = old
    if mode != "--check":
        print("\n".join(["#! workers=3 job_minutes=150 min_minutes=5 stall_minutes=0 crash_minutes=10 gpu_gb=4.0"] + lines))


if __name__ == "__main__":
    main()
