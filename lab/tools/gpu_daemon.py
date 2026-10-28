#!/usr/bin/env python3
"""gpu_daemon.py — job runner that lives independently of the Claude lab sessions.

Why (user request 2026-09-29): jobs started inside a lab session die when the session ends — regularly after
180 min, or in a crash such as the auto-mode outage on 2026-09-29 08:24 — and the GPU then sits idle until the next
session starts them again. This daemon is started by its own scheduled task (GROKVERSE-GPU-Daemon, every 10 min,
IgnoreNew), so queued jobs keep running across session changes and crashes.

Sessions submit work by writing a job file to lab/queue/inbox/<name>.jobs: one command per line, exactly as for
parallel_queue.py (forward slashes, no backslashes); blank lines and `#` comments are ignored. An optional first line
`#! workers=N job_minutes=M min_minutes=K` sets per-file limits. Files are processed in name order (prefix a number
for priority); jobs of several files may run at the same time up to the global worker cap. A new file is read only
once it has been unchanged for PICKUP_SETTLE_S; a file without job lines is rejected (P-017). Write job files outside
the inbox and move them in when complete.

Every job still runs through guarded_run.py (lab/STOP, run window, job-object binding of the whole process tree), but
WITHOUT the lab session's deadline; instead each job gets a hard per-job limit (`job_minutes`, default 300).
A guard refusal (exit 3: window closed, too little time left, STOP) puts the job back and pauses launching for a
minute. lab/STOP ends the daemon (the guards kill their jobs within seconds).

State for the sessions: lab/queue/status.json (heartbeat every few seconds, running jobs, per-file progress);
per-job logs in lab/queue/logs/<file>/job_NNN.log; finished files move to lab/queue/done/ together with
<file>.summary.json. Progress is persisted in lab/queue/progress/, so a restarted daemon continues where it stopped
(jobs that were running are started again; freq_ban.py skips completed runs by fingerprint).

Graceful restart (e.g. after a code update): create lab/queue/DRAIN — the daemon starts nothing new, lets running jobs
finish, deletes DRAIN and exits; the scheduled task starts the new code within 10 minutes.

Hang detection (user request 2026-09-29, after two EXP-105 jobs printed a traceback at 08:50 and then spun at 100 % CPU
without exiting, blocking two GPU slots for 90 min). The daemon watches each job's log:
- `crash_minutes` (default 10): the log ends in an uncaught Python traceback and has not grown for this long -> the
  child crashed but does not exit (e.g. hangs in GPU teardown); the job is killed and marked `failed:hung`. A script
  that prints a HANDLED exception as a traceback and then stays silent that long would be killed too (no lab script
  does this as of 2026-09-29); set crash_minutes=0 for such scripts.
- `stall_minutes` (default 0 = off, opt-in per file): the log has not grown for this long -> killed, `failed:stalled`.
  Only for scripts that print progress regularly; jobs run with PYTHONUNBUFFERED=1, so prints reach the log at once.
Killed jobs are not retried. The slot is freed only once the process is really gone (the kill is repeated every 30 s
until then); each kill is recorded in the job log and in guarded_runs.jsonl (killed_by: gpu_daemon).

GPU-memory guard (user request 2026-09-29, lab/PROBLEME.md P-009; rule and probes in gpu_memory.py): each file
declares the GPU memory of one job in its header (`gpu_gb`, default 3.5 = an lm_stage2 run incl. margin; small
train.py runs ~1). A job starts only if it fits the budget (--gpu-budget-gb, default 16 of the 20 GB card, measured
and booked), no memory is spilled into RAM and enough RAM/commit is free; at most one launch per LAUNCH_SPACING_S.
Launch order: jobs interrupted by a daemon restart first (state "interrupted", kept across further restarts, so
checkpointed runs do not wait behind hundreds of queued jobs), then name order. A job blocked by memory blocks the
jobs behind it (strict priority, no backfilling); status.json shows the reason and since when. A file whose gpu_gb
can never fit is rejected at pickup. Changed `#!` headers are re-read while the file is queued (job lines are not).

Usage: python lab/tools/gpu_daemon.py [--max-workers N] [--gpu-budget-gb G] [--idle-exit-min M] [--once]
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUEUE = Path(os.environ.get("GROKVERSE_QUEUE_DIR", ROOT / "lab" / "queue"))   # env override only for tests
INBOX, DONE, LOGS, PROGRESS = QUEUE / "inbox", QUEUE / "done", QUEUE / "logs", QUEUE / "progress"
STATUS = QUEUE / "status.json"
LOCKFILE = QUEUE / "daemon.lock"
DRAIN = QUEUE / "DRAIN"   # graceful restart: no new launches, running jobs finish, then the daemon exits (task restarts it)
STOP_FILE = ROOT / "lab" / "STOP"
GUARD = ROOT / "lab" / "tools" / "guarded_run.py"
EXIT_REFUSED = 3
POLL_SECONDS = 2.0
REFUSAL_PAUSE_SECONDS = 60.0
DEFAULTS = {"workers": 10, "job_minutes": 300.0, "min_minutes": 5.0, "stall_minutes": 0.0, "crash_minutes": 10.0,
            "gpu_gb": 3.5}
KILL_RETRY_SECONDS = 30.0   # a hung job that is still alive this long after the kill gets killed again
PICKUP_SETTLE_S = 5.0       # a new inbox file is read only once unchanged this long (P-017: an empty file being written
                            # was picked up and filed as done with 0 jobs); a file with no job lines is rejected, not done
LAUNCH_SPACING_S = 6.0      # at most one launch per spacing: RAM/commit readings stay meaningful between launches
FEATURES = ["name_order", "drain", "hang_kill", "memory_guard", "resume_first", "header_reload", "settled_pickup"]
TRACEBACK = "Traceback (most recent call last):"
CHAINED = ("During handling of the above exception", "The above exception was the direct cause")
TAIL_BYTES = 16384

sys.path.insert(0, str(ROOT / "lab" / "tools"))
from guarded_run import _bind_to_job_object, _kill_tree, _log  # noqa: E402
import gpu_memory  # noqa: E402


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path: Path, data: dict) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    for _ in range(20):                       # Windows: a reader may hold the file for a moment
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            time.sleep(0.1)
    os.replace(tmp, path)


def acquire_lock():
    """Single instance: a byte-range lock that Windows releases when the process dies."""
    import msvcrt
    QUEUE.mkdir(parents=True, exist_ok=True)
    fh = open(LOCKFILE, "a+")
    fh.seek(0)                                # lock byte 0, whatever the file length: all instances contend for it
    try:
        msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        fh.close()
        return None
    fh.seek(0)
    fh.truncate()
    fh.write(f"pid={os.getpid()} started={now_iso()}\n")
    fh.flush()
    return fh


MIN_GPU_GB = 0.5   # even a small torch-ROCm job holds ~0.8 GB; smaller values are typos that would defeat the memory guard


def check_options(opts: dict) -> None:
    """Reject header values that make no sense (ValueError), e.g. gpu_gb=0.35 meant as 3.5."""
    if opts["workers"] < 1 or opts["job_minutes"] <= 0 or opts["gpu_gb"] < MIN_GPU_GB:
        raise ValueError(f"invalid header: workers >= 1, job_minutes > 0, gpu_gb >= {MIN_GPU_GB} required ({opts})")
    if min(opts["min_minutes"], opts["stall_minutes"], opts["crash_minutes"]) < 0:
        raise ValueError(f"invalid header: negative minutes ({opts})")


def parse_job_file(path: Path) -> tuple[dict, list[list[str]]]:
    opts, jobs = dict(DEFAULTS), []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("#!"):
            for tok in line[2:].split():
                key, _, val = tok.partition("=")
                if key in opts and val:
                    opts[key] = type(DEFAULTS[key])(val)
            check_options(opts)
            continue
        if not line or line.startswith("#"):
            continue
        if "\\" in line:
            raise ValueError(f"backslash in job line (use forward slashes): {line}")
        cmd = shlex.split(line)
        if cmd not in jobs:
            jobs.append(cmd)
    return opts, jobs


class JobFile:
    def __init__(self, path: Path, budget_gb: float):
        self.path, self.name = path, path.stem
        self.opts, self.jobs = parse_job_file(path)
        if not self.jobs:
            raise ValueError("no job lines (empty file, or read while still being written: write elsewhere, then move)")
        if gpu_memory.oversized(self.opts["gpu_gb"], budget_gb):
            raise ValueError(f"gpu_gb={self.opts['gpu_gb']} can never fit the GPU budget of {budget_gb} GB")
        self.mtime, self.note = path.stat().st_mtime, ""
        self.progress_path = PROGRESS / f"{self.name}.json"
        prog = self._read_progress()
        # job index -> "pending" | "interrupted" | "done" | "failed:<code>"; a job that was running when the daemon
        # died is "interrupted" (kept across further restarts) and starts before all pending jobs (resume first)
        self.state = {i: prog.get(str(i), "pending") for i in range(len(self.jobs))}
        self.state = {i: ("interrupted" if s == "running" else s) for i, s in self.state.items()}
        self.running = 0

    def _read_progress(self) -> dict:
        """Persisted job states; an unreadable file is kept aside and the jobs start over (rather than dropping them)."""
        if not self.progress_path.exists():
            return {}
        try:
            return json.loads(self.progress_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            os.replace(self.progress_path, self.progress_path.with_name(self.progress_path.name + ".corrupt"))
            self.note = f"progress unreadable ({e}), kept as .corrupt; all jobs start over"[:200]
            return {}

    def save(self) -> None:
        write_json(self.progress_path, {str(i): s for i, s in self.state.items()})

    def pending(self) -> list[int]:
        """Startable jobs: interrupted ones first, then pending ones, each in index order."""
        return ([i for i, s in self.state.items() if s == "interrupted"]
                + [i for i, s in self.state.items() if s == "pending"])

    def finished(self) -> bool:
        return self.running == 0 and not self.pending()

    def refresh(self, budget_gb: float) -> None:
        """Re-read the `#!` header after the file changed; job lines stay as picked up (their order is the index)."""
        try:
            mtime = self.path.stat().st_mtime
            if mtime == self.mtime:
                return
            self.mtime = mtime
            opts, jobs = parse_job_file(self.path)
        except (OSError, ValueError) as e:
            self.note = f"header not re-read: {e}"[:200]
            return
        if gpu_memory.oversized(opts["gpu_gb"], budget_gb):
            self.note = f"new gpu_gb={opts['gpu_gb']} ignored: can never fit the GPU budget"
            return
        self.opts = opts
        self.note = "" if jobs == self.jobs else "job lines changed after pickup: ignored (only the header is re-read)"


@dataclass
class Running:
    """A launched job. `size` / `quiet_since` track the last growth of its log for the hang detection."""
    proc: subprocess.Popen
    log: object
    path: Path
    offset: int              # log size after this attempt's header: earlier attempts' output is ignored
    t0: float
    start_utc: str
    size: int
    quiet_since: float
    gpu_gb: float              # declared GPU memory, booked while the job runs (memory guard)
    was: str                   # state before the launch ("interrupted"/"pending"), restored on a guard refusal
    tb_checked: bool = False   # tail already searched for a traceback in the current quiet period
    killed: str | None = None  # 'hung' / 'stalled' once killed; recorded when the process is reaped
    kill_note: str = ""
    kill_time: float = 0.0


def launch(jf: JobFile, idx: int, env: dict) -> Running:
    logdir = LOGS / jf.name
    logdir.mkdir(parents=True, exist_ok=True)
    path = logdir / f"job_{idx:03d}.log"
    log = path.open("a", encoding="utf-8")
    full = [sys.executable, str(GUARD), "--min-minutes", str(jf.opts["min_minutes"]),
            "--job-minutes", str(jf.opts["job_minutes"]), "--", *jf.jobs[idx]]
    log.write(f"# {now_iso()} {' '.join(full)}\n")
    log.flush()
    offset = path.stat().st_size
    proc = subprocess.Popen(full, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, env=env)
    t0 = time.monotonic()
    return Running(proc, log, path, offset, t0, now_iso(), offset, t0, float(jf.opts["gpu_gb"]), jf.state[idx])


def ends_in_traceback(job: Running) -> bool:
    """True if this attempt's output ends in an uncaught Python traceback (after which the child should have exited)."""
    try:
        with job.path.open("rb") as f:
            f.seek(max(job.offset, job.size - TAIL_BYTES))
            text = f.read().decode("utf-8", "replace")
    except OSError:
        return False
    i = text.rfind(TRACEBACK)
    lines = [ln for ln in text[i + len(TRACEBACK):].splitlines() if ln.strip()] if i >= 0 else []
    if not lines or lines[-1][:1].isspace():          # last line must be the unindented "SomeError: message"
        return False
    return all(ln[:1].isspace() or ln.startswith(CHAINED) for ln in lines[:-1])   # frames only, no later output


def hang_reason(jf: JobFile, job: Running, now: float) -> str | None:
    """'hung' or 'stalled' if the job is to be killed now, else None (also updates the log-growth bookkeeping)."""
    try:
        size = job.path.stat().st_size
    except OSError:
        return None
    if size != job.size:
        job.size, job.quiet_since, job.tb_checked = size, now, False
        return None
    quiet = now - job.quiet_since
    crash_s, stall_s = jf.opts["crash_minutes"] * 60, jf.opts["stall_minutes"] * 60
    if crash_s > 0 and quiet >= crash_s and not job.tb_checked:
        job.tb_checked = True                          # read the tail once per quiet period
        if ends_in_traceback(job):
            return "hung"
    if stall_s > 0 and quiet >= stall_s:
        return "stalled"
    return None


def request_kill(job: Running, reason: str, now: float) -> None:
    """Kill a hung job's guard and process tree; the collect step books it once the process is really gone."""
    quiet_min = (now - job.quiet_since) / 60
    job.killed, job.kill_time = reason, now
    job.kill_note = (f"traceback, then no exit for {quiet_min:.1f} min" if reason == "hung"
                     else f"no output for {quiet_min:.1f} min")
    _kill_tree(job.proc)


def record_kill(jf: JobFile, idx: int, job: Running) -> None:
    """Note a reaped kill in the job log and in guarded_runs.jsonl (the killed guard cannot write its own entry)."""
    try:
        job.log.write(f"\n# {now_iso()} gpu_daemon: killed as {job.killed} ({job.kill_note})\n")
        _log({"cmd": jf.jobs[idx], "start_utc": job.start_utc, "outcome": f"killed_{job.killed}",
              "exit_code": job.proc.returncode, "elapsed_s": round(time.monotonic() - job.t0, 1),
              "end_utc": now_iso(), "killed_by": "gpu_daemon", "queue_file": jf.name, "job": idx,
              "note": job.kill_note})
    except Exception as e:  # noqa: BLE001 - bookkeeping only: must never take the daemon (and every job) down
        print(f"[daemon] could not record the kill of {jf.name}#{idx}: {e!r}", flush=True)
    print(f"[daemon] {jf.name}#{idx} killed as {job.killed}: {job.kill_note}", flush=True)


def finish_file(jf: JobFile) -> None:
    DONE.mkdir(parents=True, exist_ok=True)
    summary = {"file": jf.path.name, "finished_utc": now_iso(), "jobs": len(jf.jobs),
               "done": sum(s == "done" for s in jf.state.values()),
               "failed": {str(i): s for i, s in jf.state.items() if s.startswith("failed")},
               "commands": {str(i): " ".join(c) for i, c in enumerate(jf.jobs)}}
    write_json(DONE / f"{jf.name}.summary.json", summary)
    os.replace(jf.path, DONE / jf.path.name)
    jf.progress_path.unlink(missing_ok=True)


def next_candidate(files: dict[str, JobFile], running: dict, max_workers: int) -> tuple[JobFile, int] | None:
    """Highest-priority startable job within the worker caps: interrupted jobs first, then name order."""
    if len(running) >= max_workers:
        return None
    ordered = sorted(files.values(), key=lambda j: j.name)
    for want in ("interrupted", "pending"):
        for jf in ordered:
            if jf.running >= min(int(jf.opts["workers"]), max_workers):
                continue
            idx = next((i for i in jf.pending() if jf.state[i] == want), None)
            if idx is not None:
                return jf, idx
    return None


class Daemon:
    """The loop state of one daemon instance; each round runs the small steps below (see step())."""

    def __init__(self, a: argparse.Namespace):
        self.a = a
        self.env = {k: v for k, v in os.environ.items() if k != "LAB_SESSION_DEADLINE_UTC"}
        self.env.setdefault("PYTHONUNBUFFERED", "1")   # prints reach the job log at once (hang detection watches it)
        self.files: dict[str, JobFile] = {}
        self.running: dict[tuple[str, int], Running] = {}
        self.probe = gpu_memory.GpuProbe().start()
        self.started = now_iso()
        self.paused_until = self.next_launch_at = 0.0
        self.idle_since = time.monotonic()
        self.stopping = self.draining = False
        self.waiting_files = 0                   # inbox files not read yet because they may still be being written
        self.blocked: str | None = None          # why the next job cannot start (memory guard), for status.json
        self.blocked_since: str | None = None

    def pick_up(self) -> None:
        """Load new job files in name order (a broken or never-fitting one is rejected); re-read changed headers."""
        waiting = 0
        for path in sorted(INBOX.glob("*.jobs")):
            if path.stem in self.files:
                continue
            try:
                if time.time() - path.stat().st_mtime < PICKUP_SETTLE_S:
                    waiting += 1                               # possibly still being written: next round
                    continue
            except OSError:
                waiting += 1                                   # vanished or locked right now: next round
                continue
            try:
                self.files[path.stem] = JobFile(path, self.a.gpu_budget_gb)
            except Exception as e:  # noqa: BLE001 - a broken file must not stop the others
                try:
                    DONE.mkdir(parents=True, exist_ok=True)
                    os.replace(path, DONE / (path.name + ".rejected"))
                    write_json(DONE / f"{path.stem}.summary.json", {"file": path.name, "rejected": str(e),
                                                                     "finished_utc": now_iso()})
                except Exception as e2:  # noqa: BLE001 - retried next round
                    print(f"[daemon] could not reject {path.name}: {e2!r}", flush=True)
        self.waiting_files = waiting                           # counts as work: no idle exit while files settle
        for jf in self.files.values():
            jf.refresh(self.a.gpu_budget_gb)

    def collect(self) -> None:
        """Book jobs whose guard has exited."""
        for key in [k for k, job in self.running.items() if job.proc.poll() is not None]:
            job = self.running.pop(key)
            jf = self.files[key[0]]
            jf.running -= 1
            rc = job.proc.returncode
            if job.killed:
                jf.state[key[1]] = f"failed:{job.killed}"      # hang kill: not retried
                record_kill(jf, key[1], job)
            elif rc == 0:
                jf.state[key[1]] = "done"
            elif rc == EXIT_REFUSED:
                jf.state[key[1]] = job.was                     # window closed, too little time or STOP: retry later
                self.paused_until = time.monotonic() + REFUSAL_PAUSE_SECONDS
            else:
                jf.state[key[1]] = f"failed:{rc}"
            try:                                               # in-memory state is booked; the files can follow later
                job.log.close()
                jf.save()
            except Exception as e:  # noqa: BLE001 - never let file I/O take the daemon (and every job) down
                print(f"[daemon] could not save {key[0]}#{key[1]}: {e!r}", flush=True)

    def check_hangs(self) -> None:
        """Kill jobs that crashed without exiting or stopped printing (module docstring); collect() books them."""
        now_m = time.monotonic()
        for key, job in self.running.items():
            if job.proc.poll() is not None:
                continue                                        # exited on its own: keep its real outcome
            try:
                if job.killed:
                    if now_m - job.kill_time >= KILL_RETRY_SECONDS:
                        job.kill_time = now_m
                        _kill_tree(job.proc)                    # the first kill did not take: again
                    continue
                reason = hang_reason(self.files[key[0]], job, now_m)
                if reason:
                    request_kill(job, reason, now_m)
            except Exception as e:  # noqa: BLE001 - the hang check must never take the daemon (and all jobs) down
                print(f"[daemon] hang check failed for {key[0]}#{key[1]}: {e!r}", flush=True)

    def launch_step(self) -> None:
        """Start at most one job per LAUNCH_SPACING_S if the caps and the memory guard allow it (never raises)."""
        now_m = time.monotonic()
        if self.stopping or self.draining or now_m < max(self.paused_until, self.next_launch_at):
            return
        reason = None
        try:
            cand = next_candidate(self.files, self.running, self.a.max_workers)
            if cand:
                jf, idx = cand
                booked = sum(job.gpu_gb for job in self.running.values())
                why = gpu_memory.admission(float(jf.opts["gpu_gb"]), booked, self.probe.latest(),
                                           gpu_memory.ram_status(), self.a.gpu_budget_gb)
                if why:
                    reason = f"{jf.name}#{idx}: {why}"          # strict priority: nothing behind it starts either
                else:
                    self.running[(jf.name, idx)] = launch(jf, idx, self.env)
                    jf.state[idx] = "running"
                    jf.running += 1
                    jf.save()
                    self.next_launch_at = now_m + LAUNCH_SPACING_S
        except Exception as e:  # noqa: BLE001 - a launch problem must never take the daemon (and all jobs) down
            reason = f"launch error: {e!r}"[:300]
            self.next_launch_at = now_m + LAUNCH_SPACING_S
        self.blocked = reason
        self.blocked_since = (self.blocked_since or now_iso()) if reason else None

    def retire(self) -> None:
        for name in [n for n, jf in self.files.items() if jf.finished() and jf.path.exists()]:
            try:
                finish_file(self.files[name])
                del self.files[name]
            except Exception as e:  # noqa: BLE001 - e.g. a locked target: stays queued, retried next round
                print(f"[daemon] could not retire {name}: {e!r}", flush=True)

    def write_status(self) -> None:
        now_m = time.monotonic()
        gpu, ram = self.probe.latest(), gpu_memory.ram_status()
        state = ("stopping" if self.stopping else "draining" if self.draining else
                 "paused_refused" if now_m < self.paused_until else "running" if self.running else "idle")
        write_json(STATUS, {
            "heartbeat_utc": now_iso(), "started_utc": self.started, "pid": os.getpid(), "state": state,
            "max_workers": self.a.max_workers, "features": FEATURES,
            "memory": {"budget_gb": self.a.gpu_budget_gb,
                       "booked_gb": round(gpu_memory.RESERVE_GB + sum(j.gpu_gb for j in self.running.values()), 1),
                       "gpu_dedicated_gb": None if gpu is None else round(gpu[0], 2),
                       "gpu_shared_gb": None if gpu is None else round(gpu[1], 2),
                       "probe_age_s": self.probe.age_s(), "probe_error": self.probe.error,
                       "ram_free_gb": None if ram is None else round(ram[0], 1),
                       "commit_headroom_gb": None if ram is None else round(ram[1], 1)},
            "admission": {"blocked": self.blocked, "since": self.blocked_since},
            "running": [{"file": f, "job": i, "cmd": " ".join(self.files[f].jobs[i]), "gpu_gb": job.gpu_gb,
                         "quiet_min": round((now_m - job.quiet_since) / 60, 1), "killed": job.killed}
                        for (f, i), job in self.running.items()],
            "files": {n: {"jobs": len(jf.jobs), "pending": len(jf.pending()),
                          "interrupted": sum(s == "interrupted" for s in jf.state.values()), "running": jf.running,
                          "done": sum(s == "done" for s in jf.state.values()),
                          "failed": sum(s.startswith("failed") for s in jf.state.values()),
                          "workers": jf.opts["workers"], "gpu_gb": jf.opts["gpu_gb"], "note": jf.note}
                      for n, jf in self.files.items()}})

    @staticmethod
    def _safe(what: str, fn) -> None:
        """Run one step; an exception is printed, never raised: if the daemon dies, its job object kills every job."""
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            print(f"[daemon] {what} failed: {e!r}", flush=True)

    def step(self) -> int | None:
        """One round of the loop; returns an exit code when the daemon should end."""
        self._safe("pick_up", self.pick_up)
        self.stopping = self.stopping or STOP_FILE.exists()
        self.draining = DRAIN.exists()
        self._safe("collect", self.collect)
        self._safe("check_hangs", self.check_hangs)
        self._safe("launch", self.launch_step)
        self._safe("retire", self.retire)
        busy = bool(self.running) or self.waiting_files > 0 or any(jf.pending() for jf in self.files.values())
        if busy:
            self.idle_since = time.monotonic()
        self._safe("status", self.write_status)
        if self.stopping and not self.running:
            return 0
        if self.draining and not self.running:
            DRAIN.unlink(missing_ok=True)
            return 0
        if not busy and (self.a.once or time.monotonic() - self.idle_since > self.a.idle_exit_min * 60):
            return 0
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--max-workers", type=int, default=DEFAULTS["workers"])
    ap.add_argument("--gpu-budget-gb", type=float, default=gpu_memory.BUDGET_GB,
                    help="GPU memory the daemon fills up to (dedicated + shared, incl. desktop apps)")
    ap.add_argument("--idle-exit-min", type=float, default=30.0)
    ap.add_argument("--once", action="store_true", help="exit as soon as the inbox is empty and nothing runs")
    a = ap.parse_args()
    for d in (INBOX, DONE, LOGS, PROGRESS):
        d.mkdir(parents=True, exist_ok=True)
    lock = acquire_lock()
    if lock is None:
        print("[daemon] another instance is running", flush=True)
        return 0
    _bind_to_job_object(None)   # if the daemon dies, its guards and their jobs die with it (no orphans, no duplicates)
    daemon = Daemon(a)
    while True:
        try:
            code = daemon.step()
        except Exception as e:  # noqa: BLE001 - last resort: dying would kill every running job (job object)
            print(f"[daemon] round failed: {e!r}", flush=True)
            code = None
        if code is not None:
            return code
        try:
            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            for job in daemon.running.values():
                _kill_tree(job.proc)
                job.log.close()
            return 130


if __name__ == "__main__":
    sys.exit(main())
