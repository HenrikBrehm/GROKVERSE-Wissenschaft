"""EXP-135 analysis (session 64, written before any run; readings in README "Vorab").
Per run: lean L(P) = log(P(T_F) / P(T_G)) of the number-row power spectrum (EXP-102 power, 5 targets each).
Persistence pi = (L_switch - L_G) / (L_F - L_G) at the end, with L_F, L_G from the LM1 F and G runs of the same model seed
at step 6000 (from scratch, same trainer and device; confirmation block, already seen). pi ~ 1: F persists; ~ 0: as G only.
Per t: 'haelt fest' pi > 0.5 in both seeds; 'ueberschrieben' pi < 0.2 in both; else 'teilweise'.
Gate: held-out accuracy (common test set) > 0.5 in >= 5 of 6 switch runs, else 'nicht auswertbar (lernt G nicht)'.
Overall: 'Festlegung am Anfang' if all three t 'haelt fest'; 'Festlegung mit dem Lernen' if t=250 and t=1000 'ueberschrieben' and
t=3000 'haelt fest'; 'keine Festlegung' if all three 'ueberschrieben'; else 'unklar'.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-135-lm-switch-lockin/analyze.py
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
SPL = LAB / "confirm/lm1_splits"
PAIRS, TS = [(4100, 4000), (4101, 4001)], (250, 1000, 3000)


def _mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


A = _mod("analyze_exp102", LAB / "experiments/EXP-102-lm-ladder-stage1/analyze.py")


def run_dir(root: Path, seed: int, pair: int, arm: str, steps: int) -> Path:
    ds = [d for d in root.iterdir() if d.name.startswith(f"lm2_seed{seed}_seed{pair}_{arm}_steps{steps}_")]
    assert len(ds) == 1, (root, seed, arm, steps, ds)
    r = json.loads((ds[0] / "result.json").read_text(encoding="utf-8"))
    assert r["status"] == "completed" and r["steps_completed"] == steps, ds[0]
    return ds[0]


def lean(W: np.ndarray, TF: list[int], TG: list[int]) -> float:
    pw = A.power(W)
    return float(np.log(pw[[k - 1 for k in TF]].sum() / pw[[k - 1 for k in TG]].sum()))


def classify(pis: list[float]) -> str:
    return "haelt fest" if all(p > 0.5 for p in pis) else "ueberschrieben" if all(p < 0.2 for p in pis) else "teilweise"


def main() -> None:
    per_t, rows = {}, []
    for t in TS:
        pis = []
        for seed, pair in PAIRS:
            tg = json.loads((SPL / f"seed{pair}.json").read_text(encoding="utf-8"))["targets"]
            TF, TG = tg["F"], tg["G"]
            LF = lean(np.load(run_dir(LAB / "confirm/lm1_raw", seed, pair, "F", 6000) / "we_snapshots.npy")[-1], TF, TG)
            LG = lean(np.load(run_dir(LAB / "confirm/lm1_raw", seed, pair, "G", 6000) / "we_snapshots.npy")[-1], TF, TG)
            d = run_dir(HERE / f"raw_t{t}", seed, pair, "F", t + 6000)
            side = json.loads((d / "switch.json").read_text(encoding="utf-8"))
            assert side["switch_step"] == t
            res = json.loads((d / "result.json").read_text(encoding="utf-8"))
            W, S = np.load(d / "we_snapshots.npy"), [int(x) for x in np.load(d / "we_snapshot_steps.npy")]
            traj = {s: lean(W[i], TF, TG) for i, s in enumerate(S)}
            pi = (traj[S[-1]] - LG) / (LF - LG)
            pis.append(pi)
            rows.append({"t": t, "seed": seed, "pi": pi, "lean_end": traj[S[-1]], "lean_F_ref": LF, "lean_G_ref": LG,
                         "lean_at_switch": traj.get(t), "test_acc_end": res["curve"][-1][2],
                         "F_fact_acc_end": res["curve"][-1][1],
                         "lean_traj": {str(s): v for s, v in traj.items() if s % 1000 == 0 or s == t}})
        per_t[str(t)] = {"pis": pis, "reading": classify(pis)}
    acc = [r["test_acc_end"] for r in rows]
    if sum(a > 0.5 for a in acc) < len(acc) - 1:
        overall = "nicht auswertbar (lernt G nicht)"
    else:
        c = {t: per_t[str(t)]["reading"] for t in TS}
        overall = ("Festlegung am Anfang" if c[250] == c[1000] == c[3000] == "haelt fest" else   # monotone (review s64)
                   "Festlegung mit dem Lernen" if c[250] == c[1000] == "ueberschrieben" and c[3000] == "haelt fest" else
                   "keine Festlegung" if all(v == "ueberschrieben" for v in c.values()) else "unklar")
    out = {"reading": overall, "per_t": per_t, "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
