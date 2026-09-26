"""EXP-036 (design after Nachtrag a, Codex review 2026-09-26): are the "foreign" frequencies of mixed states set by
the init? Definition: README.md.

Pairs (split s, new init i): (30,130) (31,131) (32,132) (33,133) (34,134) (30,230) (31,231). Old = EXP-020 runs of
split s with init s. Foreign sets F_new / F_old: union over t in {10, 25, 50} of top-5(t + 2000) minus
A = F u G u fold(2k) u K_onlyF u K_onlyG (pure runs of the SAME init). All runs pass the fail-closed loader.
Unit of inference = pair. Pair evaluable if all runs valid and F_new non-empty.
  d_p = mean over k in F_new of (rank_old(k) - rank_new(k))   (ranks in the step-0 W_E spectra; > 0: new init favours them)
  success_p = d_p > 0;  J_p = |F_new n F_old| / |F_new u F_old|
Verdict: m evaluable pairs < 5 -> nicht auswertbar; one-sided sign test over pairs p < 0.05 AND mean J < 0.5 ->
init-getrieben; share of successes <= 0.5 -> nicht init-getrieben; else unklar.
Descriptive only: frequency-level pooled counts, symmetric statistic on the fresh-old pairs (33, 34), test accuracies.
Usage: python analyze.py [--selftest]
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
from conflict_freqs import EARLY, fold, foreign_sets, ranks  # noqa: E402

PAIRS = ((30, 130), (31, 131), (32, 132), (33, 133), (34, 134), (30, 230), (31, 231))
MIN_PAIRS, J_MAX, ALPHA = 5, 0.5, 0.05


def sign_p(k: int, n: int) -> float:
    """One-sided P(X >= k), X ~ Bin(n, 1/2)."""
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n


def verdict(successes: list[bool], jaccards: list[float]) -> str:
    m, k = len(successes), sum(successes)
    if m < MIN_PAIRS:
        return "nicht auswertbar"
    if sign_p(k, m) < ALPHA and float(np.mean(jaccards)) < J_MAX:
        return "init-getrieben"
    return "nicht init-getrieben" if k / m <= 0.5 else "unklar"


def pair_stats(f_new: set[int], f_old: set[int], r_new: dict[int, int], r_old: dict[int, int]) -> dict:
    d = float(np.mean([r_old[k] - r_new[k] for k in f_new]))
    union = f_new | f_old
    return {"d": d, "success": d > 0, "J": len(f_new & f_old) / len(union) if union else 0.0,
            "per_freq": {k: {"rank_new": r_new[k], "rank_old": r_old[k]} for k in sorted(f_new)}}


def main() -> None:
    rows, succ, jac, freq_level = [], [], [], []
    for s, i in PAIRS:
        new, e_new = foreign_sets(HERE / "raw", i, s, EARLY, 2000)
        old, e_old = foreign_sets(E20 / "raw", s, s, EARLY, 8000)
        if e_new or e_old:
            rows.append({"split": s, "init": i, "status": f"invalid: {e_new or e_old}"})
            continue
        if new["init_checksum"] == old["init_checksum"]:
            rows.append({"split": s, "init": i, "status": "invalid: init not changed"})
            continue
        f_new = {k for v in new["foreign"].values() for k in v}
        f_old = {k for v in old["foreign"].values() for k in v}
        r_new, r_old = ranks(new["init_spec"]), ranks(old["init_spec"])
        row = {"split": s, "init": i, "F_new": sorted(f_new), "F_old": sorted(f_old),
               "foreign_by_t": new["foreign"], "test_acc": new["test_acc"]}
        if not f_new:
            rows.append(row | {"status": "no foreign frequency (not evaluable)"})
            continue
        st = pair_stats(f_new, f_old, r_new, r_old)
        succ.append(st["success"])
        jac.append(st["J"])
        freq_level += [v["rank_new"] < v["rank_old"] for v in st["per_freq"].values()]
        if s in (33, 34) and i == s + 100 and f_old:     # old side fresh only for these splits
            st["symmetric"] = st["d"] + float(np.mean([r_new[k] - r_old[k] for k in f_old]))
        rows.append(row | {"status": "ok"} | st)
    m, k = len(succ), sum(succ)
    summary = {"rows": rows, "pairs_evaluable": m, "successes": k, "p_sign_pairs": sign_p(k, m) if m else None,
               "mean_J": float(np.mean(jac)) if jac else None, "verdict": verdict(succ, jac),
               "freq_level_descriptive": f"{sum(freq_level)}/{len(freq_level)} rank_new < rank_old"}
    for r in rows:
        print(r)
    print({k2: v for k2, v in summary.items() if k2 != "rows"})
    (HERE / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")


def selftest() -> None:
    assert verdict([True] * 4, [0.0] * 4) == "nicht auswertbar"
    assert verdict([True] * 5, [0.0] * 5) == "init-getrieben"          # p = 1/32
    assert verdict([True] * 5, [0.6] * 5) == "unklar"                   # identical-ish sets block the verdict
    assert verdict([True] * 5 + [False], [0.0] * 6) == "unklar"         # 5/6: p = 0.109
    assert verdict([True] * 6 + [False], [0.0] * 7) == "unklar"          # 6/7: p = 0.0625
    assert verdict([True] * 7, [0.0] * 7) == "init-getrieben"            # 7/7: p = 0.0078
    assert verdict([True, False] * 3, [0.0] * 6) == "nicht init-getrieben"
    # one pair with many concordant frequencies counts once
    st = pair_stats({1, 2, 3, 4, 5}, set(), {k: k for k in range(1, 57)}, {k: 57 - k for k in range(1, 57)})
    assert st["success"] and st["J"] == 0.0
    st = pair_stats({7}, {7}, {7: 30}, {7: 3})
    assert not st["success"] and st["J"] == 1.0
    assert fold(2 * 60) == 7
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
