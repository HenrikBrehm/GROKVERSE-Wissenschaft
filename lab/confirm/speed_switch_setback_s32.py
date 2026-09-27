"""Session 32 (2026-09-27), POST HOC on N28 (30 seeds), no training. Does the conflict after a switch at 25 show up as a setback in the
test curve? Setback = before the generalisation event (or before 2000 if none), test accuracy reaches >= 0.3 and later falls by >= 0.2
below its running maximum. Stated before looking: setbacks are more frequent in switch@25 runs than in destination-only runs
(count over runs; per seed also compared, exact sign test on per-seed counts difference). Descriptive: switch@50.
  python lab/confirm/speed_switch_setback_s32.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
PAT = re.compile(r"seed(\d+)_thr1_n28_seed\d+_w0_(A|B)(?:_to_n28_seed\d+_w0_(A|B)_at(\d+)(_rom)?)?_devcuda$")


def setback(r: dict) -> bool:
    dn = r["dense"]
    g = (r.get("events") or {}).get("generalization_step") or 2000
    run_max, hit = 0.0, False
    for s, a in zip(dn["test_steps"], dn["test_acc"]):
        if s >= g:
            break
        run_max = max(run_max, a)
        if run_max >= 0.3 and a <= run_max - 0.2:
            hit = True
    return hit


def main() -> None:
    R: dict = {}
    for d in (LAB / "confirm/n28_raw").iterdir():
        m = PAT.search(d.name)
        if not m or m.group(5):
            continue
        s, a, b, t = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        R.setdefault(s, {})[a if b is None else f"{a}{b}@{t}"] = setback(r)
    cnt = {k: sum(v[k] for v in R.values()) for k in ("A", "B", "AB@25", "BA@25", "AB@50", "BA@50")}
    diff = np.array([(v["AB@25"] + v["BA@25"]) - (v["A"] + v["B"]) for v in R.values()])
    nz = diff[diff != 0]
    k, n = int((nz > 0).sum()), len(nz)
    out = {"setbacks": cnt, "runs_per_arm": len(R), "per_seed_more_at25": k, "nonzero": n,
           "p_one_sided": sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0}
    (LAB / "confirm/speed_switch_setback_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
