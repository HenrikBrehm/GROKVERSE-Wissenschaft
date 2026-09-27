"""EXP-077 (pilot): splits whose ONLY structure is the token frequency of the LEFT operand (add mod 113). Session 25, pure numpy.

q(a, b) = max(0.05, 1 + eps * mean_{k in T} cos(2 pi k a / 113 + phi_k))  (independent of b), 3831 pairs without replacement
(Efraimidis-Spirakis), test = complement. Targets F, G: 5 each, disjoint, from k = 1..56 (one stream). Streams:
SeedSequence([77001, seed, arm, eps_id, purpose]). First-order theory (paper draft section 5.2): row t as RIGHT operand receives targets
distributed like rho shifted by t, so the first W_E gradient carries power p |rho_hat(k)|^2 at the target frequencies although no pair
structure along the antidiagonals exists beyond the product form.

  python lab/experiments/EXP-077-marginal-steering/make_split.py        # all seeds, arms, eps; never overwrites
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
import confirm_splits as cs  # noqa: E402  (m0 only)

P, M, SALT = 113, 5, 77_001
N_TRAIN = int(round(0.3 * P * P))
SEEDS = tuple(range(770, 780))
EPS = {"2.0": 2.0, "1.0": 1.0}
ARM_ID, EPS_ID, PURPOSE = {"F": 0, "G": 1}, {"2.0": 0, "1.0": 1}, {"targets": 0, "phases": 1, "keys": 2}
OUT = HERE / "splits"


def rng_for(seed: int, arm: str, eps: str, purpose: str) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([SALT, seed, ARM_ID[arm], EPS_ID[eps], PURPOSE[purpose]]))


def target_sets(seed: int) -> dict[str, list[int]]:
    ks = rng_for(seed, "F", "2.0", "targets").permutation(np.arange(1, (P - 1) // 2 + 1))
    return {"F": sorted(int(k) for k in ks[:M]), "G": sorted(int(k) for k in ks[M:2 * M])}


def build(seed: int, arm: str, eps: str) -> tuple[np.ndarray, list[int]]:
    T = target_sets(seed)[arm]
    a = np.arange(P).repeat(P)
    phi = rng_for(seed, arm, eps, "phases").uniform(0, 2 * np.pi, size=len(T))
    q = np.clip(1.0 + EPS[eps] * np.mean([np.cos(2 * np.pi * k * a / P + phi[i]) for i, k in enumerate(T)], axis=0), 0.05, None)
    keys = rng_for(seed, arm, eps, "keys").random(P * P) ** (1.0 / q)
    return np.sort(np.argsort(-keys)[:N_TRAIN]), T


def stem(seed: int, arm: str, eps: str) -> str:
    return f"marg_seed{seed}_eps{eps}_{arm}"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for s in SEEDS:
        for e in EPS:
            for arm in "FG":
                idx, T = build(s, arm, e)
                if len(idx) != N_TRAIN or len(np.unique(idx)) != N_TRAIN:
                    raise SystemExit("bad split")
                pw = cs.m0(idx, "add", P)
                rank = np.argsort(np.argsort(-pw, kind="stable"))
                cnt_a, cnt_b = np.bincount(idx // P, minlength=P), np.bincount(idx % P, minlength=P)
                meta = {"seed": s, "arm": arm, "eps": EPS[e], "targets": T, "targets_all": target_sets(s), "n_train": N_TRAIN,
                        "M0_target_mean_rank": float(np.mean([rank[k - 1] for k in T]) + 1),
                        "M0_target_share": float(pw[[k - 1 for k in T]].sum() / pw.sum()),
                        "cv_left": float(cnt_a.std() / cnt_a.mean()), "cv_right": float(cnt_b.std() / cnt_b.mean())}
                with open(OUT / f"{stem(s, arm, e)}.npy", "xb") as f:
                    np.save(f, idx.astype(np.int64))
                with open(OUT / f"{stem(s, arm, e)}.json", "x", encoding="utf-8") as f:
                    json.dump(meta, f, indent=1)
                print(stem(s, arm, e), T, f"M0 rank {meta['M0_target_mean_rank']:.1f} share {meta['M0_target_share']:.3f} "
                      f"cv_left {meta['cv_left']:.2f} cv_right {meta['cv_right']:.2f}")


if __name__ == "__main__":
    main()
