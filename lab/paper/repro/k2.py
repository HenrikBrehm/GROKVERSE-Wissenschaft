#!/usr/bin/env python3
"""Reproduction script for K2 (Table 3.1, Fig. 2): split composition steers the learned frequencies. Session 25, UNTESTED.

From scratch: builds the P1 splits (confirm_splits construction, experiment 1, eps 2), trains arm F and arm G per seed with the lean trainer
repro/train.py (same init per seed), and reports Delta_pow = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)] of the W_E power at step 2000 per seed,
the mean with bootstrap 95% CI and the exact / Monte-Carlo one-sided sign-flip p. Cyclic tasks only (add/mul mod p); D59 uses another trainer.
--compare-p1 prints the per-seed difference to the frozen P1 summary (lab/confirm/P1_summary.json) for the same seeds.

  python lab/tools/guarded_run.py -- python lab/paper/repro/k2.py --smoke                 # 2 seeds, 200 steps, CPU, ~1 min
  python lab/tools/guarded_run.py -- C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe lab/paper/repro/k2.py --device cuda --workers 8 --compare-p1
"""
from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
import confirm_splits as cs  # noqa: E402  (split construction of the frozen P1 block)

EXPERIMENT, EPS = 1, 2.0


def delta_pow(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float:
    s = lambda pw, S: float(pw[[k - 1 for k in S]].sum())   # noqa: E731
    return float(np.log(s(pF, F) / s(pF, G)) + np.log(s(pG, G) / s(pG, F)))


def sign_flip_p(d: np.ndarray, rng: np.random.Generator, n_mc: int = 200_000) -> float:
    if len(d) <= 20:
        flips = np.array(list(itertools.product((1.0, -1.0), repeat=len(d))))
        return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())
    flips = rng.choice((1.0, -1.0), size=(n_mc, len(d)))
    return float((np.sum((flips * d).mean(axis=1) >= d.mean() - 1e-12) + 1) / (n_mc + 1))


def run_arm(a: argparse.Namespace, s: int, arm: str, split: Path, out: Path) -> np.ndarray:
    """add: the trainer's spectra.npy (plain DFT = group basis for addition). mul (session 28 fix): spectra.npy of train.py and
    freq_ban is the plain DFT over the TOKEN index, not the multiplicative group basis that P1 measures (confirm_p1.power_at ->
    EXP-043 group_power); so the final W_E is taken from model_final.pt and measured with group_power, as in P1."""
    if not (out / "result.json").exists():
        cmd = [sys.executable, str(HERE / "train.py"), "--seed", str(s), "--split-file", str(split), "--task", a.task, "--p", str(a.p),
               "--steps", str(a.steps), "--device", a.device, "--threads", str(a.threads), "--out", str(out)]
        subprocess.run(cmd + (["--save-model"] if a.task == "mul" else []), check=True)
    if a.task == "mul":
        import torch
        sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
        from analyze import group_power
        W = torch.load(out / "model_final.pt", map_location="cpu")["W_E"].numpy().astype(np.float64)[:a.p]
        return group_power(W, a.task, a.p)[0]
    st = np.load(out / "spectra_steps.npy").tolist()
    return np.load(out / "spectra.npy")[st.index(a.steps)].astype(np.float64)


def main() -> None:
    ap = argparse.ArgumentParser(description="K2 reproduction (P1 construction)")
    ap.add_argument("--task", default="add", choices=("add", "mul"))
    ap.add_argument("--p", type=int, default=113)
    ap.add_argument("--seeds", default="1000-1049")
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default=str(HERE / "out" / "k2"))
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--compare-p1", action="store_true")
    ap.add_argument("--tol", type=float, default=1e-3, help="max |Delta_pow - P1| per seed for --compare-p1 (FFT vs basis: rounding only)")
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.seeds.split("-"))
    seeds = list(range(lo, hi + 1))
    if a.smoke:
        seeds, a.steps, a.out = seeds[:2], 200, str(Path(a.out).with_name(Path(a.out).name + "_smoke"))
    root = Path(a.out) / f"{a.task}{a.p}_steps{a.steps}_{a.device.replace(':', '')}"
    (root / "splits").mkdir(parents=True, exist_ok=True)
    jobs, targets = [], {}
    for s in seeds:
        targets[s] = cs.target_sets(EXPERIMENT, a.task, a.p, s)
        for arm in "FG":
            idx, T = cs.build(EXPERIMENT, a.task, a.p, s, arm, EPS)
            assert T == targets[s][arm]
            f = root / "splits" / f"seed{s}_{arm}.npy"
            if f.exists() and not np.array_equal(np.load(f), idx.astype(np.int64)):
                raise SystemExit(f"{f} differs from the deterministic construction")
            np.save(f, idx.astype(np.int64))
            jobs.append((s, arm, f, root / "runs" / f"seed{s}_{arm}"))
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        spec = dict(zip([(s, arm) for s, arm, _, _ in jobs], ex.map(lambda j: run_arm(a, *j), jobs)))
    rows = [{"seed": s, "Delta_pow": delta_pow(spec[(s, "F")], spec[(s, "G")], targets[s]["F"], targets[s]["G"])} for s in seeds]
    D = np.array([r["Delta_pow"] for r in rows])
    rng = np.random.default_rng(1)
    boot = np.array([rng.choice(D, len(D)).mean() for _ in range(10_000)])
    out = {"task": f"{a.task}{a.p}", "steps": a.steps, "device": a.device, "n": len(D), "mean": float(D.mean()),
           "sd": float(D.std(ddof=1)) if len(D) > 1 else None, "ci95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
           "p_one_sided": sign_flip_p(D, rng), "n_positive": int((D > 0).sum()), "rows": rows}
    if a.compare_p1:
        ref = {r["seed"]: r["Delta_pow"] for r in json.loads((LAB / "confirm" / "P1_summary.json").read_text(encoding="utf-8"))["tasks"]
               [f"{a.task}{a.p}"]["rows"] if r.get("valid")}
        diffs = [abs(r["Delta_pow"] - ref[r["seed"]]) for r in rows if r["seed"] in ref]
        out["compare_p1"] = {"n": len(diffs), "max_abs_diff": max(diffs) if diffs else None}
    (root / "k2_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1), flush=True)
    if a.compare_p1 and (not out["compare_p1"]["n"] or out["compare_p1"]["max_abs_diff"] > a.tol):
        raise SystemExit(f"[k2] does not reproduce P1 within tol {a.tol}")


if __name__ == "__main__":
    main()
