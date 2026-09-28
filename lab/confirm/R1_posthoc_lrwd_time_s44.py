"""R1 post hoc (session 44, exploration on seen data; numpy only, reads stored spectra, trains nothing).

Question: R1 found Delta_pow at step 2000 smaller at lr 5e-4 / wd 0.3 and larger at lr 2e-3 / wd 3 than the preset (P1).
With decoupled weight decay the natural time is tau = t * lr * wd (Pracher et al. 2026, arXiv 2609.26679: grokking time
scale ~ lr * wd). Are the four lr/wd cells just the preset curve Delta_pow(t) read at a rescaled time?
Prediction (fixed before computing, this docstring committed first): per cell, the ratio Delta_cell(t) / Delta_P1(tau)
with tau = t * (lr * wd) / (1e-3 * 1), preset curve = mean over the 50 P1 add-113 seeds (1000-1049) interpolated linearly
in tau on its 250-step grid (Delta(0) = 0 exactly: F and G share the init), evaluated at the cell's stored steps with
tau <= 2000.
Readings: "time rescaling explains the size differences" if the mean |log ratio| over cells and points is < 0.10 AND at
most half of the same quantity with plain steps (tau = t); "no" if the tau version is not smaller than the step version;
otherwise "partial". Train-fraction cells are excluded (different data, not a time rescaling).
Caveats: seen data; different seeds and splits between R1 cells and P1 (same construction, eps 2.0); 250-step grid.

  python lab/confirm/R1_posthoc_lrwd_time_s44.py      (analysis of stored spectra only, like the other post hoc scripts)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
R1RAW, P1RAW = LAB / "confirm/r1_raw", LAB / "confirm/raw"
CELLS = {"lr5e-4": 0.5, "lr2e-3": 2.0, "wd0.3": 0.3, "wd3": 3.0}      # lr*wd relative to the preset
P1_SEEDS = range(1000, 1050)
BOOT = 10_000


def delta_pow(pF, pG, F, G):
    s = lambda pw, S: pw[..., [k - 1 for k in S]].sum(-1)   # noqa: E731
    return np.log(s(pF, F) / s(pF, G)) + np.log(s(pG, G) / s(pG, F))


def curve(dF: Path, dG: Path, F, G) -> tuple[np.ndarray, np.ndarray]:
    for d in (dF, dG):
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        assert r["status"] == "completed" and r["steps_completed"] == 2000, d
    sF, sG = np.load(dF / "spectra_steps.npy"), np.load(dG / "spectra_steps.npy")
    assert np.array_equal(sF, sG)
    return sF, delta_pow(np.load(dF / "spectra.npy"), np.load(dG / "spectra.npy"), F, G)


def one(root: Path, pattern: str) -> Path:
    hits = sorted(root.glob(pattern))
    assert len(hits) == 1, (pattern, hits)
    return hits[0]


def main() -> None:
    P = []
    for s in P1_SEEDS:
        T = {a: json.loads((LAB / f"confirm/splits/confirm_exp1_eps2.0_add113_seed{s}_{a}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
        steps, d = curve(one(P1RAW, f"EXP-016_baseline_seed{s}_thr1_confirm_exp1_eps2.0_add113_seed{s}_F_devcuda"),
                         one(P1RAW, f"EXP-016_baseline_seed{s}_thr1_confirm_exp1_eps2.0_add113_seed{s}_G_devcuda"), T["F"], T["G"])
        P.append(d)
    P = np.array(P)
    assert np.allclose(P[:, 0], 0)
    pre_steps, pre_mean = steps, P.mean(0)
    man = json.loads((LAB / "confirm/R1_manifest.json").read_text(encoding="utf-8"))
    out, err_tau, err_t = {"preset_curve": dict(zip(pre_steps.tolist(), pre_mean.round(3).tolist())), "cells": {}}, [], []
    rng = np.random.default_rng(44)
    for cell, c in CELLS.items():
        D = []
        for s in man["seeds"][cell]:
            T = json.loads((LAB / f"confirm/r1_splits/r1_{cell}_seed{s}_F.json").read_text(encoding="utf-8"))
            F, G = T["targets"], T["other_targets"]
            st, d = curve(one(R1RAW, f"EXP-016_baseline_seed{s}_thr1_r1_{cell}_seed{s}_F_*"),
                          one(R1RAW, f"EXP-016_baseline_seed{s}_thr1_r1_{cell}_seed{s}_G_*"), F, G)
            D.append(d)
        D = np.array(D)
        rows = []
        for i, t in enumerate(st):
            tau = t * c
            if t == 0 or tau > pre_steps[-1]:
                continue
            ref_tau, ref_t = np.interp(tau, pre_steps, pre_mean), np.interp(t, pre_steps, pre_mean)
            m = rng.choice(D[:, i], size=(BOOT, len(D))).mean(1)
            rows.append({"t": int(t), "tau": float(tau), "cell_mean": float(D[:, i].mean()),
                         "ci95": [float(np.quantile(m, .025)), float(np.quantile(m, .975))],
                         "P1_at_tau": float(ref_tau), "P1_at_t": float(ref_t),
                         "ratio_tau": float(D[:, i].mean() / ref_tau), "ratio_t": float(D[:, i].mean() / ref_t)})
            err_tau.append(abs(np.log(rows[-1]["ratio_tau"])))
            err_t.append(abs(np.log(rows[-1]["ratio_t"])))
        out["cells"][cell] = rows
    e_tau, e_t = float(np.mean(err_tau)), float(np.mean(err_t))
    out["mean_abs_log_ratio"] = {"tau": e_tau, "steps": e_t, "n_points": len(err_tau)}
    out["reading"] = ("time rescaling explains the size differences" if e_tau < 0.10 and e_tau <= 0.5 * e_t
                      else "no" if e_tau >= e_t else "partial")
    (LAB / "confirm/R1_posthoc_lrwd_time_s44.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for cell, rows in out["cells"].items():
        for r in rows:
            print(f"{cell:7s} t={r['t']:5d} tau={r['tau']:6.0f}  cell {r['cell_mean']:6.2f}  P1(tau) {r['P1_at_tau']:6.2f}"
                  f"  P1(t) {r['P1_at_t']:6.2f}  ratio_tau {r['ratio_tau']:.2f}  ratio_t {r['ratio_t']:.2f}")
    print(json.dumps({k: out[k] for k in ("mean_abs_log_ratio", "reading")}, indent=1))


if __name__ == "__main__":
    main()
