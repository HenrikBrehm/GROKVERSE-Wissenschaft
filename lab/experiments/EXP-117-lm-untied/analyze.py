"""EXP-117 analysis (session 51, written before any run; readings in README "Vorab").
Input rows: EXP-105 analyze_pilot.py on we_snapshots.npy (Delta_pow on the 113 number rows of the INPUT embedding).
Output rows: the same Delta_pow on head_snapshots.npy (number rows of the untied OUTPUT layer), at the last common snapshot.
Readings at the end of the budget (both seeds):
  'nicht gelernt (Budget)'  train-fact accuracy < 0.1 in >= 3 of 4 runs (precedence; no statement)
  'Eingabe gesteuert'       Delta_in > 1 in both seeds and held-out accuracy > 0.5 in >= 3 of 4 runs
  'nur Ausgabe gesteuert'   Delta_in <= 1 in both seeds, Delta_out > 1 in both seeds, held-out > 0.5 in >= 3 of 4
  'keine Steuerung'         |Delta_in| <= 1 and |Delta_out| <= 1 in both seeds, held-out > 0.5 in >= 3 of 4
  else 'unklar'
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-117-lm-untied/analyze.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-105-lm-ladder-stage2"))
import analyze_pilot as AP  # noqa: E402  (also puts EXP-102 analyze on the path as AP.A)

SPL = "lab/experiments/EXP-102-lm-ladder-stage1/splits"
PAIRS = [f"3862:{SPL}/seed3802_F.npy,{SPL}/seed3802_G.npy", f"3863:{SPL}/seed3803_F.npy,{SPL}/seed3803_G.npy"]


def head_delta(root: Path, seed: int, fF: Path, fG: Path) -> dict:
    ds = {x: [d for d in root.iterdir() if d.name.startswith(f"lm2_seed{seed}_{f.stem}_steps")] for x, f in (("F", fF), ("G", fG))}
    assert all(len(v) == 1 for v in ds.values()), ds
    H = {x: np.load(v[0] / "head_snapshots.npy") for x, v in ds.items()}
    S = {x: [int(s) for s in np.load(v[0] / "we_snapshot_steps.npy")] for x, v in ds.items()}
    assert S["F"] == S["G"] and all(np.isfinite(h).all() for h in H.values())
    traj = {s: AP.A.delta_pow(AP.A.power(H["F"][i]), AP.A.power(H["G"][i]), AP.targets(fF), AP.targets(fG)) for i, s in enumerate(S["F"])}
    return {"dout_end": traj[S["F"][-1]], "dout_traj": {str(s): v for s, v in traj.items()}}


def main() -> None:
    root = HERE / "raw"
    argv, sys.argv = sys.argv, ["analyze_pilot.py", "--root", str(root), "--pairs", *PAIRS]
    try:
        AP.main()
    finally:
        sys.argv = argv
    out = json.loads((root / "pilot_summary.json").read_text(encoding="utf-8"))
    for row, spec in zip(out["rows"], PAIRS):
        seed, files = spec.split(":")
        fF, fG = (Path(x) for x in files.split(","))
        row.update(head_delta(root, int(seed), fF, fG))
    din = [r["dpow_end"] for r in out["rows"]]
    dout = [r["dout_end"] for r in out["rows"]]
    tr = [x for r in out["rows"] for x in r["train_acc"]]
    te = [x for r in out["rows"] for x in r["test_acc"]]
    learned = sum(x > 0.5 for x in te) >= len(te) - 1
    if sum(x < 0.1 for x in tr) >= len(tr) - 1:
        reading = "nicht gelernt (Budget)"
    elif learned and all(d > 1 for d in din):
        reading = "Eingabe gesteuert"
    elif learned and all(d <= 1 for d in din) and all(d > 1 for d in dout):
        reading = "nur Ausgabe gesteuert"
    elif learned and all(abs(d) <= 1 for d in din + dout):
        reading = "keine Steuerung"
    else:
        reading = "unklar"
    out["reading_exp117"] = reading
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"reading": reading, "dpow_in": din, "dpow_out": dout, "test_acc": te, "train_acc": tr}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
