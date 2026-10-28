#!/usr/bin/env python3
"""gpu_memory.py — memory probes and the admission rule of gpu_daemon.py (GPU-memory guard).

Why (user request 2026-09-29, lab/PROBLEME.md P-009): ten LM jobs of ~3.4 GB each were running on the 20 GB
RX 7900 XT at once; Windows spilled ~15 GB of GPU memory into RAM, the jobs ran 8x slower, RAM and commit ran out and
pagefile.sys grew by ~25 GB. The daemon knew nothing about GPU memory, and per-file worker caps add up across files.

Rule (checked before every launch): a job may start only if
    max(measured GPU demand, RESERVE_GB + declared gpu_gb of all running jobs) + its own gpu_gb <= budget,
no GPU memory is spilled into RAM, and enough RAM and commit are free. The declared sizes (`gpu_gb` in the job file
header) are the permanent book-keeping, so a burst of launches cannot overshoot while new jobs are still allocating;
the measurement is the extra brake for undeclared or growing jobs and for other programs (a game, the desktop).
"Demand" is DedicatedUsage + SharedUsage of the GPU adapter with the most dedicated memory in use (the second adapter
instance is the CPU's iGPU). If the measurement fails or is stale, only the book-keeping is used.

Measurement runs in a background thread (PowerShell CIM query, ~1-2 s), so it never blocks the daemon loop.
Tests: GROKVERSE_FAKE_MEMORY_FILE=<file with "dedicated_gb shared_gb ram_free_gb commit_free_gb"> replaces both probes.
"""
from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import threading
import time
from pathlib import Path

BUDGET_GB = 16.0            # default for --gpu-budget-gb: dedicated + shared incl. desktop apps (20 GB card, spill ~19)
RESERVE_GB = 2.5            # desktop apps and driver, added to the declared sizes (measured ~2 GB on 2026-09-29)
SPILL_GB = 3.0              # shared GPU memory above this = spilled into RAM -> no new launches (healthy: ~0.8 GB)
MIN_FREE_RAM_GB = 3.0
# Commit: each torch-ROCm process commits ~3 GB (plus driver-side commit), and Windows' system-managed pagefile grows
# only when a request needs it and shrinks again later - so the currently FREE commit is often ~1-7 GB in a healthy
# state (2026-09-29: 1.4 GB free with 3 jobs and 16.7 GB RAM free), and a guard on it would block forever. Use the
# headroom up to the largest limit the pagefile can grow to instead: RAM + min(3 x RAM, current pagefile + free disk).
PAGEFILE_MAX_FACTOR = 3.0   # system-managed pagefile: at most 3 x RAM
MIN_COMMIT_HEADROOM_GB = 8.0
PROBE_EVERY_S = 10.0
PROBE_MAX_AGE_S = 45.0      # an older measurement counts as failed -> book-keeping only
PROBE_TIMEOUT_S = 20.0
GB = 2 ** 30
FAKE = os.environ.get("GROKVERSE_FAKE_MEMORY_FILE")   # tests only
PS_QUERY = ("$m = Get-CimInstance Win32_PerfFormattedData_GPUPerformanceCounters_GPUAdapterMemory | "
            "Sort-Object DedicatedUsage -Descending | Select-Object -First 1; "
            "'{0} {1}' -f $m.DedicatedUsage, $m.SharedUsage")


def _fake_values() -> list[float]:
    return [float(x) for x in Path(FAKE).read_text(encoding="utf-8").split()]


def measure_gpu() -> tuple[float, float]:
    """(dedicated_gb, shared_gb) of the busiest GPU adapter; raises on any failure."""
    if FAKE:
        ded, shared = _fake_values()[:2]
        return ded, shared
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", PS_QUERY], capture_output=True,
                       text=True, timeout=PROBE_TIMEOUT_S, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    ded, shared = (float(x) / GB for x in r.stdout.split())
    return ded, shared


class _MemoryStatus(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def ram_status() -> tuple[float, float] | None:
    """(free RAM GB, commit headroom GB incl. possible pagefile growth), or None if unknown. Cheap (no subprocess)."""
    try:
        if FAKE:
            ram, headroom = _fake_values()[2:4]
            return ram, headroom
        st = _MemoryStatus(dwLength=ctypes.sizeof(_MemoryStatus))
        if not ctypes.WinDLL("kernel32").GlobalMemoryStatusEx(ctypes.byref(st)):
            return None
        used = st.ullTotalPageFile - st.ullAvailPageFile                  # commit charge
        pagefile = max(0, st.ullTotalPageFile - st.ullTotalPhys)          # current pagefile size (approx.)
        disk_free = shutil.disk_usage(os.environ.get("SystemDrive", "C:") + "\\").free
        limit = st.ullTotalPhys + min(PAGEFILE_MAX_FACTOR * st.ullTotalPhys, pagefile + disk_free)
        return st.ullAvailPhys / GB, (limit - used) / GB
    except Exception:  # noqa: BLE001 - unknown RAM state must not stop the daemon
        return None


class GpuProbe:
    """Measures the GPU adapter memory every PROBE_EVERY_S in a daemon thread; latest() never blocks."""

    def __init__(self) -> None:
        # single writer (the probe thread) replaces whole immutable values; attribute assignment is atomic in CPython,
        # so readers need no lock - do not turn these into in-place updates
        self._value: tuple[float, float, float] | None = None   # (monotonic time, dedicated_gb, shared_gb)
        self.error = ""
        self._thread = threading.Thread(target=self._loop, name="gpu-probe", daemon=True)

    def start(self) -> "GpuProbe":
        self._thread.start()
        return self

    def _loop(self) -> None:
        while True:
            try:
                ded, shared = measure_gpu()
                self._value, self.error = (time.monotonic(), ded, shared), ""
            except Exception as e:  # noqa: BLE001 - keep probing; a stale value falls back to book-keeping
                self.error = f"{type(e).__name__}: {e}"[:200]
            time.sleep(PROBE_EVERY_S)

    def latest(self) -> tuple[float, float] | None:
        """(dedicated_gb, shared_gb) if a measurement younger than PROBE_MAX_AGE_S exists, else None."""
        v = self._value
        if v is None or time.monotonic() - v[0] > PROBE_MAX_AGE_S:
            return None
        return v[1], v[2]

    def age_s(self) -> float | None:
        v = self._value
        return None if v is None else round(time.monotonic() - v[0], 1)


def admission(new_gb: float, booked_gb: float, gpu: tuple[float, float] | None,
              ram: tuple[float, float] | None, budget_gb: float) -> str | None:
    """None if a job declaring new_gb may start now, else the reason why not.

    booked_gb: declared gpu_gb of all running jobs. gpu: latest measurement or None. ram: ram_status() or None.
    """
    book = RESERVE_GB + booked_gb
    demand = book if gpu is None else max(book, gpu[0] + gpu[1])   # measured below the books: jobs still allocating
    if demand + new_gb > budget_gb:
        return f"gpu {demand:.1f}+{new_gb:.1f}>{budget_gb:.1f} GB" + ("" if gpu else " (no measurement, books only)")
    if gpu is not None and gpu[1] > SPILL_GB:
        return f"gpu memory spilled into RAM ({gpu[1]:.1f} GB shared)"
    if ram is not None and ram[0] < MIN_FREE_RAM_GB:
        return f"RAM {ram[0]:.1f} GB free"
    if ram is not None and ram[1] < MIN_COMMIT_HEADROOM_GB:
        return f"commit headroom {ram[1]:.1f} GB"
    return None


def oversized(gpu_gb: float, budget_gb: float) -> bool:
    """A job that can never fit, even on an otherwise empty card."""
    return RESERVE_GB + gpu_gb > budget_gb
