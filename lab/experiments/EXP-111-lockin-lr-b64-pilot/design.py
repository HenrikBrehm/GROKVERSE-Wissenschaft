"""EXP-111 (N54c power pilot, exploration; session 47, written before any EXP-111 run): at batch 64, is lock-in slower at lr 4e-3
than at 2e-3 (EXP-110 on seeds 3700-3701)? Seeds 3702-3703 (seen at lr 1e-3 in EXP-100/107/108, never at 2e-3/4e-3), EXP-100 splits,
i.i.d. minibatch AdamW, wd 1, B 64, lr 2e-3 and 4e-3, pure F/G and switches F->G, G->F on a denser grid; every run 5000 steps.
Reading (README): per seed d = log t_half(4e-3) - log t_half(2e-3); descriptive, used for the N54c power estimate.
  python lab/experiments/EXP-111-lockin-lr-b64-pilot/design.py --jobs > lab/experiments/EXP-111-lockin-lr-b64-pilot/jobs.txt
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
SPL = "lab/experiments/EXP-100-set-vs-order/splits"
REL = "lab/experiments/EXP-111-lockin-lr-b64-pilot"
SEEDS = (3702, 3703)
LRS = (2e-3, 4e-3)
BS = 64
GRID = (100, 150, 200, 250, 300, 350, 400, 500)
TOTAL = 5000


def base(s: int, split: str, lr: float) -> str:
    return (f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --test-file {SPL}/seed{s}_test.npy "
            f"--out-root {REL}/raw --split-file {SPL}/seed{s}_{split}.npy --steps {TOTAL} --stop-after-gen {TOTAL} --lr {lr!r}"
            f" --batch-size {BS}")


def jobs() -> list[str]:
    out = []
    for lr in LRS:
        for s in SEEDS:
            out += [base(s, x, lr) + f" --spectra-at 50,250,2000,2500,{TOTAL}" for x in "FG"]
            for t in GRID:
                for a, b in (("F", "G"), ("G", "F")):
                    spec = ",".join(str(x) for x in sorted({50, 250, t, 2000, 2500, TOTAL}))
                    out.append(base(s, a, lr) + f" --spectra-at {spec} --switch-split-file {SPL}/seed{s}_{b}.npy --switch-step {t}")
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["--jobs"]:
        print("\n".join(jobs()))
    else:
        raise SystemExit(__doc__)
