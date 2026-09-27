"""Session 32 (2026-09-27), POST HOC on seeds 400-409 (EXP-059 + EXP-056), no training.
Idea (critical slowing down): if the delay comes from resolving a competition between two half-built frequency sets, the spread of the
delay across seeds should peak where the mean does. Stated before looking at spreads: the SD over seeds of C(t) is largest at a t in
{20, 25, 30} among t = 10, 15, 20, 25, 30, 35, 50. Also the per-direction values (AB and BA separately) as a second view.
  python lab/confirm/speed_switch_spread_s32.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
DIRS = [LAB / "experiments/EXP-059-momentum-exposure/raw", LAB / "experiments/EXP-056-overlap-persistence/raw"]
PAT = re.compile(r"seed(\d+)_thr1_seed\d+_w0_(A|B)(?:_to_seed\d+_w0_(A|B)_at(\d+)(_rom)?)?_devcuda$")
TS = [10, 15, 20, 25, 30, 35, 50]


def main() -> None:
    lb: dict = {}
    for root in DIRS:
        for d in root.iterdir():
            m = PAT.search(d.name)
            if not m or m.group(5):
                continue
            s, a, b, t = int(m.group(1)), m.group(2), m.group(3), m.group(4)
            r = json.loads((d / "result.json").read_text(encoding="utf-8"))
            g = (r.get("events") or {}).get("generalization_step")
            lb.setdefault(s, {})[a if b is None else (a + b, int(t))] = math.log2(min(g, 2000) if g is not None else 2000)
    C = {t: np.array([((v[("AB", t)] - v["B"]) + (v[("BA", t)] - v["A"])) / 2 for v in lb.values()]) for t in TS}
    per_dir = {t: np.array([v[("AB", t)] - v["B"] for v in lb.values()] + [v[("BA", t)] - v["A"] for v in lb.values()]) for t in TS}
    sd = {t: float(C[t].std(ddof=1)) for t in TS}
    sd_dir = {t: float(per_dir[t].std(ddof=1)) for t in TS}
    out = {"sd_C": {str(t): v for t, v in sd.items()}, "argmax_sd_C": max(TS, key=sd.get),
           "sd_per_direction": {str(t): v for t, v in sd_dir.items()}, "argmax_sd_dir": max(TS, key=sd_dir.get),
           "mean_C": {str(t): float(C[t].mean()) for t in TS}}
    out["prediction_met"] = out["argmax_sd_C"] in (20, 25, 30)
    (LAB / "confirm/speed_switch_spread_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
