"""EXP-128 pilot (full-batch SGD with momentum + global gradient-norm clipping) job lines for the GPU daemon (rule 21). Session 59, written
before any clipped pilot run. Trainer: freq_ban_sgdclip.py = freq_ban.py at 267fde1e + trainer_sgdclip.patch (copy, because freq_ban.py is
hash-bound by R12 until its analysis). EXP-126 setup otherwise unchanged: EXP-100 splits F/G of seeds 3704-3707, lr 0.1, momentum 0.9,
20 000 steps without early stop, same spectra steps. Two clipping values, both derived from the calibration run (README):
C_A = 0.017 (pre-set rule: median norm of steps 1-200), C_B = 0.1 (about 3x the largest measured pre-divergence norm, clips only spikes).
  python lab/experiments/EXP-128-sgd-clip/make_jobs.py > lab/queue/staging/46_exp128_sgdclip.jobs   (then mv into lab/queue/inbox)
"""
from __future__ import annotations

from pathlib import Path

LAB = Path(__file__).resolve().parents[2]
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
FB = "lab/experiments/EXP-128-sgd-clip/freq_ban_sgdclip.py"
SPL = "lab/experiments/EXP-100-set-vs-order/splits"
REL = "lab/experiments/EXP-128-sgd-clip"
SEEDS, CLIPS, LR, STEPS = (3704, 3705, 3706, 3707), (0.017, 0.1), 0.1, 20_000
SPEC = ",".join(str(x) for x in sorted({50, 250, 2000} | set(range(2500, STEPS + 1, 2500))))


def lines() -> list[str]:
    return [f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --test-file {SPL}/seed{s}_test.npy "
            f"--out-root {REL}/raw --split-file {SPL}/seed{s}_{x}.npy --steps {STEPS} --stop-after-gen {STEPS} --spectra-at {SPEC} "
            f"--optimizer sgdm --sgd-lr {LR} --sgd-momentum 0.9 --sgd-clip {c}"
            for c in CLIPS for s in SEEDS for x in "FG"]


if __name__ == "__main__":
    print("#! workers=4 job_minutes=120 min_minutes=5 crash_minutes=10 gpu_gb=0.75")
    print("\n".join(lines()))
