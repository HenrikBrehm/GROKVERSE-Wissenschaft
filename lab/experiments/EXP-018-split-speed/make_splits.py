"""EXP-018: do spectrally engineered splits speed up grokking? Split generator (pure numpy).

Per init seed i, a common held-out test set T*_i (20 % of all pairs, uniform) is reserved first.
Three train sets of exactly 3831 pairs (the standard 30 % size) are then drawn from the pool = all \\ T*_i:
  R  uniform random                                   (flat mask spectrum)
  E  weights q(a, b) as in EXP-016 (eps = 2, targets F_i)  (5 target frequencies dominate M0)
  D  E's exact post-clipping weights, randomly permuted WITHIN each anti-diagonal a+b = c of the pool, sampled with
     the same uniform keys as E: identical weight multiset per anti-diagonal (hence identical expected c-marginal and
     weight distribution), only the arrangement along a, i.e. the Fourier structure, is destroyed
     (Nachtrag a, after the Codex review 2026-09-26; replaces a spread-spectrum D with only matched latent SD)
(A globally shuffled arm S and the spread-spectrum D were dropped before any run. Their files train_S are unused
leftovers of the first generator run; train_D was regenerated.)
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
    return keyed_sample(pool, w, n, rng.random(len(pool)))


def keyed_sample(pool: np.ndarray, w: np.ndarray, n: int, u: np.ndarray) -> np.ndarray:
    keys = u ** (1.0 / w)
    return np.sort(pool[np.argsort(-keys)[:n]])


def permute_within_antidiagonals(pool: np.ndarray, w: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Shuffle the weights among the pool pairs of each anti-diagonal c = a + b (mod p)."""
    c = (pool // P + pool % P) % P
    out = w.copy()
    for cc in range(P):
        j = np.flatnonzero(c == cc)
        out[j] = w[rng.permutation(j)]
    return out


def build(seed: int, eps: float = 2.0) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed + SALT)
    n_all = P * P
    n_test = int(round(TEST_FRAC * n_all))
    n_train = int(round(TRAIN_FRAC * n_all))
    perm = rng.permutation(n_all)
    test = np.sort(perm[:n_test])
    pool = np.sort(perm[n_test:])
    q_e = q_from_wave(wave(target_set(seed, "F"), rng), eps)[pool]
    q_d = permute_within_antidiagonals(pool, q_e, rng)
    u = rng.random(len(pool))                      # common sampling keys for E and D
    return {"test": test,
            "R": np.sort(rng.choice(pool, size=n_train, replace=False)),
            "E": keyed_sample(pool, q_e, n_train, u),
            "D": keyed_sample(pool, q_d, n_train, u)}


def swap_share(of: np.ndarray, within: np.ndarray) -> float:
    """Share of pairs (a, b) in `of` whose commuted pair (b, a) is in `within` (a != b only)."""
    a, b = of // P, of % P
    off = a != b
    return float(np.isin(b[off] * P + a[off], within).mean())


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
                             "count_cv": {n: float(c.std() / c.mean()) for n, c in cnt.items()},
                             "count_min": {n: int(c.min()) for n, c in cnt.items()},
                             "swap_in_train": swap_share(sets[arm], sets[arm]),
                             "test_swap_in_train": swap_share(sets["test"], sets[arm])}
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
        print(json.dumps({"seed": s, **{k: [round(x, 3) for x in (v["top5_power_share"], v["count_cv"]["a"],
                                        v["count_cv"]["c"], v["swap_in_train"], v["test_swap_in_train"])]
                                        for k, v in meta["arms"].items()}}))


if __name__ == "__main__":
    main()
