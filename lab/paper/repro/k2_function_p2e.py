#!/usr/bin/env python3
"""Reproduction script for K2-function, mul 113 and add 97 (Section 3.2, Fig. 5): P2e, manifest 3c484ef. Session 27, UNTESTED (needs the
train.py equivalence check first; mul through train.py is also used by repro/k2.py).

From scratch: builds the P2e splits (confirm_splits construction, experiment id 5, eps 2, seeds 2270-2289, arms F/G per task), trains each
arm 8000 steps with the lean trainer repro/train.py (--save-model; test set = complement of the train split, as the freq_ban runs without
--test-file) and applies the FROZEN P2e measure and verdict, imported read-only from lab/tools/confirm_p2e.py (measure: number rows of W_E in
group order, equal-norm step along own vs 4 control sets, margin drop on pairs outside both splits; verdict: all seeds, Holm over
{mul113, add97}, one-sided t-test, bootstrap CI with rng 5).
--compare-p2e compares mean D per task with lab/confirm/P2e_summary.json and fails above --tol.

  python lab/tools/guarded_run.py -- python lab/paper/repro/k2_function_p2e.py --smoke       # 1 seed, 300 steps, CPU
  python lab/tools/guarded_run.py -- C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe lab/paper/repro/k2_function_p2e.py --device cuda --workers 8 --compare-p2e
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
import k4c  # noqa: E402  (path setup: lab/tools, training/)
import confirm_p2e as p2e  # noqa: E402  (frozen P2e measure and verdict, read-only)
import confirm_splits as cs  # noqa: E402

TRAINER_SHA = hashlib.sha256((HERE / "train.py").read_bytes()).hexdigest()[:10]   # never reuse runs of another trainer version
LAB, EXPERIMENT, EPS, STEPS = k4c.LAB, 5, 2.0, 8000
TASKS = (("mul", 113), ("add", 97))
assert (p2e.REGISTERED["experiment"], p2e.REGISTERED["eps"], p2e.REGISTERED["steps"]) == (EXPERIMENT, EPS, STEPS)
assert [tuple(t) for t in p2e.REGISTERED["tasks"]] == list(TASKS)


def cached(out: Path, s: int, steps: int, task: str, p: int) -> bool:
    f = out / "result.json"
    if not (f.exists() and (out / "model_final.pt").exists()):
        return False
    r = json.loads(f.read_text(encoding="utf-8"))
    cfg = r.get("config", {})
    return (r.get("seed"), r.get("steps"), r.get("switch_step"), cfg.get("task"), cfg.get("p")) == (s, steps, None, task, p)


def run(a: argparse.Namespace, s: int, task: str, p: int, split: Path, out: Path) -> Path:
    if not cached(out, s, a.steps, task, p):
        cmd = [sys.executable, str(HERE / "train.py"), "--seed", str(s), "--task", task, "--p", str(p), "--split-file", str(split),
               "--steps", str(a.steps), "--device", a.device, "--threads", str(a.threads), "--save-model", "--out", str(out)]
        subprocess.run(cmd, check=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="K2-function reproduction, mul 113 and add 97 (P2e construction)")
    ap.add_argument("--seeds", default="2270-2289")
    ap.add_argument("--steps", type=int, default=STEPS)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default=str(HERE / "out" / "k2_function_p2e"))
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--compare-p2e", action="store_true")
    ap.add_argument("--tol", type=float, default=0.02, help="max |mean D - P2e mean D| per task (logit units)")
    a = ap.parse_args()
    if a.compare_p2e and (a.smoke or not a.device.startswith("cuda") or a.steps != STEPS):
        raise SystemExit("--compare-p2e needs the full 8000 steps on cuda (P2e ran on the GPU), not --smoke")
    lo, hi = (int(x) for x in a.seeds.split("-"))
    seeds = list(range(lo, hi + 1))
    if a.compare_p2e and seeds != p2e.REGISTERED["seeds"]:   # s27 review: the gate compares with the frozen mean over all registered seeds
        raise SystemExit("--compare-p2e needs exactly the registered seeds")
    if a.smoke:
        seeds, a.steps, a.out = seeds[:1], 300, str(Path(a.out).with_name(Path(a.out).name + "_smoke"))
    root = Path(a.out) / f"steps{a.steps}_{a.device.replace(':', '')}_thr{a.threads}_train{TRAINER_SHA}"
    (root / "splits").mkdir(parents=True, exist_ok=True)
    jobs, meta = [], {}
    for task, p in TASKS:
        for s in seeds:
            T = cs.target_sets(EXPERIMENT, task, p, s)
            files = {}
            for arm in "FG":
                idx, targ = cs.build(EXPERIMENT, task, p, s, arm, EPS)
                if targ != T[arm]:
                    raise SystemExit(f"{task}{p} seed {s} {arm}: targets differ from target_sets")
                f = root / "splits" / f"{task}{p}_seed{s}_{arm}.npy"
                if f.exists() and not np.array_equal(np.load(f), idx.astype(np.int64)):
                    raise SystemExit(f"{f} differs from the deterministic construction")
                np.save(f, idx.astype(np.int64))
                frozen = p2e.SPL / f"{p2e.stem(task, p, s, arm)}.npy"      # bit-exact check against the frozen P2e split if present
                if frozen.exists() and not np.array_equal(np.load(frozen), idx.astype(np.int64)):
                    raise SystemExit(f"{task}{p} seed {s} {arm}: split differs from the frozen P2e split")
                files[arm] = f
                jobs.append(((task, p, s, arm), f, root / "runs" / f"{task}{p}_seed{s}_{arm}"))
            meta[(task, p, s)] = (T, np.setdiff1d(np.arange(p * p), np.union1d(*[np.load(files[x]) for x in "FG"])))
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        outs = dict(zip([j[0] for j in jobs], ex.map(lambda j: run(a, j[0][2], j[0][0], j[0][1], j[1], j[2]), jobs)))
    rows: dict[str, list[dict]] = {}
    for task, p in TASKS:
        rows[f"{task}{p}"] = []
        for s in seeds:
            T, common = meta[(task, p, s)]
            arms = {arm: p2e.measure(task, p, s, arm, T, common, (outs[(task, p, s, arm)] / "model_final.pt").read_bytes()) for arm in "FG"}
            rows[f"{task}{p}"].append({"seed": s, "valid": False, "arms": arms, **p2e.validity(arms)})
    out: dict = {"steps": a.steps, "device": a.device, "n_planned": len(seeds),
                 "tasks": p2e.verdict(rows, len(seeds), np.random.default_rng(5)), "rows": rows}
    if a.compare_p2e:
        ref = json.loads((LAB / "confirm" / "P2e_summary.json").read_text(encoding="utf-8"))
        cmp_ = {}
        for k in rows:
            ref_D = {r["seed"]: r["D"] for r in ref["rows"][k] if r.get("valid")}
            per_seed = [abs(r["D"] - ref_D[r["seed"]]) for r in rows[k] if r.get("valid") and r["seed"] in ref_D]
            cmp_[k] = {"mean_D": out["tasks"][k].get("mean"), "frozen_mean_D": ref["tasks"][k].get("mean"), "n_seeds": len(per_seed),
                       "max_seed_abs_diff_D": max(per_seed) if per_seed else None}
        out["compare_p2e"] = cmp_
    (root / "k2_function_p2e_summary.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, default=float), flush=True)
    if a.compare_p2e:
        for k, c in out["compare_p2e"].items():
            if c["mean_D"] is None or c["frozen_mean_D"] is None or c["n_seeds"] != len(seeds) or abs(c["mean_D"] - c["frozen_mean_D"]) > a.tol:
                raise SystemExit(f"[k2_function_p2e] {k} does not reproduce P2e within tol {a.tol}")


if __name__ == "__main__":
    main()
