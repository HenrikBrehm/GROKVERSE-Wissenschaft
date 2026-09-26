"""EXP-036 Nachtrag d (fixed 2026-09-26, session 10, before any EXP-036 run): calibrated test of P36b.

Question: are the new foreign frequencies of mixed states the ones that BOTH data sets push early, before the lock-in
window (25-50 steps), and is this a tighter predictor than the init spectrum?
Per evaluable pair p (as in analyze.py: all runs valid, F_new non-empty), with the pure runs of the SAME new init:
  C = {1..56} minus A (A exactly as in foreign_sets), candidates the foreign frequencies are drawn from.
  growth_X(k) = W_E power at step TAU minus power at step 0 in pure run X (X = F, G); rank_X = rank of growth_X within C
  (1 = largest). Shared-support score S(k) = max(rank_F, rank_G) (conjunctive: both must push k), ties by
  rank_F + rank_G, then k. q(k) = position in C / |C| (1-based; P(q <= 0.25) <= 0.25 under the null).
  q_p = mean over k in F_new of q(k);  q_init_p likewise with C ordered by init power (step 0, descending).
Test 1 (vs chance): success1_p = q_p <= 0.25. Under H0 (F_new independent of S within C) P(q_p <= 0.25) <= 0.25 for any
  |F_new| >= 1, so X ~ Bin(m, 0.25) is conservative. m < 5 -> nicht auswertbar; P(X >= k) < 0.05 -> gestuetzt;
  k / m <= 0.25 -> nicht gestuetzt; else unklar.
Test 2 (vs init): success2_p = q_p < q_init_p; one-sided sign test over pairs, p < 0.05 -> enger als Init;
  k / m <= 0.5 -> nicht enger; else unklar.
Descriptive only: the same with TAU in (10, 50), and the level (not growth) variant at TAU.
Nachtrag e (after Codex review, before any run): (1) candidates without positive growth in BOTH arms rank last;
(2) pair evaluable only if not locked by t = 25 (top-5 of the t = 25 switch run != top-5 of pure F), so TAU = 20 is
pre-lock-in; (3) Test 1 is NOT selection-corrected (uniform null); (4) Test 3: success3_p = q_p < min(q_p of one-arm
growth F, G); sign test. "Shared support" is claimed only if Test 1 gestuetzt AND Test 3 significant; Test 2 is
prediction, not mechanism (unequal information).
Usage: python analyze_p36b.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
E20 = HERE.parent / "EXP-020-data-switch"
sys.path.insert(0, str(E20))
sys.path.insert(0, str(HERE))
from analyze import PAIRS, sign_p  # noqa: E402
from conflict_freqs import EARLY, G_BUDGET, fold, foreign_sets, load_run, top  # noqa: E402

TAU, TAU_DESCR = 20, (10, 50)
MIN_PAIRS, ALPHA, Q_MAX, PI0 = 5, 0.05, 0.25, 0.25


def binom_p(k: int, n: int, pi: float) -> float:
    """One-sided P(X >= k), X ~ Bin(n, pi)."""
    return sum(comb(n, i) * pi ** i * (1 - pi) ** (n - i) for i in range(k, n + 1))


def positions(cand: list[int], key) -> dict[int, float]:
    order = sorted(cand, key=key)
    return {k: (i + 1) / len(order) for i, k in enumerate(order)}


def shared_q(cand: list[int], gf: np.ndarray, gg: np.ndarray) -> dict[int, float]:
    """q per candidate under the conjunctive shared-support score; gf, gg indexed k-1. Codex (Nachtrag e): candidates
    that do not grow in BOTH arms rank after all that do."""
    rf = {k: r + 1 for r, k in enumerate(sorted(cand, key=lambda k: (-gf[k - 1], k)))}
    rg = {k: r + 1 for r, k in enumerate(sorted(cand, key=lambda k: (-gg[k - 1], k)))}
    return positions(cand, lambda k: (not (gf[k - 1] > 0 and gg[k - 1] > 0), max(rf[k], rg[k]), rf[k] + rg[k], k))


def single_q(cand: list[int], g: np.ndarray) -> dict[int, float]:
    """Nachtrag e: one-arm growth predictor (Test 3 comparison)."""
    return positions(cand, lambda k: (-g[k - 1], k))


def verdict1(succ: list[bool]) -> str:
    m, k = len(succ), sum(succ)
    if m < MIN_PAIRS:
        return "nicht auswertbar"
    if binom_p(k, m, PI0) < ALPHA:
        return "gestuetzt"
    return "nicht gestuetzt" if k / m <= PI0 else "unklar"


def verdict2(succ: list[bool]) -> str:
    m, k = len(succ), sum(succ)
    if m < MIN_PAIRS:
        return "nicht auswertbar"
    if sign_p(k, m) < ALPHA:
        return "enger als Init"
    return "nicht enger" if k / m <= 0.5 else "unklar"


def pair_row(s: int, i: int) -> dict:
    new, err = foreign_sets(HERE / "raw", i, s, EARLY, G_BUDGET)
    if err:
        return {"split": s, "init": i, "status": f"invalid: {err}"}
    f_new = sorted({k for v in new["foreign"].values() for k in v})
    if not f_new:
        return {"split": s, "init": i, "status": "no foreign frequency (not evaluable)"}
    steps = (0, TAU, *TAU_DESCR, G_BUDGET)
    pf, e1 = load_run(HERE / "raw", i, s, "F", None, G_BUDGET, steps)
    pg, e2 = load_run(HERE / "raw", i, s, "G", None, G_BUDGET, steps)
    if e1 or e2:
        return {"split": s, "init": i, "status": f"invalid early spectra: {e1 or e2}"}
    tg = json.loads((E20 / f"splits/seed{s}.json").read_text(encoding="utf-8"))["targets"]
    fg = set(tg["F"]) | set(tg["G"])
    allowed = fg | {fold(2 * k) for k in fg} | top(pf["spec"][G_BUDGET]) | top(pg["spec"][G_BUDGET])
    cand = [k for k in range(1, 57) if k not in allowed]
    assert set(f_new) <= set(cand), "foreign set must lie in the candidate set"
    sw25, e3 = load_run(HERE / "raw", i, s, "FG", 25, None, (25 + G_BUDGET,))
    if e3:
        return {"split": s, "init": i, "status": f"invalid switch run: {e3}"}
    if top(sw25["spec"][25 + G_BUDGET]) == top(pf["spec"][G_BUDGET]):   # Nachtrag e gate: locked by step 25
        return {"split": s, "init": i, "status": "locked by t = 25 (tau not pre-lock-in, not evaluable)"}
    init = pf["spec"][0]
    q_init = positions(cand, lambda k: (-init[k - 1], k))
    row = {"split": s, "init": i, "status": "ok", "F_new": f_new, "n_cand": len(cand)}
    for tau in (TAU, *TAU_DESCR):
        q = shared_q(cand, pf["spec"][tau] - init, pg["spec"][tau] - init)
        ql = shared_q(cand, pf["spec"][tau], pg["spec"][tau])
        row[f"tau{tau}"] = {"q_p": float(np.mean([q[k] for k in f_new])),
                            "q_level": float(np.mean([ql[k] for k in f_new])),
                            "q_single": min(float(np.mean([qs[k] for k in f_new]))
                                            for qs in (single_q(cand, pf["spec"][tau] - init),
                                                       single_q(cand, pg["spec"][tau] - init))),
                            "both_grow": sum(bool(pf["spec"][tau][k - 1] > init[k - 1]
                                                  and pg["spec"][tau][k - 1] > init[k - 1]) for k in f_new),
                            "per_freq": {k: round(q[k], 3) for k in f_new}}
    row["q_init"] = float(np.mean([q_init[k] for k in f_new]))
    return row


def main() -> None:
    rows = [pair_row(s, i) for s, i in PAIRS]
    ok = [r for r in rows if r["status"] == "ok"]
    s1 = [r[f"tau{TAU}"]["q_p"] <= Q_MAX for r in ok]
    s2 = [r[f"tau{TAU}"]["q_p"] < r["q_init"] for r in ok]
    s3 = [r[f"tau{TAU}"]["q_p"] < r[f"tau{TAU}"]["q_single"] for r in ok]
    summary = {"rows": rows, "pairs_evaluable": len(ok), "tau": TAU,
               "test1_successes": sum(s1), "test1_p": binom_p(sum(s1), len(s1), PI0) if s1 else None,
               "verdict_P36b_cal": verdict1(s1),
               "test2_successes": sum(s2), "test2_p": sign_p(sum(s2), len(s2)) if s2 else None,
               "verdict_vs_init": verdict2(s2),
               "test3_successes": sum(s3), "test3_p": sign_p(sum(s3), len(s3)) if s3 else None,
               "verdict_vs_single_arm": verdict2(s3).replace("Init", "Einarm"),
               "verdict_shared_support": ("gestuetzt" if verdict1(s1) == "gestuetzt" and verdict2(s3) == "enger als Init"
                                          else "nicht gezeigt"),
               "descriptive": {f"tau{t}": [round(r[f"tau{t}"]["q_p"], 3) for r in ok] for t in TAU_DESCR}
               | {"q_init": [round(r["q_init"], 3) for r in ok]}}
    for r in rows:
        print(r)
    print({k: v for k, v in summary.items() if k != "rows"})
    (HERE / "summary_p36b.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")


def selftest() -> None:
    assert abs(binom_p(0, 5, PI0) - 1) < 1e-12
    assert verdict1([True] * 4) == "nicht auswertbar"
    assert verdict1([True] * 4 + [False]) == "gestuetzt"             # P(X>=4 | 5, .25) = 0.0156
    assert verdict1([True] * 3 + [False] * 2) == "unklar"             # 0.104
    assert verdict1([True] * 4 + [False] * 3) == "unklar"             # 7 pairs: 4 -> 0.071
    assert verdict1([True] * 5 + [False] * 2) == "gestuetzt"          # 0.0129
    assert verdict1([True] + [False] * 6) == "nicht gestuetzt"
    assert verdict2([True] * 5) == "enger als Init" and verdict2([True] * 6 + [False]) == "unklar"
    assert verdict2([True, False] * 3) == "nicht enger"
    # conjunctive score: k pushed by both beats k pushed strongly by only one
    gf, gg = np.zeros(56), np.zeros(56)
    gf[[0, 1, 2]] = [9, 8, 1]      # k = 1, 2, 3 in F
    gg[[0, 1, 2]] = [-5, 7, 6]     # k = 2, 3 in G; k = 1 only in F (shrinks in G)
    q = shared_q(list(range(1, 11)), gf, gg)
    assert q[2] < q[3] < q[1] and q[2] == 0.1 and q[1] == 0.9   # k = 10 (S = 10 too) loses the tie on rank_F + rank_G
    # under H0 the mean-q success rate is <= PI0 (Monte Carlo, sizes 1-3)
    rng = np.random.default_rng(0)
    for n, nc in ((1, 30), (1, 37), (2, 30), (3, 41)):
        rate = np.mean([np.mean((rng.choice(nc, n, replace=False) + 1) / nc) <= Q_MAX
                        for _ in range(20000)])
        assert rate <= PI0 + 0.01, (n, rate)
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
