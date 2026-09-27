"""EXP-074 addendum (session 32, 2026-09-27, fixed BEFORE any EXP-074 run): time cost of resets at a switch at 50 steps.

Prospective test of the post hoc N29b/N29c timing pattern (lab/confirm/speed_switch_resets_s32.py) in two other tasks.
Units: 20 seeds (add 97 and mul 113, seeds 80-89 each; one direction F->G). b = min(first test >= 0.95, 2000) counted from step 0.
  Q1 (primary)  log2 b(VO reset) - log2 b(QK reset) > 0, pooled over the 20 units, exact one-sided sign test (non-tied units).
  Q2            log2 b(attention reset) - log2 b(MLP reset) > 0, same test.
  Q3            log2 b(attention reset) - log2 b(plain switch) > 0, same test.
  Descriptive   each arm against G only (EXP-044, same splits and test set) = the switch cost C(50) with and without reset, per task.
Arms are read from result.json fields (seed, config.p/task, switch_step, events.reset_at_switch.which, split/test files), not from
directory names. Validity: every unit needs all five EXP-074 arms and the EXP-044 G-only run, completed, same test hash and init
checksum; otherwise the unit is dropped and reported (Q-tests need >= 16 units, else 'nicht auswertbar').
  python lab/experiments/EXP-074-reset-other-tasks/time_cost.py [--selftest]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
CAP, MIN_UNITS = 2000, 16
ARMS = ("none", "attn", "mlp", "qk", "vo")


def log_b(r: dict) -> float:
    g = (r.get("events") or {}).get("generalization_step")
    return math.log2(min(g, CAP) if g is not None else CAP)


def task_of(r: dict) -> str:
    return f"{r['config']['task']}{r['config']['p']}"


def collect() -> tuple[dict, list[str]]:
    units: dict = {}
    for f in (HERE / "raw").glob("*/result.json"):
        r = json.loads(f.read_text(encoding="utf-8"))
        if r.get("status") != "completed" or r.get("switch_step") != 50:
            continue
        which = ((r.get("events") or {}).get("reset_at_switch") or {}).get("which") or "none"
        key = (task_of(r), r["seed"])
        units.setdefault(key, {})[which] = r
    for f in (LAB / "experiments/EXP-044-generalize-lockin/raw").glob("*/result.json"):
        r = json.loads(f.read_text(encoding="utf-8"))
        if r.get("status") == "completed" and r.get("switch_split_file") is None and str(r.get("split_file", "")).endswith("_train_G.npy"):
            units.setdefault((task_of(r), r["seed"]), {})["G"] = r
    bad, ok = [], {}
    for k, v in sorted(units.items()):
        miss = [a for a in ARMS + ("G",) if a not in v]
        if miss:
            bad.append(f"{k}: missing {miss}")
            continue
        if len({x["test_hash"] for x in v.values()}) != 1 or len({x["init_checksum_shared"] for x in v.values()}) != 1:
            bad.append(f"{k}: test set or init differs")
            continue
        ok[k] = {a: log_b(x) for a, x in v.items()}
    return ok, bad


def sign_test(d: np.ndarray) -> dict:
    nz = d[np.abs(d) > 1e-9]
    k, n = int((nz > 0).sum()), len(nz)
    return {"mean": float(d.mean()), "pos": k, "nonzero": n, "p_one_sided": sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0}


def evaluate(ok: dict) -> dict:
    if len(ok) < MIN_UNITS:
        return {"verdict": "nicht auswertbar", "n_units": len(ok)}
    d = lambda a, b: np.array([v[a] - v[b] for v in ok.values()])   # noqa: E731
    out = {"n_units": len(ok), "Q1_vo_minus_qk": sign_test(d("vo", "qk")), "Q2_attn_minus_mlp": sign_test(d("attn", "mlp")),
           "Q3_attn_minus_none": sign_test(d("attn", "none"))}
    for task in sorted({k[0] for k in ok}):
        sub = {k: v for k, v in ok.items() if k[0] == task}
        out[f"C50_vs_G_{task}"] = {a: float(np.mean([v[a] - v["G"] for v in sub.values()])) for a in ARMS}
    return out


def main() -> None:
    ok, bad = collect()
    out = {"note": "addendum fixed in session 32 before any EXP-074 run; exploration", "broken_or_missing": bad, **evaluate(ok)}
    (HERE / "time_cost_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


def selftest() -> None:
    fake = {("add97", s): {"none": 9.0, "attn": 10.0, "mlp": 9.5, "qk": 9.2, "vo": 10.5, "G": 9.6} for s in range(20)}
    e = evaluate(fake)
    assert e["Q1_vo_minus_qk"]["pos"] == 20 and abs(e["Q1_vo_minus_qk"]["p_one_sided"] - 0.5 ** 20) < 1e-15
    assert abs(e["Q3_attn_minus_none"]["mean"] - 1.0) < 1e-12 and abs(e["C50_vs_G_add97"]["vo"] - 0.9) < 1e-12
    assert evaluate(dict(list(fake.items())[:15]))["verdict"] == "nicht auswertbar"
    assert sign_test(np.zeros(4))["p_one_sided"] == 1.0
    assert abs(log_b({"events": {"generalization_step": 4096}}) - math.log2(CAP)) < 1e-12     # capped at 2000
    assert abs(log_b({"events": {"generalization_step": 512}}) - 9.0) < 1e-12 and abs(log_b({"events": {}}) - math.log2(CAP)) < 1e-12
    print("[EXP-074 time_cost] selftest ok")


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
