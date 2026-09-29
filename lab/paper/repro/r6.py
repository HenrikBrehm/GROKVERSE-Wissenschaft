#!/usr/bin/env python3
"""Reproduction script for R6 (short draft result 3, Fig. 8): a data switch inside the lock-in window delays grokking, more at 25 than
at 50 steps. Session 49, UNTESTED until the smoke and the full comparison below have run.

From scratch: builds the R6 splits (N28 construction: EXP-053 overlap_split with omega = 0 and calibrated eps, common test set per
seed), trains per seed pure A, pure B (2000 steps) and the switches A->B, B->A at every t in 10, 20, 25, 30, 40, 50, 75 (t + 2000
steps, AdamW state kept) with the lean trainer repro/train.py, and evaluates with the frozen block's functions (confirm_r6.cost,
family, secondary, same generator seed; pi from the final W_E power as N28). --compare-r6 compares C(t) and pi(t) per seed with the
frozen R6 summary (lab/confirm/R6_summary.json).
Long runs go to the GPU daemon (rule 21): --jobs-out FILE writes the trainer lines and exits; afterwards the same command without
--jobs-out finds the finished runs and only evaluates.

  python lab/tools/guarded_run.py -- python lab/paper/repro/r6.py --smoke                       # 1 seed, t in {25, 50}, 300 steps, CPU
  python lab/paper/repro/r6.py --device cuda --jobs-out lab/queue/inbox/32_repro_r6.jobs         # full: 480 runs
  python lab/tools/guarded_run.py -- python lab/paper/repro/r6.py --device cuda --compare-r6      # evaluation after the daemon
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "experiments/EXP-053-p3-overlap-design"))
import confirm_n28 as n28  # noqa: E402  (logratio, pi_pair; read only)
import confirm_r6 as r6  # noqa: E402  (cost, family, secondary of the frozen R6 block; read only)
import overlap_split as ov  # noqa: E402  (split construction)

GPU_PY = (LAB.parent / ".venv-gpu" / "Scripts" / "python.exe").as_posix()


def rel(q: Path) -> str:
    return q.resolve().relative_to(LAB.parent).as_posix()   # job lines: forward slashes, no backslashes


def run_cmd(a: argparse.Namespace, s: int, files: dict, first: str, second: str | None, t: int | None, out: Path) -> list[str]:
    py = GPU_PY if a.device.startswith("cuda") else Path(sys.executable).as_posix()
    steps = a.budget + (t if second else 0)
    cmd = [py, rel(HERE / "train.py"), "--seed", str(s), "--split-file", rel(files[first]), "--test-file", rel(files["test"]),
           "--steps", str(steps), "--spectra-every", str(steps), "--device", a.device, "--threads", "1", "--out", rel(out)]
    return cmd + (["--switch-split-file", rel(files[second]), "--switch-step", str(t)] if second else [])


def load(out: Path, cap: int) -> dict:
    res = json.loads((out / "result.json").read_text(encoding="utf-8"))
    g = res["generalization_step"]
    st = np.load(out / "spectra_steps.npy").tolist()
    return {"b": float(min(g, cap)) if g is not None else float(cap), "event": g is not None and g <= cap,
            "pw": np.load(out / "spectra.npy")[st.index(res["steps"])].astype(np.float64)}   # add: plain DFT = group basis


def seed_row(s: int, R: dict, F: list[int], G: list[int], ts: list[int]) -> dict:
    """As confirm_r6.seed_row, on the repro runs."""
    b = {k: v["b"] for k, v in R.items()}
    row = {"seed": s, "valid": True, "C": {str(t): r6.cost(b, t) for t in ts}}
    L = {"A": n28.logratio(R["A"]["pw"], F, G), "B": n28.logratio(R["B"]["pw"], F, G)}
    if all(np.isfinite(v) for v in L.values()) and L["A"] - L["B"] >= r6.MIN_SEP:
        row["pi"] = {str(t): n28.pi_pair(L, n28.logratio(R[("AB", t)]["pw"], F, G), n28.logratio(R[("BA", t)]["pw"], F, G))
                     for t in ts}
    return row


def main() -> None:
    ap = argparse.ArgumentParser(description="R6 reproduction (switch cost inside the lock-in window)")
    ap.add_argument("--seeds", default="2800-2829")
    ap.add_argument("--switch-steps", default=",".join(str(t) for t in r6.REGISTERED["switch_steps"]))
    ap.add_argument("--budget", type=int, default=r6.BUDGET)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default=str(HERE / "out" / "r6"))
    ap.add_argument("--jobs-out", help="write the trainer lines for the GPU daemon (rule 21) and exit")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--compare-r6", action="store_true")
    ap.add_argument("--tol-pi", type=float, default=1e-3, help="max |pi - R6| per seed and t for --compare-r6")
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.seeds.split("-"))
    seeds, ts = list(range(lo, hi + 1)), [int(x) for x in a.switch_steps.split(",")]
    if a.smoke:
        seeds, ts, a.budget, a.out = seeds[:1], [25, 50], 300, str(Path(a.out).with_name(Path(a.out).name + "_smoke"))
    cap = a.budget
    eps = json.loads(r6.CAL.read_text(encoding="utf-8"))["levels"][str(r6.OMEGA)]["eps"]
    root = Path(a.out) / f"add113_budget{a.budget}_{a.device.replace(':', '')}"
    (root / "splits").mkdir(parents=True, exist_ok=True)
    jobs, targets = [], {}
    for s in seeds:
        d = ov.build(s, r6.OMEGA, eps)
        targets[s] = ov.targets(s)
        files = {}
        for k in ("A", "B", "test"):
            f = root / "splits" / f"seed{s}_{k}.npy"
            idx = d[k].astype(np.int64)
            if f.exists() and not np.array_equal(np.load(f), idx):
                raise SystemExit(f"{f} differs from the deterministic construction")
            np.save(f, idx)
            files[k] = f
        for first in "AB":
            out = root / "runs" / f"seed{s}_{first}"
            jobs.append(((s, first), out, run_cmd(a, s, files, first, None, None, out)))
        for t in ts:
            for first, second in (("A", "B"), ("B", "A")):
                out = root / "runs" / f"seed{s}_{first}{second}_t{t}"
                jobs.append(((s, (first + second, t)), out, run_cmd(a, s, files, first, second, t, out)))
    if a.jobs_out:
        lines = [" ".join(cmd) for _, out, cmd in jobs if not (out / "result.json").exists()]
        Path(a.jobs_out).write_text("#! workers=8 job_minutes=30 min_minutes=3\n" + "\n".join(lines) + "\n", encoding="utf-8")
        print(f"[r6] {len(lines)} trainer lines -> {a.jobs_out}", flush=True)
        return

    def run(job: tuple) -> dict:
        _, out, cmd = job
        if not (out / "result.json").exists():
            subprocess.run(cmd, check=True, cwd=LAB.parent)
        return load(out, cap)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        loaded = dict(zip([k for k, _, _ in jobs], ex.map(run, jobs)))
    rows = []
    for s in seeds:
        R = {k: v for (s2, k), v in loaded.items() if s2 == s}
        rows.append(seed_row(s, R, *targets[s], ts))
    X = {"H1": np.array([r["C"]["25"] for r in rows]), "H2": np.array([r["C"]["25"] - r["C"]["50"] for r in rows])}
    out = {"budget": a.budget, "device": a.device, "n": len(rows), "hypotheses": r6.family(X, len(seeds), np.random.default_rng(6))}
    if not a.smoke:
        out["secondary"] = r6.secondary(rows, ts)
    if a.compare_r6:
        ref = {r["seed"]: r for r in json.loads((LAB / "confirm" / "R6_summary.json").read_text(encoding="utf-8"))["rows"] if r["valid"]}
        c_diff = [abs(r["C"][str(t)] - ref[r["seed"]]["C"][str(t)]) for r in rows if r["seed"] in ref for t in ts]
        pi_diff = [abs(r["pi"][str(t)] - ref[r["seed"]]["pi"][str(t)]) for r in rows if r["seed"] in ref and "pi" in r
                   and "pi" in ref[r["seed"]] for t in ts]
        pi_presence = [r["seed"] for r in rows if r["seed"] in ref and ("pi" in r) != ("pi" in ref[r["seed"]])]
        out["compare_r6"] = {"n_seeds": sum(1 for r in rows if r["seed"] in ref), "max_abs_diff_C": max(c_diff) if c_diff else None,
                             "max_abs_diff_pi": max(pi_diff) if pi_diff else None, "pi_defined_mismatch": pi_presence}
    out["rows"] = rows
    (root / "r6_summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False), flush=True)
    if a.compare_r6:
        c = out["compare_r6"]
        if not c["n_seeds"] or c["max_abs_diff_C"] > 1e-9 or (c["max_abs_diff_pi"] or 0) > a.tol_pi or c["pi_defined_mismatch"]:
            raise SystemExit("[r6] does not reproduce the frozen R6 summary")
    if not all(math.isfinite(r["C"][str(t)]) for r in rows for t in ts):
        raise SystemExit("[r6] non-finite C")


if __name__ == "__main__":
    main()
