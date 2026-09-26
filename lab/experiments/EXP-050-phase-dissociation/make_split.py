"""EXP-050: splits whose targets are strong in M0 but either strong (sym) or absent (anti) in the coherent spectrum M0c.

Construction (EXP-016 type, add mod 113): q(a, b) = max(0.05, 1 + eps * mean_{k in T} cos(2 pi k a / p + phi_{k,c})), c = a + b mod p,
3831 pairs without replacement (Efraimidis-Spirakis), eps = 2. Phase choice per target k and output c:
  sym : phi_{k,c} = -pi k c / p          -> left and right DFT contributions in phase: M0c(k) = 2 M0(k) share, targets top in both
  anti: phi_{k,c} = pi/2 - pi k c / p    -> contributions in antiphase: targets top in M0, at chance in M0c
(Derivation: left term at frequency k carries e^{i phi}, right term e^{-i(2 pi k c / p + phi)}; they cancel for phi = pi/2 - pi k c/p.)
  quadlm: phi_{k,c} = pi/4 - pi k c / p (quarter phase: cross term on the targets exactly zero, so M0c = M0 there and the
          targets are top in both; like sym/anti the deterministic phase keeps the token counts at chance, unlike the random
          phases of EXP-016, whose counts carry the targets), then the number of mirror pairs ((a,b) and (b,a) both in train, a != b) is lowered to exactly that of the anti split of the same seed and
          arm by swaps (remove one member of a random mirror pair, add a q-weighted pair that creates no new mirror pair).
          Reason (review s13): summed over all k the cross term is fixed by the mirror-pair count, so sym/anti also differ in
          mirror pairs (sym ~706, anti ~420, random ~571); quadlm vs anti keeps M0, the counts and the mirror count equal and
          differs in M0c.
Targets: F and G, 5 each, disjoint, from k = 1..56; same target sets for all modes of a seed.
Random streams: SeedSequence([50001, seed, arm, mode, purpose]). Pure numpy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P, TRAIN_FRAC, M, EPS = 113, 0.3, 5, 2.0
K = (P - 1) // 2
SALT = 50_001
ARM_ID = {"F": 0, "G": 1}
MODE_ID = {"sym": 0, "anti": 1, "quadlm": 3}
PURPOSE = {"targets": 0, "pairs": 1, "repair": 2}


def rng_for(seed: int, arm: str, mode: str, purpose: str) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([SALT, seed, ARM_ID[arm], MODE_ID[mode], PURPOSE[purpose]]))


def target_sets(seed: int) -> dict[str, list[int]]:
    ks = np.arange(1, K + 1)
    F = sorted(int(k) for k in rng_for(seed, "F", "sym", "targets").choice(ks, size=M, replace=False))
    G = sorted(int(k) for k in rng_for(seed, "G", "sym", "targets").choice(np.setdiff1d(ks, F), size=M, replace=False))
    return {"F": F, "G": G}


def weights(seed: int, arm: str, mode: str, targets: list[int], rng: np.random.Generator) -> np.ndarray:
    a, b = np.arange(P).repeat(P), np.tile(np.arange(P), P)
    c = (a + b) % P
    shift = {"sym": 0.0, "anti": np.pi / 2, "quadlm": np.pi / 4}[mode]
    wave = np.mean([np.cos(2 * np.pi * k * a / P + shift - np.pi * k * c / P) for k in targets], axis=0)
    return np.clip(1.0 + EPS * wave, 0.05, None)


def mirror_count(idx: np.ndarray) -> int:
    """Unordered pairs {(a,b), (b,a)}, a != b, with both members in the split."""
    S = np.zeros(P * P, bool)
    S[idx] = True
    a, b = idx // P, idx % P
    return int((S[b * P + a] & (a != b)).sum() // 2)


def order_bias(idx: np.ndarray) -> float:
    a, b = idx // P, idx % P
    return float(((a > b).sum() - (a < b).sum()) / len(idx))


def lower_mirrors(idx: np.ndarray, q: np.ndarray, target: int, rng: np.random.Generator) -> np.ndarray:
    S = np.zeros(P * P, bool)
    S[idx] = True
    mir = lambda x: (x % P) * P + x // P   # noqa: E731
    while True:
        cur = np.flatnonzero(S)
        paired = cur[S[mir(cur)] & (cur // P != cur % P)]
        if len(paired) // 2 <= target:
            break
        S[rng.choice(paired)] = False                                  # break one mirror pair
        cand = np.flatnonzero(~S & ~S[mir(np.arange(P * P))])          # not in train, mirror not in train (no new pair)
        S[rng.choice(cand, p=q[cand] / q[cand].sum())] = True          # q-weighted replacement keeps the steering
    out = np.flatnonzero(S)
    if len(out) != len(idx) or mirror_count(out) != target:
        raise SystemExit("mirror repair failed")
    return out


def engineered(seed: int, arm: str, mode: str, targets: list[int]) -> np.ndarray:
    rng = rng_for(seed, arm, mode, "pairs")
    q = weights(seed, arm, mode, targets, rng)
    keys = rng.random(P * P) ** (1.0 / q)
    idx = np.sort(np.argsort(-keys)[:int(round(TRAIN_FRAC * P * P))])
    if mode == "quadlm":
        target = mirror_count(engineered(seed, arm, "anti", targets))
        idx = lower_mirrors(idx, q, target, rng_for(seed, arm, mode, "repair"))
    return idx


def spectra(idx: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """M0 (EXP-015), M0c (EXP-019 coherent: left + right before |.|^2) and the a/b count spectrum, k = 1..56."""
    Mk = np.zeros((P, P))
    Mk[idx // P, idx % P] = 1.0
    t = np.arange(P)
    o = (np.arange(P)[None, :] - t[:, None]) % P
    L, R = Mk[t[:, None], o], Mk[o, t[:, None]]
    fold = lambda x: x[1:K + 1] + x[P - K:][::-1]   # noqa: E731
    m0 = fold((np.abs(np.fft.fft(L, axis=0)) ** 2 + np.abs(np.fft.fft(R, axis=0)) ** 2).sum(axis=1))
    m0c = fold((np.abs(np.fft.fft(L + R, axis=0)) ** 2).sum(axis=1))
    cnt = fold(np.abs(np.fft.fft(Mk.sum(1))) ** 2 + np.abs(np.fft.fft(Mk.sum(0))) ** 2)
    return m0, m0c, cnt


def rank(pw: np.ndarray, T: list[int]) -> float:
    r = np.argsort(np.argsort(-pw, kind="stable"))
    return float(np.mean([r[k - 1] for k in T]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", default=str(HERE / "splits"))
    a = ap.parse_args()
    ts = target_sets(a.seed)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for mode in ("sym", "anti", "quadlm"):
        for arm in "FG":
            T = ts[arm]
            idx = engineered(a.seed, arm, mode, T)
            if len(idx) != 3831 or len(np.unique(idx)) != 3831:
                raise SystemExit("bad split size")
            m0, m0c, cnt = spectra(idx)
            meta = {"seed": a.seed, "arm": arm, "mode": mode, "eps": EPS, "targets": T, "targets_F": ts["F"],
                    "targets_G": ts["G"], "n_train": 3831,
                    "rank_M0": rank(m0, T), "rank_M0c": rank(m0c, T), "rank_counts": rank(cnt, T),
                    "share_M0": float(m0[[k - 1 for k in T]].sum() / m0.sum()),
                    "share_M0c": float(m0c[[k - 1 for k in T]].sum() / m0c.sum()),
                    "mirror_pairs": mirror_count(idx), "diag_pairs": int((idx // P == idx % P).sum()),
                    "order_bias": order_bias(idx),
                    "M0c_top5": sorted((np.argsort(-m0c, kind="stable")[:M] + 1).tolist())}
            stem = f"split_add113_seed{a.seed}_{mode}_{arm}"      # no dot in the stem (Path.with_suffix pitfall)
            np.save(out / f"{stem}.npy", idx)
            (out / f"{stem}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
            print(stem, "T", T, f"rank M0 {meta['rank_M0']:.1f} M0c {meta['rank_M0c']:.1f} counts {meta['rank_counts']:.1f}",
                  f"share M0 {meta['share_M0']:.3f} M0c {meta['share_M0c']:.3f}", "mirror", meta["mirror_pairs"],
                  f"order {meta['order_bias']:+.3f}")


if __name__ == "__main__":
    main()
