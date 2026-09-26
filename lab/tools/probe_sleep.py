"""Harmless probe job for the guard acceptance (Astra point 1, rule 18b1): write own PID to a file, then sleep.

    python lab/tools/probe_sleep.py <pid-file> <seconds>

The PID written is that of the real interpreter (for a venv on Windows: the child of the venv launcher),
so the acceptance script can check that exactly this process dies with the guard.
"""
import os
import sys
import time

if __name__ == "__main__":
    pid_file, seconds = sys.argv[1], float(sys.argv[2])
    with open(pid_file, "w", encoding="ascii") as f:
        f.write(str(os.getpid()))
    time.sleep(seconds)
