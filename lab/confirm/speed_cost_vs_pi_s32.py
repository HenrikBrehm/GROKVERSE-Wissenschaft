"""Session 32 (2026-09-27, window closed), POST HOC on the stored N28 block (30 seeds), no training.

Question: is the switch cost at 25 steps largest in seeds whose final choice is most undecided (persistence pi(25) closest to 0.5)?
Stated before looking at the joint values: Spearman(|pi(25) - 0.5|, C(25)) < 0 over the 30 seeds, one-sided permutation p
(20 000, seed 0). Descriptive: Spearman(pi(25), C(25)), the same at 50, and the distribution of pi(25).
pi from lab/confirm/N28_summary.json (frozen N28 analysis); C(t) from R6_pilot_power.json (R6 definition, common cap 2000).
  python lab/confirm/speed_cost_vs_pi_s32.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
CAP = 2000


def spear(x, y) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def costs() -> dict[int, dict[int, float]]:
    pat = re.compile(r"seed(\d+)_thr1_n28_seed\d+_w0_(A|B)(?:_to_n28_seed\d+_w0_(A|B)_at(\d+)(_rom)?)?_devcuda$")
    lb: dict = {}
    for d in (LAB / "confirm/n28_raw").iterdir():
        m = pat.search(d.name)
        if not m or m.group(5):
            continue
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        g = (r.get("events") or {}).get("generalization_step")
        s, a, b, t = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        lb.setdefault(s, {})[a if b is None else (a + b, int(t))] = math.log2(min(g, CAP) if g is not None else CAP)
    return {s: {t: ((v[("AB", t)] - v["B"]) + (v[("BA", t)] - v["A"])) / 2 for t in (25, 50)} for s, v in lb.items()}


def main() -> None:
    pi = {r["seed"]: r["pi"] for r in json.loads((LAB / "confirm/N28_summary.json").read_text(encoding="utf-8"))["rows"] if r["valid"]}
    C = costs()
    seeds = sorted(set(pi) & set(C))
    p25 = np.array([pi[s]["normal25"] for s in seeds])
    p50 = np.array([pi[s]["normal50"] for s in seeds])
    c25 = np.array([C[s][25] for s in seeds])
    c50 = np.array([C[s][50] for s in seeds])
    dist = np.abs(p25 - 0.5)
    rho = spear(dist, c25)
    rng = np.random.default_rng(0)
    null = np.array([spear(dist, rng.permutation(c25)) for _ in range(20000)])
    out = {"note": "post hoc exploration on N28", "n": len(seeds), "primary_spearman_abs_pi25_minus_half_vs_C25": rho,
           "p_one_sided": float((null <= rho).mean()), "spearman_pi25_C25": spear(p25, c25), "spearman_pi50_C50": spear(p50, c50),
           "pi25_quartiles": np.percentile(p25, [0, 25, 50, 75, 100]).round(3).tolist(),
           "pi50_quartiles": np.percentile(p50, [0, 25, 50, 75, 100]).round(3).tolist()}
    (LAB / "confirm/speed_cost_vs_pi_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
