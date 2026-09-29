"""EXP-110 analysis (pilot; session 47, copied from EXP-109 while the runs were going, before any EXP-110 result was read). Global python, guard:
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-110-lockin-lr4-pilot/analyze.py
Per seed and B: pi(t) at step 5000 as EXP-108 (pure F/G of the same lr and B), t_half by linear interpolation from (0, 0),
censored at t_max. alpha per seed = slope of log t_half on log(N/B) over all four B (full batch N/B = 1).
Pilot rules (README): grid adequate for B if pi(first t) < 0.5 <= pi(last t) in both seeds; lr 2e-3 usable if every pure pair
is separated (L_F - L_G >= 0.5).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
from result_loader import Expect, find_run, load_run  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
_a43 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_a43)
_spec = importlib.util.spec_from_file_location("exp110_design", HERE / "design.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)
SPL = LAB / "experiments/EXP-100-set-vs-order/splits"
PRED = {"M_i": {1024: 18.1, 256: 36.1, 64: 72.3}, "M_add": {1024: 19.6, 256: 55.6, 64: 176.9},
        "M_pow": {1024: 23.2, 256: 57.2, 64: 140.9}}   # JOURNAL session 47, 05:00 (before any lr-4e-3 run)


def lr_(pw, F, G):
    return float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))


def power(pat, s, first, second, bs):
    L = load_run(find_run(HERE / "raw", pat),
                 Expect(seed=s, device="cuda", max_steps=D.TOTAL, split_file=SPL / f"seed{s}_{first}.npy", test_file=SPL / f"seed{s}_test.npy",
                        switch_file=(SPL / f"seed{s}_{second}.npy") if second else None,
                        config={"p": 113, "task": "add", "lr": D.LR}, snapshots_at=(D.TOTAL,)))
    if L.status != "ok":
        return f"{pat}: {L.status}: {L.reason}"
    if L.res.get("batch_size", 0) != bs:
        return f"{pat}: batch size differs"
    return _a43.group_power(L.snapshot(D.TOTAL), "add", 113)[0]


def t_half(pi):
    ts, ms = [0] + sorted(pi), [0.0] + [pi[t] for t in sorted(pi)]
    for i in range(1, len(ts)):
        if ms[i - 1] < 0.5 <= ms[i]:
            return ts[i - 1] + (0.5 - ms[i - 1]) * (ts[i] - ts[i - 1]) / (ms[i] - ms[i - 1]), False
    return float(ts[-1]), True


def main():
    out, errors = {}, []
    for s in D.SEEDS:
        T = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        F, G = T["F"], T["G"]
        n = len(np.load(SPL / f"seed{s}_F.npy"))
        row = {}
        for bs, ts in D.GRID.items():
            sfx = (f"_bs{bs}" if bs else "") + f"_lr{D.LR!r}_devcuda"
            pure = {x: power(f"EXP-018_baseline_seed{s}_thr1_seed{s}_{x}{sfx}", s, x, None, bs) for x in "FG"}
            sw = {(a, t): power(f"EXP-020_baseline_seed{s}_thr1_seed{s}_{a}_to_seed{s}_{b}_at{t}{sfx}", s, a, b, bs)
                  for t in ts for a, b in (("F", "G"), ("G", "F"))}
            bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
            if bad:
                errors.append(bad[0])
                continue
            LF, LG = lr_(pure["F"], F, G), lr_(pure["G"], F, G)
            pi = {t: ((lr_(sw[("F", t)], F, G) - LG) / (LF - LG) + (lr_(sw[("G", t)], F, G) - LF) / (LG - LF)) / 2 for t in ts}
            th, c = t_half(pi)
            row[bs] = {"sep": LF - LG, "pi": {t: round(v, 3) for t, v in pi.items()}, "t_half": th, "censored": c,
                       "grid_ok": pi[ts[0]] < 0.5 <= pi[ts[-1]]}
        if len(row) == len(D.GRID):
            x = np.log([n / b for b in D.GRID]); y = np.log([row[b]["t_half"] for b in D.GRID])
            row["alpha"] = float(np.polyfit(x, y, 1)[0])
            row["pred_logdist"] = {m: {b: float(np.log(row[b]["t_half"] / PRED[m][b])) for b in D.GRID} for m in PRED}
        out[s] = row
    (HERE / "summary.json").write_text(json.dumps({"rows": out, "errors": errors[:10]}, indent=1, default=float), encoding="utf-8")
    print(json.dumps({"rows": out, "errors": errors[:10]}, indent=1, default=float))


if __name__ == "__main__":
    main()
