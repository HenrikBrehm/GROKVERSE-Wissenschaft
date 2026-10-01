"""EXP-144 (session 71, pilot): EXP-143 at 4x width (d_model 512, as P4/EXP-049) - job file for the GPU service (rule 21).
  python lab/experiments/EXP-144-ledoux-width/make_jobs.py > lab/queue/staging/52a7zzz_exp144_width.jobs
Same splits, seed, batch, wd 0.1 and budget as the primary EXP-143 set; only --d-model 512 (wrapper flag) differs.
Order of lines = priority inside the file: F-iid, R-iid (Q1), then R-stride, F-stride (Q2, Q3).
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPL = "lab/experiments/EXP-143-ledoux-regime/splits"
OUT = "lab/experiments/EXP-144-ledoux-width/raw"
GPY = "C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe"
SEED, STEPS, STOP_AFTER, BATCH, WD, D = 14300, 250_000, 5_000, 256, "0.1", 512
TF = repr(300_000 / 9973 ** 2)
HEADER = "#! workers=4 job_minutes=600 min_minutes=5 stall_minutes=0 crash_minutes=10 gpu_gb=5"


def line(arm: str, order: str) -> str:
    order_flag = "" if order == "iid" else f" --order {order}"
    return (f"{GPY} lab/tools/freq_ban_large.py --eval-every 1000 --spectrum-every 2500 --d-model {D} -- --seed {SEED} "
            f"--condition baseline --steps {STEPS} --stop-after-gen {STOP_AFTER} --threads 1 --device cuda --p 9973 "
            f"--task add --train-frac {TF} --split-file {SPL}/split_add9973_n300000_seed{SEED}_{arm}.npy "
            f"--test-file {SPL}/test_add9973_n20000.npy --batch-size {BATCH}{order_flag} --weight-decay {WD} --out-root {OUT}")


def main() -> None:
    for arm in "FR":
        assert (ROOT / SPL / f"split_add9973_n300000_seed{SEED}_{arm}.npy").exists(), arm
    print(HEADER)
    for arm, order in (("F", "iid"), ("R", "iid"), ("R", "stride"), ("F", "stride")):
        print(line(arm, order))


if __name__ == "__main__":
    main()
