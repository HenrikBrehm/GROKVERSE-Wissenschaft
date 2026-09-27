"""EXP-082 (session 28, UNTESTED until a run window): split construction with GRADED target amplitudes. Pure numpy.

As confirm_splits.weights_cyclic (add 113, eps 2, 30 % of pairs, equal-amplitude construction of P1), but target i gets the
amplitude a_i from LEVELS (mean 1), assigned by a random permutation per arm:
    w(u, v) = clip(1 + eps * mean_i a_i cos(2 pi k_i u / n + phi_i[(u + v) % n]), 0.05)
Streams: SeedSequence([1000001, 82, 0, 113, seed, arm, purpose]) with purpose 0 targets (confirm_splits.target_sets with
experiment 82), 1 phases, 2 keys, 3 amplitude permutation. Pilot seeds 600-609 (unused, checked session 28).

  python lab/experiments/EXP-082-graded-targets/make_split.py --design     # numpy check of the lever, writes nothing
  python lab/experiments/EXP-082-graded-targets/make_split.py --write      # writes splits/ (refuses to overwrite)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "confirm"))
import confirm_splits as cs  # noqa: E402
from P1_posthoc_within import m0c_add  # noqa: E402

EXPERIMENT, P, EPS, SEEDS = 82, 113, 2.0, range(600, 610)
LEVELS = {"strong": np.array([0.4, 0.7, 1.0, 1.3, 1.6]), "weak": np.array([0.9, 0.95, 1.0, 1.05, 1.1])}
GRADE_ID = {"strong": 0, "weak": 1}


def stream(seed: int, arm: str, purpose: int, grade: str) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([cs.ROOT_SALT, EXPERIMENT, 0, P, seed, cs.ARM[arm], purpose, GRADE_ID[grade]]))


def amplitudes(seed: int, arm: str, grade: str) -> np.ndarray:
    return stream(seed, arm, 3, grade).permutation(LEVELS[grade])


def weights(T: list[int], amps: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    u, v, valid, n = cs.group_coords("add", P)
    phi = rng.uniform(0, 2 * np.pi, size=(len(T), n))
    wave = np.mean([a * np.cos(2 * np.pi * k * u / n + phi[i, (u + v) % n]) for i, (k, a) in enumerate(zip(T, amps))], axis=0)
    return np.where(valid, np.clip(1.0 + EPS * wave, 0.05, None), 1.0)


def build(seed: int, arm: str, grade: str) -> tuple[np.ndarray, list[int], np.ndarray]:
    T = cs.target_sets(EXPERIMENT, "add", P, seed)[arm]
    amps = amplitudes(seed, arm, grade)
    q = weights(T, amps, stream(seed, arm, 1, grade))
    keys = stream(seed, arm, 2, grade).random(len(q)) ** (1.0 / q)
    idx = np.sort(np.argsort(-keys)[:int(round(cs.TRAIN_FRAC * len(q)))])
    return idx, T, amps


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = np.argsort(np.argsort(x)) - 2.0, np.argsort(np.argsort(y)) - 2.0
    return float((rx * ry).sum() / 10.0)


def design() -> dict:
    """How strongly does the designed amplitude order the realized mask spectrum (the lever), and is the target share like P1?"""
    out = {}
    for g in LEVELS:
        rho, share, spread = [], [], []
        for s in SEEDS:
            for arm in "FG":
                idx, T, amps = build(s, arm, g)
                m = m0c_add(idx, P)[[k - 1 for k in T]]
                rho.append(spearman(amps, m))
                share.append(float(m.sum() / m0c_add(idx, P).sum()))
                spread.append(float(m.max() / m.min()))
        out[g] = {"mean_rho_amp_M0c": float(np.mean(rho)), "min_rho": float(np.min(rho)), "mean_target_share_M0c": float(np.mean(share)),
                  "median_M0c_max_over_min": float(np.median(spread))}
    return out


def write() -> None:
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    for g, s, arm in ((g, s, arm) for g in LEVELS for s in SEEDS for arm in "FG"):
        f = out / f"split_add113_seed{s}_{g}_{arm}.npy"
        if f.exists():
            raise SystemExit(f"{f.name} exists: never overwritten")
        idx, T, amps = build(s, arm, g)
        with open(f, "xb") as fh:
            np.save(fh, idx.astype(np.int64))
        with open(f.with_suffix(".json"), "x", encoding="utf-8") as fh:
            json.dump({"seed": s, "arm": arm, "grade": g, "targets": T, "amplitudes": [float(a) for a in amps], "eps": EPS,
                       "experiment": EXPERIMENT, "n": int(len(idx))}, fh, indent=1)


if __name__ == "__main__":
    if sys.argv[1:] == ["--design"]:
        print(json.dumps(design(), indent=1))
    elif sys.argv[1:] == ["--write"]:
        write()
    else:
        raise SystemExit(__doc__)
