"""EXP-020: causal commitment time of the frequency choice via a mid-training data switch F -> G. (UNTESTED on real runs)

Design after Nachtrag a (Codex review 2026-09-26): every switched run trains t steps on F and then exactly
G_BUDGET = 2000 steps on G; K = top-5 of W_E at the end (step t + 2000). Reference t = 0: only G for 2000 steps.
t = inf: only F (up to 8000 steps, gen_F observed; K read at step 2000).
d(t) = |K ∩ F| - |K ∩ G|. No interpolation: the commitment time is interval-censored between the last grid t with
d <= 0 and the first with d > 0. A seed supports H20 only if d is non-decreasing over the whole grid and the FIRST
grid t with d > 0 lies before gen_F (the whole interval precedes generalization); censored gen_F -> not evaluable.
Definition: README.md. The pure runs carry exp_id EXP-018 by the trainer's naming.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB.parent / "training"))
from grokverse.data import split_hash  # noqa: E402

SEEDS = range(30, 35)
SWITCH = (10, 25, 50, 150, 400, 1000)   # 10 and 25 added in Nachtrag b (before any run)
GRID = (0.0, *map(float, SWITCH), math.inf)
M, G_BUDGET, F_CAP, K_STEP_F, GEN_THR, MIN_VALID = 5, 2000, 8000, 2000, 0.95, 4


def run_dir(s: int, t: float) -> Path:
    base = f"raw/EXP-018_baseline_seed{s}_thr4_seed{s}_train_"
    if t == 0:
        return HERE / (base + "G")
    if t == math.inf:
        return HERE / (base + "F")
    return HERE / f"raw/EXP-020_baseline_seed{s}_thr4_seed{s}_train_F_to_seed{s}_train_G_at{int(t)}"


def top_at(d: Path, step: int) -> set[int] | None:
    spec, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
    if step not in steps:
        return None
    pw = spec[steps.index(step)]
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:M]}


def expected_steps(t: float) -> int | None:
    return None if t == math.inf else int(t) + G_BUDGET


def load(s: int, t: float) -> tuple[dict | None, str | None]:
    d = run_dir(s, t)
    if not (d / "result.json").exists():
        return None, f"t={t}: missing"
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    if res["status"] != "completed" or res["seed"] != s:
        return None, f"t={t}: status/seed"
    want = expected_steps(t)
    if want is not None and (res["steps_completed"] != want or res["max_steps"] != want):
        return None, f"t={t}: steps {res['steps_completed']}/{res['max_steps']}, expected {want}"
    if t == math.inf and res["max_steps"] != F_CAP:
        return None, "t=inf: cap differs"
    arm = "G" if t == 0 else "F"
    if res["split_hash"] != split_hash(np.load(HERE / f"splits/seed{s}_train_{arm}.npy")):
        return None, f"t={t}: split hash"
    if res.get("test_hash") != split_hash(np.load(HERE / f"splits/seed{s}_test.npy")):
        return None, f"t={t}: test hash"
    if t not in (0, math.inf):
        sw = res.get("events", {}).get("switch", {})
        if (res.get("switch_step") != t or sw.get("step") != t
                or sw.get("new_train_hash") != split_hash(np.load(HERE / f"splits/seed{s}_train_G.npy"))):
            return None, f"t={t}: switch not as specified"
    return res, None


def commitment(d: list[int]) -> dict:
    """Interval (lo, hi] of the commitment time on GRID; hi = first grid t with d > 0."""
    j = next(i for i, x in enumerate(d) if x > 0)          # exists: validity requires d(inf) > 0
    return {"lo": GRID[j - 1], "hi": GRID[j], "monotone": all(b >= a for a, b in zip(d, d[1:]))}


def row(s: int) -> dict:
    meta = json.loads((HERE / f"splits/seed{s}.json").read_text(encoding="utf-8"))
    F, G = set(meta["targets"]["F"]), set(meta["targets"]["G"])
    r: dict = {"seed": s, "valid": False, "d": {}, "K": {}, "diag": {}}
    res_inf = None
    for t in GRID:
        res, err = load(s, t)
        if err:
            r["reason"] = err
            return r
        K = top_at(run_dir(s, t), K_STEP_F) if t == math.inf else set(res["final_top_m_freqs"])
        if K is None:
            r["reason"] = "t=inf: no spectrum at step 2000"
            return r
        r["d"][str(t)], r["K"][str(t)] = len(K & F) - len(K & G), sorted(K)
        r["diag"][str(t)] = {"final_test_acc": res["final_acc"]["test"], "switch": res["events"].get("switch")}
        if t not in (0, math.inf):      # secondary: stability of K over the last 500 G steps
            early = top_at(run_dir(s, t), (int(t) + 1500) // 250 * 250)
            r["diag"][str(t)]["K_stable_last500"] = None if early is None else early == K
        if t == math.inf:
            res_inf = res
    d = [r["d"][str(t)] for t in GRID]
    if not (d[0] < 0 < d[-1]):
        r["reason"] = "construction did not steer (need d(0) < 0 < d(inf))"
        return r
    obs = [st for st, acc in zip(res_inf["dense"]["test_steps"], res_inf["dense"]["test_acc"]) if acc >= GEN_THR]
    c = commitment(d)
    r.update({"valid": True, "gen_F": obs[0] if obs else None, **c})
    if not obs:
        r["h20"] = "not evaluable (gen_F censored)"
    else:
        r["h20"] = "supports" if c["monotone"] and c["hi"] < obs[0] else "against"
    return r


def main() -> None:
    rows = [row(s) for s in SEEDS]
    ev = [r for r in rows if r["valid"] and r["h20"] != "not evaluable (gen_F censored)"]
    out: dict = {"rows": rows, "n_valid": sum(r["valid"] for r in rows), "n_evaluable": len(ev)}
    if len(ev) < MIN_VALID:
        out["verdict"] = "nicht auswertbar"
    else:
        k = sum(r["h20"] == "supports" for r in ev)
        out.update({"n_supports": k,
                    "p_sign_one_sided": sum(math.comb(len(ev), j) for j in range(k, len(ev) + 1)) / 2 ** len(ev),
                    "verdict": "bestätigt" if k == len(ev) == 5 else
                    ("richtungsgleich, zu wenige Seeds" if k == len(ev) else "nicht bestätigt")})
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print({k: v for k, v in r.items() if k not in ("diag",)})


if __name__ == "__main__":
    main()
