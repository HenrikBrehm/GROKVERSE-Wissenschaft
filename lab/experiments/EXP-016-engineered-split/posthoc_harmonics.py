"""Post hoc (session 5; pattern noticed by eye in the EXP-016 misses AFTER seeing them, so exploratory only):
are learned non-target frequencies harmonics fold(h*k) of the target frequencies k (h = 2, 3)?
fold(x) = min(x mod p, p - x mod p). Control: harmonics of the OTHER arm's targets. Chance per miss: |H \ T| / 51."""
from __future__ import annotations

import json
from math import prod
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P = 113


def fold(x: int) -> int:
    x %= P
    return min(x, P - x)


rows = json.loads((HERE / "posthoc_m0c.json").read_text(encoding="utf-8"))
tgt = {(r["seed"], r["arm"]): set(r["targets"]) for r in rows}
res = {}
for h in (2, 3):
    hits, ctrl, chance, chance_c, n = 0, 0, [], [], 0
    for r in rows:
        T = set(r["targets"])
        other = tgt.get((r["seed"], "G" if r["arm"] == "F" else "F"), set())
        H = {fold(h * k) for k in T} - T
        Hc = {fold(h * k) for k in other} - T
        for m in r["missed"]:
            n += 1
            hits += m in H
            ctrl += m in Hc
            chance.append(len(H) / (56 - len(T)))
            chance_c.append(len(Hc) / (56 - len(T)))
    # exact probability of >= hits under independent Bernoulli(chance_i) (Poisson-binomial via DP)
    def tail(ps: list[float], k: int) -> float:
        dp = np.zeros(len(ps) + 1)
        dp[0] = 1.0
        for q in ps:
            dp[1:] = dp[1:] * (1 - q) + dp[:-1] * q
            dp[0] *= (1 - q)
        return float(dp[k:].sum())
    res[f"h{h}"] = {"n_missed": n, "hits_own_targets": hits, "expected_by_chance": float(sum(chance)),
                    "p_ge_hits": tail(chance, hits), "hits_other_arm_control": ctrl,
                    "expected_control": float(sum(chance_c))}
detail = [{"seed": r["seed"], "arm": r["arm"], "missed": r["missed"],
           "which": {m: [k for k in r["targets"] if fold(2 * k) == m] for m in r["missed"]}} for r in rows]
(HERE / "posthoc_harmonics.json").write_text(json.dumps({"summary": res, "detail": detail}, indent=1), encoding="utf-8")
for d in detail:
    print(d)
print(json.dumps(res, indent=1))
