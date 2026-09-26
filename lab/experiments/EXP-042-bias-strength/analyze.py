"""EXP-042 analysis (pre-registered, README): EXP-020 protocol with a G split of different concentration eps_G (F, test,
targets unchanged). H42 (head start vs split bias): a more concentrated G needs a larger F head start -> later lock-in.
Primary eps_G = 8 (grid 25, 50, 100, 150): cell 'later' if lo >= 50, 'same' if (lo, hi) == (25, 50), else 'unclear'.
Secondary eps_G = 1 (grid 10, 25, 50): 'earlier' if hi <= 25, 'same' if (25, 50], else 'unclear' (descriptive only).
Completed cells that are non-monotone, cross after gen_F or miss the endpoints d(0) < 0 < d(inf) count as 'unclear'.
Reference t = inf: the EXP-020 only-F run (same init, bit-identical F); t = 0: own only-G_eps run.
Verdict (primary): >= 3 complete seeds; all 'later' -> H42 gestuetzt; all 'same' -> Neigung ohne Einfluss; else unklar.
Usage: python analyze.py [--selftest]"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[0]
SEEDS = (30, 31, 32, 34)
GRIDS = {8.0: (25, 50, 100, 150), 1.0: (10, 25, 50)}
MIN_SEEDS = 3


def classify(e: float, lo: float, hi: float) -> str:
    if (lo, hi) == (25, 50):
        return "same"
    if e == 8.0:
        return "later" if lo >= 50 else "unclear"
    return "earlier" if hi <= 25 else "unclear"


def verdict(classes: list[str]) -> str:
    if len(classes) < MIN_SEEDS:
        return "nicht auswertbar"
    if all(c == "later" for c in classes):
        return "H42 gestuetzt (staerker konzentriertes G verzoegert die Festlegung)"
    return "Neigung ohne Einfluss auf den Zeitpunkt" if all(c == "same" for c in classes) else "unklar"


def load_mod(e: float):
    spec = importlib.util.spec_from_file_location(f"exp020_eps{e:g}", LAB / "EXP-020-data-switch" / "analyze.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    base = HERE / f"eps{e:g}"
    e20_inf = m.run_dir(30, math.inf).parent                      # EXP-020/raw (before patching HERE)
    m.HERE = base                                                  # splits + own runs of this eps
    m.SWITCH = GRIDS[e]
    m.GRID = (0.0, *map(float, GRIDS[e]), math.inf)
    orig = m.run_dir
    m.run_dir = lambda s, t: e20_inf / orig(s, t).name if t == math.inf else orig(s, t)
    return m


def cell(m, e: float, s: int) -> dict:
    r = m.row(s)
    out = {"seed": s, "eps_G": e, **{k: r.get(k) for k in ("valid", "d", "K", "lo", "hi", "monotone", "gen_F", "reason")}}
    reason = r.get("reason") or ""
    if not r["valid"] and "construction did not steer" not in reason:
        return out | {"complete": False, "why": reason or "invalid run set"}
    inits = {json.loads((m.run_dir(s, t) / "result.json").read_text(encoding="utf-8"))["init_checksum_shared"]
             for t in m.GRID}
    if len(inits) != 1:
        return out | {"complete": False, "why": "init differs"}
    if not r["valid"]:
        return out | {"complete": True, "class": "unclear", "why": "endpoints d(0) < 0 < d(inf) not met"}
    if not r["monotone"] or not (r["gen_F"] and r["hi"] < r["gen_F"]):
        return out | {"complete": True, "class": "unclear", "why": "non-monotone or crossing not before gen_F"}
    return out | {"complete": True, "class": classify(e, r["lo"], r["hi"])}


def main() -> None:
    out = {}
    for e in GRIDS:
        m = load_mod(e)
        rows = []
        for s in SEEDS:
            try:
                rows.append(cell(m, e, s))
            except (OSError, KeyError, ValueError) as ex:
                rows.append({"seed": s, "eps_G": e, "complete": False, "why": f"{type(ex).__name__}: {ex}"})
        cls = [r["class"] for r in rows if r["complete"]]
        out[f"eps{e:g}"] = {"rows": rows, "classes": cls,
                            "verdict": verdict(cls) if e == 8.0 else f"descriptive: {cls}"}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    for k, v in out.items():
        print(k, v["classes"], v["verdict"])
        for r in v["rows"]:
            print("  ", r)


def selftest() -> None:
    assert classify(8.0, 50, 100) == "later" and classify(8.0, 100, 150) == "later"
    assert classify(8.0, 25, 50) == "same" and classify(8.0, 0, 25) == "unclear"
    assert classify(1.0, 10, 25) == "earlier" and classify(1.0, 0, 10) == "earlier" and classify(1.0, 25, 50) == "same"
    assert classify(1.0, 50, math.inf) == "unclear"
    assert verdict(["later"] * 2) == "nicht auswertbar" and verdict(["later"] * 3).startswith("H42")
    assert verdict(["same"] * 4).startswith("Neigung") and verdict(["later", "later", "unclear"]) == "unklar"
    m = load_mod(8.0)
    assert m.GRID == (0.0, 25.0, 50.0, 100.0, 150.0, math.inf)
    assert m.run_dir(30, math.inf).parent.parent.name == "EXP-020-data-switch"
    assert m.run_dir(30, 0).parent.parent.name == "eps8" and m.run_dir(30, 50).name.endswith("_at50")
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
