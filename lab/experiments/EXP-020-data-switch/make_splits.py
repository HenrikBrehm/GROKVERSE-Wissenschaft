"""EXP-020: train sets for the mid-training data switch (pure numpy, deterministic).

Per init seed i: common held-out test set T*_i (20 %), and from the remaining pool two engineered train sets of
3831 pairs as in EXP-016/018 (eps = 2) with DISJOINT target sets F_i and G_i (`target_set(i, "F")`, `(i, "G")`),
drawn with common uniform keys. Writes seed{i}_test.npy, seed{i}_train_F.npy, seed{i}_train_G.npy + seed{i}.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-018-split-speed"))
sys.path.insert(0, str(HERE.parent / "EXP-015-mask-spectrum"))

from make_splits import P, TEST_FRAC, TRAIN_FRAC, keyed_sample, q_from_wave, wave  # noqa: E402
from make_split import M, mask_from_idx, target_set  # noqa: E402

SALT = 50_021


def build(seed: int, eps: float = 2.0) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed + SALT)
    n_all = P * P
    perm = rng.permutation(n_all)
    n_test = int(round(TEST_FRAC * n_all))
    test, pool = np.sort(perm[:n_test]), np.sort(perm[n_test:])
    n_train = int(round(TRAIN_FRAC * n_all))
    u = rng.random(len(pool))
    out = {"test": test}
    for arm in ("F", "G"):
        q = q_from_wave(wave(target_set(seed, arm), rng), eps)[pool]
        out[arm] = keyed_sample(pool, q, n_train, u)
    return out


def main() -> None:
    import mask_spectrum as ms
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="30-34")
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.seeds.split("-"))
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    for s in range(lo, hi + 1):
        sets = build(s)
        meta = {"seed": s, "targets": {arm: target_set(s, arm) for arm in ("F", "G")},
                "overlap_FG_train": int(np.intersect1d(sets["F"], sets["G"]).size)}
        for name, idx in sets.items():
            np.save(out / f"seed{s}_{'test' if name == 'test' else 'train_' + name}.npy", idx)
            if name != "test":
                pw = ms.m0(mask_from_idx(idx))
                meta[f"M0_top5_{name}"] = sorted((np.argsort(-pw, kind="stable")[:M] + 1).tolist())
        (out / f"seed{s}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        print(json.dumps(meta))


if __name__ == "__main__":
    main()
