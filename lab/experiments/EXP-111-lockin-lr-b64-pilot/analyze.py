"""EXP-111 analysis (session 47; written while the runs were going, before any EXP-111 result was read; reading in README).
Per seed and lr: pi(t) at step 5000 at B 64 as EXP-108/109/110, t_half by the first-upward-crossing rule; d = log t_half(4e-3) -
log t_half(2e-3). Loader and power from EXP-110's analyze.py logic (same conventions), reimplemented against this design.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-111-lockin-lr-b64-pilot/analyze.py
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
from result_loader import Expect, find_run, load_run  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
_a43 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_a43)
_spec = importlib.util.spec_from_file_location("exp111_design", HERE / "design.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)
SPL = LAB / "experiments/EXP-100-set-vs-order/splits"


def logratio(pw, F, G) -> float:
    return math.log(sum(pw[k - 1] for k in F) / sum(pw[k - 1] for k in G))


def power(pat: str, s: int, first: str, second: str | None, lr: float):
    L = load_run(find_run(HERE / "raw", pat),
                 Expect(seed=s, device="cuda", max_steps=D.TOTAL, split_file=SPL / f"seed{s}_{first}.npy", test_file=SPL / f"seed{s}_test.npy",
                        switch_file=(SPL / f"seed{s}_{second}.npy") if second else None, config={"p": 113, "task": "add", "lr": lr},
                        snapshots_at=(D.TOTAL,)))
    if L.status != "ok" or L.res.get("batch_size") != D.BS:
        return f"{pat}: {L.status}: {L.reason}"
    return _a43.group_power(L.snapshot(D.TOTAL), "add", 113)[0]


def t_half(pi: dict) -> tuple[float, bool]:
    ts, ms = [0] + sorted(pi), [0.0] + [pi[t] for t in sorted(pi)]
    for i in range(1, len(ts)):
        if ms[i - 1] < 0.5 <= ms[i]:
            return ts[i - 1] + (0.5 - ms[i - 1]) * (ts[i] - ts[i - 1]) / (ms[i] - ms[i - 1]), False
    return float(ts[-1]), True


def main() -> None:
    out, errors = {}, []
    for s in D.SEEDS:
        T = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        F, G = T["F"], T["G"]
        row = {}
        for lr in D.LRS:
            sfx = f"_bs{D.BS}_lr{lr!r}_devcuda"
            pure = {x: power(f"EXP-018_baseline_seed{s}_thr1_seed{s}_{x}{sfx}", s, x, None, lr) for x in "FG"}
            sw = {(a, t): power(f"EXP-020_baseline_seed{s}_thr1_seed{s}_{a}_to_seed{s}_{b}_at{t}{sfx}", s, a, b, lr)
                  for t in D.GRID for a, b in (("F", "G"), ("G", "F"))}
            bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
            if bad:
                errors.append(bad[0])
                continue
            LF, LG = logratio(pure["F"], F, G), logratio(pure["G"], F, G)
            pi = {t: ((logratio(sw[("F", t)], F, G) - LG) / (LF - LG) + (logratio(sw[("G", t)], F, G) - LF) / (LG - LF)) / 2 for t in D.GRID}
            th, c = t_half(pi)
            row[repr(lr)] = {"sep": LF - LG, "pi": {t: round(v, 3) for t, v in pi.items()}, "t_half": th, "censored": c}
        if len(row) == 2:
            row["d_log"] = math.log(row["0.004"]["t_half"] / row["0.002"]["t_half"])
        out[s] = row
    ds = [r["d_log"] for r in out.values() if "d_log" in r]
    res = {"rows": out, "errors": errors[:5],
           "reading": "gleiche Richtung wie EXP-110" if len(ds) == 2 and all(d > 0 for d in ds) else "nicht gleiche Richtung / unvollständig"}
    (HERE / "summary.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
