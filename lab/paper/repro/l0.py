#!/usr/bin/env python3
"""Reproduction script for L0 (short draft section 6, Fig. 4): set composition (K2) steers the learned frequencies under i.i.d.
minibatch AdamW. Session 49, UNTESTED until the smoke and the full comparison below have run.

From scratch: builds the L0 splits (confirm_l0 construction: EXP-053/P1 splits with omega = 0, target sets drawn without the
stride-order frequencies), trains arm F and arm G per seed at batch 256 (H1) and 64 (H2) with the lean trainer repro/train.py
(same init per seed, 30 000 steps), and reports Delta_pow of the W_E power at the last step per seed, with the frozen block's
statistics (one-sided t-test, Holm over H1/H2, bootstrap 95% CI with the same generator seed). --compare-l0 prints the per-seed
difference to the frozen L0 summary (lab/confirm/L0_summary.json).
Long runs go to the GPU daemon (rule 21): --jobs-out FILE writes the trainer lines and exits; afterwards the same command without
--jobs-out finds the finished runs and only evaluates (existing result.json files are reused, as in k2.py).

  python lab/tools/guarded_run.py -- python lab/paper/repro/l0.py --smoke                       # 1 seed, 300 steps, CPU, ~2 min
  python lab/paper/repro/l0.py --device cuda --jobs-out lab/queue/inbox/30_repro_l0.jobs         # full: 40 runs, ~5 min each on the GPU
  python lab/tools/guarded_run.py -- python lab/paper/repro/l0.py --device cuda --compare-l0      # evaluation after the daemon
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
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
import confirm_l0 as cl  # noqa: E402  (split construction of the frozen L0 block, read only)
import confirm_p1 as c1  # noqa: E402  (t-test, Holm, bootstrap and Delta_pow of the frozen blocks)

GPU_PY = (LAB.parent / ".venv-gpu" / "Scripts" / "python.exe").as_posix()
ARMS = {"iid256": 256, "iid64": 64}
HYP = {"H1": "iid256", "H2": "iid64"}


def run_cmd(a: argparse.Namespace, s: int, bs: int, split: Path, test: Path, out: Path) -> list[str]:
    py = GPU_PY if a.device.startswith("cuda") else sys.executable
    rel = lambda q: q.resolve().relative_to(LAB.parent).as_posix()   # noqa: E731  (job lines: forward slashes, no backslashes)
    return [py, rel(HERE / "train.py"), "--seed", str(s), "--split-file", rel(split), "--test-file", rel(test), "--steps", str(a.steps),
            "--spectra-every", str(a.spectra_every), "--batch-size", str(bs), "--device", a.device, "--threads", "1", "--out", rel(out)]


def final_power(out: Path, steps: int) -> np.ndarray:
    st = np.load(out / "spectra_steps.npy").tolist()
    return np.load(out / "spectra.npy")[st.index(steps)].astype(np.float64)   # add: plain DFT = group basis


def main() -> None:
    ap = argparse.ArgumentParser(description="L0 reproduction (K2 under i.i.d. minibatch AdamW)")
    ap.add_argument("--seeds", default="3720-3729")
    ap.add_argument("--steps", type=int, default=30_000)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default=str(HERE / "out" / "l0"))
    ap.add_argument("--jobs-out", help="write the trainer lines for the GPU daemon (rule 21) and exit")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--compare-l0", action="store_true")
    ap.add_argument("--tol", type=float, default=1e-3, help="max |Delta_pow - L0| per seed for --compare-l0")
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.seeds.split("-"))
    seeds = list(range(lo, hi + 1))
    if a.smoke:
        seeds, a.steps, a.out = seeds[:1], 300, str(Path(a.out).with_name(Path(a.out).name + "_smoke"))
    a.spectra_every = 2500 if a.steps % 2500 == 0 else a.steps
    root = Path(a.out) / f"add113_steps{a.steps}_{a.device.replace(':', '')}"
    (root / "splits").mkdir(parents=True, exist_ok=True)
    jobs, targets = [], {}
    for s in seeds:
        d, (F, G) = cl.build(s), cl.targets(s)
        targets[s] = {"F": F, "G": G}
        files = {}
        for arm, key in (("F", "A"), ("G", "B"), ("test", "test")):
            f = root / "splits" / f"seed{s}_{arm}.npy"
            idx = d[key].astype(np.int64)
            if f.exists() and not np.array_equal(np.load(f), idx):
                raise SystemExit(f"{f} differs from the deterministic construction")
            np.save(f, idx)
            files[arm] = f
        for hyp_arm, bs in ARMS.items():
            for arm in "FG":
                out = root / "runs" / f"seed{s}_{arm}_bs{bs}"
                jobs.append(((s, arm, hyp_arm), out, run_cmd(a, s, bs, files[arm], files["test"], out)))
    if a.jobs_out:
        lines = [" ".join(cmd) for _, out, cmd in jobs if not (out / "result.json").exists()]
        Path(a.jobs_out).write_text("#! workers=8 job_minutes=60 min_minutes=5\n" + "\n".join(lines) + "\n", encoding="utf-8")
        print(f"[l0] {len(lines)} trainer lines -> {a.jobs_out}", flush=True)
        return

    def run(job: tuple) -> np.ndarray:
        _, out, cmd = job
        if not (out / "result.json").exists():
            subprocess.run(cmd, check=True, cwd=LAB.parent)
        return final_power(out, a.steps)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        spec = dict(zip([k for k, _, _ in jobs], ex.map(run, jobs)))
    rows = []
    for s in seeds:
        row = {"seed": s}
        for hyp_arm in ARMS:
            dp = c1.delta_pow_checked(spec[(s, "F", hyp_arm)], spec[(s, "G", hyp_arm)], targets[s]["F"], targets[s]["G"])
            if dp is None:
                raise SystemExit(f"[l0] seed {s} {hyp_arm}: Delta_pow not finite or a target power sum <= 0")
            row[f"dpow_{hyp_arm}"] = dp
        rows.append(row)
    rng = np.random.default_rng(20)                    # as confirm_l0.analyze (bootstrap drawn H1 then H2 from one generator)
    X = {h: np.array([r[f"dpow_{arm}"] for r in rows]) for h, arm in HYP.items()}
    p = {h: c1.t_test_secondary(x)["p_one_sided"] for h, x in X.items()} if len(rows) > 1 else {}
    ph = c1.holm(p) if p else {}
    out = {"steps": a.steps, "device": a.device, "n": len(rows), "rows": rows}
    for h, x in X.items():
        out[h] = {"arm": HYP[h], "mean": float(x.mean()), "ci95": c1.boot_ci(x, rng), "n_positive": int((x > 0).sum()),
                  "p": p.get(h), "p_holm": ph.get(h)}
    if a.compare_l0:
        ref = {r["seed"]: r for r in json.loads((LAB / "confirm" / "L0_summary.json").read_text(encoding="utf-8"))["rows"]
               if not r.get("technical")}
        diffs = [abs(r[k] - ref[r["seed"]][k]) for r in rows if r["seed"] in ref for k in ("dpow_iid256", "dpow_iid64")]
        out["compare_l0"] = {"n": len(diffs), "max_abs_diff": max(diffs) if diffs else None}
    (root / "l0_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1), flush=True)
    if a.compare_l0 and (not out["compare_l0"]["n"] or out["compare_l0"]["max_abs_diff"] > a.tol):
        raise SystemExit(f"[l0] does not reproduce L0 within tol {a.tol}")


if __name__ == "__main__":
    main()
