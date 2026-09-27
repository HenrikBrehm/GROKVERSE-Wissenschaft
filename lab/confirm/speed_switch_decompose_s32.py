"""Session 32 (2026-09-27), POST HOC on N28 (30 seeds), no training. Where does the delay of a switch at 25 sit: in memorising the new
split or in the gap from memorisation to generalisation? gen = mem + gap (trainer transitions, primary thresholds: train >= 0.99,
test >= 0.95; after a switch the train accuracy refers to the new split). Delay per seed and direction in steps against the
destination-only run; only direction-pairs where all four events are observed. Stated before looking: the gap carries more than half of
the delay (mean delta_gap > mean delta_mem, and delta_gap > delta_mem in most direction-pairs). Descriptive: the same at 50.
  python lab/confirm/speed_switch_decompose_s32.py
"""
import json
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
PAT = re.compile(r"seed(\d+)_thr1_n28_seed\d+_w0_(A|B)(?:_to_n28_seed\d+_w0_(A|B)_at(\d+)(_rom)?)?_devcuda$")


def main() -> None:
    R: dict = {}
    for d in (LAB / "confirm/n28_raw").iterdir():
        m = PAT.search(d.name)
        if not m or m.group(5):
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
        out[f"t{t}"] = {"pairs": len(dm), "delta_mem_mean": float(dm.mean()), "delta_gap_mean": float(dg.mean()),
                        "delta_gen_mean": float((dm + dg).mean()), "gap_share_of_delay": float(dg.mean() / (dm + dg).mean()),
                        "n_gap_gt_mem": int((dg > dm).sum()), "delta_mem_median": float(np.median(dm)), "delta_gap_median": float(np.median(dg))}
    out["prediction_met_t25"] = out["t25"]["delta_gap_mean"] > out["t25"]["delta_mem_mean"] and out["t25"]["n_gap_gt_mem"] > out["t25"]["pairs"] / 2
    (LAB / "confirm/speed_switch_decompose_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
