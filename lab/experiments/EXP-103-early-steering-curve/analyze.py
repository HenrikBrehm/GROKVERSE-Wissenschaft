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
  secondary  (session 44, after the independent recomputation, before any run) the same four points against the dense
             curve read at the summed learning rate only, tau_lr = t * lr / 1e-3 (two-phase alternative: an early,
             wd-independent alignment driven by Adam's lr-sized steps, then an lr*wd drift). Reported as
             abs_log_ratio_lr; descriptive, it does not change the reading above.
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
LR = {"wd0.3": 1.0, "lr5e-4": 0.5}                      # lr relative to the preset (tau_lr = t * LR)


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
            ref_lr = float(np.interp(t * LR[cell], st, mean)) if t * LR[cell] <= st[-1] else None
            pts.append({"cell": cell, "t": t, "tau": row["tau"], "cell_mean": row["cell_mean"], "P1_dense": ref,
                        "abs_log_ratio": abs(float(np.log(row["cell_mean"] / ref))),
                        "abs_log_ratio_lr": None if ref_lr is None else abs(float(np.log(row["cell_mean"] / ref_lr)))})
        out["points"] = pts
        e = [p["abs_log_ratio"] for p in pts]
        out["reading"] = ("artefact" if all(x < 0.10 for x in e) else "real" if sum(x > 0.20 for x in e) >= 2 else "unclear")
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "mismatch"}, indent=1))


CROSS = ("x_lr2e-3_wd0.5", "x_lr5e-4_wd2")                  # part B: lr*wd equal to the preset, lr and wd changed


def cross() -> dict:
    """Part B (session 44, fixed before any run): seeds 1000-1009, the P1 splits and inits, 2000 steps, lr*wd = 1e-3 as
    the preset but lr x2 / wd x0.5 and lr x0.5 / wd x2. Paired with the stored P1 runs of the same seed.
    Reading per cell on the seed-mean curves at t = 250..2000: m = mean_t |log(mean_X(t) / mean_P1(t))|;
      "product form holds"  m < 0.10 in both cells;
      "not only the product" m > 0.20 in at least one cell (then lr and wd act separately; direction reported);
      else "unclear". Also the paired per-seed log ratio at t = 2000 with a bootstrap 95 % CI (descriptive)."""
    out, rng = {}, np.random.default_rng(103)
    for c in CROSS:
        X, Pp = [], []
        for s in range(1000, 1010):
            T = {a: json.loads((LAB / f"confirm/splits/confirm_exp1_eps2.0_add113_seed{s}_{a}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
            for root, acc, pat in ((HERE / f"raw_{c}", X, "*"), (LAB / "confirm/raw", Pp, "devcuda")):
                dd = {}
                for a in "FG":
                    hits = sorted(root.glob(f"EXP-016_baseline_seed{s}_thr1_confirm_exp1_eps2.0_add113_seed{s}_{a}_{pat}"))
                    assert len(hits) == 1, (root, s, a, hits)
                    r = json.loads((hits[0] / "result.json").read_text(encoding="utf-8"))
                    assert r["status"] == "completed" and r["steps_completed"] == 2000, hits[0]
                    dd[a] = (np.load(hits[0] / "spectra_steps.npy"), np.load(hits[0] / "spectra.npy"))
                assert np.array_equal(dd["F"][0], dd["G"][0])
                acc.append(delta(dd["F"][1], dd["G"][1], T["F"], T["G"]))
                st = dd["F"][0]
        X, Pp = np.array(X), np.array(Pp)
        k = st > 0
        m = float(np.mean(np.abs(np.log(X[:, k].mean(0) / Pp[:, k].mean(0)))))
        lr2000 = np.log(X[:, -1] / Pp[:, -1])
        bs = rng.choice(lr2000, size=(10000, len(lr2000))).mean(1)
        out[c] = {"steps": st[k].tolist(), "mean_X": X[:, k].mean(0).round(3).tolist(), "mean_P1": Pp[:, k].mean(0).round(3).tolist(),
                  "mean_abs_log_ratio": m, "paired_log_ratio_2000": {"mean": float(lr2000.mean()),
                  "ci95": [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))]}}
    ms = [out[c]["mean_abs_log_ratio"] for c in CROSS]
    out["reading"] = ("product form holds" if all(x < 0.10 for x in ms) else
                      "not only the product" if any(x > 0.20 for x in ms) else "unclear")
    (HERE / "summary_cross.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    import sys
    cross() if sys.argv[1:] == ["--cross"] else main()
