"""EXP-018: do spectrally engineered splits speed up grokking? Split generator (pure numpy).

Per init seed i, a common held-out test set T*_i (20 % of all pairs, uniform) is reserved first.
Three train sets of exactly 3831 pairs (the standard 30 % size) are then drawn from the pool = all \\ T*_i:
  R  uniform random                                   (flat mask spectrum)
  E  weights q(a, b) as in EXP-016 (eps = 2, targets F_i)  (5 target frequencies dominate M0)
  D  same construction, but the modulation is spread over all 56 frequencies (random phases) and rescaled to the
     same standard deviation as E's wave: structured non-uniformity of equal strength, no concentrated spectrum
(A shuffled-weight arm S was dropped before any run: one draw with permuted, unstructured inclusion weights is
statistically just another uniform random subset, so it would duplicate R. Its train_S files are unused leftovers.)
All arms are evaluated on the same T*_i, so the test set no longer depends on the treatment (EXP-016 used the
complement, which carries the negated spectrum). Writes train_<arm>.npy and test.npy (flat index a*p + b) per seed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-016-engineered-split"))
sys.path.insert(0, str(HERE.parent / "EXP-015-mask-spectrum"))

from make_split import M, P, TRAIN_FRAC, mask_from_idx, target_set  # noqa: E402

TEST_FRAC = 0.2
SALT = 40_009
ARMS = ("R", "E", "D")


def wave(freqs: list[int], rng: np.random.Generator) -> np.ndarray:
    """mean_k cos(2 pi k a / p + phi_{k, a+b}) over all p*p pairs (flat a*p + b), EXP-016 construction."""
    a = np.arange(P).repeat(P)
    b = np.tile(np.arange(P), P)
    phi = rng.uniform(0, 2 * np.pi, size=(len(freqs), P))
    return np.mean([np.cos(2 * np.pi * k * a / P + phi[i, (a + b) % P])
                    for i, k in enumerate(freqs)], axis=0)


def q_from_wave(w: np.ndarray, eps: float) -> np.ndarray:
    return np.clip(1.0 + eps * w, 0.05, None)      # eps > 1 needs a floor to stay positive


def weighted_sample(pool: np.ndarray, w: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    """n items from pool without replacement, inclusion ~ w (Efraimidis-Spirakis keys)."""
    keys = rng.random(len(pool)) ** (1.0 / w)
    return np.sort(pool[np.argsort(-keys)[:n]])


def build(seed: int, eps: float = 2.0) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed + SALT)
    n_all = P * P
    n_test = int(round(TEST_FRAC * n_all))
    n_train = int(round(TRAIN_FRAC * n_all))
    perm = rng.permutation(n_all)
    test = np.sort(perm[:n_test])
    pool = np.sort(perm[n_test:])
    w_e = wave(target_set(seed, "F"), rng)
    w_d = wave(list(range(1, P // 2 + 1)), rng)
    w_d = w_d * (w_e.std() / w_d.std())            # equal modulation strength, spread spectrum
    return {"test": test,
            "R": np.sort(rng.choice(pool, size=n_train, replace=False)),
            "E": weighted_sample(pool, q_from_wave(w_e, eps)[pool], n_train, rng),
            "D": weighted_sample(pool, q_from_wave(w_d, eps)[pool], n_train, rng)}


def describe(seed: int, sets: dict[str, np.ndarray]) -> dict:
    import mask_spectrum as ms
    F = target_set(seed, "F")
    meta = {"seed": seed, "targets": F, "n_test": int(len(sets["test"])), "arms": {}}
    for arm in ARMS:
        pw = ms.m0(mask_from_idx(sets[arm]))
        top = sorted((np.argsort(-pw, kind="stable")[:M] + 1).tolist())
        # non-uniformity: spread of per-residue counts of a, b and c = a + b in the train set
        a, b = sets[arm] // P, sets[arm] % P
        cnt = {n: np.bincount(v, minlength=P) for n, v in (("a", a), ("b", b), ("c", (a + b) % P))}
        meta["arms"][arm] = {"n_train": int(len(sets[arm])), "M0_top5": top,
                             "target_power_share": float(pw[[k - 1 for k in F]].sum() / pw.sum()),
                             "top5_power_share": float(np.sort(pw)[-M:].sum() / pw.sum()),
                             "count_cv": {n: float(c.std() / c.mean()) for n, c in cnt.items()}}
    return meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="20-29")
    ap.add_argument("--eps", type=float, default=2.0)
    ap.add_argument("--out", default=str(HERE / "splits"))
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.seeds.split("-"))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for s in range(lo, hi + 1):
        sets = build(s, a.eps)
        for name, idx in sets.items():
            np.save(out / f"seed{s}_{'test' if name == 'test' else 'train_' + name}.npy", idx)
        meta = describe(s, sets)
        (out / f"seed{s}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        print(json.dumps({"seed": s, **{k: (v["target_power_share"], v["top5_power_share"], v["count_cv"]["c"])
                                        for k, v in meta["arms"].items()}}))


if __name__ == "__main__":
    main()
