"""EXP-035 analysis (pre-registered, README): EXP-020 protocol with lr warmup 200; compares the warmup commitment interval
with the no-warmup EXP-020 interval of the same seed. Reuses EXP-020/analyze.py (validity checks, K, d, interval)."""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[0]
W, LR = 200, 1e-3
SWITCH_WU = (25, 50, 100, 150, 250)


def lam(t: float) -> float:
    """Accumulated learning rate after t steps with linear warmup (lr_t = LR * min(1, t / W), t = 1..)."""
    t = int(t)
    return LR * (t * (t + 1) / (2 * W) if t <= W else (W + 1) / 2 + (t - W))


def load_mod(name: str):
    spec = importlib.util.spec_from_file_location(name, LAB / "EXP-020-data-switch" / "analyze.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> None:
    base = load_mod("exp020_base")
    wu = load_mod("exp020_wu")
    wu.SWITCH = SWITCH_WU
    wu.GRID = (0.0, *map(float, SWITCH_WU), math.inf)
    orig = wu.run_dir
    wu.run_dir = lambda s, t: HERE / "raw" / (orig(s, t).name + f"_wu{W}")
    rows = []
    for s in wu.SEEDS:
        rb, rw = base.row(s), wu.row(s)
        r = {"seed": s, "base": {k: rb.get(k) for k in ("valid", "d", "lo", "hi", "monotone", "reason")},
             "wu": {k: rw.get(k) for k in ("valid", "d", "lo", "hi", "monotone", "reason", "gen_F")}}
        if rb["valid"] and rw["valid"] and rb["hi"] <= 150:
            lo_b, hi_b = rb["lo"], rb["hi"]
            r["delayed"] = rw["hi"] > hi_b
            # H35 prediction: warmup interval in steps where the accumulated lr equals LR * (lo_b, hi_b]
            r["pred_first_positive_ge"] = next(t for t in range(1, 10_000) if lam(t) >= LR * hi_b)
            r["lambda_interval_wu"] = [lam(rw["lo"]) / LR if rw["lo"] != math.inf else None,
                                       lam(rw["hi"]) / LR if rw["hi"] != math.inf else None]
            r["evaluable"] = True
        else:
            r["evaluable"] = False
        rows.append(r)
    ev = [r for r in rows if r["evaluable"]]
    out = {"rows": rows, "n_evaluable": len(ev)}
    if len(ev) < 3:
        out["verdict"] = "nicht auswertbar"
    else:
        k = sum(r["delayed"] for r in ev)
        out["n_delayed"] = k
        out["verdict"] = ("Festlegung folgt der Parameterstrecke (H35 gestützt)" if k == len(ev)
                          else "Festlegung folgt der Schrittzahl" if k == 0 else "unklar")
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
