"""EXP-035 analysis (pre-registered, README Nachtrag a): EXP-020 protocol with lr warmup (200 steps, F phase only, full lr
after the switch); compares the warmup commitment interval with the no-warmup EXP-020 interval of the same seed.
Reuses EXP-020/analyze.py (validity, K, d, interval) with a patched run directory and grid, and adds metadata checks."""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[0]
W, LR = 200, 1e-3
SWITCH_WU = (10, 25, 50, 100, 150, 250)


def lam(t: float) -> float:
    """Accumulated learning rate after t warmup steps (lr_s = LR * min(1, s / W), s = 1..t), in units of LR."""
    t = int(t)
    return t * (t + 1) / (2 * W) if t <= W else (W + 1) / 2 + (t - W)


def load_mod(name: str):
    spec = importlib.util.spec_from_file_location(name, LAB / "EXP-020-data-switch" / "analyze.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def meta_ok(base, wu, s: int) -> str | None:
    """Fail-closed metadata checks: warmup flags, optimizer config, shared init checksum."""
    ref = None
    for mod, is_wu in ((base, False), (wu, True)):
        for t in mod.GRID:
            f = mod.run_dir(s, t) / "result.json"
            if not f.exists():
                return f"missing {f.parent.name}"
            r = json.loads(f.read_text(encoding="utf-8"))
            want_wu = W if (is_wu and t != 0) else 0
            if (r.get("warmup") or 0) != want_wu:
                return f"warmup flag {f.parent.name}"
            c = r["config"]
            key = (c.get("lr"), c.get("weight_decay"), c.get("beta1"), c.get("beta2"), r["init_checksum_shared"])
            if ref is None:
                ref = key
            elif key != ref:
                return f"config/init differs {f.parent.name}"
    return None


def d_h_curve(row: dict, s: int) -> dict | None:
    """Nachtrag b (secondary, reported only): harmonic-extended d_h (F/G side incl. fold(2k), shared ones excluded)."""
    if not row.get("K"):
        return None
    tg = json.loads((LAB / "EXP-020-data-switch" / f"splits/seed{s}.json").read_text(encoding="utf-8"))["targets"]
    fold = lambda k: min(k % 113, 113 - k % 113)  # noqa: E731
    fx = set(tg["F"]) | {fold(2 * k) for k in tg["F"]}
    gx = set(tg["G"]) | {fold(2 * k) for k in tg["G"]}
    fx, gx = fx - (fx & gx), gx - (fx & gx)
    return {str(t): len(set(K) & fx) - len(set(K) & gx) for t, K in row["K"].items()}


def main() -> None:
    base = load_mod("exp020_base")
    wu = load_mod("exp020_wu")
    wu.SWITCH = SWITCH_WU
    wu.GRID = (0.0, *map(float, SWITCH_WU), math.inf)
    orig = wu.run_dir
    wu.run_dir = lambda s, t: orig(s, t) if t == 0 else HERE / "raw" / (orig(s, t).name + f"_wu{W}")
    rows = []
    for s in wu.SEEDS:
        rb, rw = base.row(s), wu.row(s)
        r = {"seed": s, "base": {k: rb.get(k) for k in ("valid", "d", "lo", "hi", "monotone", "gen_F", "reason")},
             "wu": {k: rw.get(k) for k in ("valid", "d", "lo", "hi", "monotone", "gen_F", "reason")},
             "d_h_secondary": {"base": d_h_curve(rb, s), "wu": d_h_curve(rw, s)}}
        why = None
        if not (rb["valid"] and rw["valid"]):
            why = "invalid run set"
        else:
            why = meta_ok(base, wu, s)
        if why is None and not (rb["monotone"] and rw["monotone"]):
            why = "non-monotone d(t)"
        if why is None and not (rb["gen_F"] and rw["gen_F"] and rb["hi"] < rb["gen_F"] and rw["hi"] < rw["gen_F"]):
            why = "crossing not before generalization (or gen_F censored)"
        if why is None and rb["hi"] > 150:
            why = "baseline interval beyond warmup grid"
        if why is None:
            lo_b, hi_b, lo_w, hi_w = rb["lo"], rb["hi"], rw["lo"], rw["hi"]
            r["class"] = ("delayed" if lo_w >= hi_b else "same" if (lo_w, hi_w) == (lo_b, hi_b) else "unclear")
            r["lambda_interval_wu"] = [lam(lo_w), lam(hi_w) if hi_w != math.inf else None]
            r["lambda_interval_base"] = [lo_b, hi_b]
            r["displacement_at_switch"] = {str(t): json.loads((wu.run_dir(s, t) / "result.json").read_text())
                                           ["events"].get("displacement_at_switch") for t in SWITCH_WU}
            r["evaluable"] = True
        else:
            r["evaluable"], r["why"] = False, why
        rows.append(r)
    ev = [r for r in rows if r["evaluable"]]
    out = {"rows": rows, "n_evaluable": len(ev)}
    if len(ev) < 3:
        out["verdict"] = "nicht auswertbar"
    else:
        cls = [r["class"] for r in ev]
        out["classes"] = cls
        out["verdict"] = ("Festlegung hängt am Lernratenplan: Warmup verzögert (H35-Richtung)" if all(c == "delayed" for c in cls)
                          else "Festlegung folgt der Schrittzahl" if all(c == "same" for c in cls) else "unklar")
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
