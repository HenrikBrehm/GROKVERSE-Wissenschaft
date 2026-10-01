"""EXP-138 (session 67, pilot): under clipped full-batch SGD with momentum (R13 settings), does the split steer the W_E spectrum
through its pair structure or through its token counts? EXP-047 splits (eng = engineered, shuf = same a/b counts, pair structure
destroyed), seeds 150-153, arms F/G, clip 0.1 and 0.017, 2000 steps. Prints the job file for the GPU service (rule 21).
  python lab/experiments/EXP-138-sgd-shuf/make_jobs.py > lab/queue/staging/50_exp138_sgd_shuf.jobs
"""
SEEDS = (150, 151, 152, 153)
KINDS = ("eng", "shuf")
CLIPS = (0.1, 0.017)
GPY = "C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe"
FBS = "lab/experiments/EXP-128-sgd-clip/freq_ban_sgdclip.py"
SPL = "lab/experiments/EXP-047-marginal-control/splits"
HEADER = "#! workers=4 job_minutes=30 min_minutes=1 stall_minutes=0 crash_minutes=10 gpu_gb=0.75"


def lines() -> list[str]:
    out = [HEADER]
    for c in CLIPS:
        for s in SEEDS:
            for k in KINDS:
                for a in "FG":
                    out.append(f"{GPY} {FBS} --seed {s} --condition baseline --steps 2000 --stop-after-gen 100000 --threads 1 "
                               f"--device cuda --split-file {SPL}/split_add113_seed{s}_{k}_{a}.npy --spectra-at 250,2000 "
                               f"--optimizer sgdm --sgd-lr 0.1 --sgd-momentum 0.9 --sgd-clip {c!r} "
                               f"--out-root lab/experiments/EXP-138-sgd-shuf/raw")
    return out


if __name__ == "__main__":
    print("\n".join(lines()))
