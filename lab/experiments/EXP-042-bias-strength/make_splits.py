"""EXP-042: G train sets of different concentration eps_G for the EXP-020 protocol (pure numpy, deterministic).
Re-runs EXP-020's build() with the SAME rng stream (test set, pool, keys u, F wave, G wave phases) and changes only eps for G.
F (eps 2) and the test set are bit-identical to EXP-020 (checked); G targets unchanged. Writes eps{e}/splits/seed{s}_*.npy
+ seed{s}.json (targets, G target power share). Usage: python make_splits.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
E20 = HERE.parent / "EXP-020-data-switch"
sys.path.insert(0, str(E20))
sys.path.insert(0, str(HERE.parent / "EXP-018-split-speed"))
sys.path.insert(0, str(HERE.parent / "EXP-015-mask-spectrum"))
from make_splits import P, TEST_FRAC, TRAIN_FRAC, keyed_sample, q_from_wave, wave  # noqa: E402  (EXP-018)
from make_split import mask_from_idx, target_set  # noqa: E402

SALT, EPS_G, SEEDS = 50_021, (8.0, 1.0), (30, 31, 32, 34)


def build(seed: int, eps_g: float) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed + SALT)                 # identical stream to EXP-020 make_splits.build
    perm = rng.permutation(P * P)
    n_test = int(round(TEST_FRAC * P * P))
    test, pool = np.sort(perm[:n_test]), np.sort(perm[n_test:])
    n_train = int(round(TRAIN_FRAC * P * P))
    u = rng.random(len(pool))
    out = {"test": test}
    for arm in ("F", "G"):
        q = q_from_wave(wave(target_set(seed, arm), rng), 2.0 if arm == "F" else eps_g)[pool]
        out[arm] = keyed_sample(pool, q, n_train, u)
    return out


def main() -> None:
    import mask_spectrum as ms
    for e in EPS_G:
        d = HERE / f"eps{e:g}" / "splits"
        d.mkdir(parents=True, exist_ok=True)
        for s in SEEDS:
            o = build(s, e)
            for name in ("test", "F"):                        # fail closed: must equal EXP-020
                ref = np.load(E20 / "splits" / f"seed{s}_{'test' if name == 'test' else 'train_F'}.npy")
                if not np.array_equal(o[name], ref):
                    raise SystemExit(f"seed {s}: {name} differs from EXP-020")
            for name, idx in o.items():
                np.save(d / f"seed{s}_{'test' if name == 'test' else 'train_' + name}.npy", idx)
            pw = ms.m0(mask_from_idx(o["G"]))
            tg = {a: target_set(s, a) for a in ("F", "G")}
            meta = {"seed": s, "eps_G": e, "targets": tg,
                    "G_target_power_share": float(sum(pw[k - 1] for k in tg["G"]) / pw.sum()),
                    "overlap_FG_train": int(np.intersect1d(o["F"], o["G"]).size)}
            (d / f"seed{s}.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
            print(json.dumps(meta))


if __name__ == "__main__":
    main()
