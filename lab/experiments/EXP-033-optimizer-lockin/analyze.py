"""EXP-033 analysis (pre-registered, README Nachtrag a): seed-level, baseline-adjusted GD vs AdamW-reset at level t_s = 10."""
from __future__ import annotations

import json
import sys
from math import comb
from pathlib import Path

import importlib.util

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[0]
_spec = importlib.util.spec_from_file_location("exp026_analyze", LAB / "EXP-026-parity-crossover" / "analyze.py")
_a26 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_a26)
fold, share_diff = _a26.fold, _a26.share_diff

SEEDS = tuple(range(10, 20))
TOL = 0.02


def ds(r: dict, key: str) -> float:
    T = set(r["targets"]); H = {fold(57 * t) for t in T}
    return share_diff(r["spectra"][key]["weighted"], T, H)


def load(f: Path) -> dict | None:
    return json.loads(f.read_text()) if f.exists() else None


def sigma_ok(r: dict | None, s: int, ts: int, alpha: float) -> bool:
    if r is None:
        return False
    a = r["args"]
    return bool(r.get("complete") and a["steps"] == 5000 and a["alpha"] == alpha and a["switch_step"] == ts
                and a["alpha_after"] == 0.0 and a["seed"] == s and a["arm"] == "F" and a.get("width", 512) == 512
                and a.get("init_seed") is None and r["final_test_acc"] >= 0.9)


def anchor(s: int) -> dict | None:   # pure x^2 from init, 5000 steps AdamW (EXP-026 for 10-14, EXP-027b for 15-19)
    for f in (LAB / "EXP-026-parity-crossover" / "raw" / f"EXP-026_a3_sw0to0_seed{s}_F" / "result.json",
              LAB / "EXP-027-width-selection" / "raw_b" / f"EXP-026_a0_seed{s}_F" / "result.json"):
        r = load(f)
        if r is not None and (sigma_ok(r, s, 0, 3.0) or sigma_ok(r, s, -1, 0.0)):
            return r
    return None


def retained(s: int) -> dict | None:
    for f in (LAB / "EXP-032-early-lockin" / "raw" / f"EXP-026_a3_sw10to0_seed{s}_F" / "result.json",
              HERE / "raw" / f"EXP-026_a3_sw10to0_seed{s}_F" / "result.json"):
        r = load(f)
        if sigma_ok(r, s, 10, 3.0):
            return r
    return None


def boot_ratio(x: np.ndarray, y: np.ndarray, n: int = 10_000) -> tuple[float, float]:
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(x), (n, len(x)))
    num, den = x[idx].mean(1), y[idx].mean(1)
    rat = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)
    return float(np.nanpercentile(rat, 2.5)), float(np.nanpercentile(rat, 97.5))


def main() -> None:
    lr = json.loads((HERE / "lr.json").read_text())["lr"]
    units, valid = [], True
    for s in SEEDS:
        ar = load(HERE / "raw" / f"EXP-033_adamw_t10_seed{s}" / "result.json")
        a0 = anchor(s)
        u = {"seed": s, "ok": True}
        if not (ar and ar["complete"] and ar["final_test_acc"] >= 0.9 and a0):
            u["ok"] = False
            units.append(u); valid = False
            continue
        rt = ar["r_switch"]
        u.update(ds0=ds(a0, "5000"), ds_ar=ds(ar, "p2_5000"), dsw_ar=ds(ar, "switch"), wout_ar=ar["wout_norm_switch"],
                 rq_ar=ar["r_quantiles_switch"], gen_ar=ar["gen_step_test95"], r_target=rt)
        for opt, rid in (("gd", f"EXP-033_gd_r{rt:g}_lr{lr:g}_seed{s}"), ("sign", f"EXP-033_sign_r{rt:g}_seed{s}")):
            r = load(HERE / "raw" / rid / "result.json")
            ok = bool(r and r["complete"] and r["final_test_acc"] >= 0.9 and abs(r["r_switch"] / rt - 1) <= TOL)
            u[opt] = {"ok": ok, "reached": r and r["reached"]}
            if r and r["complete"]:
                u[opt].update(ds=ds(r, "p2_5000"), dsw=ds(r, "switch"), steps1=r["phase1_steps"], wout=r["wout_norm_switch"],
                              rq=r["r_quantiles_switch"], gen=r["gen_step_test95"], test=r["final_test_acc"],
                              overshoot=r["r_switch"] / rt - 1)
        if not u["gd"]["ok"]:
            valid = False
        rr = retained(s)
        u["ds_retained"] = ds(rr, "5000") if rr else None
        units.append(u)
    out = {"lr": lr, "units": units}
    ok = [u for u in units if u["ok"] and u["gd"]["ok"]]
    if not valid or len(ok) != 10:
        out["verdict"] = "nicht auswertbar"
    else:
        d_gd = np.array([u["gd"]["ds"] - u["ds0"] for u in ok])
        d_ar = np.array([u["ds_ar"] - u["ds0"] for u in ok])
        k_ar, k = int((d_ar > 0).sum()), int((d_gd > 0).sum())
        p = sum(comb(10, i) for i in range(k, 11)) / 2 ** 10
        lo, hi = boot_ratio(d_gd, d_ar)
        R = float(d_gd.mean() / d_ar.mean()) if d_ar.mean() > 0 else None
        if k_ar < 9:
            verdict = "nicht auswertbar (Kontrolle AdamW-reset repliziert die Festlegung nicht)"
        elif k < 9:
            verdict = "AdamW-gebunden" if hi < 0.5 else "unklar"
        elif 0.5 <= lo and hi <= 2:
            verdict = "zustandsbestimmt"
        elif lo > 2:
            verdict = "GD stärker"
        elif hi < 0.5:
            verdict = "AdamW verstärkt, Festlegung schwach vorhanden"
        else:
            verdict = "GD-Neigung vorhanden, Größenverhältnis offen"
        out.update(k_gd_pos=k, p_sign=p, k_ar_pos=k_ar, R=R, R_ci95=[lo, hi], mean_d_gd=float(d_gd.mean()),
                   mean_d_ar=float(d_ar.mean()), verdict=verdict)
        sg = [u for u in ok if u["sign"]["ok"]]
        out["secondary"] = {
            "n_sign_ok": len(sg), "mean_d_sign": float(np.mean([u["sign"]["ds"] - u["ds0"] for u in sg])) if sg else None,
            "mean_dsw": {m: float(np.mean(v)) for m, v in (("ar", [u["dsw_ar"] for u in ok]), ("gd", [u["gd"]["dsw"] for u in ok]),
                                                          ("sign", [u["sign"]["dsw"] for u in sg]))} if sg else None,
            "gd_steps1_mean": float(np.mean([u["gd"]["steps1"] for u in ok])),
            "wout_switch_mean": {"ar": float(np.mean([u["wout_ar"] for u in ok])), "gd": float(np.mean([u["gd"]["wout"] for u in ok]))},
            "retained_minus_reset_mean": float(np.mean([u["ds_retained"] - u["ds_ar"] for u in ok if u["ds_retained"] is not None])),
        }
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1))


if __name__ == "__main__":
    main()
