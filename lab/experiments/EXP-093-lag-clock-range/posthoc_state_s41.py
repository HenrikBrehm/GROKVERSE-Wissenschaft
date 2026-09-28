"""Post hoc (session 41, exploration): across the 15 cell means of EXP-092 and EXP-093, is persistence pi a function of the
target share f of the early W_E displacement at the switch (and its norm N)? Reads both summary.json files only."""
import json
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[2]
X, Y, N = [], [], []
for e in ("EXP-092-momentum-lag-clock", "EXP-093-lag-clock-range"):
    d = json.loads((LAB / "experiments" / e / "summary.json").read_text(encoding="utf-8"))["secondary"]
    for c in d["pi_means"]:
        X.append(d["fsel_means"][c]); Y.append(d["pi_means"][c]); N.append(d["dnorm_means"][c])
X, Y, N = map(np.array, (X, Y, N))
def r2(A):
    co = np.linalg.lstsq(A, Y, rcond=None)[0]; r = Y - A @ co; return float(1 - r.var() / Y.var()), co.tolist()
out = {"n_cells": len(Y), "pi_on_f": r2(np.c_[np.ones(len(X)), X]), "pi_on_f_logN": r2(np.c_[np.ones(len(X)), X, np.log(N)]),
       "pi_on_logN": r2(np.c_[np.ones(len(X)), np.log(N)])}
(Path(__file__).with_suffix(".json")).write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps(out, indent=1))
