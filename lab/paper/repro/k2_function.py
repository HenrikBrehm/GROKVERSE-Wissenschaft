#!/usr/bin/env python3
"""Reproduction script for K2-function, add 113 (Section 3.2, Fig. 5): an equal-norm step of W_E along the steered frequencies lowers the
correct-class logit margin more than along control frequencies (P2d, manifest c0cd65f). Session 27, UNTESTED (needs the train.py
equivalence check first). mul 113 / add 97 (P2e) are not covered yet (group-order rows for mul).

From scratch: builds the P2d splits (confirm_splits construction, experiment id 4, eps 2, seeds 2230-2249, arms F/G with disjoint target
sets), trains each arm 4000 steps with the lean trainer repro/train.py (--save-model; test set = complement of the train split, as the
freq_ban runs without --test-file), and applies the FROZEN P2d measure, imported read-only from lab/tools/confirm_p2d.py (drops,
control_sets, validity, verdict; model loading and margin evaluation as there):
  u_S = P_S W / ||P_S W||, W' = W - 0.02 ||W|| u_S (W = W_E[:113]); drop_S = mean correct-class margin on the pairs outside both splits,
  before minus after; D = mean over the two arms of (drop_own - mean over 4 control sets); one-sided t-test, bootstrap CI (rng 42).
--compare-p2d compares mean D with lab/confirm/P2d_summary.json (same seeds) and fails above --tol.

  python lab/tools/guarded_run.py -- python lab/paper/repro/k2_function.py --smoke           # 1 seed, 300 steps, CPU
  python lab/tools/guarded_run.py -- C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe lab/paper/repro/k2_function.py --device cuda --workers 8 --compare-p2d
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import k4c  # noqa: E402  (path setup: lab/tools, training/)
import confirm_p2 as p2  # noqa: E402  (frozen model loading and margin evaluation)
import confirm_p2d as p2d  # noqa: E402  (frozen P2d measure, read-only)
import confirm_splits as cs  # noqa: E402

LAB, EXPERIMENT, EPS, STEPS, P = k4c.LAB, 4, 2.0, 4000, 113


def cached(out: Path, s: int, steps: int) -> bool:
    f = out / "result.json"
    if not (f.exists() and (out / "model_final.pt").exists()):
        return False
    r = json.loads(f.read_text(encoding="utf-8"))
    return (r.get("seed"), r.get("steps"), r.get("switch_step")) == (s, steps, None)


def run(a: argparse.Namespace, s: int, split: Path, out: Path) -> Path:
    if not cached(out, s, a.steps):
        cmd = [sys.executable, str(HERE / "train.py"), "--seed", str(s), "--split-file", str(split), "--steps", str(a.steps),
               "--device", a.device, "--threads", str(a.threads), "--save-model", "--out", str(out)]
        subprocess.run(cmd, check=True)
    return out


def arm_row(s: int, arm: str, T: dict, common: np.ndarray, out: Path) -> dict:
    """As confirm_p2d.arm_row after loading (same sets, same drops, same base evaluation)."""
    m = p2.load_model_bytes((out / "model_final.pt").read_bytes())
    W = m.W_E.detach().numpy().astype(np.float64)[:P]
    other = "G" if arm == "F" else "F"
    sets = {"own": T[arm]} | {f"c{i}": c for i, c in enumerate(p2d.control_sets(p2.e51.control_set(T[arm], T[other]), s, arm))}
    dr = p2d.drops(m, W, sets, common, p2d.REL_DELTA * float(np.linalg.norm(W)))
    base = p2.e55.evaluate(m, None, common)
    return {"base": base, "drop_own": dr["own"], "drop_ctrl": [dr[f"c{i}"] for i in range(p2d.N_CTRL)]}


def main() -> None:
    ap = argparse.ArgumentParser(description="K2-function reproduction, add 113 (P2d construction)")
    ap.add_argument("--seeds", default="2230-2249")
    ap.add_argument("--steps", type=int, default=STEPS)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default=str(HERE / "out" / "k2_function"))
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--compare-p2d", action="store_true")
    ap.add_argument("--tol", type=float, default=0.02, help="max |mean D - P2d mean D| for --compare-p2d (logit units)")
    a = ap.parse_args()
    if a.compare_p2d and (a.smoke or not a.device.startswith("cuda") or a.steps != STEPS):
        raise SystemExit("--compare-p2d needs the full 4000 steps on cuda (P2d ran on the GPU), not --smoke")
    lo, hi = (int(x) for x in a.seeds.split("-"))
    seeds = list(range(lo, hi + 1))
    if a.smoke:
        seeds, a.steps, a.out = seeds[:1], 300, str(Path(a.out).with_name(Path(a.out).name + "_smoke"))
    root = Path(a.out) / f"steps{a.steps}_{a.device.replace(':', '')}"
    (root / "splits").mkdir(parents=True, exist_ok=True)
    jobs, meta = [], {}
    for s in seeds:
        T = cs.target_sets(EXPERIMENT, "add", P, s)
        files = {}
        for arm in "FG":
            idx, targ = cs.build(EXPERIMENT, "add", P, s, arm, EPS)
            if targ != T[arm]:
                raise SystemExit(f"seed {s} {arm}: targets differ from target_sets")
            f = root / "splits" / f"seed{s}_{arm}.npy"
            if f.exists() and not np.array_equal(np.load(f), idx.astype(np.int64)):
                raise SystemExit(f"{f} differs from the deterministic construction")
            np.save(f, idx.astype(np.int64))
            files[arm] = f
            jobs.append(((s, arm), files[arm], root / "runs" / f"seed{s}_{arm}"))
        common = np.setdiff1d(np.arange(P * P), np.union1d(*[np.load(files[x]) for x in "FG"]))
        meta[s] = (T, common)
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        outs = dict(zip([j[0] for j in jobs], ex.map(lambda j: run(a, j[0][0], j[1], j[2]), jobs)))
    rows = []
    for s in seeds:
        T, common = meta[s]
        arms = {arm: arm_row(s, arm, T, common, outs[(s, arm)]) for arm in "FG"}
        rows.append({"seed": s, "arms": arms, **p2d.validity(arms)})
    D = np.array([r["D"] for r in rows if r["valid"]])
    n_tech = sum(1 for r in rows if r.get("technical"))
    out: dict = {"steps": a.steps, "device": a.device, "n_planned": len(seeds), "n_technical": n_tech,
                 **p2d.verdict(D, len(seeds), np.random.default_rng(42), n_tech), "rows": rows}
    if a.compare_p2d:
        ref = json.loads((LAB / "confirm" / "P2d_summary.json").read_text(encoding="utf-8"))
        out["compare_p2d"] = {"mean_D": out.get("mean"), "frozen_mean_D": ref.get("mean"), "n_valid": out.get("n_valid"),
                              "frozen_n_valid": ref.get("n_valid")}
    (root / "k2_function_summary.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, default=float), flush=True)
    if a.compare_p2d:
        c = out["compare_p2d"]
        if c["mean_D"] is None or c["n_valid"] != c["frozen_n_valid"] or abs(c["mean_D"] - c["frozen_mean_D"]) > a.tol:
            raise SystemExit(f"[k2_function] does not reproduce P2d within tol {a.tol}")


if __name__ == "__main__":
    main()
