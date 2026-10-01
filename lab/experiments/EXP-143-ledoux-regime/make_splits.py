"""EXP-143 (session 70, exploration): splits for the LeDoux regime, add p = 9973 with N = 300 000 pairs (0.30 %, as LeDoux 2026).

Arms per seed (EXP-043 construction of make_split.py, re-implemented in build() with the same RNG draws):
  R : uniform random set (eps 0; LeDoux's "random subset"),
  F : frequency-targeted set (eps 2, 5 random target frequencies out of 1..4986).
Test file: one common uniform sample of TEST_N pairs, drawn FIRST; every train set is then built on the remaining
pairs (the EXP-043 code with one added line: test pairs get key -1, so they are never chosen; for all other pairs the
ranking is unchanged). The trainer's complement test set would be ~10^8 pairs. Writes splits/<stem>.npy and splits/meta.json (targets, mask top-5, mask Delta-like target share).
  python lab/experiments/EXP-143-ledoux-regime/make_splits.py [--arms R,F] [--seeds 14300] [--mask]
Memory: ~6-8 GB RAM peak per arm at p = 9973 (p^2 = 9.9e7 flat pairs); one arm at a time.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
import make_split as ms  # noqa: E402

P, N = 9973, 300_000                 # LeDoux 2026: p = 9973, 300 000 train pairs (0.30 % of 99 460 729)
EPS = {"R": 0.0, "F": 2.0}
TEST_N, TEST_SALT = 20_000, 143_007


def stem(seed: int, arm: str) -> str:
    return f"split_add{P}_n{N}_seed{seed}_{arm}"


def test_sample() -> np.ndarray:
    rng = np.random.default_rng(np.random.SeedSequence([TEST_SALT, P]))
    cand = np.unique(rng.integers(0, P * P, size=2 * TEST_N))
    rng.shuffle(cand)
    return np.sort(cand[:TEST_N]).astype(np.int64)


def build(seed: int, arm: str, test: np.ndarray) -> tuple[list[int], np.ndarray]:
    """ms.engineered_train_idx (same RNG draws in the same order) restricted to pairs outside the test sample."""
    T = ms.target_set(seed, "add", P, arm)
    rng = np.random.default_rng(seed + ms.TARGET_SALT + ms.TASK_SALT["add"] + 1 + ms.ARM_SALT[arm])
    u, v, valid, n = ms.group_coords("add", P)
    phi = rng.uniform(0, 2 * np.pi, size=(len(T), n))
    wave = np.zeros(P * P)
    for i, k in enumerate(T):           # running sum instead of a list of 5 arrays (memory); same values up to rounding
        wave += np.cos(2 * np.pi * k * u / n + phi[i, (u + v) % n])
    wave /= len(T)
    del u, v
    q = np.where(valid, np.clip(1.0 + EPS[arm] * wave, 0.05, None), 1.0)
    del wave
    keys = rng.random(P * P) ** (1.0 / q)
    keys[test] = -1.0                   # session 70: the common test sample is never a train pair
    idx = np.sort(np.argpartition(-keys, N)[:N])
    assert len(idx) == N and not np.intersect1d(idx, test).size
    return T, idx


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="R,F")
    ap.add_argument("--seeds", default="14300")
    ap.add_argument("--mask", action="store_true", help="also compute the first-order mask spectrum (~6 GB RAM)")
    a = ap.parse_args()
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    meta_path = out / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    test_path = out / f"test_add{P}_n{TEST_N}.npy"
    if not test_path.exists():
        np.save(test_path, test_sample())
        meta["test"] = {"n": TEST_N, "salt": TEST_SALT, "drawn_first": True}
    test = np.load(test_path)
    for s in (int(x) for x in a.seeds.split(",")):
        for arm in a.arms.split(","):
            st = stem(s, arm)
            if (out / f"{st}.npy").exists():
                idx = np.load(out / f"{st}.npy")
                T = ms.target_set(s, "add", P, arm)
            else:
                T, idx = build(s, arm, test)
                np.save(out / f"{st}.npy", idx.astype(np.int64))
            rec = {"targets": T, "eps": EPS[arm], "n": int(len(idx))}
            if a.mask:
                pw = ms.mask_power(idx, "add", P)
                top = sorted((np.argsort(-pw)[:5] + 1).tolist())
                rec.update({"mask_top5": top, "mask_target_share": float(pw[[k - 1 for k in T]].sum() / pw.sum()),
                            "mask_target_ratio_to_median": float(np.median(pw[[k - 1 for k in T]]) / np.median(pw))})
            meta[st] = rec
            print(st, rec, flush=True)
    meta_path.write_text(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
