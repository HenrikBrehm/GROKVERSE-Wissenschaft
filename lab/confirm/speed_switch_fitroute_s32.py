"""Session 32 (2026-09-27), POST HOC on N28 (30 seeds), no training (skeptic point 6: why does a switch at 50 speed grokking up?).
Idea: at 50 the Fourier features of the first split are fixed (pi ~ 1); the new split is then fitted through these general features
instead of by memorising, so test accuracy is already higher at the moment the new split is memorised. Stated before looking:
test accuracy at the memorisation step (first train >= 0.99 on the current split; nearest test evaluation at or before it) is higher
after a switch at 50 than in the destination-only run (per seed mean over both directions; exact one-sided sign test). Descriptive: at 25.
  python lab/confirm/speed_switch_fitroute_s32.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
PAT = re.compile(r"seed(\d+)_thr1_n28_seed\d+_w0_(A|B)(?:_to_n28_seed\d+_w0_(A|B)_at(\d+)(_rom)?)?_devcuda$")


def test_at_mem(r: dict) -> float | None:
    m = r["transitions"]["primary"]["memorization"]["first_crossing_step"]
    if m is None:
        return None
    dn = r["dense"]
    prev = [a for s, a in zip(dn["test_steps"], dn["test_acc"]) if s <= m]
    return float(prev[-1]) if prev else None


def acc_at(r: dict, step: int) -> float:
    dn = r["dense"]
    return float([a for s, a in zip(dn["test_steps"], dn["test_acc"]) if s <= step][-1])


def main() -> None:
    R: dict = {}
    RR: dict = {}
    for d in (LAB / "confirm/n28_raw").iterdir():
        m = PAT.search(d.name)
        if not m or m.group(5):
            continue
        s, a, b, t = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        R.setdefault(s, {})[a if b is None else (a + b, int(t))] = test_at_mem(r)
        RR.setdefault(s, {})[a if b is None else (a + b, int(t))] = r
    out = {}
    for t in (25, 50):
        d, sw_vals, de_vals = [], [], []
        for v in R.values():
            pair = [(v[("AB", t)], v["B"]), (v[("BA", t)], v["A"])]
            if any(x is None or y is None for x, y in pair):
                continue
            d.append(np.mean([x - y for x, y in pair]))
            sw_vals += [x for x, _ in pair]
            de_vals += [y for _, y in pair]
        d = np.array(d)
        nz = d[np.abs(d) > 1e-12]
        k, n = int((nz > 0).sum()), len(nz)
        out[f"t{t}"] = {"n_seeds": len(d), "mean_diff": float(d.mean()), "pos": k, "nonzero": n,
                        "p_one_sided": sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0,
                        "test_at_mem_switch_median": float(np.median(sw_vals)), "test_at_mem_dest_median": float(np.median(de_vals))}
    # control added after the first look (same session, labelled): destination-only test accuracy at the SAME absolute step
    # as the switch run's memorisation step (removes "later step -> more test accuracy")
    for t in (25, 50):
        d = []
        for v in RR.values():
            ds = []
            for k, dest in ((("AB", t), "B"), (("BA", t), "A")):
                m = v[k]["transitions"]["primary"]["memorization"]["first_crossing_step"]
                ds.append(acc_at(v[k], m) - acc_at(v[dest], m))
            d.append(np.mean(ds))
        d = np.array(d)
        out[f"t{t}"]["same_step_control"] = {"mean_diff": float(d.mean()), "pos": int((d > 0).sum()), "n": len(d)}
    (LAB / "confirm/speed_switch_fitroute_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
