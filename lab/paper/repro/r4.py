#!/usr/bin/env python3
"""Reproduction script for R4 (short draft result 1): an ordinary RANDOM 30 % split shapes which frequencies the embedding learns.
Session 49, UNTESTED until the smoke and the full comparison below have run.

From scratch: per unit u two inits (2600 + 2u, 2601 + 2u) and two uniform random splits (confirm_r4.split_indices), all four
combinations trained with the lean trainer repro/train.py (test = complement, 8000 steps, W_E spectra every 250 steps); similarities
(Spearman, cosine, top-5 overlap) for shared split / shared init / nothing shared and the verdict with the frozen block's functions
(confirm_r4.similarities / verdict, same generator seed 4). --compare-r4 compares every similarity per unit with the frozen R4
summary (lab/confirm/R4_summary.json).
Long runs go to the GPU daemon (rule 21): --jobs-out FILE writes the trainer lines and exits; afterwards the same command without
--jobs-out finds the finished runs and only evaluates.

  python lab/tools/guarded_run.py -- python lab/paper/repro/r4.py --smoke                       # 1 unit, 300 steps, CPU
  python lab/paper/repro/r4.py --device cuda --jobs-out lab/queue/inbox/34_repro_r4.jobs         # full: 240 runs
  python lab/tools/guarded_run.py -- python lab/paper/repro/r4.py --device cuda --compare-r4      # evaluation after the daemon
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
import confirm_r4 as r4  # noqa: E402  (split construction, similarities and verdict of the frozen R4 block; read only)

GPU_PY = (LAB.parent / ".venv-gpu" / "Scripts" / "python.exe").as_posix()


def rel(q: Path) -> str:
    return q.resolve().relative_to(LAB.parent).as_posix()   # job lines: forward slashes, no backslashes


def load(out: Path, at: tuple[int, ...]) -> dict:
    res = json.loads((out / "result.json").read_text(encoding="utf-8"))
    st = np.load(out / "spectra_steps.npy").tolist()
    sp = np.load(out / "spectra.npy")
    return {"spec": {t: sp[st.index(t)].astype(np.float64) for t in at}, "test_acc": res["final_acc"]["test"]}


def main() -> None:
    ap = argparse.ArgumentParser(description="R4 reproduction (random splits shape the learned frequencies)")
    ap.add_argument("--units", type=int, default=r4.REGISTERED["units"])
    ap.add_argument("--steps", type=int, default=r4.REGISTERED["steps"])
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default=str(HERE / "out" / "r4"))
    ap.add_argument("--jobs-out", help="write the trainer lines for the GPU daemon (rule 21) and exit")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--compare-r4", action="store_true")
    ap.add_argument("--tol", type=float, default=1e-6, help="max |similarity - R4| per unit for --compare-r4")
    a = ap.parse_args()
    at = r4.AT
    if a.smoke:
        a.units, a.steps, a.out, at = 1, 300, str(Path(a.out).with_name(Path(a.out).name + "_smoke")), (250,)
    root = Path(a.out) / f"add113_steps{a.steps}_{a.device.replace(':', '')}"
    (root / "splits").mkdir(parents=True, exist_ok=True)
    py = GPU_PY if a.device.startswith("cuda") else Path(sys.executable).as_posix()
    jobs = []
    for u in range(a.units):
        for j in (0, 1):
            f = root / "splits" / f"u{u}_s{j}.npy"
            idx = r4.split_indices(u, j)
            if f.exists() and not np.array_equal(np.load(f), idx):
                raise SystemExit(f"{f} differs from the deterministic construction")
            np.save(f, idx)
        for i, j in r4.CELLS:
            out = root / "runs" / f"u{u}_i{i}s{j}"
            cmd = [py, rel(HERE / "train.py"), "--seed", str(r4.inits(u)[i]), "--split-file", rel(root / "splits" / f"u{u}_s{j}.npy"),
                   "--steps", str(a.steps), "--spectra-every", "250", "--device", a.device, "--threads", "1", "--out", rel(out)]
            jobs.append(((u, (i, j)), out, cmd))
    if a.jobs_out:
        lines = [" ".join(cmd) for _, out, cmd in jobs if not (out / "result.json").exists()]
        Path(a.jobs_out).write_text("#! workers=8 job_minutes=60 min_minutes=5\n" + "\n".join(lines) + "\n", encoding="utf-8")
        print(f"[r4] {len(lines)} trainer lines -> {a.jobs_out}", flush=True)
        return

    def run(job: tuple) -> dict:
        _, out, cmd = job
        if not (out / "result.json").exists():
            subprocess.run(cmd, check=True, cwd=LAB.parent)
        return load(out, at)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        loaded = dict(zip([k for k, _, _ in jobs], ex.map(run, jobs)))
    keep_at, r4.AT = r4.AT, at                         # similarities() iterates over r4.AT (smoke: only step 250)
    try:
        rows = []
        for u in range(a.units):
            runs = {c: loaded[(u, c)] for c in r4.CELLS}
            rows.append({"unit": u, "technical": False, "inits": list(r4.inits(u)), **r4.similarities(runs),
                         "generalised": sum(1 for v in runs.values() if v["test_acc"] >= r4.ACC_GEN)})
        out = {"steps": a.steps, "device": a.device, "n": len(rows)}
        if not a.smoke:
            out["hypotheses"] = r4.verdict(rows, a.units, np.random.default_rng(4))
    finally:
        r4.AT = keep_at
    if a.compare_r4:
        ref = {r["unit"]: r for r in json.loads((LAB / "confirm" / "R4_summary.json").read_text(encoding="utf-8"))["rows"]
               if not r.get("technical")}
        keys = [k for k in rows[0] if k.split("_")[0] in r4.MEASURES]
        diff = [abs(r[k] - ref[r["unit"]][k]) for r in rows if r["unit"] in ref for k in keys]
        gen = [r["unit"] for r in rows if r["unit"] in ref and r["generalised"] != ref[r["unit"]]["generalised"]]
        out["compare_r4"] = {"n_units": sum(1 for r in rows if r["unit"] in ref), "max_abs_diff": max(diff) if diff else None,
                             "generalised_mismatch_units": gen}
    out["rows"] = rows
    (root / "r4_summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False), flush=True)
    if a.compare_r4:
        c = out["compare_r4"]
        if not c["n_units"] or c["max_abs_diff"] > a.tol or c["generalised_mismatch_units"]:
            raise SystemExit("[r4] does not reproduce the frozen R4 summary")


if __name__ == "__main__":
    main()
