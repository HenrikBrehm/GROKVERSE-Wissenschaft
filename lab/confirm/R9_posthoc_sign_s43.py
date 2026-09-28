"""R9 post hoc (session 43, numpy on stored snapshots of the ANALYSED block R9, descriptive, exploration; not part of R9's
registration): does Adam's sign quantisation of the early W_E motion go with lower target selectivity across the R9 cells?
Motivation: EXP-095 Nachtrag b (binarising the default displacement costs about half of the g24 target-share gap).

Per run (both directions A->B, B->A) at the switch t: D = W_E(t) - (1 - c lr wd)^t W_E(0); unit = c lr sum_j (1 - c lr wd)^j (j < t);
q = share of entries with |D| within 10 % of the unit (all steps full-size, same sign); f = target share of D's group power
(EXP-092 selectivity: targets of the first split). Cell means over 36 seeds, per-seed differences l100 - l100b and c2 - c2b.
Readings fixed HERE, BEFORE computing (session 43):
  'Quantisierung passt'       Spearman(q, f) over the six cell means <= -0.6 AND sign(q(l100) - q(l100b)) opposite to
                              sign(f(l100) - f(l100b)) in >= 27/36 seeds
  'passt nicht'               Spearman(q, f) >= 0
  else 'unklar'.
Caveats stated before: six cells only; q depends on the step size c through the unit; pi, not f, is the registered measure.
Writes R9_posthoc_sign_s43.json next to this file.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
sys.path.insert(0, str(LAB / "tools"))
import confirm_r9 as R  # noqa: E402  (CELLS, stem, run_dir helpers; read-only)

LR, WD = 1e-3, 1.0


def rank(x: np.ndarray) -> np.ndarray:
    return np.argsort(np.argsort(x)).astype(float)


def main() -> None:
    summ = json.loads((HERE / "R9_summary.json").read_text(encoding="utf-8"))
    seeds = [r["seed"] for r in summ["rows"] if r.get("valid")]
    ep = R.e56()
    out_rows = []
    for s in seeds:
        meta = json.loads((R.SPL / f"r9_seed{s}_w0.json").read_text(encoding="utf-8"))
        tg = {"A": meta["targets"]["A"], "B": meta["targets"]["B"]}
        row = {"seed": s}
        for cell, spec in R.CELLS.items():
            c, t = spec["c"], spec["t"]
            unit = c * LR * sum((1 - c * LR * WD) ** j for j in range(t))
            decay = (1 - c * LR * WD) ** t
            qs, fs = [], []
            for first, second in (("A", "B"), ("B", "A")):
                cmd = ["x", R.FB, "--seed", str(s), "--threads", "1", "--device", "cuda",
                       "--split-file", str(R.SPL / f"{R.stem(s, first)}.npy"),
                       "--switch-split-file", str(R.SPL / f"{R.stem(s, second)}.npy"), "--switch-step", str(t)]
                cmd += ["--lr-scale", f"{c:g}"] if c != 1.0 else []
                cmd += ["--pre-switch-betas", f"{spec['psb'][0]},{spec['psb'][1]}"] if spec["psb"] else []
                d = R.run_dir(cmd)
                steps = list(np.load(d / "we_snapshot_steps.npy"))
                W = np.load(d / "we_snapshots.npy").astype(np.float64)
                Wt, W0 = W[steps.index(t)], W[steps.index(0)]
                D = Wt - decay * W0
                qs.append(float(np.mean(np.abs(np.abs(D) - unit) <= 0.1 * unit)))
                pw = ep._a43.group_power(Wt - W0, "add", 113)[0]
                fs.append(float(pw[[k - 1 for k in tg[first]]].sum() / pw.sum()))
            row[f"q_{cell}"], row[f"f_{cell}"] = float(np.mean(qs)), float(np.mean(fs))
        out_rows.append(row)
    col = lambda k: np.array([r[k] for r in out_rows])   # noqa: E731
    cells = list(R.CELLS)
    qm, fm = np.array([col(f"q_{c}").mean() for c in cells]), np.array([col(f"f_{c}").mean() for c in cells])
    rho = float(np.corrcoef(rank(qm), rank(fm))[0, 1])
    dq, df = col("q_l100") - col("q_l100b"), col("f_l100") - col("f_l100b")
    opposite = int(np.sum(np.sign(dq) == -np.sign(df)))
    reading = "Quantisierung passt" if rho <= -0.6 and opposite >= 27 else "passt nicht" if rho >= 0 else "unklar"
    out = {"n": len(out_rows), "cells": cells, "q_means": dict(zip(cells, qm.tolist())), "f_means": dict(zip(cells, fm.tolist())),
           "spearman_q_f_cells": rho, "l100_minus_l100b": {"dq_mean": float(dq.mean()), "df_mean": float(df.mean()), "opposite_signs": opposite},
           "c2_minus_c2b": {"dq_mean": float((col("q_c2") - col("q_c2b")).mean()), "df_mean": float((col("f_c2") - col("f_c2b")).mean())},
           "reading": reading, "rows": out_rows}
    (HERE / "R9_posthoc_sign_s43.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
