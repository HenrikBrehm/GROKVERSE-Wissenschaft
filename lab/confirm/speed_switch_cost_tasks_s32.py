"""Session 32 (2026-09-27, window closed), POST HOC generalisation check (rule 15c) on the stored EXP-044 runs, no training.

Question: does the switch cost found for add 113 (N28/P3/EXP-056: a switch at 25 steps delays grokking, at 50 not) hold for
addition mod 97 and multiplication mod 113? EXP-044: per task 10 seeds, F only, G only, F->G at 25 / 50 / 150 (one direction).
The generalisation steps of these runs were never looked at. Stated before looking (per task):
  (i)  C(25) = log2 b(F->G@25) - log2 b(G only) > 0 in most seeds (exact one-sided sign test);
  (ii) C(25) > C(50) in most seeds (sign test); C(150) descriptive.
b = min(gen, 2000) from step 0 (common cap as in R6). Requires a common test set per seed (checked).
  python lab/confirm/speed_switch_cost_tasks_s32.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
RAW = LAB / "experiments/EXP-044-generalize-lockin/raw"
CAP = 2000
PAT = re.compile(r"_seed(\d+)_thr1_(add97|mul113)_seed\d+_train_(F|G)(?:_to_\w+?_seed\d+_train_G_at(\d+))?_(?:add97|mul113)_devcuda$")


def sign_p(k: int, n: int) -> float:
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0


def main() -> None:
    runs: dict = {}
    for d in RAW.iterdir():
        m = PAT.search(d.name)
        assert m, d.name
        s, task, arm, t = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        assert r["status"] == "completed", d.name
        g = (r.get("events") or {}).get("generalization_step")
        key = arm if t is None else int(t)
        runs.setdefault(task, {}).setdefault(s, {})[key] = {"lb": math.log2(min(g, CAP) if g is not None else CAP),
                                                            "ev": g is not None and g <= CAP, "th": r["test_hash"]}
    out = {"note": "post hoc generalisation check, EXP-044 seeds (frequencies seen, times not)"}
    for task, ss in sorted(runs.items()):
        for s, r in ss.items():
            assert len({v["th"] for v in r.values()}) == 1, (task, s, "test sets differ")
        C = {t: np.array([r[t]["lb"] - r["G"]["lb"] for r in ss.values()]) for t in (25, 50, 150)}
        d = C[25] - C[50]
        res = {"n": len(ss), "events": {str(k): sum(r[k]["ev"] for r in ss.values()) for k in ("F", "G", 25, 50, 150)}}
        for name, v in (("C25", C[25]), ("C25_minus_C50", d)):
            nz = v[np.abs(v) > 1e-9]
            k = int((nz > 0).sum())
            res[name] = {"mean": float(v.mean()), "median": float(np.median(v)), "pos": k, "nonzero": len(nz), "p_one_sided": sign_p(k, len(nz))}
        res["C50_mean"], res["C150_mean"] = float(C[50].mean()), float(C[150].mean())
        res["C50_pos_neg"] = [int((C[50] > 1e-9).sum()), int((C[50] < -1e-9).sum())]
        res["C150_pos_neg"] = [int((C[150] > 1e-9).sum()), int((C[150] < -1e-9).sum())]
        out[task] = res
    (LAB / "confirm/speed_switch_cost_tasks_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
