"""EXP-100 (L0 pilot, exploration; rule 20b): set composition vs data order under minibatch training. README.md (draft).
Session 43, UNTESTED. Needs the trainer options of trainer_l0.patch (--batch-size, --order, --optimizer sgdm).

add 113. Per seed: engineered split pair F/G built exactly like EXP-053/P1 (omega = 0, calibrated eps) but with target sets
drawn WITHOUT the stride-order frequencies O = {11, 12, 22, 23, 34, 45} (spectrum of a mod 10 on Z_113, session 43), and a
uniform random split R of the same size from the same pool (same test set). Own streams: SeedSequence([100100, seed, purpose]).
Arms (F and G each, R only where named):
  fb        full batch, AdamW, 2000 steps (P1 reference)
  fb30k     full batch, AdamW, 30 000 steps (budget-matched reference; review s43)
  iid256    batch 256, iid order, AdamW, 30 000 steps (2000 epochs)
  iid64     batch 64,  iid order, AdamW, 30 000 steps (500 epochs)
  sgdm256   batch 256, iid order, SGD momentum 0.9, lr SGD_LR (set after the calibration), 30 000 steps
  stride256 batch 256, stride order (a mod 10, a), AdamW, 30 000 steps (conflict arm)
  R: iid256 and stride256 (order alone on a random split)
Every run: --stop-after-gen = budget (fixed budget), W_E snapshots at 0, 50, 250, 2000, every 2500 steps and at the end.
Smoke, calibration and feasibility write to their own out-roots (raw_smoke, raw_calib, raw_feas): same run ids as the pilot
would otherwise be skipped or refused and would leak into the pilot (review s43, blocker).

  python lab/experiments/EXP-100-set-vs-order/design.py            # splits -> splits/, never overwrites
  python lab/experiments/EXP-100-set-vs-order/design.py --calib    # SGD lr calibration jobs (seeds 3700-3701, split F)
  python lab/experiments/EXP-100-set-vs-order/design.py --jobs     # all pilot jobs (refuses while SGD_LR is None, unless SGD_DROPPED)
  python lab/experiments/EXP-100-set-vs-order/design.py --smoke    # seed 3700: one short job per new option combination
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

SEEDS = tuple(range(3700, 3708))
O = (11, 12, 22, 23, 34, 45)
SALT = 100_100
FB_STEPS, MB_STEPS = 2000, 30_000
SGD_LRS = (0.03, 0.1, 0.3, 1.0, 3.0)   # calibration grid (widened, review s43)
SGD_LR: float | None = None      # set from the calibration before the pilot (documented in the README)
SGD_DROPPED = False              # s44: True if no calibration lr generalises -> sgdm256 leaves the arms (README: 'nicht auswertbar')
ARMS = {"fb": (0, "iid", "adamw", FB_STEPS), "fb30k": (0, "iid", "adamw", MB_STEPS), "iid256": (256, "iid", "adamw", MB_STEPS), "iid64": (64, "iid", "adamw", MB_STEPS),
        "sgdm256": (256, "iid", "sgdm", MB_STEPS), "stride256": (256, "stride", "adamw", MB_STEPS)}
R_ARMS = ("iid256", "stride256")
FEAS_EXTRA = {"stride64": (64, "stride", "adamw", MB_STEPS)}   # s44: first-order window prediction -> feasibility also at B = 64
FEAS_B16 = {"iid16": (16, "iid", "adamw", MB_STEPS), "stride16": (16, "stride", "adamw", MB_STEPS)}   # s45 (simulated review,
# before any run): B = 256/64 are 15/60 steps per epoch, far from LeDoux's ~1170; first order at B = 16 (240 steps per epoch):
# order excess 0.194 at L = 50, twice the set's target excess (firstorder_window_s45_b16.json). Feasibility only; kept OUT of
# FEAS_EXTRA so that CONFLICT_B64 does not pull B = 16 into the pilot. A B = 16 conflict arm needs its own switch + code later.
FEAS_ARMS = ("iid256", "stride256", "iid64", "stride64", "iid16", "stride16")
CONFLICT_B64 = False   # s44: set True (and record in the README) if feas_read.py shows an order effect only at B = 64
ALL_ARMS = dict(ARMS)            # s44: unchanged lookup for calib()/smoke(), also after SGD_DROPPED
if SGD_DROPPED:
    ARMS = {k: v for k, v in ARMS.items() if k != "sgdm256"}
if CONFLICT_B64:       # one switch: conflict arm stride64 on F/G and the R pair iid64/stride64 (review s44: R_ARMS must grow too)
    ARMS = {**ARMS, **FEAS_EXTRA}
    R_ARMS = R_ARMS + ("iid64", "stride64")
ROOTS = {"fb30k": "raw_fb30k"}   # plan review s43 (blocker): fb and fb30k have the same run id (steps are not in it)
PY = (LAB.parent / ".venv-gpu/Scripts/python.exe").as_posix()
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
REL = "lab/experiments/EXP-100-set-vs-order"


def rng(seed: int, purpose: int) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([SALT, seed, purpose]))


def targets(seed: int) -> tuple[list[int], list[int]]:
    ks = rng(seed, 0).permutation([k for k in range(1, (ov.P - 1) // 2 + 1) if k not in O])
    return sorted(int(k) for k in ks[:ov.M]), sorted(int(k) for k in ks[ov.M:2 * ov.M])


def build(seed: int) -> dict:
    eps = json.loads((LAB / "experiments/EXP-053-p3-overlap-design/calibration.json").read_text(encoding="utf-8"))["levels"]["0.0"]["eps"]
    keep = ov.targets
    try:
        ov.targets = targets                    # same construction as P1/EXP-053, only the target draw excludes O
        d = ov.build(seed, 0.0, eps)
    finally:
        ov.targets = keep
    pool = np.setdiff1d(np.arange(ov.P * ov.P), d["test"])
    d["R"] = np.sort(rng(seed, 1).choice(pool, ov.N_TRAIN, replace=False))
    return d


def write_splits() -> None:
    out = HERE / "splits"
    out.mkdir(exist_ok=True)
    for s in SEEDS:
        d, (F, G) = build(s), targets(s)
        assert not set(F) & set(G) and not (set(F) | set(G)) & set(O)
        for arm, key in (("F", "A"), ("G", "B"), ("R", "R")):
            assert len(d[key]) == ov.N_TRAIN and not np.intersect1d(d[key], d["test"]).size
            with open(out / f"seed{s}_{arm}.npy", "xb") as f:
                np.save(f, d[key].astype(np.int64))
        with open(out / f"seed{s}_test.npy", "xb") as f:
            np.save(f, d["test"].astype(np.int64))
        meta = {"seed": s, "targets": {"F": F, "G": G}, "order_freqs": list(O), "share_F_F": ov.share(d["A"], F),
                "share_G_G": ov.share(d["B"], G), "share_R_F": ov.share(d["R"], F), "share_O": {a: ov.share(d[k], list(O))
                                                                                               for a, k in (("F", "A"), ("G", "B"), ("R", "R"))}}
        with open(out / f"seed{s}.json", "x", encoding="utf-8") as f:
            json.dump(meta, f, indent=1)
    print(f"[exp100] wrote splits for {len(SEEDS)} seeds", flush=True)


def line(s: int, split: str, arm: str, sgd_lr: float | None = None, steps: int | None = None, root: str = "raw") -> str:
    bs, order, opt, budget = {**ALL_ARMS, **ARMS, **FEAS_EXTRA, **FEAS_B16}[arm]
    budget = steps or budget
    spec = ",".join(str(x) for x in sorted({50, 250, 2000, budget} | set(range(2500, budget + 1, 2500))))
    cmd = (f"{PY} {FB} --seed {s} --condition baseline --threads 1 --device cuda --test-file {REL}/splits/seed{s}_test.npy "
           f"--out-root {REL}/{root} --split-file {REL}/splits/seed{s}_{split}.npy --steps {budget} --stop-after-gen {budget} "
           f"--spectra-at {spec}")
    if bs:
        cmd += f" --batch-size {bs}" + (f" --order {order}" if order != "iid" else "")
    if opt == "sgdm":
        if sgd_lr is None:
            raise SystemExit("SGD_LR is not set: run the calibration first and record the choice in the README")
        cmd += f" --optimizer sgdm --sgd-lr {sgd_lr} --sgd-momentum 0.9"
    return cmd


def calib() -> list[str]:
    """Choose the SMALLEST lr of the grid that generalises (test >= 0.95) in BOTH seeds within 50 % of the budget."""
    return [line(s, "F", "sgdm256", lr, root="raw_calib") for s in SEEDS[:2] for lr in SGD_LRS]


def feas() -> list[str]:
    """Feasibility before the block (review s43): does the stride order move anything at 30 % data? R-stride vs R-iid, 3 seeds.
    Pre-set rule: if o(R-stride) - o(R-iid) <= 0.02 in all 3 seeds and no peak lies in O, the conflict arm is run in a
    second, order-favouring regime as well (train fraction 0.05 is NOT possible with the P1 splits; use --batch-size 64 stride)
    and the README records this before the block."""
    # session 44 (before any run): also B = 64 (iid vs stride), since the first-order window prediction
    # (firstorder_window_s44.py) says the order is washed out at B = 256 and can act only at B = 64; read with feas_read.py
    return [line(s, "R", arm, root="raw_feas") for s in SEEDS[:3] for arm in FEAS_ARMS]


def jobs() -> list[str]:
    out = [line(s, x, arm, SGD_LR, root=ROOTS.get(arm, "raw")) for s in SEEDS for arm in ARMS for x in "FG"]
    return out + [line(s, "R", arm) for s in SEEDS for arm in R_ARMS]


SWITCH_T = (25, 50)          # s44: secondary L0 part (rule 20b): data switch F -> G / G -> F under minibatch
SWITCH_ARMS = ("fb", "iid256")


def switch_jobs() -> list[str]:
    """Switch at t in SWITCH_T, then the arm's budget (total budget + t, as N28), both directions, pilot seeds; own root
    raw_switch. The pure F/G runs of the same seed and arm come from the pilot block (raw). Read with switch_analyze.py."""
    out = []
    for s in SEEDS:
        for arm in SWITCH_ARMS:
            budget = ARMS[arm][3]
            for t in SWITCH_T:
                for first, second in (("F", "G"), ("G", "F")):
                    out.append(line(s, first, arm, steps=budget + t, root="raw_switch")
                               + f" --switch-split-file {REL}/splits/seed{s}_{second}.npy --switch-step {t}")
    return out


def smoke() -> list[str]:
    s = SEEDS[0]
    return [line(s, "F", "iid256", steps=300, root="raw_smoke"), line(s, "F", "stride256", steps=300, root="raw_smoke"),
            line(s, "F", "sgdm256", 0.1, steps=300, root="raw_smoke")]


if __name__ == "__main__":
    arg = sys.argv[1:]
    if arg == ["--jobs"]:
        print("\n".join(jobs()))
    elif arg == ["--calib"]:
        print("\n".join(calib()))
    elif arg == ["--switch"]:
        print("\n".join(switch_jobs()))
    elif arg == ["--feas"]:
        print("\n".join(feas()))
    elif arg == ["--smoke"]:
        print("\n".join(smoke()))
    elif not arg:
        write_splits()
    else:
        raise SystemExit(__doc__)
