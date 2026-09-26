"""EXP-034 pilot B: largest lr2 in (1, 3, 10) whose anchor-GD2 run on split 70 stayed finite and reached test >= 0.9
within 10 000 GD steps. Writes lr2.json (read by queue.sh and analyze.py)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    rows = []
    for lr in (1.0, 3.0, 10.0):
        f = HERE / "raw" / f"EXP-033_adamw_t0_seed70_p2gd{lr:g}_n10000" / "result.json"
        r = json.loads(f.read_text()) if f.exists() else None
        ok = bool(r and r["complete"] and r["final_test_acc"] is not None and r["final_test_acc"] >= 0.9)
        rows.append({"lr2": lr, "ok": ok, "test": r and r["final_test_acc"], "gen95": r and r["gen_step_test95"],
                     "finite": r and r["finite"]})
    good = [x["lr2"] for x in rows if x["ok"]]
    out = {"pilot": rows, "lr2": max(good) if good else None}
    (HERE / "lr2.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))
    sys.exit(0 if good else 1)


if __name__ == "__main__":
    main()
