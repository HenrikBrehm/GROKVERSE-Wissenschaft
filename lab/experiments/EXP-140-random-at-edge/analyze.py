"""EXP-140 analysis (readings fixed in README and here before any EXP-139 or EXP-140 result, session 68).
Per selected cell (p, N) and seed: gen_R = first_crossing_step of the random arm R (None = not generalized within
30 000 steps, run completed); gen_E = mean of the engineered arms F and G of EXP-139 (same seed = same initialization;
only seeds where both F and G generalized). Cell reading: R generalized in <= 1 of 3 seeds -> 'Konstruktion ermoeglicht
Generalisierung'; otherwise median over seeds with gen_R and gen_E of ratio = gen_R / gen_E: > 1.5 -> 'Konstruktion
beschleunigt'; < 1/1.5 -> 'Zufall schneller'; else 'kein klarer Unterschied'. A missing or failed R run -> cell
'nicht auswertbar' (if fewer than 3 R runs are usable). Overall: every cell 'ermoeglicht' -> 'Inhaltssignal ersetzt
Dichte (im Budget)'; no cell evaluable -> 'nicht auswertbar'; else 'gemischt' (cells listed).
Descriptive: final test accuracy of R, gen steps.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-140-random-at-edge/analyze.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_jobs as mj  # noqa: E402

RAW = HERE / "raw"
RATIO = 1.5


def load_r(p: int, cell: str, s: int) -> dict | str:
    name = f"{mj.stem(p, cell, s)}.npy"
    hits = [r.parent for r in RAW.glob("*/result.json")
            if Path(json.loads(r.read_text(encoding="utf-8")).get("split_file") or "").name == name]
    if len(hits) != 1:
        return f"{name}: fehlt oder doppelt"
    r = json.loads((hits[0] / "result.json").read_text(encoding="utf-8"))
    if r.get("status") != "completed" or r.get("device") != "cuda" or r["config"].get("p") != p:
        return f"{name}: status {r.get('status')} / config"
    gen = (r.get("transitions") or {}).get("primary", {}).get("generalization", {}).get("first_crossing_step")
    return {"gen": gen, "final_test": (r.get("final_acc") or {}).get("test")}


def e_rows() -> dict:
    res = json.loads((mj.E139 / "summary.json").read_text(encoding="utf-8"))
    return {(c["p"], c["cell"], r["seed"]): r["gen"] for c in res["cells"] for r in c["rows"]}


def cell_eval(p: int, cell: str, loader=load_r, egen=None) -> dict:
    egen = e_rows() if egen is None else egen
    rows, bad = [], []
    for s in mj.SEEDS:
        R = loader(p, cell, s)
        if isinstance(R, str):
            bad.append(R)
            continue
        gF, gG = egen.get((p, cell, s), [None, None])
        gE = None if gF is None or gG is None else (gF + gG) / 2
        rows.append({"seed": s, "gen_R": R["gen"], "gen_E": gE, "final_test_R": R["final_test"],
                     "ratio": None if R["gen"] is None or gE is None else R["gen"] / gE})
    if len(rows) < len(mj.SEEDS):
        verdict = "nicht auswertbar"
    elif sum(r["gen_R"] is not None for r in rows) <= 1:
        verdict = "Konstruktion ermoeglicht Generalisierung"
    else:
        rat = [r["ratio"] for r in rows if r["ratio"] is not None]
        m = float(np.median(rat)) if rat else None
        verdict = ("nicht auswertbar" if m is None else "Konstruktion beschleunigt" if m > RATIO else
                   "Zufall schneller" if m < 1 / RATIO else "kein klarer Unterschied")
    return {"p": p, "cell": cell, "verdict": verdict, "rows": rows, "problems": bad}


def main(cells=None, loader=load_r, egen=None) -> dict:
    cells = mj.selected_cells() if cells is None else cells
    out = [cell_eval(p, c, loader, egen) for p, c in cells]
    ev = [c for c in out if c["verdict"] != "nicht auswertbar"]
    overall = ("nicht auswertbar" if not ev else
               "Inhaltssignal ersetzt Dichte (im Budget)" if all(c["verdict"] == "Konstruktion ermoeglicht Generalisierung" for c in out)
               else "gemischt")
    return {"cells": out, "overall": overall}


def selftest() -> None:
    cells = [(401, "n9425"), (401, "n14000")]
    egen = {(p, c, s): [5000, 7000] for p, c in cells for s in mj.SEEDS}
    r = main(cells, lambda p, c, s: {"gen": None, "final_test": 0.01}, egen)
    assert r["overall"] == "Inhaltssignal ersetzt Dichte (im Budget)", r
    r = main(cells, lambda p, c, s: {"gen": 12000 if s != 13900 else None, "final_test": 0.99}, egen)
    assert all(c["verdict"] == "Konstruktion beschleunigt" for c in r["cells"]) and r["overall"] == "gemischt"
    r = main(cells, lambda p, c, s: {"gen": 6500, "final_test": 0.99}, egen)
    assert all(c["verdict"] == "kein klarer Unterschied" for c in r["cells"])
    r = main(cells, lambda p, c, s: {"gen": 2000, "final_test": 0.99}, egen)
    assert all(c["verdict"] == "Zufall schneller" for c in r["cells"])
    r = main(cells, lambda p, c, s: "x: fehlt", egen)
    assert r["overall"] == "nicht auswertbar"
    print("[exp140] selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        res = main()
        (HERE / "summary.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        for c in res["cells"]:
            print(c["p"], c["cell"], c["verdict"], [(r["seed"], r["gen_R"], r["gen_E"]) for r in c["rows"]], c["problems"])
        print("overall:", res["overall"])
