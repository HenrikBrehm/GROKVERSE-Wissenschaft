#!/usr/bin/env python3
"""parallel_queue.py — run a list of jobs with N at a time, every job through guarded_run.py.

User wish 2026-09-26: many runs at once (CPU cores and the GPU). This tool only schedules; the run window,
the session deadline and lab/STOP are still enforced per job by guarded_run.py.

Jobs file: one command per line (as you would type it after `guarded_run.py --`); blank lines and lines
starting with `#` are ignored. Choose the interpreter per job, e.g.
    python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed 60 ... --threads 4
    .venv-gpu/Scripts/python.exe lab/experiments/EXP-001-freq-ban/freq_ban.py --seed 61 ... --device cuda --threads 1

Usage (from the project root):
    python lab/tools/parallel_queue.py JOBS.txt --workers 3 [--min-minutes 5] [--log-dir DIR] [--dry-run]

Behaviour: a guard refusal (exit 3: outside window, too little time, STOP file) stops launching new jobs;
running jobs finish. Any other failure is logged and the queue continues. Each job writes its output to
<log-dir>/job_NNN.log; a summary goes to stdout and <log-dir>/summary.json.
Exit codes: 0 all ok · 1 some job failed · 3 stopped by a guard refusal.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUARD = ROOT / "lab" / "tools" / "guarded_run.py"
EXIT_REFUSED = 3
POLL_SECONDS = 2.0


def read_jobs(path: Path) -> list[list[str]]:
    jobs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            if "\\" in line:   # shlex (POSIX) would silently eat Windows backslashes
                raise SystemExit(f"[pq] use forward slashes in job lines: {line}")
            cmd = shlex.split(line)
            if cmd in jobs:   # the same run twice would race on one run-id directory
                print(f"[pq] warning: duplicate job line skipped: {line}", flush=True)
                continue
            jobs.append(cmd)
    return jobs


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def kill_tree(proc: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True, check=False)
    else:
        proc.kill()


def launch(idx: int, cmd: list[str], min_minutes: float, log_dir: Path) -> tuple[subprocess.Popen, object]:
    log = (log_dir / f"job_{idx:03d}.log").open("w", encoding="utf-8")
    full = [sys.executable, str(GUARD), "--min-minutes", str(min_minutes), "--", *cmd]
    log.write(f"# {now_iso()} {' '.join(full)}\n")
    log.flush()
    proc = subprocess.Popen(full, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    return proc, log


def write_summary(log_dir: Path, state: str, workers: int, jobs: list, pending: list, running: dict,
                  results: list) -> dict:
    """Written after every state change, so a crashed or killed queue still leaves its progress."""
    failed = [r for r in results if r["exit_code"] not in (0, EXIT_REFUSED)]
    summary = {"state": state, "updated_utc": now_iso(), "workers": workers, "jobs_total": len(jobs),
               "completed": sum(r["exit_code"] == 0 for r in results), "failed": len(failed),
               "refused": sum(r["exit_code"] == EXIT_REFUSED for r in results),
               "running": [{"job": i, "cmd": v[2]} for i, v in running.items()],
               "not_started": [{"job": i, "cmd": c} for i, c in pending], "results": results}
    tmp = log_dir / "summary.json.tmp"
    tmp.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    os.replace(tmp, log_dir / "summary.json")
    return summary


def run_queue(jobs: list[list[str]], workers: int, min_minutes: float, log_dir: Path) -> int:
    log_dir.mkdir(parents=True, exist_ok=True)
    pending = list(enumerate(jobs, start=1))
    running: dict[int, tuple[subprocess.Popen, object, list[str], float]] = {}
    results, refused = [], False
    write_summary(log_dir, "running", workers, jobs, pending, running, results)
    try:
        while running or (pending and not refused):
            while pending and not refused and len(running) < workers:
                idx, cmd = pending.pop(0)
                proc, log = launch(idx, cmd, min_minutes, log_dir)
                running[idx] = (proc, log, cmd, time.monotonic())
                print(f"[pq] {now_iso()} start job {idx}: {' '.join(cmd)}", flush=True)
                write_summary(log_dir, "running", workers, jobs, pending, running, results)
            time.sleep(POLL_SECONDS)
            for idx in [i for i, (p, *_) in running.items() if p.poll() is not None]:
                proc, log, cmd, t0 = running.pop(idx)
                log.close()
                rc = proc.returncode
                results.append({"job": idx, "cmd": cmd, "exit_code": rc,
                                "elapsed_s": round(time.monotonic() - t0, 1), "end_utc": now_iso()})
                print(f"[pq] {now_iso()} job {idx} exit {rc}", flush=True)
                if rc == EXIT_REFUSED and not refused:
                    refused = True
                    print("[pq] guard refused a job: no new launches, waiting for running jobs", flush=True)
                write_summary(log_dir, "running", workers, jobs, pending, running, results)
    except KeyboardInterrupt:
        for proc, log, *_ in running.values():
            kill_tree(proc)     # terminate() would kill only the guard and orphan its training child
            log.close()
        write_summary(log_dir, "interrupted", workers, jobs, pending, {}, results)
        raise
    summary = write_summary(log_dir, "stopped_by_guard" if refused else "done", workers, jobs, pending,
                            running, results)
    print(f"[pq] {summary['state']}: {summary['completed']} ok, {summary['failed']} failed, "
          f"{summary['refused']} refused, {len(pending)} not started (log {log_dir})", flush=True)
    if refused:
        return EXIT_REFUSED
    return 1 if summary["failed"] else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("jobs_file", type=Path)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--min-minutes", type=float, default=5.0)
    ap.add_argument("--log-dir", type=Path, default=None)
    ap.add_argument("--dry-run", action="store_true", help="print the parsed jobs and exit")
    a = ap.parse_args()
    if a.workers < 1:
        ap.error("--workers must be >= 1")
    jobs = read_jobs(a.jobs_file)
    if not jobs:
        ap.error(f"no jobs in {a.jobs_file}")
    if a.dry_run:
        for i, cmd in enumerate(jobs, start=1):
            print(f"{i:3d}: {' '.join(cmd)}")
        return 0
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    log_dir = a.log_dir or ROOT / "lab" / "runner" / "logs" / f"pq_{stamp}"
    return run_queue(jobs, a.workers, a.min_minutes, log_dir)


if __name__ == "__main__":
    sys.exit(main())
