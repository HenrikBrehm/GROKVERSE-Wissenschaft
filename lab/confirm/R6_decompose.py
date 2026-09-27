"""R6 descriptive addendum (session 32, fixed BEFORE any R6 run): where does the delay of a switch at 25 sit?
Prediction from N28 (post hoc, speed_switch_decompose_s32.py: 90 % of the delay in the gap): on the fresh R6 seeds the mean gap share of
the delay at t = 25 is > 0.5, and gap-delay > memorisation-delay in most direction pairs. Descriptive (outside the R6 family); reads
result.json transitions of lab/confirm/r6_raw after --analyze has validated the block (run only if R6_summary.json has n_valid == 30).
  python lab/confirm/R6_decompose.py
"""
import json
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
PAT = re.compile(r"seed(\d+)_thr1_r6_seed\d+_w0_(A|B)(?:_to_r6_seed\d+_w0_(A|B)_at(\d+))?_devcuda$")


def main() -> None:
    summ = json.loads((LAB / "confirm/R6_summary.json").read_text(encoding="utf-8"))
    if summ.get("n_valid") != summ.get("n_planned"):
        raise SystemExit("R6 not fully valid; decomposition not run")
    R: dict = {}
    for d in (LAB / "confirm/r6_raw").iterdir():
        m = PAT.search(d.name)
        if not m:
            continue
        s, a, b, t = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        tr = json.loads((d / "result.json").read_text(encoding="utf-8"))["transitions"]["primary"]
        R.setdefault(s, {})[a if b is None else (a + b, int(t))] = (tr["memorization"]["first_crossing_step"], tr["generalization"]["first_crossing_step"])
    out = {}
    for t in (25, 50):
        dm, dg = [], []
        for v in R.values():
            for sw, dest in ((("AB", t), "B"), (("BA", t), "A")):
                (m1, g1), (m0, g0) = v[sw], v[dest]
                if None in (m1, g1, m0, g0):
                    continue
                dm.append(m1 - m0)
                dg.append((g1 - m1) - (g0 - m0))
        dm, dg = np.array(dm, float), np.array(dg, float)
        tot = (dm + dg).mean()
        out[f"t{t}"] = {"pairs": len(dm), "delta_mem_mean": float(dm.mean()), "delta_gap_mean": float(dg.mean()),
                        "gap_share": float(dg.mean() / tot) if tot else None, "n_gap_gt_mem": int((dg > dm).sum())}
    t25 = out["t25"]
    out["prediction_met"] = bool(t25["gap_share"] is not None and t25["gap_share"] > 0.5 and t25["n_gap_gt_mem"] > t25["pairs"] / 2)
    (LAB / "confirm/R6_decompose.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
