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
STOP file / clock unreliable) · 124 killed on timeout · otherwise the command's code.
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
WINDOW_END_OVERRIDES = {date(2026, 9, 26): 18}   # user, 2026-09-26: training allowed until 18:00 today
BUFFER_MINUTES = 3.0          # kept free before 13:00 for a controlled shutdown
EXIT_REFUSED, EXIT_TIMEOUT = 3, 124


def berlin_now(now_utc: datetime | None = None) -> datetime:
    """Current time in Europe/Berlin. Raises if the tz database is unavailable."""
    from zoneinfo import ZoneInfo  # needs the `tzdata` package on Windows
    now_utc = now_utc or datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        raise ValueError("now_utc must be timezone-aware")
    return now_utc.astimezone(ZoneInfo("Europe/Berlin"))


def window_status(now_utc: datetime, session_deadline_utc: datetime | None,
                  job_minutes: float | None = None) -> dict:
    """Pure decision function: is a run allowed now, and for how long at most?"""
    local = berlin_now(now_utc)
    end_hour = WINDOW_END_OVERRIDES.get(local.date(), WINDOW_END_HOUR)
    in_window = 0 <= local.hour < end_hour
    end_local = local.replace(hour=end_hour, minute=0, second=0, microsecond=0)
    to_end = (end_local - local).total_seconds() / 60.0 - BUFFER_MINUTES
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
    proc = subprocess.Popen(cmd, cwd=ROOT, **kw)
    try:
        code = proc.wait(timeout=timeout_s)
        entry["outcome"] = "completed" if code == 0 else "failed"
    except subprocess.TimeoutExpired:
        _kill_tree(proc)
        code = EXIT_TIMEOUT
        entry["outcome"] = "killed_timeout"
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
    if a.check:
        print(json.dumps(window_status(datetime.now(timezone.utc), _session_deadline(),
                                       a.job_minutes), indent=2))
        return 0
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not cmd:
        ap.error("no command given (use: guarded_run.py -- python ...)")
    return run_guarded(cmd, a.job_minutes, a.min_minutes)


if __name__ == "__main__":
    sys.exit(main())
