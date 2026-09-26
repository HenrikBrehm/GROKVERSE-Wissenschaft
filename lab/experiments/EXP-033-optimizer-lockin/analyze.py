"""EXP-033 analysis (pre-registered in README.md): GD vs AdamW phase 1 at matched feature amplitude."""
from __future__ import annotations

import json
import sys
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
E26 = HERE.parents[0] / "EXP-026-parity-crossover"
sys.path.insert(0, str(E26))
from analyze import fold, share_diff  # noqa: E402

LEVELS = (5, 10, 20)
SEEDS = (10, 11, 12, 13, 14)


def ds_of(r: dict, key: str) -> float:
    T = set(r["targets"]); H = {fold(57 * t) for t in T}
    return share_diff(r["spectra"][key]["weighted"], T, H)


def main(lr: float) -> None:
    e32 = {(x["ts"], x["seed"]): x for x in json.loads((HERE.parents[0] / "EXP-032-early-lockin" / "summary.json").read_text())["rows"]}
    units, bad = [], []
    for ts in LEVELS:
        for s in SEEDS:
            ar = HERE / "raw" / f"EXP-033_adamw_t{ts}_seed{s}" / "result.json"
            rt = e32[(ts, s)]["r_at_switch"]["median"]
            gd = HERE / "raw" / f"EXP-033_gd_r{rt:g}_lr{lr:g}_seed{s}" / "result.json"
            u = {"ts": ts, "seed": s, "ds0": e32[(0, s)]["ds"], "ds32": e32[(ts, s)]["ds"]}
            for name, f in (("ar", ar), ("gd", gd)):
                if not f.exists():
                    u[name] = None
                    continue
                r = json.loads(f.read_text())
                ok = r["complete"] and r["final_test_acc"] is not None and r["final_test_acc"] >= 0.9
                u[name] = {"ok": ok, "complete": r["complete"], "test": r["final_test_acc"], "gen95": r["gen_step_test95"],
                           "phase1_steps": r["phase1_steps"], "r_switch": r["r_switch"], "wout_switch": r["wout_norm_switch"],
                           "ds": ds_of(r, "p2_5000") if r["complete"] else None, "ds_switch": ds_of(r, "switch")}
            units.append(u)
    out = {"lr": lr, "units": units}
    gd_ok = [u for u in units if u["gd"] and u["gd"]["ok"]]
    finals_ok = all(u[n]["test"] >= 0.9 for u in units for n in ("ar", "gd") if u[n] and u[n]["complete"])
    ar_ok = all(u["ar"] and u["ar"]["ok"] for u in units)
    if len(gd_ok) < 12 or not ar_ok or not finals_ok:
        out["verdict"] = "nicht auswertbar"
    else:
        k = sum(u["gd"]["ds"] > u["ds0"] for u in gd_ok)
        n = len(gd_ok)
        p = sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n
        q = float(np.mean([u["gd"]["ds"] for u in gd_ok]) / np.mean([u["ar"]["ds"] for u in gd_ok]))
        p33a = k >= 13 if n == 15 else k >= n - 2 and p < 0.05
        verdict = ("AdamW-gebunden" if not p33a else "zustandsbestimmt" if 0.5 <= q <= 2
                   else "GD stärker" if q > 2 else "AdamW verstärkt, Festlegung schwach vorhanden")
        out.update(n_gd_valid=n, k_above_anchor=k, p_sign=p, Q=q, verdict=verdict)
        for lv in LEVELS:
            sel = [u for u in gd_ok if u["ts"] == lv]
            out[f"level{lv}"] = {m: float(np.mean([f(u) for u in sel])) for m, f in (
                ("ds_gd", lambda u: u["gd"]["ds"]), ("ds_ar", lambda u: u["ar"]["ds"]), ("ds32", lambda u: u["ds32"]),
                ("ds_switch_gd", lambda u: u["gd"]["ds_switch"]), ("ds_switch_ar", lambda u: u["ar"]["ds_switch"]),
                ("gd_phase1_steps", lambda u: u["gd"]["phase1_steps"]), ("wout_gd", lambda u: u["gd"]["wout_switch"]),
                ("wout_ar", lambda u: u["ar"]["wout_switch"]))}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1))


if __name__ == "__main__":
    main(float(sys.argv[1]))
