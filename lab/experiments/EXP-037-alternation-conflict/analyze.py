"""EXP-037: does sustained F/G conflict during the critical period hand the frequency choice to the init? README.md.

Runs: EXP-020 splits and inits of seeds 30-32, F/G blocks of A steps (A = 5, 25) for steps 1..200, then G for 2000.
K = top-5 of W_E at step 2200. A_s, "foreign" and init ranks exactly as in EXP-020 Nachtrag d (conflict_freqs.py),
with the pure EXP-020 runs of the same seed. d = |K n F| - |K n G| (F, G = targets).
Primary (A = 5): gestuetzt if >= 2 of 3 seeds have >= 1 foreign frequency AND the pooled median init rank of the
distinct foreign frequencies is <= 14. Otherwise: F-Akkumulation if d >= +2 in >= 2 seeds; G (Rezenz) if d <= -2 in
>= 2 seeds; else unklar. Missing/invalid run -> nicht auswertbar. A = 25 is reported with the same rule (secondary).
Usage: python analyze.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
E20 = HERE.parent / "EXP-020-data-switch"
sys.path.insert(0, str(E20))
from conflict_freqs import G_BUDGET, fold, load_run, ranks, top  # noqa: E402

SEEDS, ARMS, SWITCH = (30, 31, 32), (5, 25), 200


def classify(rows: list[dict]) -> str:
    if len(rows) != len(SEEDS) or any(r.get("error") for r in rows):
        return "nicht auswertbar"
    with_foreign = sum(1 for r in rows if r["foreign"])
    pooled = [v for r in rows for v in r["init_ranks"].values()]
    if with_foreign >= 2 and pooled and float(np.median(pooled)) <= 14:
        return "gestuetzt"
    if sum(r["d"] >= 2 for r in rows) >= 2:
        return "F-Akkumulation"
    if sum(r["d"] <= -2 for r in rows) >= 2:
        return "G (Rezenz)"
    return "unklar"


def seed_row(s: int, a: int) -> dict:
    tg = json.loads((E20 / f"splits/seed{s}.json").read_text(encoding="utf-8"))["targets"]
    f, g = set(tg["F"]), set(tg["G"])
    pf, e1 = load_run(E20 / "raw", s, s, "F", None, 8000, (0, G_BUDGET))
    pg, e2 = load_run(E20 / "raw", s, s, "G", None, G_BUDGET, (0, G_BUDGET))
    run, e3 = load_run(HERE / "raw", s, s, "FG", SWITCH, None, (0, SWITCH + G_BUDGET), suffix=f"_alt{a}")
    if e1 or e2 or e3:
        return {"seed": s, "error": e1 or e2 or e3}
    res = run["result"]
    if res.get("alternate_every") != a or res["events"].get("alternations") != (SWITCH - 1) // a:
        return {"seed": s, "error": "alternation not as specified"}
    if len({pf["init_checksum"], pg["init_checksum"], run["init_checksum"]}) != 1:
        return {"seed": s, "error": "init checksum differs from EXP-020"}
    allowed = f | g | {fold(2 * k) for k in f | g} | top(pf["spec"][G_BUDGET]) | top(pg["spec"][G_BUDGET])
    k_set = top(run["spec"][SWITCH + G_BUDGET])
    r_init = ranks(pf["spec"][0])
    foreign = sorted(k_set - allowed)
    return {"seed": s, "K": sorted(k_set), "d": len(k_set & f) - len(k_set & g), "foreign": foreign,
            "init_ranks": {k: r_init[k] for k in foreign}, "test_acc": run["test_acc"]}


def main() -> None:
    out = {}
    for a in ARMS:
        rows = [seed_row(s, a) for s in SEEDS]
        out[f"A{a}"] = {"rows": rows, "verdict": classify(rows), "role": "primary" if a == 5 else "secondary"}
        for r in rows:
            print(f"A={a}", r)
        print(f"A={a}: {out[f'A{a}']['verdict']} ({out[f'A{a}']['role']})")
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


def selftest() -> None:
    def r(d: int, foreign: dict[int, int]) -> dict:
        return {"d": d, "foreign": sorted(foreign), "init_ranks": foreign}
    assert classify([r(0, {3: 2}), r(1, {9: 10}), r(3, {})]) == "gestuetzt"
    assert classify([r(0, {3: 30}), r(1, {9: 40}), r(3, {})]) == "unklar"          # foreign, but not init-ranked
    assert classify([r(3, {}), r(2, {}), r(-1, {5: 1})]) == "F-Akkumulation"
    assert classify([r(-3, {}), r(-2, {}), r(0, {})]) == "G (Rezenz)"
    assert classify([r(0, {}), r(1, {})]) == "nicht auswertbar"
    assert classify([{"seed": 1, "error": "x"}, r(0, {}), r(0, {})]) == "nicht auswertbar"
    assert (SWITCH - 1) // 5 == 39 and (SWITCH - 1) // 25 == 7
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
