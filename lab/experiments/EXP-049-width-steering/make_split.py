"""EXP-049: engineered splits (add mod 113, EXP-016 construction) for the width test, seeds 170-179, arms F and G.

Reuses target_sets() and engineered() of EXP-047 (SeedSequence([47001, seed, arm, purpose]); seeds 170-179 were never used
there, so the streams are new). The same split is trained at d_model 128 and 512. Pure numpy.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
# EXP-047's module is itself called make_split and imports EXP-043's make_split: load it under its own name
_spec = importlib.util.spec_from_file_location("exp047_make_split", HERE.parent / "EXP-047-marginal-control/make_split.py")
_m47 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_m47)
P, engineered, target_sets = _m47.P, _m47.engineered, _m47.target_sets


def m0(idx: np.ndarray) -> np.ndarray:
    """EXP-015 M0 for add mod 113, k = 1..56."""
    Mk = np.zeros((P, P))
    Mk[idx // P, idx % P] = 1.0
    t, c = np.arange(P)[:, None], np.arange(P)[None, :]
    o = (c - t) % P
    pw = (np.abs(np.fft.fft(Mk[t, o], axis=0)) ** 2 + np.abs(np.fft.fft(Mk[o, t], axis=0)) ** 2).sum(axis=1)
    K = (P - 1) // 2
    return pw[1:K + 1] + pw[P - K:][::-1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", default=str(HERE / "splits"))
    a = ap.parse_args()
    ts = target_sets(a.seed)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for arm in "FG":
        idx = engineered(a.seed, arm, ts[arm])
        if len(idx) != 3831 or len(np.unique(idx)) != 3831:
            raise SystemExit("bad split size")
        pw = m0(idx)
        rank = np.argsort(np.argsort(-pw, kind="stable"))
        meta = {"seed": a.seed, "arm": arm, "eps": 2.0, "targets": ts[arm], "targets_F": ts["F"], "targets_G": ts["G"],
                "n_train": 3831, "target_ranks": [int(rank[k - 1]) for k in ts[arm]],
                "target_power_share": float(pw[[k - 1 for k in ts[arm]]].sum() / pw.sum())}
        stem = f"split_add113_seed{a.seed}_eps2.0_{arm}"          # no Path.with_suffix ('.0_F')
        np.save(out / f"{stem}.npy", idx)
        (out / f"{stem}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
        print(stem, "targets", ts[arm], "ranks", meta["target_ranks"], f"share {meta['target_power_share']:.3f}")


if __name__ == "__main__":
    main()
