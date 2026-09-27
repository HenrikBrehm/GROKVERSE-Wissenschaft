#!/usr/bin/env python3
"""EXP-080 analysis (N36 pilot, session 26, UNTESTED). Reading fixed in README before any run.

Per seed s and switch step t: B_R(task) = auc1000(none) - auc1000(R) (benefit of reset R for learning the new task; mean training loss over
the first 1000 post-switch steps). Interaction I(t) = [B_qk - B_vo](sub) - [B_qk - B_vo](sq). N36 predicts I > 0 ("the path the switch
needs holds"); "the value path always holds" predicts B_vo > B_qk in both tasks and I near 0.

  python lab/tools/guarded_run.py -- python lab/experiments/EXP-080-route-vs-content/analyze.py [--selftest]
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SEEDS, TS, TASKS, RESETS, POST = list(range(800, 810)), (50, 1000), ("sub", "sq"), ("none", "qk", "vo"), 2000


def load(s: int, t: int, task: str, reset: str) -> float | str:
    f = HERE / "raw" / f"s{s}_t{t}_{task}_{reset}" / "result.json"
    if not f.exists():
        return "fehlt"
    r = json.loads(f.read_text(encoding="utf-8"))
    if (r.get("seed"), r.get("switch_step"), r.get("new_task"), r.get("reset"), r.get("post_steps"), r.get("device")) != (s, t, task, reset, POST, "cuda"):
        return "defekt: result.json does not match the job"
    v = r.get("auc1000")
    return float(v) if isinstance(v, (int, float)) and np.isfinite(v) else "defekt: auc"


def sign_flip_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1.0, -1.0), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def summarize(d: np.ndarray, rng: np.random.Generator) -> dict:
    boot = np.array([rng.choice(d, len(d)).mean() for _ in range(10_000)])
    return {"n": len(d), "mean": float(d.mean()), "sd": float(d.std(ddof=1)) if len(d) > 1 else None,
            "ci95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
            "p_one_sided_gt0": sign_flip_p(d) if len(d) <= 20 else None, "n_positive": int((d > 0).sum())}


def reading(I: dict, Bvo_minus_qk: dict) -> str:
    if I["n"] < 8:
        return "nicht auswertbar"
    if I["mean"] > 0 and I["p_one_sided_gt0"] < 0.05:
        return "Wechselwirkung wie N36 (der benötigte Pfad hält; Pilot)"
    if all(b["ci95"][0] > 0 for b in Bvo_minus_qk.values()) and I["ci95"][0] <= 0 <= I["ci95"][1]:
        return "Wertepfad wirkt in beiden Wechseln stärker (keine Wechselwirkung; Pilot)"
    return "unklar"


def main() -> None:
    rng = np.random.default_rng(80)
    out: dict = {"problems": []}
    for t in TS:
        rows = []
        for s in SEEDS:
            v = {(k, r): load(s, t, k, r) for k in TASKS for r in RESETS}
            bad = [f"{k}/{r}: {x}" for (k, r), x in v.items() if isinstance(x, str)]
            if bad:
                out["problems"].append(f"seed {s} t {t}: " + "; ".join(bad))
                continue
            B = {k: {r: v[(k, "none")] - v[(k, r)] for r in ("qk", "vo")} for k in TASKS}
            rows.append({"seed": s, "B": B, "I": (B["sub"]["qk"] - B["sub"]["vo"]) - (B["sq"]["qk"] - B["sq"]["vo"])})
        res: dict = {"n_valid": len(rows), "rows": rows}
        if len(rows) >= 2:
            res["I"] = summarize(np.array([r["I"] for r in rows]), rng)
            res["B_vo_minus_B_qk"] = {k: summarize(np.array([r["B"][k]["vo"] - r["B"][k]["qk"] for r in rows]), rng) for k in TASKS}
            res["B"] = {k: {r: summarize(np.array([row["B"][k][r] for row in rows]), rng) for r in ("qk", "vo")} for k in TASKS}
            res["reading"] = reading(res["I"], res["B_vo_minus_B_qk"]) if t == 50 else "sekundär, nur berichtet"
        else:
            res["reading"] = "nicht auswertbar"
        out[f"t{t}"] = res
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: ({kk: vv for kk, vv in v.items() if kk != "rows"} if isinstance(v, dict) else v) for k, v in out.items()}, indent=1, ensure_ascii=False))


def selftest() -> None:
    rng = np.random.default_rng(0)
    mk = lambda m, sd=0.05: summarize(np.random.default_rng(1).normal(m, sd, 10), rng)   # noqa: E731
    assert reading(mk(0.3), {"sub": mk(-0.2), "sq": mk(0.2)}).startswith("Wechselwirkung")
    assert reading(mk(0.0, 0.05), {"sub": mk(0.2), "sq": mk(0.2)}).startswith("Wertepfad")
    assert reading({**mk(0.3), "n": 7}, {"sub": mk(0.2), "sq": mk(0.2)}) == "nicht auswertbar"
    assert reading(mk(-0.3), {"sub": mk(-0.2), "sq": mk(0.2)}) == "unklar"
    print("[EXP-080] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
