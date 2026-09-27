"""Session 32 (2026-09-27, window closed), POST HOC replication on the stored P3 block (seeds 1050-1079, GPU), no training.

Hypothesis fixed from the N28 analysis (speed_switch_cost_n28_s32.py, same session) BEFORE looking at any P3 generalisation step:
  Q-a' a switch at 25 delays grokking against the destination-only run; unit = seed, statistic = mean over both directions of
       log2(bounded time switch) - log2(bounded time destination-only) (bounded = min(gen, horizon)); exact one-sided sign test
       over seeds, primary for overlap level w0 (like N28), w400 (omega = 0.4: 40 % of the train pairs shared, drawn uniformly) descriptive.
  python lab/confirm/speed_switch_cost_p3_s32.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
RAW = LAB / "confirm/p3_raw"
PAT = re.compile(r"seed(\d+)_thr1_p3_seed\d+_(w\d+)_(A|B)(?:_to_p3_seed\d+_w\d+_(A|B)_at(\d+))?_devcuda$")


def sign_p(k: int, n: int) -> float:
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0


def main() -> None:
    runs = {}
    for d in RAW.iterdir():
        m = PAT.search(d.name)
        s, w, a, b = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        assert r["status"] == "completed", d.name
        g, h = (r.get("events") or {}).get("generalization_step"), r["steps_completed"]
        runs.setdefault(w, {}).setdefault(s, {})[a if b is None else a + b] = {"lb": math.log2(min(g if g is not None else h, h)),
                                                                              "ev": g is not None, "th": r["test_hash"]}
    out = {"note": "post hoc replication, hypothesis fixed from N28 before looking"}
    for w, ss in sorted(runs.items()):
        for s, r in ss.items():
            assert len({v["th"] for v in r.values()}) == 1, (w, s)
        d = [((r["AB"]["lb"] - r["B"]["lb"]) + (r["BA"]["lb"] - r["A"]["lb"])) / 2 for r in ss.values()]
        k, n = sum(v > 0 for v in d), sum(v != 0 for v in d)
        out[w] = {"n_seeds": len(ss), "later": k, "nonzero": n, "p_one_sided": sign_p(k, n), "median_log2": float(np.median(d)),
                  "events": {arm: sum(r[arm]["ev"] for r in ss.values()) for arm in ("A", "B", "AB", "BA")}}
    (LAB / "confirm/speed_switch_cost_p3_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
