"""EXP-071 (exploration): does the OV lead at the switch predict persistence pi per seed? Definition: README.md (fixed before any run).
Reuses the EXP-070 measure (L = OV gain ratio, E = W_E energy ratio); pi per seed from EXP-059. Run under guarded_run.py.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np


def spearmanr(x, y) -> tuple[float]:
    """Spearman rho as Pearson on average ranks (no scipy in this environment)."""
    def rank(v):
        v = np.asarray(v, dtype=float)
        o = np.argsort(v, kind="stable")
        r = np.empty(len(v))
        r[o] = np.arange(len(v))
        for u in np.unique(v):                             # average ranks for ties
            r[v == u] = r[v == u].mean()
        return r
    return (float(np.corrcoef(rank(x), rank(y))[0, 1]),)

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
_spec = importlib.util.spec_from_file_location("exp070", LAB / "experiments/EXP-070-ov-alignment/analyze.py")
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)
TS = (10, 15, 20, 25, 30, 35, 50)
OLD_A = (10, 25, 50)                                   # A-first runs at these t come from EXP-070


def load(s: int, t: int, first: str):
    import torch
    root = V.HERE / "raw" if (first == "A" and t in OLD_A) else HERE / "raw"
    hits = list((root / f"t{t}").glob(f"EXP-018_baseline_seed{s}_thr1_seed{s}_w0_{first}_devcuda"))
    if len(hits) != 1:
        return None
    res = json.loads((hits[0] / "result.json").read_text(encoding="utf-8"))
    if res.get("status") != "completed" or res.get("steps_completed") != t or not (hits[0] / "model_final.pt").exists():
        return None
    m = V.init_model(s)
    m.load_state_dict(torch.load(hits[0] / "model_final.pt", map_location="cpu"))
    return m


def features(s: int, t: int, A: list[int], B: list[int]) -> dict | None:
    mA, mB = load(s, t, "A"), load(s, t, "B")
    if mA is None or mB is None:
        return None
    a, b = V.measures(mA, A, B), V.measures(mB, B, A)   # own targets first in both directions
    if not all(np.isfinite([a["L"], a["E"], b["L"], b["E"]])):
        return None
    return {"L": (a["L"] + b["L"]) / 2, "E": (a["E"] + b["E"]) / 2}


def main() -> None:
    pi_rows = {r["seed"]: r for r in json.loads(next((LAB / "experiments").glob("EXP-059*/summary.json")).read_text(encoding="utf-8"))["rows"]}
    rows, missing = [], []
    for s in V.SEEDS:
        meta = json.loads((V.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        A, B = meta["targets"]["A"], meta["targets"]["B"]
        for t in TS:
            f = features(s, t, A, B)
            pi = pi_rows.get(s, {}).get(f"pi_n{t}")
            if f is None or pi is None or not pi_rows[s].get("valid"):
                missing.append(f"seed {s} t {t}")
                continue
            rows.append({"seed": s, "t": t, "pi": float(pi), **f})
    per_t = {}
    for t in TS:
        rs = [r for r in rows if r["t"] == t]
        if len(rs) < 8:
            per_t[t] = None
            continue
        pi = [r["pi"] for r in rs]
        per_t[t] = {"n": len(rs), "rho_L": float(spearmanr([r["L"] for r in rs], pi)[0]),
                    "rho_E": float(spearmanr([r["E"] for r in rs], pi)[0]),
                    "L_median": float(np.median([r["L"] for r in rs])), "E_median": float(np.median([r["E"] for r in rs]))}
    ok = [v for v in per_t.values() if v is not None]
    rhoL = np.array([v["rho_L"] for v in ok])
    if len(ok) < 5:
        verdict = "nicht auswertbar"
    elif np.median(rhoL) > 0.3 and (rhoL > 0).sum() >= 5:
        verdict = "L traegt Seed-Information"
    elif np.median(np.abs(rhoL)) < 0.1:
        verdict = "keine Information"
    else:
        verdict = "unklar"
    allpi = [r["pi"] for r in rows]
    pooled = {"rho_pi_t": float(spearmanr([r["t"] for r in rows], allpi)[0]),
              "rho_pi_L": float(spearmanr([r["L"] for r in rows], allpi)[0]),
              "rho_pi_E": float(spearmanr([r["E"] for r in rows], allpi)[0])}
    out = {"n_rows": len(rows), "missing": missing, "verdict": verdict, "median_rho_L": float(np.median(rhoL)) if len(ok) else None,
           "n_rho_L_pos": int((rhoL > 0).sum()), "median_rho_E": float(np.median([v["rho_E"] for v in ok])) if ok else None,
           "per_t": per_t, "pooled": pooled, "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
