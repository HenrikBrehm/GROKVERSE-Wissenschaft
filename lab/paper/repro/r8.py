#!/usr/bin/env python3
"""Reproduction script for R8 (short draft result 3): only a switch to OTHER target frequencies costs grokking time; a switch at t = 25
to a fresh split with the SAME targets (A -> A2) costs less. Session 49, UNTESTED until the smoke and the full comparison have run.

From scratch: builds A, B, A2 and the test set per seed (confirm_r8.build: A/B/test as N28/R6, A2 with the same targets F, fresh
phases and keys, matched share), trains A, B, A2 alone (2000 steps) and A->B, B->A, A->A2, A2->A with a switch at 25 (2025 steps,
AdamW state kept) with the lean trainer repro/train.py, and evaluates with the frozen block's functions (confirm_r8.cost / verdict,
same generator seed 8). --compare-r8 compares C_AB, C_AA2 and D per seed with the frozen R8 summary (lab/confirm/R8_summary.json);
event times are integers, so the costs must agree exactly.
Long runs go to the GPU daemon (rule 21): --jobs-out FILE writes the trainer lines and exits; afterwards the same command without
--jobs-out finds the finished runs and only evaluates.

  python lab/tools/guarded_run.py -- python lab/paper/repro/r8.py --smoke                       # 1 seed, 300 steps, CPU
  python lab/paper/repro/r8.py --device cuda --jobs-out lab/queue/inbox/33_repro_r8.jobs         # full: 175 runs
  python lab/tools/guarded_run.py -- python lab/paper/repro/r8.py --device cuda --compare-r8      # evaluation after the daemon
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
sys.path.insert(0, str(LAB / "experiments/EXP-053-p3-overlap-design"))
import confirm_r8 as r8  # noqa: E402  (split construction, cost and verdict of the frozen R8 block; read only)

GPU_PY = (LAB.parent / ".venv-gpu" / "Scripts" / "python.exe").as_posix()


def rel(q: Path) -> str:
    return q.resolve().relative_to(LAB.parent).as_posix()   # job lines: forward slashes, no backslashes


def run_cmd(a: argparse.Namespace, s: int, files: dict, first: str, second: str | None, out: Path) -> list[str]:
    py = GPU_PY if a.device.startswith("cuda") else sys.executable
    steps = a.budget + (r8.T_SW if second else 0)
    cmd = [py, rel(HERE / "train.py"), "--seed", str(s), "--split-file", rel(files[first]), "--test-file", rel(files["test"]),
           "--steps", str(steps), "--spectra-every", str(steps), "--device", a.device, "--threads", "1", "--out", rel(out)]
    return cmd + (["--switch-split-file", rel(files[second]), "--switch-step", str(r8.T_SW)] if second else [])


def bounded_time(out: Path, cap: int) -> dict:
    g = json.loads((out / "result.json").read_text(encoding="utf-8"))["generalization_step"]
    return {"b": float(min(g, cap)) if g is not None else float(cap), "event": g is not None and g <= cap}


def main() -> None:
    ap = argparse.ArgumentParser(description="R8 reproduction (only a switch to other targets costs time)")
    ap.add_argument("--seeds", default=f"{r8.REGISTERED['seeds'][0]}-{r8.REGISTERED['seeds'][-1]}")
    ap.add_argument("--budget", type=int, default=r8.BUDGET)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default=str(HERE / "out" / "r8"))
    ap.add_argument("--jobs-out", help="write the trainer lines for the GPU daemon (rule 21) and exit")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--compare-r8", action="store_true")
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.seeds.split("-"))
    seeds = list(range(lo, hi + 1))
    if a.smoke:
        seeds, a.budget, a.out = seeds[:1], 300, str(Path(a.out).with_name(Path(a.out).name + "_smoke"))
    root = Path(a.out) / f"add113_budget{a.budget}_{a.device.replace(':', '')}"
    (root / "splits").mkdir(parents=True, exist_ok=True)
    jobs = []
    for s in seeds:
        d = r8.build(s)
        files = {}
        for k in r8.ARMS + ("test",):
            f = root / "splits" / f"seed{s}_{k}.npy"
            idx = d[k].astype(np.int64)
            if f.exists() and not np.array_equal(np.load(f), idx):
                raise SystemExit(f"{f} differs from the deterministic construction")
            np.save(f, idx)
            files[k] = f
        for k in r8.ARMS:
            out = root / "runs" / f"seed{s}_{k}"
            jobs.append(((s, k), out, run_cmd(a, s, files, k, None, out)))
        for x, y in r8.SWITCHES:
            out = root / "runs" / f"seed{s}_{x}to{y}"
            jobs.append(((s, f"{x}>{y}"), out, run_cmd(a, s, files, x, y, out)))
    if a.jobs_out:
        lines = [" ".join(cmd) for _, out, cmd in jobs if not (out / "result.json").exists()]
        Path(a.jobs_out).write_text("#! workers=8 job_minutes=30 min_minutes=3\n" + "\n".join(lines) + "\n", encoding="utf-8")
        print(f"[r8] {len(lines)} trainer lines -> {a.jobs_out}", flush=True)
        return

    def run(job: tuple) -> dict:
        _, out, cmd = job
        if not (out / "result.json").exists():
            subprocess.run(cmd, check=True, cwd=LAB.parent)
        return bounded_time(out, a.budget)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        loaded = dict(zip([k for k, _, _ in jobs], ex.map(run, jobs)))
    rows = []
    for s in seeds:
        b = {k: v["b"] for (s2, k), v in loaded.items() if s2 == s}
        cab, caa = r8.cost(b, "A", "B"), r8.cost(b, "A", "A2")
        rows.append({"seed": s, "valid": True, "C_AB": cab, "C_AA2": caa, "D": cab - caa,
                     "events": {k: v["event"] for (s2, k), v in loaded.items() if s2 == s}})
    out = {"budget": a.budget, "device": a.device, "n": len(rows)}
    if len(rows) > 1:
        out["result"] = r8.verdict(rows, len(seeds), np.random.default_rng(8))
    if a.compare_r8:
        ref = {r["seed"]: r for r in json.loads((LAB / "confirm" / "R8_summary.json").read_text(encoding="utf-8"))["rows"] if r["valid"]}
        diff = [abs(r[k] - ref[r["seed"]][k]) for r in rows if r["seed"] in ref for k in ("C_AB", "C_AA2", "D")]
        out["compare_r8"] = {"n_seeds": sum(1 for r in rows if r["seed"] in ref), "max_abs_diff": max(diff) if diff else None}
    out["rows"] = rows
    (root / "r8_summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False), flush=True)
    if a.compare_r8 and (not out["compare_r8"]["n_seeds"] or out["compare_r8"]["max_abs_diff"] > 1e-9):
        raise SystemExit("[r8] does not reproduce the frozen R8 costs")


if __name__ == "__main__":
    main()
