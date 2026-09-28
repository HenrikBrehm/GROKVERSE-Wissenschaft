"""EXP-103 (session 44, exploration): dense early Delta_pow curve of the P1 preset (add 113, seeds 1000-1049, 250 steps,
spectra at 10, 25, 50, ..., 250) to test the one open point of the R1 post hoc (lab/confirm/R1_posthoc_lrwd_time_s44.py):
is the misfit at tau < 250 an artefact of interpolating the preset curve linearly between step 0 and 250?

Readings, fixed before any run (session 44):
  check      the step-250 Delta_pow of every seed must equal the stored P1 value at step 250 within 1e-4 (same trainer,
             seed, split and device); otherwise "not comparable" and nothing else is read.
  artefact   the four early R1 points (wd 0.3 at t = 250, 500, 750; lr 5e-4 at t = 250; tau = 75, 150, 225, 125) all lie
             within |log(cell / P1_dense(tau))| < 0.10 -> "early misfit was interpolation; time rescaling in lr*wd holds
             from tau = 75 on".
  real       two or more of them outside 0.20 -> "early steering does not tick in lr*wd" (e.g. weight decay has not acted
             yet; then compare with tau = sum lr, i.e. t * lr / 1e-3).
  (else)     "unclear".
Cell means come from lab/confirm/R1_posthoc_lrwd_time_s44.json (seen data).

  python lab/tools/parallel_queue.py lab/experiments/EXP-103-early-steering-curve/jobs.txt --workers 4
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-103-early-steering-curve/analyze.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
EARLY = [("wd0.3", 250), ("wd0.3", 500), ("wd0.3", 750), ("lr5e-4", 250)]


def delta(pF, pG, F, G):
    s = lambda pw, S: pw[..., [k - 1 for k in S]].sum(-1)   # noqa: E731
    return np.log(s(pF, F) / s(pF, G)) + np.log(s(pG, G) / s(pG, F))


def run(root: Path, s: int, a: str) -> Path:
    hits = sorted(root.glob(f"EXP-016_baseline_seed{s}_thr1_confirm_exp1_eps2.0_add113_seed{s}_{a}_devcuda"))
    assert len(hits) == 1, (root, s, a)
    r = json.loads((hits[0] / "result.json").read_text(encoding="utf-8"))
    assert r["status"] == "completed", hits[0]
    return hits[0]


def main() -> None:
    curves, mism = [], []
    for s in range(1000, 1050):
        T = {a: json.loads((LAB / f"confirm/splits/confirm_exp1_eps2.0_add113_seed{s}_{a}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
        dF, dG = run(HERE / "raw", s, "F"), run(HERE / "raw", s, "G")
        st = np.load(dF / "spectra_steps.npy")
        assert np.array_equal(st, np.load(dG / "spectra_steps.npy"))
        d = delta(np.load(dF / "spectra.npy"), np.load(dG / "spectra.npy"), T["F"], T["G"])
        oF, oG = run(LAB / "confirm/raw", s, "F"), run(LAB / "confirm/raw", s, "G")
        ost = list(np.load(oF / "spectra_steps.npy"))
        old = delta(np.load(oF / "spectra.npy")[ost.index(250)], np.load(oG / "spectra.npy")[ost.index(250)], T["F"], T["G"])
        if abs(d[list(st).index(250)] - old) > 1e-4:
            mism.append([s, float(d[list(st).index(250)]), float(old)])
        curves.append(d)
    out: dict = {"steps": st.tolist(), "n_mismatch_250": len(mism), "mismatch": mism}
    if mism:
        out["reading"] = "not comparable"
    else:
        mean = np.mean(curves, 0)
        out["curve"] = mean.round(4).tolist()
        r1 = json.loads((LAB / "confirm/R1_posthoc_lrwd_time_s44.json").read_text(encoding="utf-8"))["cells"]
        pts = []
        for cell, t in EARLY:
            row = next(r for r in r1[cell] if r["t"] == t)
            ref = float(np.interp(row["tau"], st, mean))
            pts.append({"cell": cell, "t": t, "tau": row["tau"], "cell_mean": row["cell_mean"], "P1_dense": ref,
                        "abs_log_ratio": abs(float(np.log(row["cell_mean"] / ref)))})
        out["points"] = pts
        e = [p["abs_log_ratio"] for p in pts]
        out["reading"] = ("artefact" if all(x < 0.10 for x in e) else "real" if sum(x > 0.20 for x in e) >= 2 else "unclear")
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "mismatch"}, indent=1))


if __name__ == "__main__":
    main()
