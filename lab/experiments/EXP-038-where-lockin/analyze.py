"""EXP-038: where does the frequency commitment live, in W_E or in the downstream weights? Definition: README.md.

EXP-020 protocol at t = 150 (seeds 30-34): F for 150 steps, then G for 2000. At the switch, arm RW resets W_E, arm RR
resets all other parameters (each with its AdamW state). Reference: the EXP-020 run at t = 150 (no reset).
Measure (fixed in advance, lesson from EXP-020 seed 33): d_h = |K n Fx| - |K n Gx| with Fx = F u fold(2F),
Gx = G u fold(2G), frequencies on both sides removed; K = top-5 of W_E at step 2150.
Per seed: flipped(arm) = d_h(arm) <= 0. Seed valid if both arms and the reference are valid and d_h(reference) > 0.
Pattern per seed: "W_E" (RW flipped, RR not), "downstream" (RR flipped, RW not), "redundant" (neither), "both" (both).
Verdict: < 4 valid seeds -> nicht auswertbar; >= 4 valid seeds share one pattern -> that pattern; else gemischt.
Usage: python analyze.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
E20 = HERE.parent / "EXP-020-data-switch"
sys.path.insert(0, str(E20))
from conflict_freqs import fold, load_run, top  # noqa: E402

SEEDS, T, TOTAL = (30, 31, 32, 33, 34), 150, 2150


def d_h(K: set[int], f: set[int], g: set[int]) -> int:
    fx, gx = f | {fold(2 * k) for k in f}, g | {fold(2 * k) for k in g}
    both = fx & gx
    return len(K & (fx - both)) - len(K & (gx - both))


def pattern(rw_flipped: bool, rr_flipped: bool) -> str:
    return {(True, False): "W_E", (False, True): "downstream", (False, False): "redundant",
            (True, True): "both"}[(rw_flipped, rr_flipped)]


def verdict(patterns: list[str]) -> str:
    if len(patterns) < 4:
        return "nicht auswertbar"
    top_pat, n = Counter(patterns).most_common(1)[0]
    return top_pat if n >= 4 else "gemischt"


def seed_row(s: int) -> dict:
    tg = json.loads((E20 / f"splits/seed{s}.json").read_text(encoding="utf-8"))["targets"]
    f, g = set(tg["F"]), set(tg["G"])
    ref, e0 = load_run(E20 / "raw", s, s, "FG", T, None, (0, TOTAL))
    if e0:
        return {"seed": s, "error": e0}
    out = {"seed": s, "d_h_ref": d_h(top(ref["spec"][TOTAL]), f, g)}
    for arm, which in (("RW", "we"), ("RR", "rest")):
        r, e = load_run(HERE / "raw", s, s, "FG", T, None, (0, TOTAL), suffix=f"_rs{which}")
        if e:
            return {"seed": s, "error": e}
        ev = r["result"]["events"].get("reset_at_switch", {})
        if r["result"].get("reset_at_switch") != which or ev.get("which") != which or not ev.get("n_params"):
            return {"seed": s, "error": f"{arm}: reset not as specified"}
        if r["init_checksum"] != ref["init_checksum"]:
            return {"seed": s, "error": f"{arm}: init differs from EXP-020"}
        K = top(r["spec"][TOTAL])
        out[arm] = {"K": sorted(K), "d_h": d_h(K, f, g), "test_acc": r["test_acc"],
                    "train_acc_after_reset": ev.get("train_acc_after")}
    if out["d_h_ref"] <= 0:
        return out | {"error": "reference not committed to F (d_h_ref <= 0)"}
    return out | {"pattern": pattern(out["RW"]["d_h"] <= 0, out["RR"]["d_h"] <= 0)}


def main() -> None:
    rows = [seed_row(s) for s in SEEDS]
    pats = [r["pattern"] for r in rows if "pattern" in r and not r.get("error")]
    out = {"rows": rows, "patterns": pats, "verdict": verdict(pats)}
    for r in rows:
        print(r)
    print({"patterns": pats, "verdict": out["verdict"]})
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


def selftest() -> None:
    assert d_h({1, 2, 3}, {1, 2}, {3}) == 1
    assert d_h({2, 4}, {1}, {2}) == -1           # 2 = 2*1 is on both sides -> ignored; 4 = 2*2 counts for G
    assert d_h({4}, {1}, {2}) == -1
    assert pattern(True, False) == "W_E" and pattern(False, True) == "downstream"
    assert verdict(["W_E"] * 4 + ["both"]) == "W_E"
    assert verdict(["W_E"] * 3 + ["both"] * 2) == "gemischt"
    assert verdict(["redundant"] * 3) == "nicht auswertbar"
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
