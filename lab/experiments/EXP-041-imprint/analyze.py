"""EXP-041 analysis (pre-registered, README): does a short prefix imprint the frequency choice when the rest of training
uses a different split, in both directions (engineered E -> random R, and R -> E)? Splits of EXP-018 (seeds 20-25,
common test set). K = top-5 of W_E at the end (step t + 2000; pure runs: step 2000).
  Ex = targets(E) u fold(2 targets(E)); Rx = K_R u fold(2 K_R) (K_R = pure-R run of the same init); shared removed.
  d(K) = |K n Ex| - |K n Rx|.
Seed valid: all 5 runs pass the fail-closed loader, same init checksum, d(pure E) > 0 > d(pure R).
P41a (E -> R at 150): held = d > 0.  P41b (R -> E at 150): held = d < 0.  Secondary: R -> E at 50 (descriptive).
Verdicts (each): m valid < 5 -> nicht auswertbar; one-sided sign test p < 0.05 for 'held' -> gepraegt;
  one-sided sign test p < 0.05 for 'flipped' (d of the opposite sign) -> ueberschrieben; else gemischt.
  (d = 0 counts as neither and against both.)
Usage: python analyze.py [--selftest]"""
from __future__ import annotations

import json
import sys
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[0]
SPL = LAB / "EXP-018-split-speed" / "splits"
sys.path.insert(0, str(LAB.parent.parent / "training"))
from grokverse.data import split_hash  # noqa: E402

P, M, G_BUDGET, MIN_SEEDS, ALPHA = 113, 5, 2000, 5, 0.05
SEEDS = range(20, 26)
RUNS = {"R": ("R", None, None), "E": ("E", None, None), "ER150": ("E", "R", 150), "RE150": ("R", "E", 150),
        "RE50": ("R", "E", 50)}


def fold(k: int) -> int:
    k %= P
    return min(k, P - k)


def sign_p(k: int, n: int) -> float:
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n


def run_dir(s: int, key: str) -> Path:
    a, b, t = RUNS[key]
    if b is None:
        return HERE / "raw" / f"EXP-018_baseline_seed{s}_thr4_seed{s}_train_{a}"
    return HERE / "raw" / f"EXP-020_baseline_seed{s}_thr4_seed{s}_train_{a}_to_seed{s}_train_{b}_at{t}"


def load(s: int, key: str) -> tuple[dict | None, str | None]:
    a, b, t = RUNS[key]
    d = run_dir(s, key)
    try:
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, f"{key}: unreadable ({type(e).__name__})"
    want = G_BUDGET + (t or 0)
    if r.get("status") != "completed" or r.get("seed") != s or r.get("steps_completed") != want:
        return None, f"{key}: status/seed/steps"
    if r.get("split_hash") != split_hash(np.load(SPL / f"seed{s}_train_{a}.npy")):
        return None, f"{key}: split hash"
    if r.get("test_hash") != split_hash(np.load(SPL / f"seed{s}_test.npy")):
        return None, f"{key}: test hash"
    if t is not None:
        sw = r.get("events", {}).get("switch", {})
        if sw.get("step") != t or sw.get("new_train_hash") != split_hash(np.load(SPL / f"seed{s}_train_{b}.npy")):
            return None, f"{key}: switch not as specified"
    return r, None


def d_value(K: set[int], ex: set[int], rx: set[int]) -> int:
    shared = ex & rx
    return len(K & (ex - shared)) - len(K & (rx - shared))


def verdict(held: list[bool], flipped: list[bool]) -> str:
    m = len(held)
    if m < MIN_SEEDS:
        return "nicht auswertbar"
    if sign_p(sum(held), m) < ALPHA:
        return "gepraegt"
    return "ueberschrieben" if sign_p(sum(flipped), m) < ALPHA else "gemischt"


def seed_row(s: int) -> dict:
    runs = {}
    for key in RUNS:
        r, err = load(s, key)
        if err:
            return {"seed": s, "valid": False, "why": err}
        runs[key] = r
    if len({r["init_checksum_shared"] for r in runs.values()}) != 1:
        return {"seed": s, "valid": False, "why": "init differs"}
    tE = set(json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"])
    K = {k: set(r["final_top_m_freqs"]) for k, r in runs.items()}
    ex = tE | {fold(2 * k) for k in tE}
    rx = K["R"] | {fold(2 * k) for k in K["R"]}
    d = {k: d_value(v, ex, rx) for k, v in K.items()}
    row = {"seed": s, "K": {k: sorted(v) for k, v in K.items()}, "d": d,
           "test_acc": {k: r["final_acc"]["test"] for k, r in runs.items()}}
    if not (d["E"] > 0 > d["R"]):
        return row | {"valid": False, "why": "pure runs not discriminable (need d(E) > 0 > d(R))"}
    return row | {"valid": True}


def main() -> None:
    rows = [seed_row(s) for s in SEEDS]
    ok = [r for r in rows if r["valid"]]
    out = {"rows": rows, "n_valid": len(ok)}
    for key, sign in (("ER150", 1), ("RE150", -1), ("RE50", -1)):
        held = [r["d"][key] * sign > 0 for r in ok]
        flipped = [r["d"][key] * sign < 0 for r in ok]
        out[key] = {"held": sum(held), "flipped": sum(flipped), "m": len(ok),
                    "verdict": verdict(held, flipped) + (" (sekundaer, beschreibend)" if key == "RE50" else "")}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


def selftest() -> None:
    assert d_value({1, 2, 3, 4, 5}, {1, 2, 3}, {4, 9}) == 2
    assert d_value({1, 4}, {1, 4}, {4, 9}) == 1                 # shared frequency 4 counts for neither side
    assert verdict([True] * 4, [False] * 4) == "nicht auswertbar"
    assert verdict([True] * 5, [False] * 5) == "gepraegt"
    assert verdict([False] * 6, [True] * 6) == "ueberschrieben"
    assert verdict([True] * 5 + [False], [False] * 6) == "gemischt"   # 5/6: p = 0.109
    assert verdict([True] * 3 + [False] * 3, [False] * 3 + [True] * 3) == "gemischt"
    assert fold(2 * 60) == 7
    assert run_dir(20, "RE50").name == "EXP-020_baseline_seed20_thr4_seed20_train_R_to_seed20_train_E_at50"
    assert run_dir(20, "R").name == "EXP-018_baseline_seed20_thr4_seed20_train_R"
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
