"""EXP-102 (rule 20e, LM ladder stage 1, pilot = exploration): splits and job lines. Session 44, UNTESTED.

add 113, 30 % data. Per seed an engineered split pair F/G built exactly like P1/EXP-053 (omega = 0, calibrated eps,
overlap_split.build with its own target draw) and a uniform random split R of the same size from the same pool.
Seeds 3800-3809 (checked in session 44: no other experiment or registration names 3800-3999).

Rungs (one switch each, run on F and G; R only where named):
  r0     all off (study setup; reference, must match freq_ban.py statistically)
  op     --op-token
  fs     --full-softmax
  tie    --full-softmax --tie              (tying needs the full vocabulary as output; answer loss)
  all    --full-softmax --loss all
  allnb  --full-softmax --loss all_but_b   (control: pair structure p(b|a) of the train set is not a target)
  R: all and allnb (p(b|a) is ~uniform on a random split, the difference should vanish there)
Minibatch (rung 4) follows after L0 with the batch size chosen there. Budget 2000 steps (P1 reads Delta_pow at 2000).

Why the allnb control (session 44). CORRECTED after pba_spectrum_s44.py (computed before any run): the pair weight is
1 + eps * mean_k cos(2 pi k a / p + phi_k(a + b)); at fixed b the conditional p(b | a) carries NO target power over a
(share 0.088, chance 0.089), the target structure sits in (a, c) coordinates (0.18) and in the marginals (count(b): 0.225,
count(a): 0.165 on the F targets; R: 0.074 / 0.089). With loss on all positions the model must predict b after "a (+)",
so it learns the target-structured marginal p(b), mostly in the output layer; with tied embeddings (a real LM ties and
predicts every position) that goes straight into W_E. Hence the pair tieall / tieallnb in addition to all / allnb.

  python lab/experiments/EXP-102-lm-ladder-stage1/design.py            # splits -> splits/ (never overwrites)
  python lab/experiments/EXP-102-lm-ladder-stage1/design.py --jobs     # pilot job lines
  python lab/experiments/EXP-102-lm-ladder-stage1/design.py --smoke    # seed 3800, 50 steps, every rung, raw_smoke
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-053-p3-overlap-design"))
import overlap_split as ov  # noqa: E402

SEEDS = tuple(range(3800, 3810))
SALT = 102_100
STEPS = 2000
RUNGS = {"r0": "", "op": "--op-token", "fs": "--full-softmax", "tie": "--full-softmax --tie",
         "all": "--full-softmax --loss all", "allnb": "--full-softmax --loss all_but_b",
         "tieall": "--full-softmax --tie --loss all", "tieallnb": "--full-softmax --tie --loss all_but_b"}   # s44, see below
R_RUNGS = ("all", "allnb", "tieall", "tieallnb")
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
REL = "lab/experiments/EXP-102-lm-ladder-stage1"


def build(seed: int) -> dict:
    eps = json.loads((LAB / "experiments/EXP-053-p3-overlap-design/calibration.json").read_text(encoding="utf-8"))["levels"]["0.0"]["eps"]
    d = ov.build(seed, 0.0, eps)
    pool = np.setdiff1d(np.arange(ov.P * ov.P), d["test"])
    d["R"] = np.sort(np.random.default_rng(np.random.SeedSequence([SALT, seed, 1])).choice(pool, ov.N_TRAIN, replace=False))
    return d


def write_splits() -> None:
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    for s in SEEDS:
        d, (F, G) = build(s), ov.targets(s)
        for arm, key in (("F", "A"), ("G", "B"), ("R", "R")):
            assert len(d[key]) == ov.N_TRAIN and not np.intersect1d(d[key], d["test"]).size
            with open(out / f"seed{s}_{arm}.npy", "xb") as f:
                np.save(f, d[key].astype(np.int64))
        meta = {"seed": s, "targets": {"F": F, "G": G}, "share_F_F": ov.share(d["A"], F), "share_G_G": ov.share(d["B"], G),
                "share_R_F": ov.share(d["R"], F), "share_R_G": ov.share(d["R"], G)}
        with open(out / f"seed{s}.json", "x", encoding="utf-8") as f:
            json.dump(meta, f, indent=1)
    print(f"[exp102] wrote splits for {len(SEEDS)} seeds", flush=True)


def line(s: int, split: str, rung: str, steps: int = STEPS, root: str = "raw") -> str:
    flags = RUNGS[rung]
    return (f"{PY} {REL}/lm_ladder.py --seed {s} --split-file {REL}/splits/seed{s}_{split}.npy --steps {steps} "
            f"--device cuda --threads 1 --out-root {REL}/{root}" + (f" {flags}" if flags else ""))


def jobs() -> list[str]:
    return [line(s, x, r) for s in SEEDS for r in RUNGS for x in "FG"] + [line(s, "R", r) for s in SEEDS for r in R_RUNGS]


def smoke() -> list[str]:
    return [line(SEEDS[0], "F", r, steps=50, root="raw_smoke") for r in RUNGS]


if __name__ == "__main__":
    arg = sys.argv[1:]
    if arg == ["--jobs"]:
        print("\n".join(jobs()))
    elif arg == ["--smoke"]:
        print("\n".join(smoke()))
    elif not arg:
        write_splits()
    else:
        raise SystemExit(__doc__)
