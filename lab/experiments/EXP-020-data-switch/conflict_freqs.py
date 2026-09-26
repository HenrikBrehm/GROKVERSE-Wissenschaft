"""EXP-020 Nachtrag d (session 9): "foreign" frequencies in mixed states. Descriptive, secondary; no training.

Definition (fixed 2026-09-26 ~15:00 Berlin, after seeing seeds 30-32, BEFORE any run of seeds 33/34):
  A_s = F u G u {fold(2k) : k in F u G} u K_onlyF u K_onlyG   (K_only* = top-5 of the pure runs at step 2000)
  foreign(t) = top-5 of the switched run at step t + 2000 minus A_s
  early = t in {10, 25, 50}, late = t in {150, 400, 1000}
  init rank = rank (1 = strongest of 56) in the step-0 W_E spectrum (identical in all runs of a seed)
Predictions for the fresh seeds 33, 34 (each seed judged separately, must be valid = all 8 runs present):
  P-d1: at least one foreign frequency in at least one early run, and none in any late run.
  P-d2: pooled over both seeds, the median init rank of the distinct foreign frequencies (per seed) is <= 14.
Seeds 30-32 are exploration and are only reported.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P, M = 113, 5
EARLY, LATE = (10, 25, 50), (150, 400, 1000)
FRESH = (33, 34)


def fold(k: int) -> int:
    k %= P
    return min(k, P - k)


def spectrum(d: Path, step: int) -> np.ndarray | None:
    if not (d / "spectra.npy").exists():
        return None
    spec, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
    return spec[steps.index(step)] if step in steps else None


def ranks(pw: np.ndarray) -> dict[int, int]:
    order = np.lexsort((np.arange(len(pw)), -pw))
    return {int(k) + 1: r + 1 for r, k in enumerate(order)}


def top(pw: np.ndarray) -> set[int]:
    return {k for k, r in ranks(pw).items() if r <= M}


def analyze_seed(s: int) -> dict | None:
    meta = HERE / f"splits/seed{s}.json"
    base = f"raw/EXP-018_baseline_seed{s}_thr4_seed{s}_train_"
    pf, pg = spectrum(HERE / (base + "F"), 2000), spectrum(HERE / (base + "G"), 2000)
    init = spectrum(HERE / (base + "F"), 0)
    if not meta.exists() or pf is None or pg is None or init is None:
        return None
    tg = json.loads(meta.read_text(encoding="utf-8"))["targets"]
    fg = set(tg["F"]) | set(tg["G"])
    allowed = fg | {fold(2 * k) for k in fg} | top(pf) | top(pg)
    init_r = ranks(init)
    out = {"seed": s, "A_size": len(allowed), "foreign": {}, "complete": True}
    for t in (*EARLY, *LATE):
        pw = spectrum(HERE / f"raw/EXP-020_baseline_seed{s}_thr4_seed{s}_train_F_to_seed{s}_train_G_at{t}", t + 2000)
        if pw is None:
            out["complete"] = False
            continue
        out["foreign"][t] = sorted(top(pw) - allowed)
    distinct = sorted({k for v in out["foreign"].values() for k in v})
    out["init_ranks"] = {k: init_r[k] for k in distinct}
    out["early_any"] = any(out["foreign"].get(t) for t in EARLY)
    out["late_none"] = not any(out["foreign"].get(t) for t in LATE)
    return out


def main() -> None:
    rows = [r for s in range(30, 35) if (r := analyze_seed(s)) is not None]
    for r in rows:
        tag = "fresh" if r["seed"] in FRESH else "exploration"
        print(f"seed {r['seed']} ({tag}, complete={r['complete']}, |A|={r['A_size']}): foreign={r['foreign']} "
              f"init_ranks={r['init_ranks']} early_any={r['early_any']} late_none={r['late_none']}")
    fresh = [r for r in rows if r["seed"] in FRESH and r["complete"]]
    for r in fresh:
        print(f"P-d1 seed {r['seed']}: {'met' if r['early_any'] and r['late_none'] else 'not met'}")
    pooled = [v for r in fresh for v in r["init_ranks"].values()]
    if len(fresh) == len(FRESH):
        med = float(np.median(pooled)) if pooled else float("nan")
        print(f"P-d2: median init rank {med} over {len(pooled)} freqs -> {'met' if pooled and med <= 14 else 'not met'}")
    else:
        print(f"P-d2: not evaluable yet ({len(fresh)}/{len(FRESH)} fresh seeds complete)")
    (HERE / "conflict_freqs.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
