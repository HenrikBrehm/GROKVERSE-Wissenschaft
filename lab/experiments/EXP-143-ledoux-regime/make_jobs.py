"""EXP-143 (session 70, pilot): job file for the GPU service (rule 21), 4 arms x seed 14300 at add 9973, N = 300 000.
  python lab/experiments/EXP-143-ledoux-regime/make_jobs.py > lab/queue/staging/52a8_exp143_ledoux.jobs
Arms: R/F set x iid/stride order, batch 256, through lab/tools/freq_ban_large.py (eval every 1000, spectrum every 5000).
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
REL = "lab/experiments/EXP-143-ledoux-regime"
GPY = "C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe"
SEEDS = (14300,)
STEPS, STOP_AFTER, BATCH = 250_000, 5_000, 256
TF = repr(300_000 / 9973 ** 2)
HEADER = "#! workers=4 job_minutes=330 min_minutes=5 stall_minutes=0 crash_minutes=10 gpu_gb=2.5"


def line(seed: int, arm: str, order: str) -> str:
    split = f"{REL}/splits/split_add9973_n300000_seed{seed}_{arm}.npy"
    order_flag = "" if order == "iid" else f" --order {order}"
    return (f"{GPY} lab/tools/freq_ban_large.py --eval-every 1000 --spectrum-every 5000 -- --seed {seed} "
            f"--condition baseline --steps {STEPS} --stop-after-gen {STOP_AFTER} --threads 1 --device cuda --p 9973 "
            f"--task add --train-frac {TF} --split-file {split} --test-file {REL}/splits/test_add9973_n20000.npy "
            f"--batch-size {BATCH}{order_flag} --out-root {REL}/raw")


def main() -> None:
    for s in SEEDS:
        for arm in "FR":
            assert (HERE / "splits" / f"split_add9973_n300000_seed{s}_{arm}.npy").exists(), (s, arm)
    print(HEADER)
    for s in SEEDS:
        for arm, order in (("F", "iid"), ("R", "iid"), ("F", "stride"), ("R", "stride")):
            print(line(s, arm, order))


if __name__ == "__main__":
    main()
