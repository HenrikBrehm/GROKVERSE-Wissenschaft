"""EXP-044: is the early lock-in (K4, EXP-020) found for add 97 / mul 113 too? UNTESTED (written out of window).

Per task and seed i (80-89), all runs on the GPU: only-F (2000 steps), only-G (2000), switch F -> G at t in {25, 50, 150}
(t steps on F, then exactly 2000 on G). K = top-5 of W_E in the group basis (EXP-043 analyze.group_power) at the final step.
d = |K & F| - |K & G|. Valid seed: d(only-F) > 0 and d(only-G) < 0 and all five runs completed with matching split hashes.
Primary: sign test over valid seeds on d(150) (d > 0 vs d < 0, ties dropped), one-sided, Holm over the tasks that ran.
Definition: README.md.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB.parent / "training"))
from grokverse.data import split_hash  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from result_loader import Expect, find_run, load_run  # noqa: E402  (Astra 16: shared loader)
from paket_a_device import DEV, FB_SUFFIX, TR_SUFFIX  # noqa: E402  (session 15: CPU fallback for programme A)

_spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
_a43 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_a43)
group_power, top = _a43.group_power, _a43.top

TASKS = (("add", 97), ("mul", 113))
SEEDS = range(80, 90)
SWITCH = (25, 50, 150)
PRIMARY_T, ALPHA, MIN_VALID = 150, 0.05, 8


def find(task: str, p: int, s: int, kind: str) -> Path | None:
    stem = f"{task}{p}_seed{s}"
    pat = {"F": f"EXP-043_baseline_seed{s}_thr*_{stem}_train_F_{task}{p}{FB_SUFFIX}",
           "G": f"EXP-043_baseline_seed{s}_thr*_{stem}_train_G_{task}{p}{FB_SUFFIX}"}.get(
        kind, f"EXP-044_baseline_seed{s}_thr*_{stem}_train_F_to_{stem}_train_G_at{kind}_{task}{p}{FB_SUFFIX}")
    hits = sorted((HERE / "raw").glob(pat))
    return hits[0] if len(hits) == 1 else None


def final_K(d: Path | None, task: str, p: int, s: int, kind: str) -> tuple[set[int] | None, dict, str]:
    """Astra 16: shared loader; checks seed, device, the exact budget (2000, or t + 2000 for a switch at t), train/test/switch
    hashes, task/p and a finite W_E snapshot at the final step."""
    st = HERE / f"splits/{task}{p}_seed{s}"
    switch = kind not in ("F", "G")
    budget = int(kind) + 2000 if switch else 2000
    first = "G" if kind == "G" else "F"
    L = load_run(d, Expect(seed=s, device=DEV, max_steps=budget, split_file=f"{st}_train_{first}.npy",
                           test_file=f"{st}_test.npy", switch_file=f"{st}_train_G.npy" if switch else None,
                           config={"p": p, "task": task}, snapshots_at=(budget,)))
    if L.status != "ok":
        return None, L.res, f"{L.status}: {L.reason}"
    return top(group_power(L.snapshot(budget), task, p)[0]), L.res, ""


def row(task: str, p: int, s: int) -> dict:
    meta = json.loads((HERE / f"splits/{task}{p}_seed{s}.json").read_text(encoding="utf-8"))
    F, G = set(meta["targets"]["F"]), set(meta["targets"]["G"])
    hashes = {arm: split_hash(np.load(HERE / f"splits/{task}{p}_seed{s}_train_{arm}.npy")) for arm in "FG"}
    test_hash = split_hash(np.sort(np.load(HERE / f"splits/{task}{p}_seed{s}_test.npy")))   # Codex s12: common test set
    r: dict = {"seed": s, "valid": False, "F": sorted(F), "G": sorted(G)}
    d_of, extra = {}, {}
    for kind in ("F", "G") + tuple(str(t) for t in SWITCH):
        K, res, why = final_K(find(task, p, s, kind), task, p, s, kind)
        if K is None:
            r["reason"] = f"{kind}: {why}"
            return r
        if kind not in ("F", "G") and (res.get("switch_hash") != hashes["G"] or res["switch_step"] != int(kind)):
            r["reason"] = f"{kind}: switch hash/step"
            return r
        d_of[kind] = len(K & F) - len(K & G)
        extra[kind] = {"K": sorted(K), "gen": res["events"].get("generalization_step"),
                       "test_acc": res["final_acc"]["test"], "switch": res["events"].get("switch")}
        if kind == "F":                                   # memorization step of only-F: first train acc >= 0.99
            tr = res["dense"]
            r["memo_step_F"] = next((st for st, acc in zip(tr["train_steps"], tr["train_acc"]) if acc >= 0.99), None)
    r.update({"d": d_of, "runs": extra})
    r["valid"] = d_of["F"] > 0 and d_of["G"] < 0
    if not r["valid"]:
        r["reason"] = "construction did not steer in this seed (d(F) <= 0 or d(G) >= 0)"
    return r


def sign_p(pos: int, neg: int) -> float:
    n = pos + neg
    return float(sum(comb(n, k) for k in range(pos, n + 1)) / 2 ** n) if n else 1.0


def main() -> None:
    ran = [(t, p) for t, p in TASKS if (HERE / "raw").exists() and any((HERE / "raw").glob(f"*_{t}{p}_*"))]
    out: dict = {"tasks": {}}
    for task, p in ran:
        rows = [row(task, p, s) for s in SEEDS]
        valid = [r for r in rows if r["valid"]]
        t: dict = {"rows": rows, "n_valid": len(valid)}
        if len(valid) >= MIN_VALID:
            dp = [r["d"][str(PRIMARY_T)] for r in valid]
            pos, neg = sum(x > 0 for x in dp), sum(x < 0 for x in dp)
            t.update({"d150": dp, "pos": pos, "neg": neg, "ties": len(dp) - pos - neg, "p": sign_p(pos, neg),
                      "mean_d150": float(np.mean(dp)),
                      "d_by_t_mean": {str(x): float(np.mean([r["d"][str(x)] for r in valid])) for x in SWITCH},
                      "n_150_before_memo": sum(1 for r in valid if r.get("memo_step_F") and PRIMARY_T < r["memo_step_F"])})
        out["tasks"][f"{task}{p}"] = t
    ev = sorted(((k, t["p"]) for k, t in out["tasks"].items() if "p" in t), key=lambda x: x[1])
    still = True
    for i, (k, pv) in enumerate(ev):
        sig = still and pv < ALPHA / (len(ran) - i)     # Codex s12: family = all tasks that ran (README), not only evaluable
        still = sig
        out["tasks"][k]["holm_significant"] = sig
    for t in out["tasks"].values():
        t["verdict"] = ("nicht auswertbar" if "p" not in t else "widerspricht" if t["mean_d150"] <= 0
                        else "festgelegt" if t["holm_significant"] else "richtungsgleich, nicht signifikant")
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for k, t in out["tasks"].items():
        print(k, {x: v for x, v in t.items() if x != "rows"})


if __name__ == "__main__":
    main()
