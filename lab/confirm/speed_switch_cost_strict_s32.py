"""Session 32 (2026-09-27), POST HOC robustness of the N28 switch cost to the event definition, no training.
Event variants from the stored dense curves: 'first' = trainer event (first test >= 0.95); 'strict' = first test evaluation s with
test >= 0.95 at s, s+25, s+50 and train acc >= 0.99 at some step <= s (the R5 definition). Cap 2000 from step 0 for both.
Question fixed before looking: do C(25) > 0 (28/30 under 'first') and C(25) - C(50) > 0 (27/30) keep their sign counts under 'strict'?
  python lab/confirm/speed_switch_cost_strict_s32.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
CAP = 2000
PAT = re.compile(r"seed(\d+)_thr1_n28_seed\d+_w0_(A|B)(?:_to_n28_seed\d+_w0_(A|B)_at(\d+)(_rom)?)?_devcuda$")


def strict_event(dn: dict) -> int | None:
    ts, ta = dn["test_steps"], dn["test_acc"]
    tr = [(s, a) for s, a in zip(dn["train_steps"], dn["train_acc"]) if a >= 0.99]
    mem = tr[0][0] if tr else None
    for i in range(len(ts) - 2):
        if mem is not None and mem <= ts[i] and ts[i + 1] - ts[i] == 25 and ts[i + 2] - ts[i + 1] == 25 and min(ta[i:i + 3]) >= 0.95:
            return ts[i]
    return None


def main() -> None:
    lb = {"first": {}, "strict": {}}
    for d in (LAB / "confirm/n28_raw").iterdir():
        m = PAT.search(d.name)
        if not m or m.group(5):
            continue
        s, a, b, t = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        key = a if b is None else (a + b, int(t))
        g1, g2 = (r.get("events") or {}).get("generalization_step"), strict_event(r["dense"])
        for name, g in (("first", g1), ("strict", g2)):
            lb[name].setdefault(s, {})[key] = math.log2(min(g, CAP) if g is not None else CAP)
    out = {}
    for name, v in lb.items():
        C = {t: np.array([((x[("AB", t)] - x["B"]) + (x[("BA", t)] - x["A"])) / 2 for x in v.values()]) for t in (25, 50)}
        d = C[25] - C[50]
        out[name] = {"C25_mean": float(C[25].mean()), "C25_pos": int((C[25] > 1e-9).sum()), "C50_mean": float(C[50].mean()),
                     "C50_neg": int((C[50] < -1e-9).sum()), "H2_mean": float(d.mean()), "H2_pos": int((d > 1e-9).sum())}
    (LAB / "confirm/speed_switch_cost_strict_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
