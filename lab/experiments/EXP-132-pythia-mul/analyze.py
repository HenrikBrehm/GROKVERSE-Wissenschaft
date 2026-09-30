"""EXP-132 analysis (session 61, written before any EXP-132 run; readings in README.md, same rules as EXP-127).

Per seed (1000, 1001; arms F, G): primary Delta_pow of the residual change U = E_in(T) - c E_in(0) of the 113 number rows,
power in the DISCRETE-LOG basis (ft_mul.power_mul, k = 1..55), P1 Delta_pow with the split's log-coordinate targets.
Readings: gate = held-out accuracy >= 0.5 at the end in >= 3 of 4 runs, else "nicht auswertbar (lernt nicht)";
"K2 haelt (mul)" if Delta_pow > 1 in both seeds; "bricht" if |Delta_pow| <= 1 in both; else "unklar".
Descriptive: top-5 of U in the log basis and in the additive basis (EXP-127: 23, 11, 2, 56, 3), ablation C_in/C_both.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-132-pythia-mul/analyze.py [--root DIR] [--steps N]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
from make_split import group  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp127_analyze", LAB / "experiments/EXP-127-pretrained-lm/analyze.py")
_a127 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_a127)                # by path: several experiments have a module called "analyze"
delta_pow, power, residual = _a127.delta_pow, _a127.power, _a127.residual   # EXP-127 helpers; `power` = additive basis

P, SEEDS = 113, (1000, 1001)
N, ELEM = group("mul", P)
K = (N - 1) // 2


def power_log(W: np.ndarray) -> np.ndarray:
    sq = (np.abs(np.fft.fft(W[ELEM].astype(np.float64), axis=0)) ** 2).sum(1)
    return 2.0 * sq[1:K + 1] / N


def top5(pw: np.ndarray) -> list[int]:
    return [int(k) + 1 for k in np.argsort(-pw)[:5]]


def load(root: Path, seed: int, arm: str, steps: int) -> dict | str:
    hits = [p for p in root.glob(f"pt_seed{seed}_seed{seed}_{arm}_steps{steps}_*") if (p / "result.json").exists()]
    if len(hits) != 1:
        return "fehlt" if not hits else "mehrdeutig"
    r = json.loads((hits[0] / "result.json").read_text(encoding="utf-8"))
    if r.get("status") != "completed":
        return "defekt"
    snaps = np.load(hits[0] / "in_snapshots.npy")
    if not np.isfinite(snaps).all():
        return "defekt"
    return {"r": r, "E0": snaps[0], "ET": snaps[-1]}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(HERE / "raw"))
    ap.add_argument("--steps", type=int, default=4000)
    a = ap.parse_args()
    root = Path(a.root)
    rows, status, tests = [], {}, []
    for s in SEEDS:
        tj = json.loads((HERE / f"splits/seed{s}.json").read_text(encoding="utf-8"))["targets"]
        runs = {arm: load(root, s, arm, a.steps) for arm in "FG"}
        status[str(s)] = {arm: (v if isinstance(v, str) else "ok") for arm, v in runs.items()}
        if any(isinstance(v, str) for v in runs.values()):
            continue
        U = {arm: residual(runs[arm]["ET"], runs[arm]["E0"]) for arm in "FG"}
        pl = {arm: power_log(U[arm]) for arm in "FG"}
        row = {"seed": s, "targets": tj, "dpow_update_in": delta_pow(pl["F"], pl["G"], tj["F"], tj["G"]),
               "dpow_rows_in": delta_pow(power_log(runs["F"]["ET"]), power_log(runs["G"]["ET"]), tj["F"], tj["G"])}
        for arm in "FG":
            r = runs[arm]["r"]
            tests.append(r["curve"][-1][2])
            row[f"test_{arm}"] = r["curve"][-1][2]
            row[f"top5_log_{arm}"] = top5(pl[arm])
            row[f"top5_add_{arm}"] = top5(power(U[arm]))
            row[f"C_in_{arm}"] = r["ablation"]["C_in"]
            row[f"C_both_{arm}"] = r["ablation"]["C_both"]
        rows.append(row)
    if len(tests) < 4 or sum(t >= 0.5 for t in tests) < 3:
        reading = "nicht auswertbar (lernt nicht)" if len(tests) == 4 else "nicht auswertbar (fehlende Läufe)"
    else:
        d = [r["dpow_update_in"] for r in rows]
        if any(x is None for x in d):
            reading = "nicht auswertbar (nicht endlich)"
        elif all(x > 1 for x in d):
            reading = "K2 haelt (mul)"
        elif all(abs(x) <= 1 for x in d):
            reading = "bricht"
        else:
            reading = "unklar"
    out = {"reading": reading, "status": status, "rows": rows, "steps": a.steps}
    name = "summary.json" if a.steps == 4000 else f"summary_steps{a.steps}.json"
    (HERE / name).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
