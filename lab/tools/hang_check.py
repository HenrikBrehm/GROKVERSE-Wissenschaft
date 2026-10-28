"""Hang check for jobs of the GPU daemon (lab/runner/RUNBOOK.md, class A3); read-only unless --kill.

For every job in lab/queue/status.json -> running, the job's process tree (the guard started by the daemon and all its
descendants) is sampled several times. Verdicts:
  skip       quiet_min below the threshold, or the daemon is already killing the job
  busy       the tree still works: CPU, disk/network I/O or GPU use above the thresholds in at least one interval
  hung       quiet >= threshold and in every interval: tree CPU < --cpu-cores-max, I/O < --io-bytes-max, no GPU use
  protected  hung, but the job belongs to a confirmation block (script or --out-root under lab/confirm) -> report only
  unknown    status stale or malformed, tree not identified or a measurement failed -> never killed
With --kill, each hung job is re-verified (same guard and starter, same create times, same command) and the starter's
process tree is terminated; the result (also a failed kill) is appended to lab/runner/logs/auto_actions.jsonl.
Prints one JSON document. Exit code 0 unless the status file cannot be read (2).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parents[2]
QUEUE = Path(os.environ.get("GROKVERSE_QUEUE_DIR", ROOT / "lab" / "queue"))
ACTION_LOG = Path(os.environ.get("GROKVERSE_ACTION_LOG", ROOT / "lab" / "runner" / "logs" / "auto_actions.jsonl"))
GUARD_MARKER = "guarded_run.py"
MAX_HEARTBEAT_AGE_S = 120.0
CREATE_NO_WINDOW = 0x08000000
GPU_QUERY = ("Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine | "
             "ForEach-Object { $_.Name + '|' + $_.UtilizationPercentage }")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def gpu_use_by_pid() -> dict[int, float]:
    """Summed GPU engine utilization per PID; values above 100 are counter glitches and are dropped.

    Any unreadable per-process line or an empty answer (dwm.exe always has engine instances) is a failed
    measurement and raises, so that a job is never judged idle because its GPU line could not be read."""
    out = subprocess.run(["powershell", "-NoProfile", "-Command", GPU_QUERY], capture_output=True, text=True,
                         timeout=60, creationflags=CREATE_NO_WINDOW)
    if out.returncode != 0:
        raise RuntimeError(f"GPU counter query failed: {out.stderr.strip()[:200]}")
    use: dict[int, float] = {}
    for line in out.stdout.splitlines():
        line = line.strip()
        if not line.startswith("pid_"):
            continue
        m = re.match(r"pid_(\d+)_.*\|\s*(\d+(?:[.,]\d+)?)$", line)
        if not m:
            raise RuntimeError(f"unreadable GPU counter line: {line[:120]}")
        value = float(m.group(2).replace(",", "."))
        if value <= 100:
            use[int(m.group(1))] = use.get(int(m.group(1)), 0.0) + value
    if not use:
        raise RuntimeError("GPU counter returned no instances")
    return use


def is_confirmation(cmd: str) -> bool:
    """True if the job belongs to a confirmation block: script or --out-root under lab/confirm, or a confirm_* script.

    Reading split files from lab/confirm (as the Pythia pilots do) does not make a job a confirmation run."""
    toks = [t.replace("\\", "/") for t in cmd.split()]
    script = next((t for t in toks if t.endswith(".py")), "")
    out_root = toks[toks.index("--out-root") + 1] if "--out-root" in toks[:-1] else ""
    return ("lab/confirm/" in script or Path(script).name.startswith("confirm_")
            or out_root.rstrip("/").endswith("lab/confirm") or "lab/confirm/" in out_root + "/")


def find_guard(daemon: psutil.Process, cmd: str) -> psutil.Process:
    """The daemon's child running guarded_run.py for exactly this job command.

    The daemon writes cmd as " ".join(tokens) and starts the guard with the same tokens after "--", so joining the
    guard's argv the same way reproduces cmd; more than one match (duplicate job lines) is refused as ambiguous."""
    hits = []
    for child in daemon.children(recursive=False):
        argv = child.cmdline()
        if any(GUARD_MARKER in a for a in argv) and "--" in argv and " ".join(argv[argv.index("--") + 1:]) == cmd:
            hits.append(child)
    if len(hits) != 1:
        raise LookupError(f"{len(hits)} guard processes match the job command")
    return hits[0]


def snapshot(tree: list[psutil.Process]) -> dict:
    cpu = io = 0.0
    for p in tree:
        t = p.cpu_times()
        cpu += t.user + t.system
        c = p.io_counters()
        io += c.read_bytes + c.write_bytes
    return {"t": time.monotonic(), "cpu_s": cpu, "io_bytes": io}


def measure(guard: psutil.Process, samples: int, interval: float) -> dict:
    """CPU cores, I/O bytes and GPU use of the guard's tree per interval; any change of the tree counts as activity.

    GPU use is the decisive signal for GPU jobs: healthy ROCm jobs can need as little as 0.06 CPU cores (measured
    30.09.), so a low CPU value alone never makes a GPU job idle."""
    tree = [guard, *guard.children(recursive=True)]
    pids = sorted(p.pid for p in tree)
    snaps, gpu_max = [snapshot(tree)], 0.0
    for k in range(samples):
        gpu = gpu_use_by_pid()
        gpu_max = max(gpu_max, sum(gpu.get(pid, 0.0) for pid in pids))
        if k == samples - 1:
            break
        time.sleep(interval)
        if sorted(p.pid for p in [guard, *guard.children(recursive=True)]) != pids:
            return {"tree_changed": True, "pids": pids}
        snaps.append(snapshot(tree))
    steps = [(b["cpu_s"] - a["cpu_s"]) / max(b["t"] - a["t"], 1e-6) for a, b in zip(snaps, snaps[1:])]
    ios = [b["io_bytes"] - a["io_bytes"] for a, b in zip(snaps, snaps[1:])]
    return {"tree_changed": False, "pids": pids, "cpu_cores": [round(s, 3) for s in steps],
            "io_bytes": [int(x) for x in ios], "gpu_util_max": round(gpu_max, 1)}


def judge(job: dict, daemon: psutil.Process | None, dup_cmds: set[str], a: argparse.Namespace) -> dict:
    cmd = job.get("cmd")
    res = {"file": job.get("file"), "job": job.get("job"), "quiet_min": job.get("quiet_min"),
           "cmd": cmd if isinstance(cmd, str) else ""}
    if job.get("killed"):
        return {**res, "verdict": "skip", "reason": "daemon is already killing it"}
    try:
        quiet = float(job.get("quiet_min"))
    except (TypeError, ValueError):
        return {**res, "verdict": "unknown", "reason": "quiet_min missing or not a number"}
    if quiet < a.min_quiet:
        return {**res, "verdict": "skip", "reason": f"quiet < {a.min_quiet} min"}
    if not res["cmd"]:
        return {**res, "verdict": "unknown", "reason": "cmd missing"}
    if res["cmd"] in dup_cmds:
        return {**res, "verdict": "unknown", "reason": "same command listed more than once"}
    if daemon is None:
        return {**res, "verdict": "unknown", "reason": "daemon not verified (stale heartbeat or other process)"}
    try:
        guard = find_guard(daemon, res["cmd"])
        starters = guard.children(recursive=False)
        if len(starters) != 1:
            raise LookupError(f"guard has {len(starters)} direct children")
        starter = starters[0]
        ids = {"guard": {"pid": guard.pid, "create_time": guard.create_time()},
               "starter": {"pid": starter.pid, "create_time": starter.create_time(),
                           "cmdline": " ".join(starter.cmdline())}}
        m = measure(guard, a.samples, a.interval)
    except (psutil.Error, LookupError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        return {**res, "verdict": "unknown", "reason": f"{type(exc).__name__}: {exc}"[:300]}
    res.update(measurement=m, **ids)
    idle = (not m["tree_changed"] and all(c < a.cpu_cores_max for c in m["cpu_cores"])
            and all(x < a.io_bytes_max for x in m["io_bytes"]) and m["gpu_util_max"] == 0)
    if not idle:
        return {**res, "verdict": "busy"}
    if is_confirmation(res["cmd"]):
        return {**res, "verdict": "protected", "reason": "confirmation block: report only"}
    return {**res, "verdict": "hung"}


def kill(res: dict) -> dict:
    """Re-verify guard and starter, then terminate the starter's tree; never retried."""
    try:
        guard = psutil.Process(res["guard"]["pid"])
        starter = psutil.Process(res["starter"]["pid"])
        same = (guard.create_time() == res["guard"]["create_time"] and starter.create_time() == res["starter"]["create_time"]
                and " ".join(starter.cmdline()) == res["starter"]["cmdline"] and starter.ppid() == guard.pid)
        if not same:
            return {"result": "not killed: processes changed since the measurement"}
        victims = [starter, *starter.children(recursive=True)]
    except psutil.NoSuchProcess:
        return {"result": "not killed: process already gone"}
    except psutil.Error as exc:
        return {"result": f"not killed: {type(exc).__name__}: {exc}"[:300]}
    errors = []
    for p in reversed(victims):                     # grandchildren first; a process may exit on its own meanwhile
        try:
            p.kill()
        except psutil.NoSuchProcess:
            pass
        except psutil.Error as exc:
            errors.append(f"{p.pid}: {type(exc).__name__}")
    gone, alive = psutil.wait_procs(victims, timeout=15)
    return {"result": "ok" if not alive else "still alive", "killed_pids": sorted(p.pid for p in gone),
            "alive_pids": sorted(p.pid for p in alive), "errors": errors}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--min-quiet", type=float, default=15.0, help="minutes without log output before a job is sampled")
    ap.add_argument("--samples", type=int, default=3, help="snapshots per job (intervals = samples - 1)")
    ap.add_argument("--interval", type=float, default=30.0, help="seconds between snapshots")
    ap.add_argument("--cpu-cores-max", type=float, default=0.3, help="tree CPU (cores) below which an interval is idle")
    ap.add_argument("--io-bytes-max", type=float, default=1e6, help="tree I/O bytes below which an interval is idle")
    ap.add_argument("--daemon-marker", default="gpu_daemon.py", help="text that must appear in the daemon's command line")
    ap.add_argument("--kill", action="store_true", help="terminate jobs judged hung (RUNBOOK A3)")
    a = ap.parse_args()
    if a.samples < 2 or a.interval <= 0:
        ap.error("--samples must be >= 2 and --interval > 0")
    try:
        status = json.loads((QUEUE / "status.json").read_text(encoding="utf-8"))
        running = [j for j in status.get("running", []) if isinstance(j, dict)]
    except (OSError, ValueError, AttributeError) as exc:
        print(json.dumps({"error": f"status.json unreadable: {exc}"}))
        return 2
    report = {"now_utc": now_utc(), "daemon_pid": status.get("pid"), "jobs": []}
    try:
        beat = datetime.fromisoformat(status["heartbeat_utc"])
        report["heartbeat_age_s"] = round((datetime.now(timezone.utc) - beat).total_seconds(), 1)
    except (KeyError, TypeError, ValueError):
        report["heartbeat_age_s"] = None
    daemon = None
    try:
        proc = psutil.Process(int(status["pid"]))
        fresh = report["heartbeat_age_s"] is not None and report["heartbeat_age_s"] < MAX_HEARTBEAT_AGE_S
        if fresh and any(a.daemon_marker in part for part in proc.cmdline()):
            daemon = proc
    except (KeyError, TypeError, ValueError, psutil.Error):
        pass
    cmds = [j.get("cmd") for j in running]
    dup_cmds = {c for c in cmds if isinstance(c, str) and cmds.count(c) > 1}
    for job in running:
        try:
            res = judge(job, daemon, dup_cmds, a)
        except Exception as exc:                     # one malformed entry must not stop the report for the others
            res = {"file": job.get("file"), "job": job.get("job"), "verdict": "unknown",
                   "reason": f"unexpected {type(exc).__name__}: {exc}"[:300]}
        if a.kill and res["verdict"] == "hung":
            res["kill"] = kill(res)
            entry = {"time_utc": now_utc(), "class": "A3", "tool": "hang_check.py", **res}
            ACTION_LOG.parent.mkdir(parents=True, exist_ok=True)
            with ACTION_LOG.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        report["jobs"].append(res)
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
