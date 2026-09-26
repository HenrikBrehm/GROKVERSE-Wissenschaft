"""EXP-044: data-switch splits for add mod 97 / mul mod 113 (pure numpy, deterministic). UNTESTED.

Per task and init seed i: common held-out test set T*_i (20 % of all p^2 pairs), and from the remaining pool two engineered
train sets of round(0.3 p^2) pairs with DISJOINT target sets (EXP-043 construction in group coordinates, eps = 2), drawn with
INDEPENDENT keys (unlike EXP-020, whose F and G shared ~73 % of pairs; here the expected overlap is the chance level
n_train / pool ~ 37 %). Writes {task}{p}_seed{i}_{test,train_F,train_G}.npy + .json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-043-generalize-steering"))
from make_split import M, TRAIN_FRAC, group_coords, mask_power, target_set  # noqa: E402

SALT = 44_017
TEST_FRAC = 0.2


def build(seed: int, task: str, p: int, eps: float = 2.0) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed + SALT + (500_000 if task == "mul" else 0))
    n_all = p * p
    perm = rng.permutation(n_all)
    n_test = int(round(TEST_FRAC * n_all))
    test, pool = np.sort(perm[:n_test]), np.sort(perm[n_test:])
    n_train = int(round(TRAIN_FRAC * n_all))
    u, v, valid, n = group_coords(task, p)
    out = {"test": test}
    for arm in ("F", "G"):
        T = target_set(seed, task, p, arm)
        phi = rng.uniform(0, 2 * np.pi, size=(len(T), n))
        wave = np.mean([np.cos(2 * np.pi * k * u / n + phi[j, (u + v) % n]) for j, k in enumerate(T)], axis=0)
        q = np.where(valid, np.clip(1.0 + eps * wave, 0.05, None), 1.0)[pool]
        keys = rng.random(len(pool)) ** (1.0 / q)          # independent keys per arm
        out[arm] = np.sort(pool[np.argsort(-keys)[:n_train]])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=("add", "mul"), required=True)
    ap.add_argument("--p", type=int, required=True)
    ap.add_argument("--seeds", default="80-89")
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.seeds.split("-"))
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    for s in range(lo, hi + 1):
        sets = build(s, a.task, a.p)
        stem = f"{a.task}{a.p}_seed{s}"
        meta = {"seed": s, "task": a.task, "p": a.p, "targets": {arm: target_set(s, a.task, a.p, arm) for arm in "FG"},
                "overlap_FG_train": int(np.intersect1d(sets["F"], sets["G"]).size), "n_train": int(len(sets["F"])),
                "n_test": int(len(sets["test"]))}
        for name, idx in sets.items():
            np.save(out / f"{stem}_{'test' if name == 'test' else 'train_' + name}.npy", idx)
            if name != "test":
                pw = mask_power(idx, a.task, a.p)
                meta[f"M0_top5_{name}"] = sorted((np.argsort(-pw, kind="stable")[:M] + 1).tolist())
        (out / f"{stem}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        print(json.dumps({k: v for k, v in meta.items() if k != "seed"}))


if __name__ == "__main__":
    main()
