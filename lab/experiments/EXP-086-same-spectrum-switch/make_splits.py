"""EXP-086 splits (session 32, pure numpy, no training): same-spectrum and random controls for the switch cost (N43, skeptic point 1).

For seeds 400-409 the EXP-056 omega-0 files give A (targets F) and the common test set. New here (pool = all pairs minus test):
  A2  3831 pairs from pool minus A, weighted towards the SAME target frequencies F with the EXP-016 wave construction but FRESH
      phases (own stream) and fresh keys; eps calibrated per seed by bisection so that the realised M0 target share of A2 on F matches
      that of A (|diff| <= 0.005). Disjoint from A: same frequency set and strength, different pair pattern.
      NOT feasible (checked, session 32): the same construction with A's OWN phases. A already holds the high-weight pairs of its
      pattern, the rest of the pool carries the negative image, and the share on F stays at chance (0.083 at eps 80, seed 400).
  R1, R2  two disjoint uniform random subsets of the pool, 3831 pairs each.
Streams: SeedSequence([86_001, seed, purpose]). Writes splits/seed{s}_{A2,R1,R2}.npy and seed{s}.json; never overwrites; if files
exist, checks them bit for bit against a rebuild.   python lab/experiments/EXP-086-same-spectrum-switch/make_splits.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-053-p3-overlap-design"))
import overlap_split as ov  # noqa: E402

SEEDS, SALT, P, N = tuple(range(400, 410)), 86_001, 113, ov.N_TRAIN
SPL56 = LAB / "experiments/EXP-056-overlap-persistence/splits"
PURPOSE = {"phases": 0, "keys": 1, "random": 2}
ARMS = ("A2", "R1", "R2")


def rng(seed: int, purpose: str) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([SALT, seed, PURPOSE[purpose]]))


def weighted_draw(cands: np.ndarray, q: np.ndarray, keys: np.ndarray, n: int) -> np.ndarray:
    """Weighted sampling without replacement (Efraimidis-Spirakis, as overlap_split): top n of u^(1/q)."""
    return np.sort(cands[np.argsort(-(keys ** (1.0 / q[cands])), kind="stable")[:n]])


def build(seed: int) -> dict:
    A, test = np.load(SPL56 / f"seed{seed}_w0_A.npy"), np.load(SPL56 / f"seed{seed}_test.npy")
    pool = np.setdiff1d(np.arange(P * P), test)
    cand = np.setdiff1d(pool, A)
    F, _ = ov.targets(seed)
    goal = ov.share(A, F)

    def calibrated(phase_rng: np.random.Generator, keys: np.ndarray) -> tuple[np.ndarray, float]:
        state = phase_rng.bit_generator.state
        lo, hi = 0.5, 80.0
        for _ in range(40):                               # share rises monotonically in eps for fixed phases and keys
            mid = (lo * hi) ** 0.5
            phase_rng.bit_generator.state = state          # identical phases for every eps
            X = weighted_draw(cand, ov.weights(F, mid, phase_rng), keys, N)
            s_ = ov.share(X, F)
            if abs(s_ - goal) <= 0.002:
                break
            lo, hi = (mid, hi) if s_ < goal else (lo, mid)
        return X, mid

    A2, eps2 = calibrated(rng(seed, "phases"), rng(seed, "keys").random(len(cand)))              # fresh phases
    rr = rng(seed, "random").permutation(pool)
    R1, R2 = np.sort(rr[:N]), np.sort(rr[N:2 * N])
    for X in (A2,):
        assert len(X) == N and not np.intersect1d(X, A).size and not np.intersect1d(X, test).size
    assert not np.intersect1d(R1, R2).size and not np.intersect1d(np.union1d(R1, R2), test).size
    meta = {"seed": seed, "targets_F": F, "eps_A2": float(eps2), "share_A_F": goal,
            "share_A2_F": ov.share(A2, F), "share_R1_F": ov.share(R1, F), "share_R2_F": ov.share(R2, F),
            "overlap_A_R1": int(np.intersect1d(A, R1).size)}
    return {"A2": A2, "R1": R1, "R2": R2, "meta": meta}


def main() -> None:
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    for s in SEEDS:
        d = build(s)
        assert all(abs(d["meta"][f"share_{k}_F"] - d["meta"]["share_A_F"]) <= 0.005 for k in ("A2",)), d["meta"]
        for k in ARMS:
            f = out / f"seed{s}_{k}.npy"
            if f.exists():
                assert np.array_equal(np.load(f), d[k].astype(np.int64)), f"{f.name} differs from rebuild"
            else:
                with open(f, "xb") as fh:
                    np.save(fh, d[k].astype(np.int64))
        mf = out / f"seed{s}.json"
        if not mf.exists():
            mf.write_bytes(json.dumps(d["meta"], indent=1).encode("utf-8"))
        print(s, {k: round(v, 4) if isinstance(v, float) else v for k, v in d["meta"].items() if k != "targets_F"})


if __name__ == "__main__":
    main()
