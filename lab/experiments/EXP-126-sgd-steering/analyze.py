"""EXP-126 analysis (session 57, written before any run; readings in README "Vorab"). Per lr and seed: F and G runs (full-batch SGD with
momentum). A run is 'divergiert' if its spectrum at 20 000 is not finite, 'nicht gelernt' if final train accuracy < 0.99. A seed is
evaluable at this lr if both runs are finite and learned. Delta_pow = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)] at 20 000
(confirm_p1.delta_pow_checked, P1 definition). Reading per lr: 'K2 ohne Adam' if >= 3 evaluable seeds and Delta_pow > 1 in all of them;
'bricht' if >= 3 evaluable and |Delta_pow| <= 1 in all; 'nicht auswertbar' if < 3 evaluable; else 'unklar'.
Descriptive: Delta_pow at 2000, divergence and learning counts, generalization step, test accuracy.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-126-sgd-steering/analyze.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
import confirm_p1 as c1  # noqa: E402

SPL = LAB / "experiments/EXP-100-set-vs-order/splits"
SEEDS, LRS, END = (3704, 3705, 3706, 3707), (0.05, 0.1), 20_000


def run(s: int, x: str, lr: float) -> dict:
    ds = list((HERE / "raw").glob(f"*_seed{s}_thr1_seed{s}_{x}_sgdm{lr!r}_0.9_devcuda"))
    if len(ds) != 1:
        return {"state": "fehlt"}
    r = json.loads((ds[0] / "result.json").read_text(encoding="utf-8"))
    if r.get("status") != "completed" or r.get("steps_completed") != END:
        return {"state": "fehlt"}
    S, st = np.load(ds[0] / "spectra.npy"), [int(v) for v in np.load(ds[0] / "spectra_steps.npy")]
    sp = {t: S[i] for i, t in enumerate(st)}
    if END not in sp or not np.isfinite(sp[END]).all() or not np.isfinite((r.get("final_acc") or {}).get("train", np.nan)):
        return {"state": "divergiert"}
    fa = r["final_acc"]
    return {"state": "ok" if fa["train"] >= 0.99 else "nicht gelernt", "end": sp[END], "at2k": sp.get(2000), "train": fa["train"],
            "test": fa.get("test"), "gen": (r.get("events") or {}).get("generalization_step")}


def main() -> None:
    out: dict = {}
    for lr in LRS:
        rows = []
        for s in SEEDS:
            T = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
            a, b = run(s, "F", lr), run(s, "G", lr)
            row = {"seed": s, "F": a["state"], "G": b["state"]}
            for k, v in (("F", a), ("G", b)):
                row[f"train_{k}"], row[f"test_{k}"], row[f"gen_{k}"] = v.get("train"), v.get("test"), v.get("gen")
            if a["state"] == b["state"] == "ok":
                row["dpow_end"] = c1.delta_pow_checked(a["end"], b["end"], T["F"], T["G"])
                if a["at2k"] is not None and b["at2k"] is not None and np.isfinite(a["at2k"]).all() and np.isfinite(b["at2k"]).all():
                    row["dpow_2000"] = c1.delta_pow_checked(a["at2k"], b["at2k"], T["F"], T["G"])
            rows.append(row)
        ev = [r["dpow_end"] for r in rows if r.get("dpow_end") is not None and np.isfinite(r["dpow_end"])]
        reading = ("nicht auswertbar" if len(ev) < 3 else "K2 ohne Adam" if all(d > 1 for d in ev)
                   else "bricht" if all(abs(d) <= 1 for d in ev) else "unklar")
        out[repr(lr)] = {"reading": reading, "n_evaluable": len(ev), "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
