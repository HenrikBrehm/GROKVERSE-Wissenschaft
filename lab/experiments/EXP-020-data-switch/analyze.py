"""EXP-020: causal commitment time of the frequency choice via a mid-training data switch F -> G. (UNTESTED on real runs)

Per seed: runs t = inf (only F), t = 0 (only G), t in SWITCH (F until t, then G); all exactly 2000 steps.
d(t) = |K ∩ F| - |K ∩ G| with K = top-5 of W_E at step 2000. t_half = first grid t with d > 0, interpolated in
log(t + 25) to the last grid t with d <= 0. H20: t_half < gen_F (first test acc >= 0.95 on T* in the t = inf run,
2000 if never). Definition: README.md. Note: the pure runs (no switch) carry exp_id EXP-018 by the trainer's naming.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB.parent / "training"))
from grokverse.data import split_hash  # noqa: E402

SEEDS = range(30, 35)
SWITCH = (50, 150, 400, 1000)
M, STEPS, GEN_THR, MIN_VALID = 5, 2000, 0.95, 4
OFFSET = 25.0


def run_dir(s: int, t: float) -> Path:
    base = f"raw/EXP-018_baseline_seed{s}_thr4_seed{s}_train_"
    if t == 0:
        return HERE / (base + "G")
    if t == np.inf:
        return HERE / (base + "F")
    return HERE / f"raw/EXP-020_baseline_seed{s}_thr4_seed{s}_train_F_to_seed{s}_train_G_at{int(t)}"


def top_at(d: Path, step: int) -> set[int] | None:
    spec, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
    if step not in steps:
        return None
    pw = spec[steps.index(step)]
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:M]}


def load(s: int, t: float) -> tuple[dict | None, str | None]:
    d = run_dir(s, t)
    if not (d / "result.json").exists():
        return None, f"t={t}: missing"
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    if res["status"] != "completed" or res["seed"] != s or res["steps_completed"] != STEPS:
        return None, f"t={t}: status/seed/steps"
    arm = "G" if t == 0 else "F"
    if res["split_hash"] != split_hash(np.load(HERE / f"splits/seed{s}_train_{arm}.npy")):
        return None, f"t={t}: split hash"
    if res.get("test_hash") != split_hash(np.load(HERE / f"splits/seed{s}_test.npy")):
        return None, f"t={t}: test hash"
    if t not in (0, np.inf):
        if (res.get("switch_step") != t or res.get("events", {}).get("switch", {}).get("step") != t
                or res.get("switch_hash") != split_hash(np.load(HERE / f"splits/seed{s}_train_G.npy"))):
            return None, f"t={t}: switch not as specified"
    return res, None


def t_half(grid: list[float], d: list[int]) -> float | None:
    """First grid point with d > 0, log-interpolated to the preceding point (grid ascending, inf last)."""
    for j in range(1, len(grid)):
        if d[j] > 0:                          # first crossing; all earlier d <= 0
            lo, hi = grid[j - 1], grid[j]
            if hi == np.inf:
                return float(np.inf)
            x0, x1 = np.log(lo + OFFSET), np.log(hi + OFFSET)
            frac = (0 - d[j - 1]) / (d[j] - d[j - 1]) if d[j] != d[j - 1] else 1.0
            return float(np.exp(x0 + frac * (x1 - x0)) - OFFSET)
    return None


def row(s: int) -> dict:
    meta = json.loads((HERE / f"splits/seed{s}.json").read_text(encoding="utf-8"))
    F, G = set(meta["targets"]["F"]), set(meta["targets"]["G"])
    grid = [0.0, *map(float, SWITCH), np.inf]
    r: dict = {"seed": s, "valid": False, "d": {}}
    res_inf = None
    for t in grid:
        res, err = load(s, t)
        if err:
            r["reason"] = err
            return r
        K = top_at(run_dir(s, t), STEPS)
        r["d"][str(t)] = len(K & F) - len(K & G)
        r.setdefault("K", {})[str(t)] = sorted(K)
        r.setdefault("test_acc_2000", {})[str(t)] = res["final_acc"]["test"]
        if t == np.inf:
            res_inf = res
    d = [r["d"][str(t)] for t in grid]
    if not (d[0] < 0 < d[-1]):
        r["reason"] = "construction did not steer (need d(0) < 0 < d(inf))"
        return r
    gen = next((st for st, acc in zip(res_inf["dense"]["test_steps"], res_inf["dense"]["test_acc"])
                if acc >= GEN_THR), STEPS)
    th = t_half(grid, d)
    r.update({"valid": True, "gen_F": int(gen), "t_half": th, "monotone": bool(np.all(np.diff(d) >= 0)),
              "supports": th is not None and th < gen})
    return r


def main() -> None:
    rows = [row(s) for s in SEEDS]
    valid = [r for r in rows if r["valid"]]
    out: dict = {"rows": rows, "n_valid": len(valid)}
    if len(valid) < MIN_VALID:
        out["verdict"] = "nicht auswertbar"
    else:
        k = sum(r["supports"] for r in valid)
        out.update({"n_supports": k, "p_sign_one_sided": 0.5 ** len(valid) * sum(
            __import__("math").comb(len(valid), j) for j in range(k, len(valid) + 1)),
                    "verdict": "bestätigt" if k == len(valid) == 5 else
                    ("richtungsgleich, zu wenige Seeds" if k == len(valid) else "nicht bestätigt")})
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
