"""EXP-033 Nachtrag a: deterministic, outcome-blind GD learning-rate choice from the phase-1 pilot (split 10, init 99).
Rule: largest lr in LRS whose pilot reached r >= TARGET within the cap, stayed finite, and overshot by <= 2 %.
Writes lr.json (manifest read by queue.sh and analyze.py)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LRS = (0.3, 1.0, 3.0, 10.0, 30.0)
TARGET = 0.0167


def main() -> None:
    rows = []
    for lr in LRS:
        f = HERE / "raw_smoke" / f"EXP-033_gd_r{TARGET:g}_lr{lr:g}_seed10_init99_p1" / "result.json"
        if not f.exists():
            rows.append({"lr": lr, "ok": False, "why": "missing"})
            continue
        r = json.loads(f.read_text())
        over = None if r["r_switch"] is None else r["r_switch"] / TARGET - 1
        ok = bool(r["reached"] and r["finite"] and over is not None and over <= 0.02)
        rows.append({"lr": lr, "ok": ok, "steps": r["phase1_steps"], "overshoot": over, "finite": r["finite"]})
    good = [x["lr"] for x in rows if x["ok"]]
    out = {"rule": __doc__.splitlines()[1], "pilot": rows, "lr": max(good) if good else None}
    (HERE / "lr.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    if not good:
        sys.exit(1)


if __name__ == "__main__":
    main()
