"""EXP-026 analysis (Nachtrag a, pre-registered in README.md before any run): commitment clock by alpha switch.

Arms: alpha = 3 until switch step t_s, then 0 (pure x^2); t_s in {0, 50, 250, 1000, 2500, never}. Units: EXP-016
splits seeds 10-14, arm F. Endpoint d = ov(Top-5, F) - ov(Top-5, H) of the h = 2 weighted spectrum at step 5000.
Fails closed unless the full 6 x 5 grid is complete.
Nachtrag b (before any run): primary endpoint is the continuous share difference
ds = share(F) - share(H) of the normalised h = 2 spectrum; the top-5 d is secondary.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P = 113
TS = (0, 50, 250, 1000, 2500, -1)          # -1 = never (rank last)
SEEDS = (10, 11, 12, 13, 14)


def _rank(x: np.ndarray) -> np.ndarray:
    """Average ranks with ties."""
    order = np.argsort(x, kind="stable")
    r = np.empty(len(x))
    r[order] = np.arange(len(x), dtype=float)
    for v in np.unique(x):
        m = x == v
        r[m] = r[m].mean()
    return r


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = _rank(x), _rank(y)
    if rx.std() == 0 or ry.std() == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def fold(k: int) -> int:
    k %= P
    return min(k, P - k)


def run_id(ts: int, s: int) -> str:
    return f"EXP-026_a3_seed{s}_F" if ts < 0 else f"EXP-026_a3_sw{ts}to0_seed{s}_F"


def share_diff(sp: list[float], T: set[int], H: set[int]) -> float:
    w = np.array(sp) / np.sum(sp)
    return float(w[[k - 1 for k in T]].sum() - w[[k - 1 for k in H]].sum())


def top5(sp: list[float]) -> set[int]:
    return set(int(k) for k in np.argsort(-np.array(sp))[:5] + 1)


def load() -> list[dict]:
    rows = []
    for ts in TS:
        for s in SEEDS:
            f = HERE / "raw" / run_id(ts, s) / "result.json"
            if not f.exists():
                continue
            r = json.loads(f.read_text())
            a = r["args"]
            ok = (r.get("complete") and a["steps"] == 5000 and a["alpha"] == 3.0 and a["switch_step"] == ts
                  and a["alpha_after"] == 0.0 and a["arm"] == "F" and a["init_seed"] is None)
            if not ok:
                continue
            T = set(r["targets"]); H = {fold(57 * t) for t in T}
            last = r["spectra"]["5000"]
            tq, tl = top5(last["weighted"]), top5(last["weighted_lin"])
            rows.append({"ts": ts, "seed": s, "ov_F": len(tq & T), "ov_H": len(tq & H), "d": len(tq & T) - len(tq & H),
                         "d_lin": len(tl & T) - len(tl & H), "ds": share_diff(last["weighted"], T, H),
                         "ds_lin": share_diff(last["weighted_lin"], T, H), "test_acc": r["final_test_acc"],
                         "gen95": r["gen_step_test95"]})
    return rows


def main() -> None:
    rows = load()
    out = {"n_valid": len(rows), "rows": rows}
    if len(rows) != len(TS) * len(SEEDS):
        out["verdict"] = "nicht auswertbar (Raster unvollständig)"
    else:
        out["secondary_mean_d_top5"] = {str(ts): float(np.mean([x["d"] for x in rows if x["ts"] == ts])) for ts in TS}
        md = {ts: float(np.mean([x["ds"] for x in rows if x["ts"] == ts])) for ts in TS}
        md_lin_never = float(np.mean([x["ds_lin"] for x in rows if x["ts"] == -1]))
        out["mean_ds"] = {str(k): v for k, v in md.items()}
        out["mean_ds_lin_never"] = md_lin_never
        out["gen95_mean"] = {str(ts): float(np.mean([x["gen95"] if x["gen95"] is not None else np.nan
                                                     for x in rows if x["ts"] == ts])) for ts in TS}
        anchors = md[0] < 0 and md[-1] > 0 and md_lin_never > 0
        rank = np.array([TS.index(x["ts"]) for x in rows], float)
        d = np.array([x["ds"] for x in rows], float)
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
        out.update(anchors_ok=bool(anchors), rho=rho, p_perm=float(p))
        if not anchors:
            out["verdict"] = "Uhr nicht ablesbar (kein Vorzeichenwechsel zwischen t_s = 0 und nie)"
        elif p < 0.05 and rho > 0:
            out["verdict"] = "Uhr ablesbar"
            finite = [ts for ts in TS if ts >= 0]
            hi = next(ts for ts in finite + [-1] if all(md[t] > 0 for t in (finite + [-1])[(finite + [-1]).index(ts):]))
            lo = None if hi == finite[0] else (finite + [-1])[(finite + [-1]).index(hi) - 1]
            out["commit_interval"] = [lo, hi]           # t* in (lo, hi]; hi = -1: after 2500 or never
            out["when"] = ("A (früh, t_hi <= 250)" if 0 <= hi <= 250 else
                           "B (spät, t_hi >= 2500 oder nie)" if hi < 0 or hi >= 2500 else "Zwischenlage (t_hi = 1000)")
        else:
            out["verdict"] = "Anker ok, Trend n. s."
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
