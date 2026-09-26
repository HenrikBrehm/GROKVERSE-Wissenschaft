"""EXP-032 analysis (pre-registered in README.md): fine switch grid t_s in {0, 1, 5, 10, 20, 50}."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
E26 = HERE.parents[0] / "EXP-026-parity-crossover"
sys.path.insert(0, str(E26))
from analyze import fold, share_diff, spearman  # noqa: E402

TS = (0, 1, 5, 10, 20, 50)
SEEDS = (10, 11, 12, 13, 14)


def path(ts: int, s: int) -> Path:
    base = E26 if ts in (0, 50) else HERE
    return base / "raw" / f"EXP-026_a3_sw{ts}to0_seed{s}_F" / "result.json"


def main() -> None:
    rows = []
    for ts in TS:
        for s in SEEDS:
            f = path(ts, s)
            if not f.exists():
                continue
            r = json.loads(f.read_text())
            a = r["args"]
            if not (r.get("complete") and a["steps"] == 5000 and a["alpha"] == 3.0 and a["switch_step"] == ts
                    and a["alpha_after"] == 0.0 and a["seed"] == s and a["arm"] == "F" and a.get("width", 512) == 512):
                continue
            T = set(r["targets"]); H = {fold(57 * t) for t in T}
            row = {"ts": ts, "seed": s, "ds": share_diff(r["spectra"]["5000"]["weighted"], T, H),
                   "test_acc": r["final_test_acc"], "gen95": r["gen_step_test95"]}
            snap = r["spectra"].get(str(ts))
            if snap is not None:
                row.update(ds_at_switch=share_diff(snap["weighted"], T, H), r_at_switch=snap.get("amp"))
            rows.append(row)
    out = {"n_valid": len(rows), "rows": rows}
    if len(rows) != len(TS) * len(SEEDS):
        out["verdict"] = "nicht auswertbar (Raster unvollständig)"
    elif any(x["test_acc"] < 0.9 for x in rows):
        out["verdict"] = "nicht auswertbar (Endnetz generalisiert nicht)"
    else:
        rank = np.array([TS.index(x["ts"]) for x in rows], float)
        d = np.array([x["ds"] for x in rows])
        seed = np.array([x["seed"] for x in rows])
        rho = spearman(rank, d)
        rng = np.random.default_rng(0)
        cnt = 0
        for _ in range(10_000):
            pr = rank.copy()
            for s in SEEDS:
                m = seed == s
                pr[m] = rng.permutation(pr[m])
            cnt += np.nan_to_num(spearman(pr, d), nan=-1.0) >= rho
        p = (cnt + 1) / 10_001
        md = {ts: float(np.mean([x["ds"] for x in rows if x["ts"] == ts])) for ts in TS}
        t_half = next(ts for ts in TS if md[ts] >= 0.5 * md[50])
        ok1 = p < 0.05 and rho > 0
        out.update(rho=rho, p_perm=float(p), mean_ds={str(k): v for k, v in md.items()}, t_half=t_half,
                   gen95_mean={str(ts): float(np.mean([x["gen95"] for x in rows if x["ts"] == ts])) for ts in TS},
                   verdict=("nicht aufgelöst" if not ok1 else "Festlegung in ≤ 20 Schritten" if t_half <= 20
                            else "Festlegung zwischen 20 und 50"))
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
