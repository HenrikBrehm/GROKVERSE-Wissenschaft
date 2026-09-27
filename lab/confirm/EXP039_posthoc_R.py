"""Post hoc (session 29, exploration on seen EXP-039 runs; no training).
Question: before EXP-040 runs, does the quantitative H40 (EXP-040 Nachtrag c) already hold at init scale 1?
H40 says the choice locks in when the F-target amplitude displacement reaches the init amplitude of the
competitors, i.e. R(t) = mean_k |c_k(t) - c_k(0)| / median_j |c_j(0)| ~ 0.5-2 at the upper end hi of the
lock-in interval (and R(lo) below it). Same formula as EXP-040 analyze.target_displacement, measured in the
only-F run of each EXP-039 cell (identical to the switch runs up to the switch).
Expectation written before computing: if H40 in its quantitative form holds, R(hi) in [0.5, 2] in most cells
and R(lo) < R(hi); cv(R_hi) < cv(Lambda_hi) over cells (Nachtrag b; here only c-cells, s = 1)."""
import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "experiments" / "EXP-001-freq-ban"))
from freq_ban import fourier_basis  # noqa: E402

E39 = LAB / "experiments" / "EXP-039-lr-clock"


def fdir(seed: int, c: float) -> Path:
    cs = "2" if c == 2.0 else "0.5"
    return E39 / "raw" / f"EXP-018_baseline_seed{seed}_thr4_seed{seed}_train_F_lrs{cs}"


def R_curve(seed: int, c: float) -> dict:
    d = fdir(seed, c)
    snaps, steps = np.load(d / "we_snapshots.npy"), np.load(d / "we_snapshot_steps.npy").tolist()
    p = snaps.shape[1]
    B = fourier_basis(p)
    tg = json.loads((LAB / "experiments" / "EXP-020-data-switch" / f"splits/seed{seed}.json").read_text(encoding="utf-8"))["targets"]["F"]
    co = [B.T @ w.astype(np.float64) for w in snaps]
    amp0 = [np.linalg.norm(co[0][2 * k - 1:2 * k + 1]) for k in range(1, (p - 1) // 2 + 1)]
    ref = float(np.median(amp0))
    return {int(st): float(np.mean([np.linalg.norm(co[i][2 * k - 1:2 * k + 1] - co[0][2 * k - 1:2 * k + 1]) for k in tg])) / ref
            for i, st in enumerate(steps)}


def main() -> None:
    rows = json.loads((E39 / "summary.json").read_text(encoding="utf-8"))["rows"]
    out = []
    for r in rows:
        if not (r.get("valid") and r.get("monotone") and r.get("complete")) or r["hi"] in (None, "inf") or r["hi"] == float("inf"):
            continue
        Rc = R_curve(r["seed"], r["c"])
        lo, hi = int(r["lo"]), int(r["hi"])
        out.append({"seed": r["seed"], "c": r["c"], "lo": lo, "hi": hi, "lambda_hi": hi * r["c"],
                    "R_lo": round(Rc.get(lo, float("nan")), 3), "R_hi": round(Rc.get(hi, float("nan")), 3),
                    "R_curve": {k: round(v, 3) for k, v in Rc.items()}})
    lam = np.array([o["lambda_hi"] for o in out])
    rr = np.array([o["R_hi"] for o in out])
    cv = lambda x: float(np.std(x) / np.mean(x))  # noqa: E731
    res = {"cells": out, "n": len(out), "cv_lambda_hi": round(cv(lam), 3), "cv_R_hi": round(cv(rr), 3),
           "n_R_hi_in_0.5_2": int(sum(0.5 <= x <= 2 for x in rr)), "R_hi_median": round(float(np.median(rr)), 3)}
    (Path(__file__).with_suffix(".json")).write_text(json.dumps(res, indent=1), encoding="utf-8")
    for o in out:
        print(o["seed"], o["c"], (o["lo"], o["hi"]), "Lam_hi", o["lambda_hi"], "R_lo", o["R_lo"], "R_hi", o["R_hi"])
    print({k: v for k, v in res.items() if k != "cells"})


if __name__ == "__main__":
    main()
