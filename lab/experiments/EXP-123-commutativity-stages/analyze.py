"""EXP-123 (session 55): analysis, written before any main run (reading fixed in README.md "Vorab").

Per run (swap_trace.py result.json): t_swap / t_other = first traced step (grid 25) with acc_swap / acc_other >= 0.5 (None = censored
at last_step); m = acc_other at t_swap. Technical check: overall test curve equals the frozen R5 freq_ban dense test curve of the same
seed/split at every common step to <= 2 predictions; else the run is technical (excluded).
H1 (random arm R): positive unit if t_swap observed and (t_other is None or t_other >= t_swap + 100); one-sided exact sign test.
H2 (paired E2_0 vs R): d = m(E2_0) - m(R) over units with t_swap observed in both; one-sided exact sign-permutation test on the mean
(all 2^n sign flips), bootstrap 95 % CI; minimum effect mean d >= 0.05.
Holm over {H1, H2}. Verdicts as in README. Secondary (descriptive): D_0 arm, t_swap / t_mem / t_gen per arm.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-123-commutativity-stages/analyze.py [--raw DIR]
"""
from __future__ import annotations

import argparse
import itertools
import json
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
UNITS = range(20)
ARMS = ("R", "E2_0", "D_0")
N_TEST = 2554
MIN_GAP = 100
MIN_D = 0.05


def first(steps: list[int], vals: list[float], thr: float) -> int | None:
    return next((s for s, v in zip(steps, vals) if v >= thr), None)


def load(raw: Path, u: int, arm: str) -> dict | None:
    init = json.loads((ROOT / f"lab/confirm/r5_splits/r5_u{u}.json").read_text(encoding="utf-8"))["init"]
    f = raw / f"u{u}_{arm}" / "result.json"
    if not f.exists():
        return {"unit": u, "arm": arm, "status": "fehlt"}
    r = json.loads(f.read_text(encoding="utf-8"))
    if r.get("status") != "completed" or r.get("seed") != init:
        return {"unit": u, "arm": arm, "status": "defekt"}
    t = r["trace"]
    ref = json.loads((ROOT / f"lab/confirm/r5_raw/EXP-018_baseline_seed{init}_thr1_r5_u{u}_{arm}_devcuda/result.json")
                     .read_text(encoding="utf-8"))["dense"]
    refd = dict(zip(ref["test_steps"], ref["test_acc"]))
    dev = max(abs(a - refd[s]) for s, a in zip(t["step"], t["test"]) if s in refd)
    ts = first(t["step"], t["swap"], 0.5)
    row = {"unit": u, "arm": arm, "seed": init, "status": "ok" if dev * N_TEST <= 2.01 else "technisch", "max_dev_preds": dev * N_TEST,
           "last_step": r["last_step"], "t_gen": r["generalization_step"], "t_mem": first(t["step"], t["train"], 0.99),
           "t_swap": ts, "t_other": first(t["step"], t["other"], 0.5),
           "m": t["other"][t["step"].index(ts)] if ts is not None else None}
    return row


def sign_test(k: int, n: int) -> float:
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n


def perm_p(d: np.ndarray) -> float:
    obs, n = d.mean(), len(d)
    if n > 20:
        raise SystemExit("exact permutation limited to n <= 20")
    cnt = sum((np.array(s) * np.abs(d)).mean() >= obs - 1e-12 for s in itertools.product((1, -1), repeat=n))
    return cnt / 2 ** n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(HERE / "raw"))
    a = ap.parse_args()
    rows = [load(Path(a.raw), u, arm) for u in UNITS for arm in ARMS]
    for r in rows:
        print(json.dumps(r), flush=True)
    ok = {(r["unit"], r["arm"]): r for r in rows if r["status"] == "ok"}
    bad = [r for r in rows if r["status"] != "ok"]
    out: dict = {"rows": rows, "n_not_ok": len(bad)}
    if len(bad) > 3:
        out["reading"] = f"nicht auswertbar ({len(bad)} Laeufe fehlen/defekt/technisch)"
    else:
        rr = [ok[(u, "R")] for u in UNITS if (u, "R") in ok and ok[(u, "R")]["t_swap"] is not None]
        pos = [r for r in rr if r["t_other"] is None or r["t_other"] >= r["t_swap"] + MIN_GAP]
        p1 = sign_test(len(pos), len(rr)) if rr else 1.0
        pairs = [u for u in UNITS if (u, "R") in ok and (u, "E2_0") in ok and ok[(u, "R")]["m"] is not None
                 and ok[(u, "E2_0")]["m"] is not None]
        d = np.array([ok[(u, "E2_0")]["m"] - ok[(u, "R")]["m"] for u in pairs])
        p2 = perm_p(d) if len(d) else 1.0
        rng = np.random.default_rng(123)
        boot = [rng.choice(d, len(d)).mean() for _ in range(20000)] if len(d) else [0.0]
        ci = [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))]
        ps = sorted([("H1", p1), ("H2", p2)], key=lambda x: x[1])
        holm = {ps[0][0]: min(1.0, 2 * ps[0][1])}
        holm[ps[1][0]] = min(1.0, max(holm[ps[0][0]], ps[1][1]))
        h1 = "gestuetzt" if holm["H1"] < 0.05 and len(rr) >= 10 and len(pos) >= 0.8 * len(rr) else "nicht gestuetzt"
        h2 = ("gestuetzt" if holm["H2"] < 0.05 and len(d) >= 10 and d.mean() >= MIN_D
              else "Richtung ja, unter Mindesteffekt" if holm["H2"] < 0.05 else "nicht gestuetzt")
        desc = {}
        for arm in ARMS:
            rs = [ok[(u, arm)] for u in UNITS if (u, arm) in ok]
            fr = [r["t_swap"] / r["t_gen"] for r in rs if r["t_swap"] and r["t_gen"]]
            desc[arm] = {"n": len(rs), "gen_observed": sum(r["t_gen"] is not None for r in rs),
                         "median_t_mem": float(np.median([r["t_mem"] for r in rs if r["t_mem"] is not None] or [np.nan])),
                         "median_t_swap": float(np.median([r["t_swap"] for r in rs if r["t_swap"] is not None] or [np.nan])),
                         "median_t_other": float(np.median([r["t_other"] for r in rs if r["t_other"] is not None] or [np.nan])),
                         "median_m": float(np.median([r["m"] for r in rs if r["m"] is not None] or [np.nan])),
                         "median_tswap_over_tgen": float(np.median(fr)) if fr else None}
        out.update({"H1": {"n": len(rr), "positive": len(pos), "p": p1, "p_holm": holm["H1"], "verdict": h1},
                    "H2": {"n": len(d), "mean_d": float(d.mean()) if len(d) else None, "ci95": ci, "n_pos": int((d > 0).sum()),
                           "p": p2, "p_holm": holm["H2"], "verdict": h2}, "descriptive": desc})
        out["reading"] = f"H1 {h1}; H2 {h2}"
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
