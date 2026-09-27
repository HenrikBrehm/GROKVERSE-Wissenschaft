"""EXP-085 (pilot, session 32, fixed before any run): switch cost and persistence in the shared-embedding MLP. Definition: README.md.

Seeds 400-409, EXP-056 splits (omega 0), --arch mlp, GPU. Pure A/B 10000 steps; switches A->B, B->A at t in TS, then 10000 steps.
  time   b = min(first test >= 0.95, CAP) from step 0, CAP = 10000 for every arm; C(t) = per seed mean over both directions of
         log2 b(switch@t) - log2 b(destination only)
  pi(t)  as EXP-056/059/075, but from the W_E snapshot 2000 steps after the switch (pure runs: step 2000), so it matches EXP-075
Reading (pre-registered, README): S2 rule of R6 on the median pi(t) and the mean C(t).
Run under guarded_run.py (imports torch via the shared loader).
  python lab/experiments/EXP-085-mlp-switch-cost/analyze.py [--selftest]
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
_spec = importlib.util.spec_from_file_location("exp056", LAB / "experiments/EXP-056-overlap-persistence/analyze.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

SEEDS, TS, CAP, MIN_VALID, MIN_PI = tuple(range(400, 410)), (10, 25, 50, 100, 200), 10000, 8, 8


def load(s: int, kind: str, t: int) -> dict | str:
    first, second = kind[0], kind[1:] or None
    st1 = A.stem(s, 0.0, first)
    steps = CAP + (t if second else 0)
    snap = (t + 2000) if second else 2000
    pat = f"EXP-0*_baseline_seed{s}_thr*_{st1}" + (f"_to_{A.stem(s, 0.0, second)}_at{t}" if second else "") + "_mlp" + A.SUF
    L = A.load_run(A.find_run(HERE / "raw", pat),
                   A.Expect(seed=s, device=A.DEV, max_steps=steps, split_file=A.SPL / f"{st1}.npy", test_file=A.SPL / f"seed{s}_test.npy",
                            switch_file=A.SPL / f"{A.stem(s, 0.0, second)}.npy" if second else None,
                            config={"p": 113, "task": "add", "arch": "mlp"}, snapshots_at=(snap,)))
    if L.status != "ok":
        return f"{kind}@{t}: {L.status}: {L.reason}"
    if L.res["steps_completed"] != steps:
        return f"{kind}@{t}: stopped at {L.res['steps_completed']} != {steps}"
    g = (L.res.get("events") or {}).get("generalization_step")
    return {"lb": math.log2(min(g, CAP) if g is not None else CAP), "pw": A._a43.group_power(L.snapshot(snap), "add", 113)[0]}


def s2_rule(mc: dict[int, float], med_pi: dict[int, float], n_pi: int) -> str:
    """As R6 (confirm_r6.s2_rule): C <= 0 wherever median pi >= 0.9 and C > 0 wherever 0.2 <= median pi <= 0.8."""
    if n_pi < MIN_PI:
        return "nicht auswertbar"
    hi = [t for t in mc if med_pi[t] >= 0.9]
    mid = [t for t in mc if 0.2 <= med_pi[t] <= 0.8]
    if not hi or not mid:
        return "nicht auswertbar"
    return "gestützt" if all(mc[t] <= 0 for t in hi) and all(mc[t] > 0 for t in mid) else "nicht gestützt"


def main() -> None:
    rows = []
    for s in SEEDS:
        meta = json.loads((A.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        R = {("A", 0): load(s, "A", 0), ("B", 0): load(s, "B", 0)}
        for t in TS:
            for k in ("AB", "BA"):
                R[(k, t)] = load(s, k, t)
        bad = [v for v in R.values() if isinstance(v, str)]
        if bad:
            rows.append({"seed": s, "valid": False, "reason": "; ".join(bad[:3])})
            continue
        row = {"seed": s, "valid": True,
               "C": {str(t): ((R[("AB", t)]["lb"] - R[("B", 0)]["lb"]) + (R[("BA", t)]["lb"] - R[("A", 0)]["lb"])) / 2 for t in TS},
               "events_pure": [R[("A", 0)]["lb"] < math.log2(CAP), R[("B", 0)]["lb"] < math.log2(CAP)]}
        LA, LB = A.logratio(R[("A", 0)]["pw"], F, G), A.logratio(R[("B", 0)]["pw"], F, G)
        if LA - LB >= 2.0:
            row["pi"] = {str(t): A.pi_of({"A": LA, "B": LB, "AB": A.logratio(R[("AB", t)]["pw"], F, G),
                                          "BA": A.logratio(R[("BA", t)]["pw"], F, G)})["pi"] for t in TS}
        rows.append(row)
    ok = [r for r in rows if r["valid"]]
    out: dict = {"n_valid": len(ok), "n_with_pi": sum("pi" in r for r in ok)}
    if len(ok) >= MIN_VALID:
        mc = {t: float(np.mean([r["C"][str(t)] for r in ok])) for t in TS}
        with_pi = [r for r in ok if "pi" in r]
        med_pi = {t: float(np.median([r["pi"][str(t)] for r in with_pi])) if with_pi else float("nan") for t in TS}
        out |= {"mean_C": {str(t): v for t, v in mc.items()}, "median_pi": {str(t): v for t, v in med_pi.items()},
                "C_pos": {str(t): sum(r["C"][str(t)] > 1e-9 for r in ok) for t in TS},
                "S2": s2_rule(mc, med_pi, len(with_pi))}
    else:
        out["S2"] = "nicht auswertbar"
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    assert s2_rule({10: 0.3, 25: 0.5, 50: -0.2}, {10: 0.1, 25: 0.5, 50: 0.95}, 8) == "gestützt"
    assert s2_rule({10: 0.3, 25: -0.1, 50: -0.2}, {10: 0.1, 25: 0.5, 50: 0.95}, 8) == "nicht gestützt"
    assert s2_rule({10: 0.3, 25: 0.5, 50: 0.2}, {10: 0.1, 25: 0.5, 50: 0.95}, 8) == "nicht gestützt"
    assert s2_rule({10: 0.3, 25: 0.5}, {10: 0.1, 25: 0.5}, 8) == "nicht auswertbar"          # no pi >= 0.9 in range
    assert s2_rule({10: 0.3, 25: 0.5, 50: -0.2}, {10: 0.1, 25: 0.5, 50: 0.95}, 7) == "nicht auswertbar"
    print("[exp085] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
