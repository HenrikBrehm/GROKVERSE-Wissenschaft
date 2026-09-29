"""EXP-119 analysis (exploration, 2 seeds; readings fixed in session 52 before any run).
Per run from result.json (curve every 250 steps; cols step, train_fact_acc, test_fact_acc, ...):
  t_test  = first step with held-out fact accuracy >= 0.5, linearly interpolated between snapshots; None = not by 6000
  t_train = same for training-fact accuracy (reported; gap t_test - t_train per arm)
Per seed: q = t_test(R) / mean(t_test(F), t_test(G)); if R is censored, q >= 6000 / mean (lower bound, counts as >= 1.5 only if
  that bound is >= 1.5). If F or G is censored, the seed has no q ("not learned (budget)").
Readings: "constructed faster" q >= 1.5 in both seeds; "no advantage" q <= 1.15 in both seeds; else "unclear".
Descriptive: final held-out accuracy per arm, Delta_pow(F, G) at 6000 (as LM1).
Added in session 52 before any EXP-119 run (descriptive, R4 analogue): per run, Spearman rho between the split's own mask
  spectrum M0 (EXP-043 make_split.mask_power, add 113) and the power of the 113 number rows of the tied embedding at the last
  snapshot (EXP-102 analyze.power); reported for F, G and R, no reading attached. Not a confirmation; R5 in the toy model is
~6.5x at a similar mask concentration, but the LM learns training and held-out facts almost together (EXP-114), so the toy
grokking gap has no direct counterpart here.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-119-lm-speed-r5/analyze.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from make_jobs import ARMS, PAIRS, STEPS  # noqa: E402


def cross(curve: list, col: int, thr: float = 0.5) -> float | None:
    for (s0, *r0), (s1, *r1) in zip(curve, curve[1:]):
        a0, a1 = r0[col - 1], r1[col - 1]
        if a0 >= thr:
            return float(s0)
        if a1 >= thr:
            return float(s0 + (thr - a0) / (a1 - a0) * (s1 - s0))
    return None


def load(seed: int, split_seed: int, arm: str) -> dict:
    ds = [d for d in (HERE / "raw").iterdir() if d.name.startswith(f"lm2_seed{seed}_seed{split_seed}_{arm}_steps{STEPS}_")]
    if len(ds) != 1:
        return {"status": "missing"}
    r = json.loads((ds[0] / "result.json").read_text(encoding="utf-8"))
    if r.get("status") != "completed" or r.get("steps_completed") != STEPS:
        return {"status": "incomplete"}
    c = r["curve"]
    return {"status": "ok", "t_test": cross(c, 2), "t_train": cross(c, 1), "final_test": c[-1][2], "dir": ds[0],
            "rho_mask_we": mask_rho(ds[0], split_seed, arm)}


def mask_rho(run_dir: Path, split_seed: int, arm: str) -> float:
    """Session 52 addition (descriptive): Spearman(mask spectrum of the run's split, W_E number-row power at the end)."""
    import importlib.util
    import numpy as np
    lab = HERE.parents[1]
    def mod(name: str, path: Path):
        spec = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    ms = mod("exp043_make_split", lab / "experiments/EXP-043-generalize-steering/make_split.py")
    a102 = mod("exp102_analyze", lab / "experiments/EXP-102-lm-ladder-stage1/analyze.py")
    m0 = ms.mask_power(np.load(lab / "experiments/EXP-102-lm-ladder-stage1/splits" / f"seed{split_seed}_{arm}.npy"), "add", 113)
    pw = a102.power(np.load(run_dir / "we_snapshots.npy")[-1])
    rk = lambda v: np.argsort(np.argsort(v)).astype(float)   # noqa: E731  (no ties expected in float spectra)
    return float(np.corrcoef(rk(m0), rk(pw))[0, 1])


def seed_q(runs: dict) -> float | None | str:
    if any(runs[x]["status"] != "ok" for x in ARMS):
        return "incomplete"
    tF, tG, tR = (runs[x]["t_test"] for x in ARMS)
    if tF is None or tG is None:
        return "not learned (budget)"
    m = (tF + tG) / 2
    return (tR if tR is not None else float(STEPS)) / m


def reading(qs: list, censored: list) -> str:
    if any(isinstance(q, str) for q in qs):
        return "no reading (" + ", ".join(q for q in qs if isinstance(q, str)) + ")"
    if all(q >= 1.5 for q in qs):
        return "constructed faster"
    if all(q <= 1.15 and not c for q, c in zip(qs, censored)):
        return "no advantage"
    return "unclear"


def selftest() -> None:
    c = [[0, 0.0, 0.0], [250, 0.2, 0.0], [500, 0.8, 0.4], [750, 1.0, 0.6]]
    assert cross(c, 1) == 375.0 and abs(cross(c, 2) - 625.0) < 1e-9 and cross(c, 2, 0.9) is None
    ok = lambda t: {"status": "ok", "t_test": t}  # noqa: E731
    assert abs(seed_q({"F": ok(2000.0), "G": ok(2000.0), "R": ok(3000.0)}) - 1.5) < 1e-12
    assert seed_q({"F": ok(2000.0), "G": ok(2000.0), "R": ok(None)}) == 3.0
    assert seed_q({"F": ok(None), "G": ok(2000.0), "R": ok(None)}) == "not learned (budget)"
    assert reading([1.6, 3.0], [False, True]) == "constructed faster"
    assert reading([1.1, 1.0], [False, False]) == "no advantage"
    assert reading([1.1, 1.6], [False, False]) == "unclear"
    print("selftest ok")


def main() -> None:
    if "--selftest" in sys.argv:
        selftest()
        return
    rows, qs, cens = [], [], []
    for m, s in PAIRS:
        runs = {x: load(m, s, x) for x in ARMS}
        q = seed_q(runs)
        qs.append(q)
        cens.append(runs["R"].get("t_test") is None)
        rows.append({"model_seed": m, "split_seed": s, "q": q,
                     "arms": {x: {k: v for k, v in r.items() if k != "dir"} for x, r in runs.items()}})
    out = {"note": "exploration, 2 seeds", "reading": reading(qs, cens), "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
