"""EXP-034 analysis (pre-registered, README): part A (level 5, AdamW phase 2) and part B (GD phase 2), fresh splits 60-69."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[0]
_spec = importlib.util.spec_from_file_location("exp026_analyze", LAB / "EXP-026-parity-crossover" / "analyze.py")
_a26 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_a26)
fold, share_diff = _a26.fold, _a26.share_diff
SEEDS = tuple(range(60, 70))
TOL = 0.02


def load(rid: str) -> dict | None:
    f = HERE / "raw" / rid / "result.json"
    return json.loads(f.read_text()) if f.exists() else None


def ds(r: dict, key: str) -> float:
    T = set(r["targets"]); H = {fold(57 * t) for t in T}
    return share_diff(r["spectra"][key]["weighted"], T, H)


def good(r: dict | None) -> bool:
    return bool(r and r["complete"] and r["final_test_acc"] is not None and r["final_test_acc"] >= 0.9)


def part(t_ar: int, suffix: str, end: str) -> dict:
    units, n_bad = [], 0
    for s in SEEDS:
        an, ar = load(f"EXP-033_adamw_t0_seed{s}{suffix}"), load(f"EXP-033_adamw_t{t_ar}_seed{s}{suffix}")
        gd = load(f"EXP-033_gd_r{ar['r_switch']:g}_lr3_seed{s}_bt{suffix}") if ar else None
        ok = good(an) and good(ar) and good(gd) and abs(gd["r_switch"] / ar["r_switch"] - 1) <= TOL
        u = {"seed": s, "ok": ok, "tests": [r and r["final_test_acc"] for r in (an, ar, gd)]}
        if ok:
            d0 = ds(an, end)
            u.update(ds0=d0, d_ar=ds(ar, end) - d0, d_gd=ds(gd, end) - d0, dsw_ar=ds(ar, "switch"), dsw_gd=ds(gd, "switch"),
                     gen=[an["gen_step_test95"], ar["gen_step_test95"], gd["gen_step_test95"]])
        else:
            n_bad += 1
        units.append(u)
    ok = [u for u in units if u["ok"]]
    out = {"units": units, "n_valid": len(ok)}
    if ok:
        out.update(k_ar=int(sum(u["d_ar"] > 0 for u in ok)), k_gd=int(sum(u["d_gd"] > 0 for u in ok)),
                   mean_d_ar=float(np.mean([u["d_ar"] for u in ok])), mean_d_gd=float(np.mean([u["d_gd"] for u in ok])),
                   dsw_gd_gt_ar=int(sum(u["dsw_gd"] > u["dsw_ar"] for u in ok)))
    return out


def boot_ratio(x: np.ndarray, y: np.ndarray, n: int = 10_000) -> list[float]:
    rng = np.random.default_rng(0)
    idx = rng.integers(0, len(x), (n, len(x)))
    num, den = x[idx].mean(1), y[idx].mean(1)
    rat = np.where(den > 0, num / np.where(den > 0, den, 1), np.nan)
    return [float(np.nanpercentile(rat, 2.5)), float(np.nanpercentile(rat, 97.5))]


def main() -> None:
    res = {}
    A5, A10 = part(5, "", "p2_5000"), part(10, "", "p2_5000")
    for A, lv in ((A5, 5), (A10, 10)):
        if A["n_valid"] < 10:
            A["verdict"] = "nicht auswertbar (unvollständig oder ungültig)"
        elif A["k_ar"] < 9:
            A["verdict"] = f"nicht auswertbar (Tor: AR{lv} repliziert EXP-032/033 nicht)"
        elif lv == 5:
            A["verdict"] = ("Festlegung bei 1.25 × Init ohne AdamW in Phase 1" if A["k_gd"] >= 9
                            else "bei der 5-Schritte-Stufe nicht ohne AdamW gezeigt")
        else:
            A["verdict"] = "EXP-033 an frischen Splits bestätigt" if A["k_gd"] >= 9 else "EXP-033 an frischen Splits nicht bestätigt"
    res["A5"], res["A10"] = A5, A10
    f2 = HERE / "lr2.json"
    lr2 = json.loads(f2.read_text())["lr2"] if f2.exists() else None
    if lr2 is None:
        res["B"] = {"verdict": "nicht durchführbar (keine zulässige lr2)" if f2.exists() else "noch nicht gelaufen"}
    else:
        B = part(10, f"_p2gd{lr2:g}_n10000", "p2_10000")
        B["lr2"] = lr2
        gate = A10.get("n_valid") == 10 and A10.get("k_ar", 0) >= 9 and A10.get("k_gd", 0) >= 9
        if B["n_valid"] < 10:
            B["verdict"] = "nicht auswertbar (unvollständig oder ungültig)"
        elif not gate:
            B["verdict"] = "nicht auswertbar (Tor: Stufe 10 mit AdamW-Phase-2 nicht repliziert)"
        else:
            ci = {}
            for arm in ("ar", "gd"):
                x = np.array([u[f"d_{arm}"] for u in B["units"]]); y = np.array([u[f"d_{arm}"] for u in A10["units"]])
                ci[arm] = boot_ratio(x, y)
            B["R2_ci95"] = ci
            if B["k_ar"] >= 9 and B["k_gd"] >= 9:
                B["verdict"] = "Erhalt ohne AdamW"
            elif any(ci[a][1] < 0.5 for a in ci):
                B["verdict"] = "Erhalt unter GD-Phase-2 deutlich schwächer (" + ", ".join(a for a in ci if ci[a][1] < 0.5) + ")"
            else:
                B["verdict"] = "unklar"
        res["B"] = B
    (HERE / "summary.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps({p: {k: v for k, v in d.items() if k != "units"} for p, d in res.items()}, indent=1))


if __name__ == "__main__":
    main()
