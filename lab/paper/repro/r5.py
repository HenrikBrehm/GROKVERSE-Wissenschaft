#!/usr/bin/env python3
"""Reproduction script for R5 (short draft result 2): spectrally concentrated training splits generalise earlier than uniform ones and
than per-output-matched controls. Session 49, UNTESTED until the smoke and the full comparison below have run.

From scratch: builds the R5 units (confirm_r5 construction: common test set, uniform arm R, engineered arms E2_0/E2_1/E1_0/E8_0,
matched controls D_0/D_1), trains all seven arms per unit with the lean trainer repro/train.py (8000 steps, dense accuracy trace),
finds the registered event (test acc >= 0.95 at three consecutive evaluations after train acc >= 0.99) and evaluates with the frozen
block's statistics (confirm_r5.contrast / verdict, same generator seed). --compare-r5 compares the event times per unit and arm with
the frozen R5 summary (lab/confirm/R5_summary.json); they must be identical (integers).
Long runs go to the GPU daemon (rule 21): --jobs-out FILE writes the trainer lines and exits; afterwards the same command without
--jobs-out finds the finished runs and only evaluates.

  python lab/tools/guarded_run.py -- python lab/paper/repro/r5.py --smoke                      # 1 unit, 300 steps, CPU, ~2 min
  python lab/paper/repro/r5.py --device cuda --jobs-out lab/queue/inbox/31_repro_r5.jobs        # full: 140 runs
  python lab/tools/guarded_run.py -- python lab/paper/repro/r5.py --device cuda --compare-r5     # evaluation after the daemon
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
import confirm_r5 as cr  # noqa: E402  (split construction, event and statistics of the frozen R5 block, read only)

GPU_PY = (LAB.parent / ".venv-gpu" / "Scripts" / "python.exe").as_posix()


def run_cmd(a: argparse.Namespace, seed: int, split: Path, test: Path, out: Path) -> list[str]:
    py = GPU_PY if a.device.startswith("cuda") else Path(sys.executable).as_posix()
    rel = lambda q: q.resolve().relative_to(LAB.parent).as_posix()   # noqa: E731  (job lines: forward slashes, no backslashes)
    return [py, rel(HERE / "train.py"), "--seed", str(seed), "--split-file", rel(split), "--test-file", rel(test), "--steps", str(a.steps),
            "--spectra-every", "250", "--dense", "--device", a.device, "--threads", "1", "--out", rel(out)]


def measure(out: Path, tgts: list[list[int]]) -> dict:
    res = json.loads((out / "result.json").read_text(encoding="utf-8"))
    st = np.load(out / "spectra_steps.npy").tolist()
    pw = np.load(out / "spectra.npy")[st.index(250)].astype(np.float64)
    return {"event": cr.event(res["dense"], int(res["steps"])), "first_crossing": res["generalization_step"],
            "we_share_250": float(np.mean([pw[[k - 1 for k in tg]].sum() / pw.sum() for tg in tgts])),
            "test_final": res["final_acc"]["test"]}


def main() -> None:
    ap = argparse.ArgumentParser(description="R5 reproduction (engineered splits generalise earlier)")
    ap.add_argument("--units", type=int, default=cr.N_UNITS)
    ap.add_argument("--steps", type=int, default=cr.CAP)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default=str(HERE / "out" / "r5"))
    ap.add_argument("--jobs-out", help="write the trainer lines for the GPU daemon (rule 21) and exit")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--compare-r5", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        a.units, a.steps, a.out = 1, 300, str(Path(a.out).with_name(Path(a.out).name + "_smoke"))
    root = Path(a.out) / f"add113_steps{a.steps}_{a.device.replace(':', '')}"
    (root / "splits").mkdir(parents=True, exist_ok=True)
    jobs = []
    for u in range(a.units):
        sets = cr.build_unit(u)["sets"]
        files = {}
        for arm in ("test",) + cr.ARMS:
            f = root / "splits" / f"u{u}_{arm}.npy"
            if f.exists() and not np.array_equal(np.load(f), sets[arm]):
                raise SystemExit(f"{f} differs from the deterministic construction")
            np.save(f, sets[arm])
            files[arm] = f
        for arm in cr.ARMS:
            out = root / "runs" / f"u{u}_{arm}"
            jobs.append(((u, arm), out, run_cmd(a, cr.init_seed(u), files[arm], files["test"], out)))
    if a.jobs_out:
        lines = [" ".join(cmd) for _, out, cmd in jobs if not (out / "result.json").exists()]
        Path(a.jobs_out).write_text("#! workers=8 job_minutes=60 min_minutes=5\n" + "\n".join(lines) + "\n", encoding="utf-8")
        print(f"[r5] {len(lines)} trainer lines -> {a.jobs_out}", flush=True)
        return

    def run(job: tuple) -> dict:
        (u, arm), out, cmd = job
        if not (out / "result.json").exists():
            subprocess.run(cmd, check=True, cwd=LAB.parent)
        return measure(out, cr.arm_targets(u, arm))

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        runs = dict(zip([k for k, _, _ in jobs], ex.map(run, jobs)))
    rows = []
    for u in range(a.units):
        t = {arm: runs[(u, arm)]["event"] for arm in cr.ARMS}
        Lo = {h: cr.contrast(t, h) for h in cr.CONTRASTS}
        rows.append({"unit": u, "technical": False, "times": {arm: list(v) for arm, v in t.items()},
                     "L": {h: float(v[0]) for h, v in Lo.items()}, "order": {h: v[1] for h, v in Lo.items()},
                     **{k: {arm: runs[(u, arm)][k] for arm in cr.ARMS} for k in ("first_crossing", "we_share_250", "test_final")}})
    out = {"steps": a.steps, "device": a.device, "hypotheses": cr.verdict(rows, a.units, np.random.default_rng(5)), "rows": rows}
    if a.compare_r5:
        ref = {r["unit"]: r for r in json.loads((LAB / "confirm" / "R5_summary.json").read_text(encoding="utf-8"))["rows"]
               if not r.get("technical")}
        diff = [(r["unit"], arm) for r in rows if r["unit"] in ref for arm in cr.ARMS
                if r["times"][arm] != ref[r["unit"]]["times"][arm]]
        out["compare_r5"] = {"n_units": sum(1 for r in rows if r["unit"] in ref), "event_time_mismatches": diff}
    (root / "r5_summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False), flush=True)
    if a.compare_r5 and (not out["compare_r5"]["n_units"] or out["compare_r5"]["event_time_mismatches"]):
        raise SystemExit("[r5] does not reproduce the frozen R5 event times")


if __name__ == "__main__":
    main()
