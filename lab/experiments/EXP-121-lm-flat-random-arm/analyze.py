"""EXP-121 analysis (written session 54 before any run). Readings as in README "Vorab":
gate: t_train exists for Rf in both seeds, else 'nicht gelernt (Budget)';
'Paarstruktur schliesst die Luecke': no t_test by 4000 in both seeds, or gap t_test - t_train >= 1000 in both;
'Flache Bauart reicht': gap <= 300 in both; else 'unklar'. EXP-115 F/G gaps are listed for comparison (already seen).
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-121-lm-flat-random-arm/analyze.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-119-lm-speed-r5"))
from analyze import cross  # noqa: E402

MODEL_SEEDS = (3950, 3951)


def row(d: Path) -> dict:
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    c = r["curve"]
    tr, te = cross(c, 1), cross(c, 2)
    return {"run": d.name, "status": r["status"], "steps": r["steps_completed"], "t_train": tr, "t_test": te,
            "gap": (te - tr) if (tr is not None and te is not None) else None, "final_train": c[-1][1], "final_test": c[-1][2]}


def main() -> None:
    rows, ref = {}, {}
    for s in MODEL_SEEDS:
        runs = [d for d in (HERE / "raw").glob(f"lm2_seed{s}_*Rf*") if (d / "result.json").exists()]
        rows[s] = row(runs[0]) if len(runs) == 1 else {"status": f"{len(runs)} runs found"}
        ref[s] = [row(d) for d in sorted((LAB / "experiments/EXP-115-lm-flat-marginals/raw").glob(f"lm2_seed{s}_*"))]
    ok = all(r.get("status") == "completed" and r.get("t_train") is not None for r in rows.values())
    if not ok:
        reading = "nicht gelernt (Budget)" if all(r.get("status") == "completed" for r in rows.values()) else "nicht auswertbar"
    elif all(r["t_test"] is None or r["gap"] >= 1000 for r in rows.values()):
        reading = "Paarstruktur schliesst die Luecke"
    elif all(r["gap"] is not None and r["gap"] <= 300 for r in rows.values()):
        reading = "Flache Bauart reicht"
    else:
        reading = "unklar"
    out = {"reading": reading, "Rf": rows, "EXP115_FG_seen": ref, "note": "exploration, 2 runs; Rf test set is a subset of the F/G test set"}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
