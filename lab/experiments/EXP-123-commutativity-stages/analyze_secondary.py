"""EXP-123 secondary / sensitivity (session 55, written before the analysis was run; README "Klarstellungen" 1, 2 and 5).
Uses the frozen analyze.py loader and statistics unchanged. Reports: (a) conservative H1 (units with t_other observed but no t_swap
count as negative); units with t_swap > 7900; (b) H1 and H2 statistics at thresholds 0.3 and 0.7 instead of 0.5 (post hoc);
(c) per arm, the same statistics for D_0 against R and against E2_0 (descriptive).
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-123-commutativity-stages/analyze_secondary.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import analyze as A

HERE = Path(__file__).resolve().parent


def traces(u: int, arm: str) -> dict | None:
    f = HERE / "raw" / f"u{u}_{arm}" / "result.json"
    return json.loads(f.read_text(encoding="utf-8"))["trace"] if f.exists() else None


def times(t: dict, thr: float) -> tuple[int | None, int | None, float | None]:
    ts, to = A.first(t["step"], t["swap"], thr), A.first(t["step"], t["other"], thr)
    return ts, to, (t["other"][t["step"].index(ts)] if ts is not None else None)


def main() -> None:
    ok = {(r["unit"], r["arm"]) for r in (A.load(HERE / "raw", u, arm) for u in A.UNITS for arm in A.ARMS) if r["status"] == "ok"}
    out: dict = {}
    for thr in (0.3, 0.5, 0.7):
        res: dict = {}
        tr = {(u, arm): times(traces(u, arm), thr) for (u, arm) in ok}
        r_units = [u for u in A.UNITS if (u, "R") in ok]
        det = [u for u in r_units if tr[(u, "R")][0] is not None]
        pos = [u for u in det if tr[(u, "R")][1] is None or tr[(u, "R")][1] >= tr[(u, "R")][0] + A.MIN_GAP]
        neg_extra = [u for u in r_units if tr[(u, "R")][0] is None and tr[(u, "R")][1] is not None]
        late = [u for u in det if tr[(u, "R")][0] > 7900]
        res["H1"] = {"n_det": len(det), "pos": len(pos), "p": A.sign_test(len(pos), len(det)) if det else None,
                     "conservative": {"n": len(det) + len(neg_extra), "pos": len(pos),
                                      "p": A.sign_test(len(pos), len(det) + len(neg_extra)) if det or neg_extra else None},
                     "units_tother_without_tswap": neg_extra, "units_tswap_gt_7900": late}
        for a_arm, b_arm in (("E2_0", "R"), ("D_0", "R"), ("E2_0", "D_0")):
            us = [u for u in A.UNITS if (u, a_arm) in ok and (u, b_arm) in ok and tr[(u, a_arm)][2] is not None
                  and tr[(u, b_arm)][2] is not None]
            d = np.array([tr[(u, a_arm)][2] - tr[(u, b_arm)][2] for u in us])
            res[f"m_{a_arm}_minus_{b_arm}"] = {"n": len(d), "mean": float(d.mean()) if len(d) else None,
                                                "n_pos": int((d > 0).sum()), "p": A.perm_p(d) if len(d) else None}
        for arm in A.ARMS:
            ms = [tr[(u, arm)][2] for u in A.UNITS if (u, arm) in ok and tr[(u, arm)][2] is not None]
            res[f"median_m_{arm}"] = float(np.median(ms)) if ms else None
        out[str(thr)] = res
        print(thr, json.dumps(res), flush=True)
    (HERE / "summary_secondary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
