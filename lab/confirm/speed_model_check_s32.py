"""Session 32 (2026-09-27, window closed), POST HOC check on SEEN runs, no training.

Question: does the M_share model fixed in EXP-084/prediction_s32.py (b = T_inf + A / (s - s0), calibrated on the eps-2 / eps-8
medians of EXP-020/042 and the EXP-003d random median) reproduce the stored groups that did NOT enter the fit?
Stated before looking at the comparison: "reproduces" = the observed median log2(b_obs / b_pred) of each generalising group lies
within +-0.35 (about one factor 1.27), and groups predicted to be censored within their horizon are mostly (>= 80 %) censored.
s = M0 power share on the run's own 5 targets, recomputed from the split .npy with confirm_splits.m0 for every group (also the
calibration runs, to check that the docstring shares 0.18 / 0.36 are right).
  python lab/confirm/speed_model_check_s32.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
import confirm_splits as cs  # noqa: E402

pred = json.loads((LAB / "experiments/EXP-084-dose-curve/prediction_s32.json").read_text(encoding="utf-8"))["m_share_params"]
T_INF, A, S0 = pred["T_inf"], pred["A"], pred["s0"]


def b_pred(s: float) -> float:
    return math.inf if s <= S0 else T_INF + A / (s - S0)


def targets_for(split_file: Path) -> list[int]:
    name = split_file.stem
    meta_single = split_file.with_suffix(".json")
    if meta_single.exists():                                   # EXP-016 / EXP-047: one json per split
        return json.loads(meta_single.read_text(encoding="utf-8"))["targets"]
    seed_json = split_file.parent / f"{name.split('_')[0]}.json"
    d = json.loads(seed_json.read_text(encoding="utf-8"))
    t = d["targets"]
    if isinstance(t, dict):                                    # EXP-020/042: {"F": [...], "G": [...]}
        return t[name.split("_")[-1]]
    return t                                                   # EXP-018: one target set per seed (E arm; R uses it too)


def row(run: Path) -> dict:
    r = json.loads((run / "result.json").read_text(encoding="utf-8"))
    sf = ROOT / r["split_file"]
    s = float((lambda pw, tg: pw[[k - 1 for k in tg]].sum() / pw.sum())(cs.m0(np.load(sf), "add", 113), targets_for(sf)))
    return {"run": run.name, "s": s, "gen": (r.get("events") or {}).get("generalization_step"), "horizon": r["steps_completed"],
            "device": r["config"].get("device", "cpu")}


GROUPS = {
    "calib eps2 (EXP-020 G)": [LAB / f"experiments/EXP-020-data-switch/raw/EXP-018_baseline_seed{s}_thr4_seed{s}_train_G" for s in (30, 31, 32, 34)],
    "calib eps8 (EXP-042 G)": [LAB / f"experiments/EXP-042-bias-strength/eps8/raw/EXP-018_baseline_seed{s}_thr4_seed{s}_train_G" for s in (30, 31, 32, 34)],
    "seen eps1 (EXP-042 G)": [LAB / f"experiments/EXP-042-bias-strength/eps1/raw/EXP-018_baseline_seed{s}_thr4_seed{s}_train_G" for s in (30, 31, 32, 34)],
    "EXP-016 eng (CPU)": sorted((LAB / "experiments/EXP-016-engineered-split/raw").glob("EXP-016_*")),
    "EXP-047 eng (GPU)": sorted((LAB / "experiments/EXP-047-marginal-control/raw").glob("*_eng_[FG]_devcuda")),
    "EXP-047 shuf (GPU)": sorted((LAB / "experiments/EXP-047-marginal-control/raw").glob("*_shuf_[FG]_devcuda")),
    "EXP-041 E (CPU, common test)": sorted(LAB.glob("experiments/EXP-041*/raw/EXP-018_baseline_seed*_thr4_seed*_train_E")),
    "EXP-041 R (CPU, common test)": sorted(LAB.glob("experiments/EXP-041*/raw/EXP-018_baseline_seed*_thr4_seed*_train_R")),
    "P1 F/G (GPU)": sorted((LAB / "confirm/raw").glob("EXP-016_*add113_seed*_[FG]_devcuda")),
}


def main() -> None:
    out = {"note": "post hoc on seen runs; model parameters frozen in prediction_s32.json (commit 6d0231f) before this check",
           "params": pred, "groups": {}}
    for name, runs in GROUPS.items():
        rows = [row(d) for d in runs if (d / "result.json").exists()]
        s = np.array([x["s"] for x in rows])
        obs = [x for x in rows if x["gen"] is not None]
        pc = [x for x in rows if b_pred(x["s"]) > x["horizon"]]          # predicted censored within the horizon
        g = {"n": len(rows), "s_median": float(np.median(s)), "s_range": [float(s.min()), float(s.max())],
             "n_generalised": len(obs), "horizon": max(x["horizon"] for x in rows),
             "b_pred_at_median_s": b_pred(float(np.median(s)))}
        if obs:
            lr = np.array([math.log2(x["gen"] / b_pred(x["s"])) for x in obs if math.isfinite(b_pred(x["s"]))])
            g.update({"b_obs_median": float(np.median([x["gen"] for x in obs])),
                      "median_log2_obs_over_pred": float(np.median(lr)) if len(lr) else None,
                      "within_0.35": bool(len(lr) and abs(np.median(lr)) <= 0.35)})
        if pc:
            g["pred_censored"] = len(pc)
            g["pred_censored_and_censored"] = sum(1 for x in pc if x["gen"] is None)
        out["groups"][name] = g
        print(name, json.dumps(g))
    (LAB / "confirm/speed_model_check_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
