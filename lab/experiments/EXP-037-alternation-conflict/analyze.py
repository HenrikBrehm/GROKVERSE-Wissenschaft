"""EXP-037: does sustained F/G conflict during the critical period hand the frequency choice to the init? README.md.

Runs: EXP-020 splits and inits of seeds 30-32, F/G blocks of A steps (A = 5, 25) for steps 1..200, then G for 2000.
K = top-5 of W_E at step 2200. A_s, "foreign" and init ranks as in EXP-020 Nachtrag d (conflict_freqs.py), with the
pure EXP-020 runs of the same seed. d = |K n F| - |K n G| (F, G = targets).
Nachtrag a (Codex): A additionally contains the top-5 of M0 of the mean mask (F + G)/2; control C_F100 = F for 100 steps,
then G for 2100 (same exposure, no alternation). h37(arm) = >= 2 of 3 seeds with >= 1 foreign frequency AND pooled median
init rank of the distinct foreign frequencies <= 14; facc = d >= +2 in >= 2 seeds; rec = d <= -2 in >= 2 seeds.
Primary (A = 5): invalid/missing run (arm or control) -> nicht auswertbar; h37 and (facc or rec) -> mehrdeutig;
h37 and h37(C_F100) -> nicht spezifisch; h37 alone -> gestuetzt; else F-Akkumulation / G (Rezenz) / unklar.
A = 25 with the same rule (secondary). Mean-mask M0 ranks of the foreign frequencies are reported.
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

sys.path.insert(0, str(HERE.parent / "EXP-012-init-gradient"))
sys.path.insert(0, str(HERE.parent / "EXP-015-mask-spectrum"))
from mask_spectrum import m0  # noqa: E402

SEEDS, ARMS, SWITCH, P, TOTAL = (30, 31, 32), (5, 25), 200, 113, 2200


def valid(rows: list[dict]) -> bool:
    return len(rows) == len(SEEDS) and not any(r.get("error") for r in rows)


def h37(rows: list[dict]) -> bool:
    pooled = [v for r in rows for v in r["init_ranks"].values()]
    return sum(1 for r in rows if r["foreign"]) >= 2 and bool(pooled) and float(np.median(pooled)) <= 14


def classify(rows: list[dict], control: list[dict]) -> str:
    if not valid(rows) or not valid(control):
        return "nicht auswertbar"
    facc = sum(r["d"] >= 2 for r in rows) >= 2
    rec = sum(r["d"] <= -2 for r in rows) >= 2
    if h37(rows):
        if facc or rec:
            return "mehrdeutig"
        return "nicht spezifisch" if h37(control) else "gestuetzt"
    return "F-Akkumulation" if facc else "G (Rezenz)" if rec else "unklar"


def mean_mask_m0(s: int) -> np.ndarray:
    M = np.zeros((P, P))
    for arm in ("F", "G"):
        idx = np.load(E20 / f"splits/seed{s}_train_{arm}.npy")
        M[idx // P, idx % P] += 0.5
    return m0(M)


def seed_row(s: int, a: int | None) -> dict:
    """a = alternation block length; None = control C_F100."""
    tg = json.loads((E20 / f"splits/seed{s}.json").read_text(encoding="utf-8"))["targets"]
    f, g = set(tg["F"]), set(tg["G"])
    pf, e1 = load_run(E20 / "raw", s, s, "F", None, 8000, (0, G_BUDGET))
    pg, e2 = load_run(E20 / "raw", s, s, "G", None, G_BUDGET, (0, G_BUDGET))
    if a is None:
        run, e3 = load_run(HERE / "raw", s, s, "FG", 100, TOTAL, (0, TOTAL))
    else:
        run, e3 = load_run(HERE / "raw", s, s, "FG", SWITCH, None, (0, TOTAL), suffix=f"_alt{a}")
    if e1 or e2 or e3:
        return {"seed": s, "error": e1 or e2 or e3}
    res = run["result"]
    n_alt = 0 if a is None else (SWITCH - 1) // a
    if (res.get("alternate_every") or 0) != (a or 0) or res["events"].get("alternations", 0) != n_alt:
        return {"seed": s, "error": "alternation not as specified"}
    if len({pf["init_checksum"], pg["init_checksum"], run["init_checksum"]}) != 1:
        return {"seed": s, "error": "init checksum differs from EXP-020"}
    mm = mean_mask_m0(s)
    allowed = (f | g | {fold(2 * k) for k in f | g} | top(pf["spec"][G_BUDGET]) | top(pg["spec"][G_BUDGET])
               | top(mm))
    k_set = top(run["spec"][TOTAL])
    r_init, r_mm = ranks(pf["spec"][0]), ranks(mm)
    foreign = sorted(k_set - allowed)
    return {"seed": s, "K": sorted(k_set), "d": len(k_set & f) - len(k_set & g), "foreign": foreign,
            "init_ranks": {k: r_init[k] for k in foreign}, "meanmask_ranks": {k: r_mm[k] for k in foreign},
            "test_acc": run["test_acc"]}


def main() -> None:
    control = [seed_row(s, None) for s in SEEDS]
    out = {"C_F100": {"rows": control, "h37": h37(control) if valid(control) else None}}
    for r in control:
        print("C_F100", r)
    for a in ARMS:
        rows = [seed_row(s, a) for s in SEEDS]
        out[f"A{a}"] = {"rows": rows, "verdict": classify(rows, control), "role": "primary" if a == 5 else "secondary"}
        for r in rows:
            print(f"A={a}", r)
        print(f"A={a}: {out[f'A{a}']['verdict']} ({out[f'A{a}']['role']})")
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


def selftest() -> None:
    def r(d: int, foreign: dict[int, int]) -> dict:
        return {"d": d, "foreign": sorted(foreign), "init_ranks": foreign}
    ctl = [r(3, {}), r(3, {}), r(3, {})]
    assert classify([r(0, {3: 2}), r(1, {9: 10}), r(3, {})], ctl) == "gestuetzt"
    assert classify([r(0, {3: 30}), r(1, {9: 40}), r(3, {})], ctl) == "unklar"          # foreign, not init-ranked
    assert classify([r(3, {}), r(2, {}), r(-1, {5: 1})], ctl) == "F-Akkumulation"
    assert classify([r(-3, {}), r(-2, {}), r(0, {})], ctl) == "G (Rezenz)"
    assert classify([r(-3, {3: 2}), r(-2, {9: 5}), r(0, {})], ctl) == "mehrdeutig"      # H37 and recency overlap
    assert classify([r(3, {3: 2}), r(2, {9: 5}), r(0, {})], ctl) == "mehrdeutig"        # H37 and F-accumulation
    assert classify([r(0, {3: 2}), r(1, {9: 10}), r(3, {})],
                    [r(0, {3: 2}), r(0, {4: 3}), r(3, {})]) == "nicht spezifisch"      # control shows it too
    assert classify([r(0, {}), r(1, {})], ctl) == "nicht auswertbar"
    assert classify([{"seed": 1, "error": "x"}, r(0, {}), r(0, {})], ctl) == "nicht auswertbar"
    assert classify([r(0, {}), r(0, {}), r(0, {})], [{"seed": 1, "error": "x"}, r(0, {}), r(0, {})]) == "nicht auswertbar"
    assert (SWITCH - 1) // 5 == 39 and (SWITCH - 1) // 25 == 7
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
