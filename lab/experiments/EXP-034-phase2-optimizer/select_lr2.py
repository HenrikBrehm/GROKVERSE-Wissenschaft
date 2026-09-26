"""EXP-034 pilot B (Nachtrag a): largest lr2 in (1, 3, 10) for which ALL three runs on held-out split 70 (anchor,
AR10, GD10 start states, GD phase 2 for 10 000 steps) stayed finite, completed and reached test >= 0.9.
Writes lr2.json (null if none); read by queue.sh and analyze.py."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(rid: str) -> dict | None:
    f = HERE / "raw" / rid / "result.json"
    return json.loads(f.read_text()) if f.exists() else None


def main() -> None:
    rows = []
    for lr in (1.0, 3.0, 10.0):
        suf = f"_p2gd{lr:g}_n10000"
        an, ar = load(f"EXP-033_adamw_t0_seed70{suf}"), load(f"EXP-033_adamw_t10_seed70{suf}")
        gd = load(f"EXP-033_gd_r{ar['r_switch']:g}_lr3_seed70_bt{suf}") if ar and ar["r_switch"] else None
        runs = {"anchor": an, "ar10": ar, "gd10": gd}
        ok = {k: bool(r and r["complete"] and r["final_test_acc"] is not None and r["final_test_acc"] >= 0.9) for k, r in runs.items()}
        rows.append({"lr2": lr, "ok": all(ok.values()), "per_state": ok,
                     "test": {k: r and r["final_test_acc"] for k, r in runs.items()},
                     "gen95": {k: r and r["gen_step_test95"] for k, r in runs.items()}})
    good = [x["lr2"] for x in rows if x["ok"]]
    out = {"pilot": rows, "lr2": max(good) if good else None}
    (HERE / "lr2.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
