"""Session 32 (2026-09-27, window closed), POST HOC exploration on the stored EXP-056 pilot (10 seeds, GPU), no training.

Question: does the share omega of pairs common to both splits (0 / 0.2 / 0.4, EXP-053 construction with matched steering) change
the cost of a switch at 25 steps? Motivation: P3 (seen in this session) had median C(25) 0.53 at omega 0 and >= 1.10 at 0.4;
EXP-020 (F/G share ~73 % of their pairs) still showed slow runs at 50. The EXP-056 generalisation steps were never looked at.
Stated before looking: per seed C(25, omega 0.4) > C(25, omega 0) (exact one-sided sign test), and the median C rises over
omega 0 < 0.2 < 0.4. C as in confirm_r6 (common cap 2000 from step 0; mean over both directions of log2 b(switch) - log2 b(dest)).
  python lab/confirm/speed_switch_cost_overlap_s32.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
RAW = LAB / "experiments/EXP-056-overlap-persistence/raw"
PAT = re.compile(r"seed(\d+)_thr1_seed\d+_(w\d+)_(A|B)(?:_to_seed\d+_w\d+_(A|B)_at25)?_devcuda$")
CAP = 2000


def main() -> None:
    runs: dict = {}
    for d in RAW.iterdir():
        m = PAT.search(d.name)
        s, w, a, b = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        assert r["status"] == "completed", d.name
        g = (r.get("events") or {}).get("generalization_step")
        runs.setdefault(s, {}).setdefault(w, {})[a if b is None else a + b] = math.log2(min(g, CAP) if g is not None else CAP)
    C = {s: {w: ((v["AB"] - v["B"]) + (v["BA"] - v["A"])) / 2 for w, v in ws.items()} for s, ws in runs.items()}
    diff = np.array([c["w400"] - c["w0"] for c in C.values()])
    nz = diff[np.abs(diff) > 1e-9]
    k, n = int((nz > 0).sum()), len(nz)
    out = {"note": "post hoc exploration, EXP-056 seeds (frequencies seen, times not)", "C": C,
           "median_C": {w: float(np.median([c[w] for c in C.values()])) for w in ("w0", "w200", "w400")},
           "w400_gt_w0": k, "nonzero": n, "p_one_sided": sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0,
           "monotone_seeds": sum(c["w0"] < c["w200"] < c["w400"] for c in C.values())}
    (LAB / "confirm/speed_switch_cost_overlap_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "C"}, indent=1))


if __name__ == "__main__":
    main()
