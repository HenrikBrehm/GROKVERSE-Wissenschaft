"""EXP-022: does a single-frequency split force a single-frequency solution? (UNTESTED on real runs) Definition: README.md.
Runs carry exp_id EXP-018 by the trainer's naming (--split-file + --test-file)."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "training"))
from grokverse.data import split_hash  # noqa: E402

SEEDS, ARMS, CAP, THR = range(40, 45), ("S1", "S5", "R"), 8000, 0.95
P = 113


def fold(x: int) -> int:
    x %= P
    return min(x, P - x)


def load(s: int, arm: str) -> tuple[dict | None, str | None]:
    d = HERE / f"raw/EXP-018_baseline_seed{s}_thr4_seed{s}_train_{arm}"
    if not (d / "result.json").exists():
        return None, "missing"
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    if res["status"] != "completed" or res["seed"] != s or res["max_steps"] != CAP:
        return None, "status/seed/cap"
    if res["split_hash"] != split_hash(np.load(HERE / f"splits/seed{s}_train_{arm}.npy")):
        return None, "split hash"
    if res.get("test_hash") != split_hash(np.load(HERE / f"splits/seed{s}_test.npy")):
        return None, "test hash"
    obs = [st for st, a in zip(res["dense"]["test_steps"], res["dense"]["test_acc"]) if a >= THR]
    if not obs and res["steps_completed"] != CAP:
        return None, "stopped early without crossing"
    pw = np.load(d / "spectra.npy")[-1]
    return {"n_eff": float(pw.sum() ** 2 / (pw ** 2).sum()), "top1_share": float(pw.max() / pw.sum()),
            "top1": int(np.argmax(pw)) + 1, "gen": obs[0] if obs else None,
            "final_test_acc": res["final_acc"]["test"], "pw": pw}, None


def main() -> None:
    rows = []
    for s in SEEDS:
        meta = json.loads((HERE / f"splits/seed{s}.json").read_text(encoding="utf-8"))
        r: dict = {"seed": s, "f1": meta["f1"]}
        for arm in ARMS:
            x, err = load(s, arm)
            if err:
                r["reason"] = f"{arm}: {err}"
                break
            pw = x.pop("pw")
            if arm == "S1":
                x["share_f1"] = float(pw[meta["f1"] - 1] / pw.sum())
                x["share_2f1"] = float(pw[fold(2 * meta["f1"]) - 1] / pw.sum())
            r[arm] = x
        r["valid"] = "reason" not in r
        rows.append(r)
    valid = [r for r in rows if r["valid"]]
    out: dict = {"rows": rows, "n_valid": len(valid)}
    if len(valid) < 4:
        out["verdict"] = "nicht auswertbar"
    else:
        k = sum(r["S1"]["n_eff"] < r["S5"]["n_eff"] for r in valid)
        out.update({"n_S1_lower": k,
                    "p_sign": sum(math.comb(len(valid), j) for j in range(k, len(valid) + 1)) / 2 ** len(valid),
                    "verdict": "bestätigt" if k == len(valid) == 5 else
                    ("richtungsgleich, zu wenige Seeds" if k == len(valid) else "nicht bestätigt"),
                    "mean_n_eff": {a: float(np.mean([r[a]["n_eff"] for r in valid])) for a in ARMS},
                    "S1_top1_is_f1": sum(r["S1"]["top1"] == r["f1"] for r in valid)})
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
