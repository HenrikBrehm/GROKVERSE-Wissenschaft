"""Session 32 (2026-09-27, window closed), POST HOC dry run of R6 on stored runs (seeds 400-409), no training.

EXP-059 (switches at 10/15/20/30/35/50, plus optimizer-moment resets) and EXP-056 (A only, B only, switch at 25; omega 0) share
splits, test set and initialization per seed (hashes checked below), GPU. Together they give a fine switch-cost curve.
Generalisation steps of EXP-059 never looked at (EXP-056 omega-0 values were read in cycle 8 of this session).
Stated before looking (derived from N28 / R6):
  P-a  mean C(t) > 0 for t in 20..35;  P-b  mean C(50) <= 0;  P-c  the largest mean C lies at t in 20..35;
  S2   (R6 rule, pi from EXP-059 README / FINDINGS: 0.01, 0.19, 0.30, 0.56, 1.05 at t = 10, 20, 25, 35, 50):
       C <= 0 where pi >= 0.9 (t = 50), C > 0 where 0.2 <= pi <= 0.8 (t = 25, 35).
C(t) as in R6: b = min(gen, 2000) from step 0; per seed mean over both directions of log2 b(switch@t) - log2 b(destination only).
  python lab/confirm/speed_switch_curve_s32.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
DIRS = [LAB / "experiments/EXP-059-momentum-exposure/raw", LAB / "experiments/EXP-056-overlap-persistence/raw"]
PAT = re.compile(r"seed(\d+)_thr1_seed\d+_w0_(A|B)(?:_to_seed\d+_w0_(A|B)_at(\d+)(_rom)?)?_devcuda$")
CAP = 2000


def main() -> None:
    lb: dict = {}
    for root in DIRS:
        for d in root.iterdir():
            m = PAT.search(d.name)
            if not m:
                continue
            s, a, b, t, rom = int(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5)
            r = json.loads((d / "result.json").read_text(encoding="utf-8"))
            assert r["status"] == "completed", d.name
            g = (r.get("events") or {}).get("generalization_step")
            key = a if b is None else (a + b, t + ("r" if rom else ""))
            assert key not in lb.get(s, {}), (s, key)
            lb.setdefault(s, {})[key] = (math.log2(min(g, CAP) if g is not None else CAP), r["test_hash"], r["init_checksum_shared"])
    for s, v in lb.items():
        assert len({x[1] for x in v.values()}) == 1 and len({x[2] for x in v.values()}) == 1, (s, "test set or init differs")
    ts = ["10", "15", "20", "25", "30", "35", "50", "30r", "35r", "40r", "50r"]
    C = {t: np.array([((v[("AB", t)][0] - v["B"][0]) + (v[("BA", t)][0] - v["A"][0])) / 2 for v in lb.values()]) for t in ts}
    mean = {t: float(C[t].mean()) for t in ts}
    plain = ["10", "15", "20", "25", "30", "35", "50"]
    peak = max(plain, key=lambda t: mean[t])
    out = {"note": "post hoc dry run of R6 on seeds 400-409 (EXP-059 + EXP-056)", "n": len(lb),
           "C": {t: {"mean": mean[t], "median": float(np.median(C[t])), "pos": int((C[t] > 1e-9).sum()), "neg": int((C[t] < -1e-9).sum())} for t in ts},
           "P_a_C_pos_20_35": all(mean[t] > 0 for t in ("20", "25", "30", "35")), "P_b_C50_le_0": mean["50"] <= 0,
           "P_c_peak": peak, "P_c_ok": peak in ("20", "25", "30", "35"),
           "S2": "gestützt" if mean["50"] <= 0 and mean["25"] > 0 and mean["35"] > 0 else "nicht gestützt"}
    (LAB / "confirm/speed_switch_curve_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
