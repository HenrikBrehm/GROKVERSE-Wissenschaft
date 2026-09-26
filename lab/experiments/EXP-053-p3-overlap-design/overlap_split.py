"""EXP-053 (Entwurf, Paket B / P3): split pairs A, B with a CONTROLLED share of common pairs and matched steering strength.

add mod 113, common held-out test set (20 % of all pairs), train sets of round(0.3 p^2) = 3831 pairs from the remaining pool:
  S  : round(omega * 3831) shared pairs, drawn UNIFORMLY from the pool (no target content)
  A  : S + pairs weighted by q_F (EXP-016 construction), B : S + pairs weighted by q_G
  A and B pick their non-shared pairs in alternation from their own key orders (symmetric competitive draw), so the
  overlap is exactly |S|. A sequential draw (A first, B from the rest) is NOT used: the rest of the pool then carries the
  negative image of A's pattern and B gets F power (offline, session 14: F share in B 0.12-0.21 vs chance 0.09).
eps(omega) is calibrated on calibration seeds 900-909 so that the M0 target share of A and B stays at SHARE_GOAL for every
overlap level (uniform S dilutes the steering). Streams: SeedSequence([SALT, seed, level, purpose]). Pure numpy.

  python overlap_split.py --calibrate          # eps per omega -> calibration.json (calibration seeds only)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-043-generalize-steering"))
from make_split import mask_power  # noqa: E402

P, TRAIN_FRAC, TEST_FRAC, M = 113, 0.3, 0.2, 5
N_TRAIN = int(round(TRAIN_FRAC * P * P))
SALT = 53_001
OMEGAS = (0.0, 0.2, 0.4)                    # 0.75 is not reachable with matched strength (offline: share <= 0.12 at eps -> inf)
SHARE_GOAL = 0.185                          # EXP-016 level (0.185-0.199)
CAL_SEEDS = tuple(range(900, 910))
PURPOSE = {"targets": 0, "test": 1, "shared": 2, "phases": 3, "keys": 4}


def rng_for(seed: int, level: int, purpose: str) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([SALT, seed, level, PURPOSE[purpose]]))


def targets(seed: int) -> tuple[list[int], list[int]]:
    rng = rng_for(seed, 0, "targets")
    ks = rng.permutation(np.arange(1, (P - 1) // 2 + 1))
    return sorted(int(k) for k in ks[:M]), sorted(int(k) for k in ks[M:2 * M])


def weights(T: list[int], eps: float, rng: np.random.Generator) -> np.ndarray:
    a, b = np.arange(P).repeat(P), np.tile(np.arange(P), P)
    phi = rng.uniform(0, 2 * np.pi, size=(len(T), P))
    wave = np.mean([np.cos(2 * np.pi * k * a / P + phi[i, (a + b) % P]) for i, k in enumerate(T)], axis=0)
    return np.clip(1.0 + eps * wave, 0.05, None)


def build(seed: int, omega: float, eps: float) -> dict[str, np.ndarray]:
    level = int(round(omega * 1000))
    perm = rng_for(seed, 0, "test").permutation(P * P)            # same test set for every overlap level of a seed
    n_test = int(round(TEST_FRAC * P * P))
    test, pool = np.sort(perm[:n_test]), np.sort(perm[n_test:])
    n_s = int(round(omega * N_TRAIN))
    S = np.sort(rng_for(seed, level, "shared").choice(pool, n_s, replace=False))
    rest = np.setdiff1d(pool, S)
    F, G = targets(seed)
    rp = rng_for(seed, level, "phases")
    qF, qG = weights(F, eps, rp), weights(G, eps, rp)
    rk = rng_for(seed, level, "keys")
    order = {x: rest[np.argsort(-(rk.random(len(rest)) ** (1.0 / q[rest])), kind="stable")] for x, q in (("A", qF), ("B", qG))}
    taken = np.zeros(P * P, bool)
    pick: dict[str, list[int]] = {"A": [], "B": []}
    pos = {"A": 0, "B": 0}
    while min(len(v) for v in pick.values()) < N_TRAIN - n_s:
        for x in "AB":
            if len(pick[x]) < N_TRAIN - n_s:
                while taken[order[x][pos[x]]]:
                    pos[x] += 1
                taken[order[x][pos[x]]] = True
                pick[x].append(int(order[x][pos[x]]))
    return {"test": test, "A": np.union1d(S, pick["A"]), "B": np.union1d(S, pick["B"]), "S": S}


def share(idx: np.ndarray, T: list[int]) -> float:
    pw = mask_power(idx, "add", P)
    return float(pw[[k - 1 for k in T]].sum() / pw.sum())


def strength(omega: float, eps: float) -> float:
    out = []
    for s in CAL_SEEDS:
        d, (F, G) = build(s, omega, eps), targets(s)
        out += [share(d["A"], F), share(d["B"], G)]
    return float(np.mean(out))


def calibrate() -> None:
    res = {}
    for om in OMEGAS:
        lo, hi = 0.5, 40.0                                          # strength rises monotonically in eps (offline)
        for _ in range(12):
            mid = (lo * hi) ** 0.5
            lo, hi = (mid, hi) if strength(om, mid) < SHARE_GOAL else (lo, mid)
        eps = (lo * hi) ** 0.5
        rows = []
        for s in CAL_SEEDS:
            d, (F, G) = build(s, om, eps), targets(s)
            rows.append({"seed": s, "A_F": share(d["A"], F), "A_G": share(d["A"], G), "B_G": share(d["B"], G),
                         "B_F": share(d["B"], F), "overlap": len(np.intersect1d(d["A"], d["B"])) / N_TRAIN,
                         "test_disjoint": not np.intersect1d(d["test"], np.union1d(d["A"], d["B"])).size})
        m = {k: float(np.mean([r[k] for r in rows])) for k in ("A_F", "A_G", "B_G", "B_F", "overlap")}
        res[str(om)] = {"eps": eps, "mean": m, "all_test_disjoint": all(r["test_disjoint"] for r in rows)}
        print(om, round(eps, 3), {k: round(v, 3) for k, v in m.items()}, res[str(om)]["all_test_disjoint"], flush=True)
    (HERE / "calibration.json").write_text(json.dumps({"share_goal": SHARE_GOAL, "cal_seeds": list(CAL_SEEDS),
                                                       "levels": res}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1:] == ["--calibrate"]:
        calibrate()
    else:
        raise SystemExit(__doc__)
