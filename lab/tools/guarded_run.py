#!/usr/bin/env python3
"""guarded_run.py — the ONLY sanctioned way to start a test run or training run in GROKVERSE lab.

Enforces the binding run window of the lab mission (lab/runner/PROMPT.md §7):

* runs may only execute between 00:00 and 13:00 Europe/Berlin (DST-aware);
* the whole run, including child processes, must be over by 13:00;
* a hard timeout = min(session budget, time to 13:00 - buffer[, optional job budget]);
  since 2026-09-25 there is no fixed per-job limit any more (user wish): the agent watches
  its runs itself and aborts them when they stall or diverge;
* if the Berlin time cannot be determined reliably, nothing is started.

Usage (from the project root):

    python lab/tools/guarded_run.py [--job-minutes N] [--min-minutes 5] -- <command ...>
    python lab/tools/guarded_run.py --check          # print the window status, start nothing

The session deadline (UTC ISO timestamp) is read from the environment variable
LAB_SESSION_DEADLINE_UTC, which the outer runner sets. Without it only the 13:00
limit (and an optional --job-minutes) apply.

Exit codes: 0 command succeeded · 3 refused (outside window / not enough time /
STOP file / clock unreliable) or killed because lab/STOP appeared during the run ·
124 killed on timeout · otherwise the command's code. `--check` exits 0 only if a job may start now.
While a job runs, lab/STOP and the timeout are re-checked every few seconds; on Windows the job tree is
bound to a job object, so it dies with the guard.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "lab" / "runner" / "logs" / "guarded_runs.jsonl"
STOP_FILE = ROOT / "lab" / "STOP"

WINDOW_END_HOUR = 13          # runs must be finished by 13:00 Berlin
# one-off exceptions granted by the user (Berlin date -> end hour)
WINDOW_END_OVERRIDES = {date(2026, 9, 26): 18,   # user, 2026-09-26: training allowed until 18:00 today
                        date(2026, 9, 28): 18}   # user, 2026-09-27 21:20: tomorrow runs allowed until 18:00
WINDOW_START_HOUR = 0         # a start override may be fractional: 1.5 = 01:30
WINDOW_START_OVERRIDES: dict = {date(2026, 9, 28): 1.5}  # user 2026-09-27 21:55: stop now, resume at 01:30
# continuous windows granted by the user (Berlin local time, [start, end)); outside them the daily rules apply
EXTRA_WINDOWS = [(datetime(2026, 9, 28, 23, 59), datetime(2026, 10, 6, 0, 0))]  # user 2026-09-28 ~18:30: 24/7 week
STOP_POLL_SECONDS = 5.0       # while a job runs: re-check lab/STOP and the deadline this often
EXIT_STOPPED = 3              # a job killed because lab/STOP appeared counts like a refusal (queues stop)
BUFFER_MINUTES = 3.0          # kept free before 13:00 for a controlled shutdown
EXIT_REFUSED, EXIT_TIMEOUT = 3, 124


def berlin_now(now_utc: datetime | None = None) -> datetime:
    """Current time in Europe/Berlin. Raises if the tz database is unavailable."""
    from zoneinfo import ZoneInfo  # needs the `tzdata` package on Windows
    now_utc = now_utc or datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        raise ValueError("now_utc must be timezone-aware")
    return now_utc.astimezone(ZoneInfo("Europe/Berlin"))


def _daily_window(local: datetime) -> tuple[bool, datetime]:
    """Daily rule (00:00-13:00 plus dated overrides) at Berlin time `local`: (in window, window end)."""
    end_hour = WINDOW_END_OVERRIDES.get(local.date(), WINDOW_END_HOUR)
    start_hour = WINDOW_START_OVERRIDES.get(local.date(), WINDOW_START_HOUR)
    in_window = start_hour <= local.hour + local.minute / 60.0 < end_hour
    # end_hour 24 = the window runs through midnight; if the next day's window starts at 00:00 it is chained,
    # so a job started before midnight is not cut off at 23:57
    day = local.replace(hour=0, minute=0, second=0, microsecond=0)
    while end_hour >= 24:
        day = day + timedelta(days=1)
        if WINDOW_START_OVERRIDES.get(day.date(), WINDOW_START_HOUR) != 0:
            end_hour = 0
            break
        end_hour = WINDOW_END_OVERRIDES.get(day.date(), WINDOW_END_HOUR)
    return in_window, day.replace(hour=end_hour)


def window_status(now_utc: datetime, session_deadline_utc: datetime | None,
                  job_minutes: float | None = None) -> dict:
    """Pure decision function: is a run allowed now, and for how long at most?"""
    local = berlin_now(now_utc)
    in_window, end_local = _daily_window(local)
    naive = local.replace(tzinfo=None)
    for start, end in EXTRA_WINDOWS:
        if start <= naive < end:
            end_aware = end.replace(tzinfo=local.tzinfo)
            candidates = [end_aware] + ([end_local] if in_window else [])
            daily_in, daily_end = _daily_window(end_aware)   # chain into a daily window that begins right at `end`
            if daily_in:
                candidates.append(daily_end)
            in_window, end_local = True, max(candidates)
    # subtract in UTC: same-tzinfo aware datetimes subtract as wall-clock time and would be off by 1 h on DST days
    to_end = (end_local.astimezone(timezone.utc) - now_utc).total_seconds() / 60.0 - BUFFER_MINUTES
    limits = {"window_end_minus_buffer": to_end}
    if job_minutes is not None:
        limits["job_budget"] = job_minutes
    if session_deadline_utc is not None:
        limits["session_budget"] = (session_deadline_utc - now_utc).total_seconds() / 60.0
    binding = min(limits, key=limits.get)
    return {"now_berlin": local.isoformat(), "in_window": in_window,
            "max_minutes": max(0.0, limits[binding]) if in_window else 0.0,
            "binding_limit": binding if in_window else "outside_window",
            "limits_minutes": limits}


def _session_deadline() -> datetime | None:
    raw = os.environ.get("LAB_SESSION_DEADLINE_UTC")
    if not raw:
        return None
    dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _kill_tree(proc: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                       capture_output=True, check=False)
    else:
        import signal
        os.killpg(proc.pid, signal.SIGTERM)
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)


def _bind_to_job_object(proc: subprocess.Popen | None):
    """Windows: a job object that kills all its processes when the guard's handle closes.

    proc=None (preferred, before the child is started): the guard puts ITSELF into the job, so every
    child and grandchild inherits it from birth - including the real interpreter behind a venv launcher
    (.venv-gpu/Scripts/python.exe), which a later per-child assignment could miss. If the guard dies
    (killed queue, crashed runner), Windows then kills the whole training tree. Returns the job handle
    (keep it alive) or None.
    """
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)

        class IO_COUNTERS(ctypes.Structure):
            _fields_ = [(n, ctypes.c_ulonglong) for n in ("r_ops", "w_ops", "o_ops", "r_bytes", "w_bytes", "o_bytes")]

        class BASIC(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class EXTENDED(ctypes.Structure):
            _fields_ = [("Basic", BASIC), ("Io", IO_COUNTERS), ("ProcessMemoryLimit", ctypes.c_size_t),
                        ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t),
                        ("PeakJobMemoryUsed", ctypes.c_size_t)]

        # explicit signatures: without them ctypes passes handles as C int, and the 64-bit pseudo handle of
        # GetCurrentProcess() (-1) overflowed (found by lab session 20 in the guard acceptance, 2026-09-27)
        k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
        k32.CreateJobObjectW.restype = wintypes.HANDLE
        k32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
        k32.SetInformationJobObject.restype = wintypes.BOOL
        k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
        k32.AssignProcessToJobObject.restype = wintypes.BOOL
        k32.GetCurrentProcess.argtypes = []
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.CloseHandle.argtypes = [wintypes.HANDLE]
        k32.CloseHandle.restype = wintypes.BOOL
        job = k32.CreateJobObjectW(None, None)
        info = EXTENDED()
        info.Basic.LimitFlags = 0x2000                      # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        ok = k32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info))  # 9 = ExtendedLimitInformation
        if proc is None:
            k32.GetCurrentProcess.restype = wintypes.HANDLE
            ok = ok and k32.AssignProcessToJobObject(job, k32.GetCurrentProcess())
        else:
            hproc = k32.OpenProcess(0x0100 | 0x0001, False, proc.pid)   # PROCESS_SET_QUOTA | PROCESS_TERMINATE
            ok = ok and k32.AssignProcessToJobObject(job, hproc)
            k32.CloseHandle(hproc)
        if not ok:
            print(f"[guard] warning: job object not applied (winerror {ctypes.get_last_error()})", flush=True)
            return None
        return job
    except Exception as e:  # noqa: BLE001 - best effort; timeout and STOP polling still apply
        print(f"[guard] warning: job object not applied ({e})", flush=True)
        return None


def _log(entry: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def run_guarded(cmd: list[str], job_minutes: float | None, min_minutes: float) -> int:
    now = datetime.now(timezone.utc)
    try:
        st = window_status(now, _session_deadline(), job_minutes)
    except Exception as e:  # noqa: BLE001 — unreliable clock => refuse, never guess
        print(f"[guard] REFUSED: cannot determine Europe/Berlin time ({e})", file=sys.stderr)
        return EXIT_REFUSED
    entry = {"cmd": cmd, "start_utc": now.isoformat(), **st}
    if STOP_FILE.exists():
        entry["outcome"] = "refused_stop_file"
    elif not st["in_window"]:
        entry["outcome"] = "refused_outside_window"
    elif st["max_minutes"] < min_minutes:
        entry["outcome"] = "refused_insufficient_time"
    if "outcome" in entry:
        _log(entry)
        print(f"[guard] REFUSED ({entry['outcome']}): {json.dumps(st)}", file=sys.stderr)
        return EXIT_REFUSED

    timeout_s = st["max_minutes"] * 60.0
    print(f"[guard] start at {st['now_berlin']} Berlin, hard timeout {st['max_minutes']:.1f} min "
          f"(binding: {st['binding_limit']})", flush=True)
    kw = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" \
        else {"start_new_session": True}
    t0 = time.monotonic()
    job = _bind_to_job_object(None)   # guard joins the job first; children inherit it from birth
    proc = subprocess.Popen(cmd, cwd=ROOT, **kw)
    if job is None:
        job = _bind_to_job_object(proc)   # fallback: bind the direct child afterwards
    _ = job   # the handle must stay open while the child runs
    try:
        code = None
        while code is None:
            try:
                code = proc.wait(timeout=STOP_POLL_SECONDS)
            except subprocess.TimeoutExpired:
                if STOP_FILE.exists():
                    _kill_tree(proc)
                    code, entry["outcome"] = EXIT_STOPPED, "killed_stop_file"
                elif time.monotonic() - t0 >= timeout_s:
                    _kill_tree(proc)
                    code, entry["outcome"] = EXIT_TIMEOUT, "killed_timeout"
        entry.setdefault("outcome", "completed" if code == 0 else "failed")
    except KeyboardInterrupt:
        _kill_tree(proc)
        entry["outcome"] = "interrupted"
        _log({**entry, "exit_code": 130, "elapsed_s": time.monotonic() - t0})
        raise
    entry.update({"exit_code": code, "elapsed_s": round(time.monotonic() - t0, 1),
                  "end_utc": datetime.now(timezone.utc).isoformat()})
    _log(entry)
    print(f"[guard] {entry['outcome']} (exit {code}) after {entry['elapsed_s']} s", flush=True)
    return code


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--job-minutes", type=float, default=None,
                    help="optional self-imposed cap for this job (no default limit)")
    ap.add_argument("--min-minutes", type=float, default=5.0,
                    help="refuse unless at least this much run time is available")
    ap.add_argument("--check", action="store_true", help="print the window status and exit")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    if a.job_minutes is not None and a.job_minutes <= 0:
        ap.error("--job-minutes must be positive")
    if a.check:   # exit 0 only if a job could start now (Astra review: --check used to always return 0)
        st = window_status(datetime.now(timezone.utc), _session_deadline(), a.job_minutes)
        st["stop_file"] = STOP_FILE.exists()
        st["allowed"] = st["in_window"] and not st["stop_file"] and st["max_minutes"] >= a.min_minutes
        print(json.dumps(st, indent=2))
        return 0 if st["allowed"] else EXIT_REFUSED
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not cmd:
        ap.error("no command given (use: guarded_run.py -- python ...)")
    return run_guarded(cmd, a.job_minutes, a.min_minutes)


if __name__ == "__main__":
    sys.exit(main())
