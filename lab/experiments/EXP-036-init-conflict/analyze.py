"""EXP-036: are the "foreign" frequencies of mixed states (EXP-020 Nachtrag d) set by the init? Definition: README.md.

Pairs: split set s in {30, 31, 32} (EXP-020 splits) x new init seed s + 100. For the new init:
  A = F u G u {fold(2k)} u K_onlyF u K_onlyG (K_only* = top-5 of W_E at step 2000 of the pure runs of THIS init)
  foreign = union over t in {10, 25, 50} of top-5(step t + 2000) minus A
For every distinct foreign frequency k of a pair: success if rank_new(k) < rank_old(k), ranks in the step-0 W_E spectrum
of the new init (EXP-036) and of the old init (EXP-020 seed s). Pooled one-sided sign test.
Verdict: n < 5 -> nicht auswertbar; share >= 0.75 and p < 0.05 -> init-getrieben; share <= 0.5 -> nicht init-getrieben;
else unklar. Secondary (descriptive): overlap with the EXP-020 foreign set of the same split, median rank_new.
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
from conflict_freqs import fold, ranks, spectrum, top  # noqa: E402

SPLITS, OFFSET, EARLY, G_BUDGET = (30, 31, 32), 100, (10, 25, 50), 2000


def sign_p(k: int, n: int) -> float:
    """One-sided P(X >= k), X ~ Bin(n, 1/2)."""
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n


def verdict(k: int, n: int) -> str:
    if n < 5:
        return "nicht auswertbar"
    share = k / n
    if share >= 0.75 and sign_p(k, n) < 0.05:
        return "init-getrieben"
    return "nicht init-getrieben" if share <= 0.5 else "unklar"


def foreign_set(root: Path, init: int, s: int, fg: set[int]) -> tuple[set[int] | None, np.ndarray | None, str]:
    base = f"EXP-018_baseline_seed{init}_thr4_seed{s}_train_"
    pf, pg = spectrum(root / (base + "F"), G_BUDGET), spectrum(root / (base + "G"), G_BUDGET)
    init_pw = spectrum(root / (base + "F"), 0)
    if pf is None or pg is None or init_pw is None:
        return None, None, "pure run missing"
    allowed = fg | {fold(2 * k) for k in fg} | top(pf) | top(pg)
    out: set[int] = set()
    for t in EARLY:
        d = root / f"EXP-020_baseline_seed{init}_thr4_seed{s}_train_F_to_seed{s}_train_G_at{t}"
        res = d / "result.json"
        if not res.exists() or json.loads(res.read_text(encoding="utf-8"))["status"] != "completed":
            return None, None, f"t={t} missing/incomplete"
        pw = spectrum(d, t + G_BUDGET)
        if pw is None:
            return None, None, f"t={t} no spectrum at {t + G_BUDGET}"
        out |= top(pw) - allowed
    return out, init_pw, "ok"


def main() -> None:
    rows, pooled = [], []
    for s in SPLITS:
        tg = json.loads((E20 / f"splits/seed{s}.json").read_text(encoding="utf-8"))["targets"]
        fg = set(tg["F"]) | set(tg["G"])
        new, init_new, why = foreign_set(HERE / "raw", s + OFFSET, s, fg)
        old, init_old, why_old = foreign_set(E20 / "raw", s, s, fg)
        if new is None or old is None:
            rows.append({"split": s, "status": f"new: {why}; old: {why_old}"})
            continue
        if np.allclose(init_new, init_old):
            rows.append({"split": s, "status": "init spectra identical (init not changed)"})
            continue
        r_new, r_old = ranks(init_new), ranks(init_old)
        per = {k: {"rank_new": r_new[k], "rank_old": r_old[k], "success": r_new[k] < r_old[k]} for k in sorted(new)}
        pooled += [v["success"] for v in per.values()]
        rows.append({"split": s, "init": s + OFFSET, "status": "ok", "foreign_new": per,
                     "foreign_old": sorted(old), "overlap": sorted(new & old),
                     "median_rank_new": float(np.median([v["rank_new"] for v in per.values()])) if per else None})
    k, n = sum(pooled), len(pooled)
    complete = all(r["status"] == "ok" for r in rows)
    summary = {"rows": rows, "k": k, "n": n, "p_one_sided": sign_p(k, n) if n else None,
               "verdict": verdict(k, n) if complete else "nicht auswertbar (unvollständig)"}
    for r in rows:
        print(r)
    print(f"sign test: {k}/{n} rank_new < rank_old, p = {summary['p_one_sided']}, verdict: {summary['verdict']}")
    (HERE / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")


def selftest() -> None:
    assert verdict(4, 4) == "nicht auswertbar"
    assert verdict(5, 5) == "init-getrieben" and sign_p(5, 5) == 1 / 32
    assert verdict(6, 8) == "unklar"            # 0.75 but p = 0.145
    assert verdict(9, 12) == "unklar"           # 0.75, p = 0.073
    assert verdict(10, 12) == "init-getrieben"  # p = 0.019
    assert verdict(3, 6) == "nicht init-getrieben"
    assert fold(2 * 60) == 7 and fold(113 + 5) == 5
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
