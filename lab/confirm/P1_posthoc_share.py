"""P1 post hoc, descriptive (session 28; NOT part of the registered P1 analysis, no test, no Holm).

Question (reviewer-facing): Delta_pow (P1) is a relative log ratio between the two target sets. How large is the steering in
absolute terms? Per task, seed and arm (F/G), from the bound P1 runs through the frozen P1 loader (power_at):
  own    = share of the group power of W_E on the arm's own 5 targets at step 2000 (chance = 5 / number of components),
  own0   = the same share at step 0 (initialization; add/mul only: D59 runs store spectra, step 0 read from spectra.npy),
  other  = share on the other arm's 5 targets at step 2000,
  hits   = how many of the arm's 5 targets are among the 5 strongest components at step 2000.
Numpy only, reads stored runs, trains nothing. Output: lab/confirm/P1_posthoc_share.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
import confirm_p1 as c  # noqa: E402
from result_loader import Expect, find_run, load_run  # noqa: E402

sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
from analyze import group_power  # noqa: E402

N_BOOT = 10_000


def share(pw: np.ndarray, S: list[int]) -> float:
    return float(pw[[k - 1 for k in S]].sum() / pw.sum())


def top5(pw: np.ndarray) -> set[int]:
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:5]}


def power0(man: dict, t: dict, s: int, arm: str) -> np.ndarray | None:
    """Step-0 power of the same bound run (same file set the frozen loader checked for STEP)."""
    st = c.stem(man, t, s, arm)
    split = c.SPLITS / f"{st}.npy"
    dev = man["device"]
    if t["task"] == "D":
        d = find_run(c.RAW, f"EXP-046_seed{s}_{st}_dev{dev}")
        L = load_run(d, Expect(seed=s, device=dev, max_steps=c.STEP, split_file=split,
                               config={"p": 2 * t["p"], "group": f"D{t['p']}"}, at=(0,)))
        return L.spectrum(0) if L.status == "ok" and c.unbound(man, d) is None else None
    suffix = "" if (t["task"], t["p"]) == ("add", 113) else f"_{t['task']}{t['p']}"
    d = find_run(c.RAW, f"EXP-0*_baseline_seed{s}_thr*_{st}{suffix}_dev{dev}")
    L = load_run(d, Expect(seed=s, device=dev, max_steps=c.STEP, split_file=split,
                           config={"p": t["p"], "task": t["task"]}, snapshots_at=(0,)))
    if L.status != "ok" or c.unbound(man, d) is not None:
        return None
    return group_power(L.snapshot(0), t["task"], t["p"])[0]


def ci(x: np.ndarray, rng: np.random.Generator) -> list[float]:
    b = rng.choice(x, size=(N_BOOT, len(x))).mean(axis=1)
    return [float(np.quantile(b, 0.025)), float(np.quantile(b, 0.975))]


def seed_means(rows: list[dict], key: str) -> np.ndarray:
    """F and G of one seed share the initialization: the seed, not the arm, is the resampling unit."""
    by: dict[int, list[float]] = {}
    for r in rows:
        by.setdefault(r["seed"], []).append(r[key])
    return np.array([np.mean(v) for v in by.values()])


def main() -> None:
    man = json.loads((LAB / "confirm/P1_manifest.json").read_text(encoding="utf-8"))
    rng = np.random.default_rng(2026_09_28)
    out = {"note": "post hoc, descriptive; not part of the registered P1 analysis", "manifest_commit": man["commit"], "tasks": {}}
    for t in man["tasks"]:
        name = f"{t['task']}{t['p']}"
        rows, bad = [], []
        for s in man["seeds"]:
            T = {a: json.loads((c.SPLITS / f"{c.stem(man, t, s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
            for arm, oth in (("F", "G"), ("G", "F")):
                pw = c.power_at(man, t, s, arm)
                if isinstance(pw, str):
                    bad.append(f"{s}{arm}: {pw}")
                    continue
                p0 = power0(man, t, s, arm)
                rows.append({"seed": s, "arm": arm, "n_comp": len(pw), "own": share(pw, T[arm]), "other": share(pw, T[oth]),
                             "own0": None if p0 is None else share(p0, T[arm]), "hits": len(top5(pw) & set(T[arm]))})
        if not rows:
            out["tasks"][name] = {"valid": 0, "bad": bad}
            continue
        own = np.array([r["own"] for r in rows])
        oth = np.array([r["other"] for r in rows])
        own0 = np.array([r["own0"] for r in rows if r["own0"] is not None])
        hits = np.array([r["hits"] for r in rows])
        out["tasks"][name] = {
            "valid_arms": len(rows), "bad": bad, "chance_share": 5 / rows[0]["n_comp"],
            "own_mean": float(own.mean()), "own_ci_by_seed": ci(seed_means(rows, "own"), rng), "own_min": float(own.min()), "own_max": float(own.max()),
            "other_mean": float(oth.mean()), "own0_mean": float(own0.mean()) if len(own0) else None, "own0_n": len(own0),
            "hits_mean": float(hits.mean()), "hits_hist": {str(k): int((hits == k).sum()) for k in range(6)},
        }
        print(name, json.dumps({k: v for k, v in out["tasks"][name].items() if k != "bad"}), "bad:", len(bad), flush=True)
    (LAB / "confirm/P1_posthoc_share.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
