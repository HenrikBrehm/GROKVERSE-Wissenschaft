"""EXP-136 analysis (readings fixed in README before any run). Per cell (p, fraction) and seed: Delta_pow of the final
W_E group power at step 2000 (primary, as P1/EXP-043) between the F and the G run; descriptive: Delta_pow at the last
snapshot, top-5 overlap with the own targets, generalization step, final test accuracy.
Cell reading: fewer than 3 valid seeds -> 'nicht auswertbar'; Delta_pow(2000) > 1 in 3/3 -> 'steuert';
|Delta_pow(2000)| <= 1 in >= 2/3 -> 'bricht'; else 'unklar'.
Secondary reading (added after the independent code review, session 65, before any block run): the same rule on Delta_pow
at the last snapshot ('verdict_end'), reported with the number of runs per cell that never generalised (n_not_generalised),
because at low data the step-2000 value can come from the memorisation phase.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-136-large-modulus/analyze.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_jobs as mj  # noqa: E402

RAW = HERE / "raw"
STEP = 2000


def group_power(W: np.ndarray, p: int) -> np.ndarray:
    """Same formula as EXP-043 analyze.group_power for add p (odd p): power per k = 1..(p-1)//2 of the number rows."""
    sq = (np.abs(np.fft.fft(W[:p], axis=0)) ** 2).sum(axis=1)
    return 2.0 * sq[1:(p - 1) // 2 + 1] / p


def delta_pow(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float | None:
    s = lambda pw, S: float(pw[[k - 1 for k in S]].sum())   # noqa: E731
    sums = [s(pF, F), s(pF, G), s(pG, G), s(pG, F)]
    if not all(np.isfinite(x) and x > 0 for x in sums):
        return None
    d = float(np.log(sums[0] / sums[1]) + np.log(sums[2] / sums[3]))
    return d if np.isfinite(d) else None


def find_run(split_npy: str) -> Path | None:
    hits = [r.parent for r in RAW.glob("*/result.json")
            if Path(json.loads(r.read_text(encoding="utf-8")).get("split_file") or "").name == split_npy]
    return hits[0] if len(hits) == 1 else None


def load(p: int, fr: str, s: int, arm: str) -> dict | str:
    st = mj.stem(p, fr, s, arm)
    d = find_run(f"{st}.npy")
    if d is None:
        return f"{st}: fehlt oder doppelt"
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    if r.get("status") != "completed":
        return f"{st}: status {r.get('status')}"
    if r["config"].get("p") != p or r.get("device") != "cuda" or abs(r["config"].get("train_frac") - mj.fracs(p)[fr]) > 1e-12:
        return f"{st}: config differs"
    steps = np.load(d / "we_snapshot_steps.npy").tolist()
    snaps = np.load(d / "we_snapshots.npy")
    if STEP not in steps:
        return f"{st}: no snapshot at {STEP}"
    W, Wl = snaps[steps.index(STEP)].astype(np.float64), snaps[-1].astype(np.float64)
    if not (np.isfinite(W).all() and np.isfinite(Wl).all()):
        return f"{st}: non-finite snapshot"
    meta = json.loads((HERE / "splits" / f"{st}.json").read_text(encoding="utf-8"))
    gen = (r.get("transitions") or {}).get("primary", {}).get("generalization", {}).get("first_crossing_step")
    return {"pw": group_power(W, p), "pw_last": group_power(Wl, p), "last_step": int(steps[-1]), "T": meta["targets"],
            "gen": gen, "final_acc": r.get("final_acc")}


def top5(pw: np.ndarray) -> set[int]:
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:5]}   # tie-break as EXP-043


def reading(x: np.ndarray, n_valid: int) -> str:
    if n_valid < len(mj.SEEDS):
        return "nicht auswertbar"
    if (x > 1).all():
        return "steuert"
    if (np.abs(x) <= 1).sum() >= 2:
        return "bricht"
    return "unklar"


def placebo_sd(F: dict, G: dict, n: int = 500) -> float:
    """Descriptive noise floor (session 65, after the load test): SD of Delta_pow(2000) for random disjoint 5-sets outside F u G."""
    rng = np.random.default_rng(136)
    pool = np.array([k for k in range(1, len(F["pw"]) + 1) if k not in set(F["T"]) | set(G["T"])])
    v = [delta_pow(F["pw"], G["pw"], list(c[:5]), list(c[5:])) for c in (rng.choice(pool, 10, replace=False) for _ in range(n))]
    return float(np.std([x for x in v if x is not None]))


def cell(p: int, fr: str, loader=load) -> dict:
    rows, bad = [], []
    for s in mj.SEEDS:
        F, G = loader(p, fr, s, "F"), loader(p, fr, s, "G")
        if isinstance(F, str) or isinstance(G, str):
            bad.append(F if isinstance(F, str) else G)
            continue
        d, d_last = delta_pow(F["pw"], G["pw"], F["T"], G["T"]), delta_pow(F["pw_last"], G["pw_last"], F["T"], G["T"])
        if d is None or d_last is None:
            bad.append(f"seed {s}: Delta_pow not finite")
            continue
        rows.append({"seed": s, "dpow_2000": d, "dpow_last": d_last, "placebo_sd_2000": placebo_sd(F, G),
                     "last_step": [F["last_step"], G["last_step"]], "gen": [F["gen"], G["gen"]],
                     "final_acc": [F["final_acc"], G["final_acc"]],
                     "top5_own_2000": [len(top5(F["pw"]) & set(F["T"])), len(top5(G["pw"]) & set(G["T"]))]})
    x, x_end = np.array([r["dpow_2000"] for r in rows]), np.array([r["dpow_last"] for r in rows])
    return {"p": p, "fraction": fr, "train_frac": mj.fracs(p)[fr], "verdict": reading(x, len(rows)),
            "verdict_end": reading(x_end, len(rows)), "n_not_generalised": sum(g is None for r in rows for g in r["gen"]),
            "rows": rows, "problems": bad}


def main(loader=load) -> dict:
    out = {"cells": [cell(p, fr, loader) for p in mj.PS for fr in ("hi", "lo")]}
    return out


def selftest() -> None:
    rng = np.random.default_rng(0)

    def fake(strength: float):
        def ld(p, fr, s, arm):
            T = [1, 2, 3, 4, 5] if arm == "F" else [6, 7, 8, 9, 10]
            pw = np.ones((p - 1) // 2) + rng.random((p - 1) // 2) * 0.1
            pw[[k - 1 for k in T]] += strength
            return {"pw": pw, "pw_last": pw, "last_step": 2000, "T": T, "gen": None, "final_acc": None}
        return ld
    assert all(c["verdict"] == c["verdict_end"] == "steuert" and c["n_not_generalised"] == 6 for c in main(fake(5.0))["cells"])
    assert all(c["verdict"] == "bricht" for c in main(fake(0.0))["cells"])
    assert all(c["verdict"] == "nicht auswertbar" for c in main(lambda *a: "x: fehlt")["cells"])
    print("[exp136] selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        res = main()
        (HERE / "summary.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        for c in res["cells"]:
            print(c["p"], c["fraction"], c["verdict"], [round(r["dpow_2000"], 2) for r in c["rows"]], "| end:", c["verdict_end"],
                  [round(r["dpow_last"], 2) for r in c["rows"]], "| not generalised:", c["n_not_generalised"], c["problems"])
