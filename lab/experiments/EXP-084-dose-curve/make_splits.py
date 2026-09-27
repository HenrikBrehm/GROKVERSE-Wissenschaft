"""EXP-084 (session 31, exploration): dose curve of grokking speed against the concentration eps of the EXP-016/018 split construction.
Per unit u (init seed 2780 + u, reserved 2780-2789): own streams SeedSequence([TAG, u, ...]) independent of the init; common held-out test
set (20 %), pool = rest, ONE key vector and ONE wave (targets A) for all engineered arms, so arms differ only in eps. Arms: R (uniform),
eps in EPS. Writes splits/u{u}_{arm}.npy, u{u}_test.npy and u{u}.json (targets, M0 target share, per-output count CV). Pure numpy.
  python lab/experiments/EXP-084-dose-curve/make_splits.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
import confirm_splits as cs  # noqa: E402

P, N_TRAIN, N_FREQ, M = 113, 3831, 56, 5
N_TEST = int(round(0.2 * P * P))
TAG, SEED0, N_UNITS = 20261002, 2780, 10
EPS = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0)
ARMS = ("R",) + tuple(f"e{e:g}" for e in EPS)


def stream(*key: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([TAG, *key]))


def wave(freqs: list[int], rng: np.random.Generator) -> np.ndarray:
    a, b = np.arange(P).repeat(P), np.tile(np.arange(P), P)
    phi = rng.uniform(0, 2 * np.pi, size=(len(freqs), P))
    return np.mean([np.cos(2 * np.pi * k * a / P + phi[i, (a + b) % P]) for i, k in enumerate(freqs)], axis=0)


def build(u: int) -> tuple[dict[str, np.ndarray], list[int]]:
    perm = stream(u, 0).permutation(P * P)
    test, pool = np.sort(perm[:N_TEST]), np.sort(perm[N_TEST:])
    tg = sorted(int(k) for k in stream(u, 1).choice(np.arange(1, N_FREQ + 1), size=M, replace=False))
    keys = stream(u, 2).random(len(pool))
    w = wave(tg, stream(u, 4))[pool]
    sets = {"test": test, "R": np.sort(stream(u, 3).choice(pool, size=N_TRAIN, replace=False))}
    for e in EPS:
        q = np.clip(1.0 + e * w, 0.05, None)
        sets[f"e{e:g}"] = np.sort(pool[np.argsort(-(keys ** (1.0 / q)))[:N_TRAIN]])
    return {k: v.astype(np.int64) for k, v in sets.items()}, tg


def describe(sets: dict[str, np.ndarray], tg: list[int]) -> dict:
    out = {}
    for a in ARMS:
        x = sets[a]
        pw = cs.m0(x, "add", P)
        c = np.bincount((x // P + x % P) % P, minlength=P)
        out[a] = {"m0_target_share": float(pw[[k - 1 for k in tg]].sum() / pw.sum()), "count_cv_c": float(c.std() / c.mean()),
                  "overlap_with_R": int(np.intersect1d(x, sets["R"]).size)}
    return out


def main() -> None:
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    for u in range(N_UNITS):
        sets, tg = build(u)
        for k, v in sets.items():
            f = out / f"u{u}_{k}.npy"
            if f.exists():
                if not np.array_equal(np.load(f), v):
                    raise SystemExit(f"{f.name} exists and differs: never overwrite")
                continue
            np.save(f, v)
        meta = {"unit": u, "init_seed": SEED0 + u, "targets": tg, "arms": describe(sets, tg)}
        (out / f"u{u}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        print(u, {a: round(m["m0_target_share"], 3) for a, m in meta["arms"].items()})


if __name__ == "__main__":
    main()
