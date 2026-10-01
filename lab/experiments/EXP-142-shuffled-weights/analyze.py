"""EXP-142 analysis (readings fixed in README before any U run). Per seed: gen_U (censored at 30 000) against gen_E = mean of the
EXP-139 F/G gen steps of the same seed (add 401 / 14 000) and, for reference, gen_R of EXP-140.
  Reading: U generalizes in <= 1 of 3 seeds -> 'Frequenzstruktur noetig (nicht blosses Ungleichgewicht)';
           U in >= 2 of 3 and median(gen_U / gen_E) <= 1.5 -> 'Ungleichgewicht reicht'; else 'Ungleichgewicht hilft teilweise'.
           Any missing / not completed U run -> 'nicht auswertbar'.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-142-shuffled-weights/analyze.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
SEEDS, BUDGET = (13900, 13901, 13902), 30_000
SRC = {"F": LAB / "experiments/EXP-139-pair-count/raw", "G": LAB / "experiments/EXP-139-pair-count/raw",
       "R": LAB / "experiments/EXP-140-random-at-edge/raw", "U": HERE / "raw"}


def gen_of(arm: str, s: int) -> tuple[str, int | None]:
    name = f"split_add401_n14000_seed{s}_{arm}.npy"
    hits = [json.loads(f.read_text(encoding="utf-8")) for f in SRC[arm].glob("*/result.json")]
    hits = [r for r in hits if Path(r.get("split_file") or "").name == name]
    if len(hits) != 1 or hits[0].get("status") != "completed" or hits[0].get("max_steps") != BUDGET:
        return "problem", None
    g = ((hits[0].get("transitions") or {}).get("primary") or {}).get("generalization", {}).get("first_crossing_step")
    return "ok", g


def reading(rows: list[dict]) -> str:
    if any(r["problem"] for r in rows):
        return "nicht auswertbar"
    n_u = sum(r["gen_U"] is not None for r in rows)
    if n_u <= 1:
        return "Frequenzstruktur noetig (nicht blosses Ungleichgewicht)"
    ratio = float(np.median([(r["gen_U"] or BUDGET) / r["gen_E"] for r in rows]))
    return "Ungleichgewicht reicht" if ratio <= 1.5 else "Ungleichgewicht hilft teilweise"


def main() -> None:
    rows = []
    for s in SEEDS:
        g = {a: gen_of(a, s) for a in "FGRU"}
        cens = {a: BUDGET if v[1] is None else v[1] for a, v in g.items()}
        rows.append({"seed": s, "problem": any(v[0] != "ok" for v in g.values()), "gen_F": g["F"][1], "gen_G": g["G"][1],
                     "gen_R": g["R"][1], "gen_U": g["U"][1], "gen_E": (cens["F"] + cens["G"]) / 2})
    out = {"reading": reading(rows), "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


def selftest() -> None:
    base = {"problem": False, "gen_E": 5000.0}
    assert reading([{**base, "gen_U": None}] * 2 + [{**base, "gen_U": 6000}]).startswith("Frequenzstruktur")
    assert reading([{**base, "gen_U": 6000}] * 3) == "Ungleichgewicht reicht"
    assert reading([{**base, "gen_U": 20000}] * 2 + [{**base, "gen_U": None}]) == "Ungleichgewicht hilft teilweise"
    assert reading([{**base, "gen_U": 6000, "problem": True}] * 3) == "nicht auswertbar"
    print("[exp142] selftest ok")


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
