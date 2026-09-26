"""EXP-039 analysis (pre-registered, README): EXP-020 protocol with a constant lr scale c on the F phase (steps <= 250),
full lr after the switch. Unit = cell (seed, c). Reuses EXP-020/analyze.py (loader, K, d, interval) with a patched run
directory and grid, plus fail-closed metadata checks (lr_scale flag, optimizer config, shared init checksum).
H39 (lambda clock): c = 2 -> interval (12, 25]; c = 0.5 -> (50, 100]. Step clock: (25, 50] for both c.
Nachtrag a (Codex, before any run): grid c = 2: 10, 12, 25, 50; c = 0.5: 25, 50, 100, 150. A cell is 'lambda'/'step' only
if its observed interval equals the predicted one; completed cells that are non-monotone, cross after gen_F or miss the
endpoints count as 'unclear' (not excluded). Unit = seed with both cells complete: 'lambda' if both lambda, 'step' if
both step, else 'unclear'. Verdict: >= 3 complete seeds; all lambda -> Lambda-Uhr gestuetzt (AdamW, this schedule);
all step -> Schrittuhr; else unklar.
Usage: python analyze.py [--selftest]"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[0]
SEEDS = (30, 32, 34, 31)
GRIDS = {2.0: (10, 12, 25, 50), 0.5: (25, 50, 100, 150)}
MIN_SEEDS = 3


def classify(c: float, lo: float, hi: float) -> str:
    """Interval-safe: 'lambda' / 'step' only on the discriminating grid points, else 'unclear'."""
    lam = (12, 25) if c == 2.0 else (50, 100)
    return "lambda" if (lo, hi) == lam else "step" if (lo, hi) == (25, 50) else "unclear"


def seed_class(a: str, b: str) -> str:
    return a if a == b and a in ("lambda", "step") else "unclear"


def verdict(classes: list[str]) -> str:
    """classes: one per complete seed."""
    if len(classes) < MIN_SEEDS:
        return "nicht auswertbar"
    if all(c == "lambda" for c in classes):
        return "Lambda-Uhr gestuetzt"
    return "Schrittuhr" if all(c == "step" for c in classes) else "unklar"


def load_mod(c: float):
    spec = importlib.util.spec_from_file_location(f"exp020_c{c}", LAB / "EXP-020-data-switch" / "analyze.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.SWITCH = GRIDS[c]
    m.GRID = (0.0, *map(float, GRIDS[c]), math.inf)
    orig = m.run_dir
    m.run_dir = lambda s, t: orig(s, t) if t == 0 else HERE / "raw" / (orig(s, t).name + f"_lrs{c:g}")
    return m


def meta_ok(m, c: float, s: int) -> str | None:
    ref = None
    for t in m.GRID:
        f = m.run_dir(s, t) / "result.json"
        r = json.loads(f.read_text(encoding="utf-8"))
        want = 1.0 if t == 0 else c
        if float(r.get("lr_scale", 1.0)) != want or (r.get("warmup") or 0) != 0:
            return f"lr_scale/warmup flag {f.parent.name}"
        if t != 0 and r.get("lr_scale_until") != 250:
            return f"lr_scale_until {f.parent.name}"
        cf = r["config"]
        key = (cf.get("lr"), cf.get("weight_decay"), cf.get("beta1"), cf.get("beta2"), r["init_checksum_shared"])
        if ref is None:
            ref = key
        elif key != ref:
            return f"config/init differs {f.parent.name}"
    return None


def cell(m, c: float, s: int) -> dict:
    r = m.row(s)
    out = {"seed": s, "c": c, **{k: r.get(k) for k in ("valid", "d", "K", "lo", "hi", "monotone", "gen_F", "reason")}}
    reason = r.get("reason") or ""
    if not r["valid"] and "construction did not steer" not in reason:
        return out | {"complete": False, "why": reason or "invalid run set"}   # missing/corrupt runs only
    why = meta_ok(m, c, s)
    if why:
        return out | {"complete": False, "why": why}
    if not r["valid"]:
        return out | {"complete": True, "class": "unclear", "why": "endpoints d(0) < 0 < d(inf) not met"}
    if not r["monotone"] or not (r["gen_F"] and r["hi"] < r["gen_F"]):
        return out | {"complete": True, "class": "unclear", "why": "non-monotone or crossing not before gen_F"}
    disp = {str(t): json.loads((m.run_dir(s, t) / "result.json").read_text(encoding="utf-8"))["events"]
            .get("displacement_at_switch") for t in GRIDS[c]}
    return out | {"complete": True, "class": classify(c, r["lo"], r["hi"]),
                  "lambda_interval": [c * r["lo"], c * r["hi"] if r["hi"] != math.inf else None],
                  "displacement_at_switch": disp}


def main() -> None:
    rows = []
    for c in GRIDS:
        m = load_mod(c)
        for s in SEEDS:
            try:
                rows.append(cell(m, c, s))
            except (OSError, KeyError, ValueError) as e:
                rows.append({"seed": s, "c": c, "complete": False, "why": f"{type(e).__name__}: {e}"})
    by = {(r["seed"], r["c"]): r for r in rows}
    seeds = {s: seed_class(by[(s, 2.0)]["class"], by[(s, 0.5)]["class"]) for s in SEEDS
             if by[(s, 2.0)]["complete"] and by[(s, 0.5)]["complete"]}
    out = {"rows": rows, "seed_classes": seeds, "n_seeds": len(seeds), "verdict": verdict(list(seeds.values()))}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


def selftest() -> None:
    assert classify(2.0, 12, 25) == "lambda" and classify(2.0, 25, 50) == "step"
    assert classify(2.0, 10, 12) == "unclear"                     # crossing at step 11-12: Lambda <= 24, not lambda
    assert classify(2.0, 0, 10) == "unclear" and classify(2.0, 50, math.inf) == "unclear"
    assert classify(0.5, 50, 100) == "lambda" and classify(0.5, 25, 50) == "step"
    assert classify(0.5, 0, 25) == "unclear" and classify(0.5, 100, 150) == "unclear"
    assert seed_class("lambda", "lambda") == "lambda" and seed_class("lambda", "step") == "unclear"
    assert seed_class("unclear", "unclear") == "unclear"
    assert verdict(["lambda"] * 2) == "nicht auswertbar"
    assert verdict(["lambda"] * 3) == "Lambda-Uhr gestuetzt"
    assert verdict(["step"] * 4) == "Schrittuhr" and verdict(["lambda"] * 3 + ["unclear"]) == "unklar"
    m = load_mod(2.0)
    assert m.GRID == (0.0, 10.0, 12.0, 25.0, 50.0, math.inf)
    assert m.run_dir(30, 25).name.endswith("_at25_lrs2") and m.run_dir(30, math.inf).name.endswith("train_F_lrs2")
    assert m.run_dir(30, 0).parent.parent.name == "EXP-020-data-switch"
    m = load_mod(0.5)
    assert m.run_dir(30, 50).name.endswith("_at50_lrs0.5")
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
