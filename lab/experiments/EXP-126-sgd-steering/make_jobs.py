"""EXP-126 (is split steering K2 an Adam artefact?) job lines for the GPU daemon (rule 21). Session 57, written before any run.
Full-batch SGD with momentum 0.9 (freq_ban --optimizer sgdm; weight decay decoupled and matched to AdamW's lr*wd = 1e-3 per step, as in
L0), learning rates 0.05 and 0.1, on the EXP-100 splits F/G (common init and test set per seed) of seeds 3704-3707, 20 000 steps without
early stop, spectra at 50, 250, 2000 and every 2500 steps. Unchanged trainer. Own out-root.
  python lab/experiments/EXP-126-sgd-steering/make_jobs.py > lab/queue/staging/43z_exp126_sgd.jobs   (then mv into lab/queue/inbox)
"""
from __future__ import annotations

from pathlib import Path

LAB = Path(__file__).resolve().parents[2]
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
SPL = "lab/experiments/EXP-100-set-vs-order/splits"
REL = "lab/experiments/EXP-126-sgd-steering"
SEEDS, LRS, STEPS = (3704, 3705, 3706, 3707), (0.05, 0.1), 20_000
SPEC = ",".join(str(x) for x in sorted({50, 250, 2000} | set(range(2500, STEPS + 1, 2500))))


def lines() -> list[str]:
    return [f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --test-file {SPL}/seed{s}_test.npy "
            f"--out-root {REL}/raw --split-file {SPL}/seed{s}_{x}.npy --steps {STEPS} --stop-after-gen {STEPS} --spectra-at {SPEC} "
            f"--optimizer sgdm --sgd-lr {lr} --sgd-momentum 0.9"
            for lr in LRS for s in SEEDS for x in "FG"]


if __name__ == "__main__":
    print("#! workers=4 job_minutes=120 min_minutes=5 crash_minutes=10 gpu_gb=0.75")
    print("\n".join(lines()))
