"""EXP-124 (session 55, draft): job lines. Units u0-u9 of R5, split E2_0, init seed from r5_uN.json. Arm T bans the unit's own
target set A (targets["0"], the E2_0 targets); arm C bans five frequencies drawn once per unit from 1..56 minus set A with
numpy default_rng([124, unit]) (fixed before any run). Prints the job file (header for the GPU daemon) to stdout.
  python lab/experiments/EXP-124-commutativity-ban/make_jobs.py > lab/experiments/EXP-124-commutativity-ban/jobs.txt
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PY = "C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe"
D = "lab/experiments/EXP-124-commutativity-ban"


def arms(u: int) -> dict[str, list[int]]:
    meta = json.loads((ROOT / f"lab/confirm/r5_splits/r5_u{u}.json").read_text(encoding="utf-8"))
    tgt = sorted(meta["targets"]["0"])
    pool = [k for k in range(1, 57) if k not in tgt]
    ctl = sorted(int(k) for k in np.random.default_rng([124, u]).choice(pool, 5, replace=False))
    return {"T": tgt, "C": ctl}


def main() -> None:
    print("#! workers=3 job_minutes=60 min_minutes=5 stall_minutes=15 crash_minutes=10 gpu_gb=1")
    for u in range(10):
        init = json.loads((ROOT / f"lab/confirm/r5_splits/r5_u{u}.json").read_text(encoding="utf-8"))["init"]
        for arm, ban in arms(u).items():
            print(f"{PY} {D}/ban_trace.py --seed {init} --split-file lab/confirm/r5_splits/r5_u{u}_E2_0.npy "
                  f"--test-file lab/confirm/r5_splits/r5_u{u}_test.npy --steps 8000 --device cuda --ban {','.join(map(str, ban))} "
                  f"--out {D}/raw/u{u}_{arm}")


if __name__ == "__main__":
    main()
