#!/usr/bin/env python3
"""Reproduction script for K4 / K4b (Section 3.3, Fig. 4 confirmed points): persistence index pi after a data switch and the effect
of zeroing Adam's first moment at the switch (N28, manifest fa154bd). Session 27, UNTESTED (needs the train.py equivalence check first).

From scratch: builds the N28 splits (EXP-053 overlap_split, omega = 0, calibrated eps), trains per seed pure A and pure B (2000 steps)
and the switch runs A->B, B->A for the arms normal@25, m@25, m@35, normal@50 (t + 2000 steps; "m" = --reset-optim-part m: exp_avg
zeroed at the switch, exp_avg_sq and step counters kept) with the lean trainer repro/train.py. From the final W_E power
(spectra.npy, last row; same definition as EXP-043 group_power):
  L = log[P(T_A) / P(T_B)],  pi(arm) = mean of (L_AB - L_B)/(L_A - L_B) and (L_BA - L_A)/(L_B - L_A)   (EXP-056 / P3 / N28 definition)
  seed valid only if L_A - L_B >= 2 (MIN_SEP of N28)
  H1: pi_normal(25) - pi_m(25) - 0.05 > 0          H2 (non-inferiority): pi_m(35) - pi_normal(25) + 0.05 > 0
Statistics as the frozen analysis (one-sided t-test, Holm with the P2b placeholder p = 1 as in N28, bootstrap 95 % CI; confirm_p1 helpers).
--compare-n28 compares the per-arm mean pi with lab/confirm/N28_summary.json (same seeds 2200-2229) and fails above --tol.

  python lab/tools/guarded_run.py -- python lab/paper/repro/k4b.py --smoke                  # 1 seed, 300 steps, CPU
  python lab/tools/guarded_run.py -- C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe lab/paper/repro/k4b.py --device cuda --workers 8 --compare-n28
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import k4c  # noqa: E402  (path setup, overlap_split, calibration, confirm_p1 helpers)

TRAINER_SHA = hashlib.sha256((HERE / "train.py").read_bytes()).hexdigest()[:10]   # s27 review: never reuse runs of another trainer version

LAB, BUDGET, MIN_SEP, H1_MIN, NI_MARGIN = k4c.LAB, 2000, 2.0, 0.05, 0.05
ARMS = (("normal", 25), ("m", 25), ("m", 35), ("normal", 50))   # frozen N28 arms


def cached(out: Path, s: int, steps: int, t: int | None, part: str | None) -> bool:
    f = out / "result.json"
    if not (f.exists() and (out / "spectra.npy").exists()):
        return False
    r = json.loads(f.read_text(encoding="utf-8"))
    return (r.get("seed"), r.get("steps"), r.get("switch_step"), r.get("reset_optim_part")) == (s, steps, t, part)


def run(a: argparse.Namespace, s: int, first: Path, second: Path | None, t: int | None, part: str | None, test: Path, out: Path) -> Path:
    steps = a.budget + (t or 0)
    if not cached(out, s, steps, t, "m" if part == "m" else None):   # s27 review: result.json stores null for normal arms
        cmd = [sys.executable, str(HERE / "train.py"), "--seed", str(s), "--split-file", str(first), "--test-file", str(test),
               "--steps", str(steps), "--device", a.device, "--threads", str(a.threads), "--out", str(out)]
        if second is not None:
            cmd += ["--switch-split-file", str(second), "--switch-step", str(t)]
            if part == "m":
                cmd += ["--reset-optim-part", "m"]
        subprocess.run(cmd, check=True)
    return out


def final_logratio(out: Path, TA: list[int], TB: list[int]) -> float:
    pw = np.load(out / "spectra.npy")[-1]
    return float(np.log(pw[[k - 1 for k in TA]].sum() / pw[[k - 1 for k in TB]].sum()))


def main() -> None:
    ap = argparse.ArgumentParser(description="K4/K4b reproduction (N28 construction)")
    ap.add_argument("--seeds", default="2200-2229")
    ap.add_argument("--budget", type=int, default=BUDGET)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default=str(HERE / "out" / "k4b"))
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--compare-n28", action="store_true")
    ap.add_argument("--tol", type=float, default=0.05, help="max |mean pi - N28 mean pi| per arm for --compare-n28")
    a = ap.parse_args()
    if a.compare_n28 and (a.smoke or not a.device.startswith("cuda") or a.budget != BUDGET):
        raise SystemExit("--compare-n28 needs the full budget on cuda (N28 ran on the GPU), not --smoke")
    lo, hi = (int(x) for x in a.seeds.split("-"))
    seeds = list(range(lo, hi + 1))
    if a.smoke:
        seeds, a.budget, a.out = seeds[:1], 300, str(Path(a.out).with_name(Path(a.out).name + "_smoke"))
    root = Path(a.out) / f"budget{a.budget}_{a.device.replace(':', '')}_thr{a.threads}_train{TRAINER_SHA}"
    (root / "splits").mkdir(parents=True, exist_ok=True)
    eps = json.loads(k4c.CAL.read_text(encoding="utf-8"))["levels"][str(k4c.OMEGA)]["eps"]
    jobs, targets = [], {}
    for s in seeds:
        TA, TB = k4c.ov.targets(s)
        d = k4c.ov.build(s, k4c.OMEGA, eps)
        files = {}
        for k in ("A", "B", "test"):
            f = root / "splits" / f"seed{s}_{k}.npy"
            if f.exists() and not np.array_equal(np.load(f), d[k].astype(np.int64)):
                raise SystemExit(f"{f} differs from the deterministic construction")
            np.save(f, d[k].astype(np.int64))
            files[k] = f
        targets[s] = (TA, TB)
        for k in ("A", "B"):
            jobs.append(((s, "pure", k), files[k], None, None, None, files["test"], root / "runs" / f"seed{s}_pure{k}"))
        for part, t in ARMS:
            for first, second, tag in (("A", "B", "AB"), ("B", "A", "BA")):
                jobs.append(((s, f"{part}{t}", tag), files[first], files[second], t, part, files["test"],
                             root / "runs" / f"seed{s}_{tag}_{part}{t}"))
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        outs = dict(zip([j[0] for j in jobs], ex.map(lambda j: run(a, j[0][0], j[1], j[2], j[3], j[4], j[5], j[6]), jobs)))
    rows = []
    for s in seeds:
        TA, TB = targets[s]
        L = {k: final_logratio(outs[(s, "pure", k)], TA, TB) for k in ("A", "B")}
        if not (np.isfinite(L["A"]) and np.isfinite(L["B"]) and L["A"] - L["B"] >= MIN_SEP):
            rows.append({"seed": s, "valid": False, "L": L})
            continue
        pi, bad = {}, None
        for part, t in ARMS:
            lab_, lba = (final_logratio(outs[(s, f"{part}{t}", tag)], TA, TB) for tag in ("AB", "BA"))
            if not (np.isfinite(lab_) and np.isfinite(lba)):   # as confirm_n28 (s27 review)
                bad = f"non-finite L in {part}{t}"
                break
            pi[f"{part}{t}"] = ((lab_ - L["B"]) / (L["A"] - L["B"]) + (lba - L["A"]) / (L["B"] - L["A"])) / 2
        rows.append({"seed": s, "valid": False, "reason": bad, "L": L} if bad else {"seed": s, "valid": True, "L": L, "pi": pi})
    ok = [r for r in rows if r["valid"]]
    out: dict = {"budget": a.budget, "device": a.device, "n": len(rows), "n_valid": len(ok),
                 "pi_mean": {f"{p}{t}": float(np.mean([r["pi"][f"{p}{t}"] for r in ok])) for p, t in ARMS} if ok else {}}
    X = {"H1": np.array([r["pi"]["normal25"] - r["pi"]["m25"] - H1_MIN for r in ok]),
         "H2": np.array([r["pi"]["m35"] - r["pi"]["normal25"] + NI_MARGIN for r in ok])}
    if len(ok) >= 3:
        tt = {k: k4c.c1.t_test_secondary(v) for k, v in X.items()}
        ph = k4c.c1.holm({**{k: v["p_one_sided"] for k, v in tt.items()}, "_P2b": 1.0})
        rng = np.random.default_rng(28)
        for k, v in X.items():
            out[k] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)), "p_holm": ph[k], "ci95": k4c.c1.boot_ci(v, rng),
                      "n_positive": int((v > 0).sum())}
    out["rows"] = rows
    if a.compare_n28:
        ref = {r["seed"]: r for r in json.loads((LAB / "confirm" / "N28_summary.json").read_text(encoding="utf-8"))["rows"] if r.get("valid")}
        both = [r for r in ok if r["seed"] in ref]
        diff = {k: abs(float(np.mean([r["pi"][k] for r in both])) - float(np.mean([ref[r["seed"]]["pi"][k] for r in both])))
                for k in out["pi_mean"]} if both else {}
        out["compare_n28"] = {"n_seeds": len(both), "mean_abs_diff_pi": diff,
                              "max_seed_abs_diff_pi": max(abs(r["pi"][k] - ref[r["seed"]]["pi"][k]) for r in both for k in diff) if both else None}
    (root / "k4b_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1), flush=True)
    if a.compare_n28 and (out["compare_n28"]["n_seeds"] != len(seeds) or max(out["compare_n28"]["mean_abs_diff_pi"].values()) > a.tol):
        raise SystemExit(f"[k4b] does not reproduce N28 within tol {a.tol}")


if __name__ == "__main__":
    main()
