"""R6 descriptive addendum (session 32, fixed BEFORE any R6 run): after a switch at 50 the new split is fitted through the already fixed
features. Prediction from N28 (post hoc, speed_switch_fitroute_s32.py: +0.25 test accuracy at the same step, 30/30; none at 25, 15/30):
on the fresh R6 seeds, test accuracy at the moment the new split is memorised (train >= 0.99; last test evaluation at or before it)
exceeds the destination-only run's test accuracy at the same absolute step, per seed mean over both directions:
  at t = 50 in a majority of seeds with exact one-sided sign test p < 0.05 ('gestützt'); at t = 25 reported descriptively.
Run only after `confirm_r6.py --analyze` reported a complete block.   python lab/confirm/R6_fitroute.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
PAT = re.compile(r"seed(\d+)_thr1_r6_seed\d+_w0_(A|B)(?:_to_r6_seed\d+_w0_(A|B)_at(\d+))?_devcuda$")


def acc_at(r: dict, step: int) -> float:
    dn = r["dense"]
    return float([a for s, a in zip(dn["test_steps"], dn["test_acc"]) if s <= step][-1])


def main() -> None:
    summ = json.loads((LAB / "confirm/R6_summary.json").read_text(encoding="utf-8"))
    if summ.get("n_valid") != summ.get("n_planned"):
        raise SystemExit("R6 not fully valid; addendum not run")
    R: dict = {}
    for d in (LAB / "confirm/r6_raw").iterdir():
        m = PAT.search(d.name)
        if not m:
            continue
        s, a, b, t = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        R.setdefault(s, {})[a if b is None else (a + b, int(t))] = json.loads((d / "result.json").read_text(encoding="utf-8"))
    out = {}
    for t in sorted({k[1] for v in R.values() for k in v if isinstance(k, tuple)}):
        diffs = []
        for v in R.values():
            ds = []
            for k, dest in ((("AB", t), "B"), (("BA", t), "A")):
                mem = v[k]["transitions"]["primary"]["memorization"]["first_crossing_step"]
                if mem is not None:
                    ds.append(acc_at(v[k], mem) - acc_at(v[dest], mem))
            if len(ds) == 2:
                diffs.append(float(np.mean(ds)))
        d = np.array(diffs)
        nz = d[np.abs(d) > 1e-12]
        k, n = int((nz > 0).sum()), len(nz)
        out[str(t)] = {"n_seeds": len(d), "mean_diff": float(d.mean()) if len(d) else None, "pos": k, "nonzero": n,
                       "p_one_sided": sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0}
    r50 = out.get("50", {})
    out["reading_t50"] = "gestützt" if r50.get("p_one_sided", 1.0) < 0.05 else "nicht gestützt"
    (LAB / "confirm/R6_fitroute.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
