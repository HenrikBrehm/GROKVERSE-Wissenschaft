"""EXP-132: facts and held-out test sets for the Pythia multiplication pilot (session 61; no training).

Facts F/G = the P1 mul113 splits (lab/confirm/splits/confirm_exp1_eps2.0_mul113_seed<S>_{F,G}.npy, 3831 pairs each, targets
in discrete-log coordinates, generator 3). Test = 2554 pairs with a, b != 0 drawn from the pairs in neither F nor G
(numpy default_rng(SeedSequence([132, S]))), the same test set for F and G of a seed. Writes splits/seed<S>_{F,G}.npy (copies),
seed<S>_test.npy, seed<S>.json {"targets": {"F": .., "G": ..}, "seed": S}; never overwrites.
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-132-pythia-mul/build_splits.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "confirm/splits"
OUT = HERE / "splits"
P, N_TEST, SEEDS = 113, 2554, (1000, 1001)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for s in SEEDS:
        if (OUT / f"seed{s}.json").exists():
            print(f"[skip] seed {s} exists")
            continue
        arms, targets = {}, {}
        for arm in "FG":
            arms[arm] = np.load(SRC / f"confirm_exp1_eps2.0_mul113_seed{s}_{arm}.npy").astype(np.int64)
            meta = json.loads((SRC / f"confirm_exp1_eps2.0_mul113_seed{s}_{arm}.json").read_text(encoding="utf-8"))
            assert meta["task"] == "mul" and meta["p"] == P and meta["arm"] == arm
            targets[arm] = meta["targets"]
        used = np.union1d(arms["F"], arms["G"])
        a, b = np.arange(P * P) // P, np.arange(P * P) % P
        pool = np.setdiff1d(np.flatnonzero((a != 0) & (b != 0)), used)
        test = np.sort(np.random.default_rng(np.random.SeedSequence([132, s])).choice(pool, N_TEST, replace=False))
        assert not np.intersect1d(test, used).size
        for arm in "FG":
            np.save(OUT / f"seed{s}_{arm}.npy", arms[arm])
        np.save(OUT / f"seed{s}_test.npy", test)
        (OUT / f"seed{s}.json").write_text(json.dumps({"targets": targets, "seed": s}, indent=1), encoding="utf-8")
        print(f"seed {s}: F {len(arms['F'])}, G {len(arms['G'])}, overlap {len(np.intersect1d(arms['F'], arms['G']))}, "
              f"pool {len(pool)}, test {len(test)}, targets {targets}")


if __name__ == "__main__":
    main()
