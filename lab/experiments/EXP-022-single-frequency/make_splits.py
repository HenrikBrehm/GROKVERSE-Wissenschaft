"""EXP-022: can data selection force a single-frequency solution? Split generator (pure numpy, deterministic).

Per init seed i (40-44): common held-out test set T*_i (20 %), and from the pool three train sets of 3831 pairs:
  S1  engineered with ONE target frequency f1_i (random member of target_set(i, "F")), eps1 = 0.9 so that
      q = 1 + 0.9 cos(...) >= 0.1 needs no clipping (with eps = 2 the floor at 0.05 creates harmonics 2k, 3k, ... in M0)
  S5  engineered with the five targets target_set(i, "F") (as EXP-018 arm E)
  D1  S1's exact weights permuted WITHIN each anti-diagonal of the pool (as EXP-018 arm D), same sampling keys as S1:
      identical weight distribution and expected c-marginal, no Fourier allocation (Nachtrag a, Codex review)
  R   uniform random (only descriptive; EXP-018 covers R)
S1, D1 and S5 use common sampling keys. Writes seed{i}_test.npy, seed{i}_train_{S1,D1,S5,R}.npy and seed{i}.json
with balance metrics (residue count CVs, commuted-pair coverage, clipping rate, top shares).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-018-split-speed"))
sys.path.insert(0, str(HERE.parent / "EXP-015-mask-spectrum"))
from make_splits import (P, TEST_FRAC, TRAIN_FRAC, keyed_sample, permute_within_antidiagonals,  # noqa: E402
                         q_from_wave, swap_share, wave)
from make_split import M, mask_from_idx, target_set  # noqa: E402

SALT = 60_013
SEEDS = range(40, 45)


def build(seed: int, eps: float = 2.0, eps1: float = 0.9) -> tuple[dict[str, np.ndarray], dict]:
    rng = np.random.default_rng(seed + SALT)
    perm = rng.permutation(P * P)
    n_test, n_train = int(round(TEST_FRAC * P * P)), int(round(TRAIN_FRAC * P * P))
    test, pool = np.sort(perm[:n_test]), np.sort(perm[n_test:])
    T5 = target_set(seed, "F")
    f1 = int(rng.choice(T5))
    u = rng.random(len(pool))
    w1, w5 = wave([f1], rng), wave(T5, rng)
    q1 = q_from_wave(w1, eps1)[pool]
    q5 = q_from_wave(w5, eps)[pool]
    sets = {"test": test,
            "S1": keyed_sample(pool, q1, n_train, u),
            "S5": keyed_sample(pool, q5, n_train, u),
            "R": np.sort(rng.choice(pool, size=n_train, replace=False))}
    sets["D1"] = keyed_sample(pool, permute_within_antidiagonals(pool, q1, rng), n_train, u)
    clip = {"S1": float(np.mean(1 + eps1 * w1[pool] < 0.05)), "S5": float(np.mean(1 + eps * w5[pool] < 0.05))}
    return sets, {"seed": seed, "f1": f1, "targets5": T5, "eps5": eps, "eps1": eps1, "clip_rate": clip}


def main() -> None:
    import mask_spectrum as ms
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    for s in SEEDS:
        sets, meta = build(s)
        for name, idx in sets.items():
            np.save(out / f"seed{s}_{'test' if name == 'test' else 'train_' + name}.npy", idx)
            if name != "test":
                pw = ms.m0(mask_from_idx(idx))
                order = np.argsort(-pw, kind="stable")
                meta[f"{name}_M0_top5"] = [int(k) + 1 for k in order[:M]]
                meta[f"{name}_top1_share"] = float(pw[order[0]] / pw.sum())
                meta[f"{name}_top5_share"] = float(pw[order[:M]].sum() / pw.sum())
                a, b = idx // P, idx % P
                meta[f"{name}_count_cv"] = {n: float(np.bincount(v, minlength=P).std() / np.bincount(v, minlength=P).mean())
                                            for n, v in (("a", a), ("b", b), ("c", (a + b) % P))}
                meta[f"{name}_swap_in_train"] = swap_share(idx, idx)
                meta[f"{name}_test_swap_in_train"] = swap_share(sets["test"], idx)
        (out / f"seed{s}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        print(json.dumps(meta))


if __name__ == "__main__":
    main()
