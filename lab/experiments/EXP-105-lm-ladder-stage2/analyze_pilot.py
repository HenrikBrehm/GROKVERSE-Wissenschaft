"""EXP-105 pilot analysis (exploration; session 48, written before any pilot run; readings as in README 'Pilotplan').
Input: pairs of runs (F, G) per seed under --root, found by run-id prefix 'lm2_seed{S}_{stem}_steps{N}_'.
Delta_pow on the 113 number-token rows of the tied embedding (EXP-102 analyze.power), at every snapshot; target sets
from the split metadata (EXP-102: splits/seed{s}.json targets F/G; EXP-104: s{s}_F_m10.json targets / other_targets).
Readings at the end of the budget:
  'K2 haelt im LM'       Delta_pow > 1 in both seeds and held-out accuracy > 0.5 in >= 3 of 4 runs
  'nur Repraesentation'  Delta_pow > 1 in both seeds and held-out accuracy < 0.1 in >= 3 of 4 runs
  'bricht'               |Delta_pow| <= 1 in both seeds
  else 'unklar'
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-105-lm-ladder-stage2/analyze_pilot.py \
      --root lab/experiments/EXP-105-lm-ladder-stage2/raw_pilot --pairs 3860:SPLITDIR/seed3800_F.npy,SPLITDIR/seed3800_G.npy ...
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-102-lm-ladder-stage1"))
import analyze as A  # noqa: E402


def targets(split: Path) -> list[int]:
    """Targets of the arm whose split file this is."""
    meta = split.with_suffix(".json")
    if meta.exists():                                                    # EXP-104 style
        return json.loads(meta.read_text(encoding="utf-8"))["targets"]
    seed, arm = split.stem.replace("seed", "").split("_")               # EXP-102 style seed3800_F
    return json.loads((split.parent / f"seed{seed}.json").read_text(encoding="utf-8"))["targets"][arm]


def load(root: Path, seed: int, split: Path) -> dict:
    ds = [d for d in root.iterdir() if d.name.startswith(f"lm2_seed{seed}_{split.stem}_steps")]
    assert len(ds) == 1, (seed, split, ds)
    r = json.loads((ds[0] / "result.json").read_text(encoding="utf-8"))
    assert r["status"] == "completed" and r["steps_completed"] == r["config"]["steps"], ds[0]
    W, S = np.load(ds[0] / "we_snapshots.npy"), [int(x) for x in np.load(ds[0] / "we_snapshot_steps.npy")]
    assert np.isfinite(W).all()
    return {"P": {s: A.power(W[i]) for i, s in enumerate(S)}, "steps": S, "res": r}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--pairs", nargs="+", required=True, help="SEED:F_SPLIT,G_SPLIT")
    a = ap.parse_args()
    root, rows = Path(a.root), []
    for spec in a.pairs:
        seed, files = spec.split(":")
        fF, fG = (Path(x) for x in files.split(","))
        TF, TG = targets(fF), targets(fG)
        rF, rG = load(root, int(seed), fF), load(root, int(seed), fG)
        cF, cG = rF["res"]["config"], rG["res"]["config"]
        diff = [k for k in cF if k not in ("split_sha256",) and cF[k] != cG.get(k)]
        assert not diff, (seed, "F and G differ in", diff)                  # same test set, steps, hyperparameters, script
        common = [s for s in rF["steps"] if s in rG["P"]]
        traj = {s: A.delta_pow(rF["P"][s], rG["P"][s], TF, TG) for s in common}
        end = common[-1]
        rows.append({"seed": int(seed), "dpow_end": traj[end], "end_step": end,
                     "dpow_traj": {str(s): v for s, v in traj.items()},
                     "test_acc": [rF["res"]["curve"][-1][2], rG["res"]["curve"][-1][2]],
                     "train_acc": [rF["res"]["curve"][-1][1], rG["res"]["curve"][-1][1]],
                     "val_loss": [rF["res"]["curve"][-1][3], rG["res"]["curve"][-1][3]],
                     "arith_share": rF["res"]["arith_token_share"], "fact_rounds": rF["res"]["fact_rounds"],
                     "gen": [rF["res"]["events"].get("generalization_step"), rG["res"]["events"].get("generalization_step")]})
    dp = [r["dpow_end"] for r in rows]
    acc = [x for r in rows for x in r["test_acc"]]
    n = len(acc)
    big = all(d is not None and d > 1 for d in dp)
    reading = ("K2 haelt im LM" if big and sum(x > 0.5 for x in acc) >= n - 1 else
               "nur Repraesentation" if big and sum(x < 0.1 for x in acc) >= n - 1 else
               "bricht" if all(d is not None and abs(d) <= 1 for d in dp) else "unklar")
    out = {"reading": reading, "rows": rows}
    (root / "pilot_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({"reading": reading, "rows": [{k: v for k, v in r.items() if k != "dpow_traj"} for r in rows]}, indent=1))


if __name__ == "__main__":
    main()
