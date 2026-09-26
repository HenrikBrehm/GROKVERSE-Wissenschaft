"""EXP-024 analysis (pre-registered in README.md): overlap of final top-5 with targets F and half-targets H(F).

Valid = run complete (all steps, finite weights), intended unit (seeds 10-19, arms F/G, not 12/G), default init.
Control (Codex review, secondary): overlap with fold(m*F) for every other multiplier m = 3..55 (m = 56 = -57 is H).
"""
from __future__ import annotations

import json
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P = 113


def fold(k: int) -> int:
    k %= P
    return min(k, P - k)


def sign_test(d: list[int]) -> float:
    nz = [x for x in d if x != 0]
    n, pos = len(nz), sum(x > 0 for x in nz)
    return sum(comb(n, i) for i in range(pos, n + 1)) / 2 ** n if n else 1.0


def main() -> None:
    out = {}
    for act in ("quad", "relu"):
        rows = []
        for f in sorted((HERE / "raw").glob(f"EXP-024_{act}_seed*/result.json")):
            r = json.loads(f.read_text())
            unit = (r["args"]["seed"], r["args"]["arm"])
            if "_init" in r["run_id"] or unit[0] not in range(10, 20) or unit == (12, "G"):
                continue
            T = set(r["targets"]); H = {fold(57 * t) for t in T}
            top = set(r["final_top5"])
            ok = r.get("complete", False) and r["args"]["steps"] == 5000
            ov_m = [len(top & {fold(m * t) for t in T}) for m in range(3, 56)]
            rows.append({"run": r["run_id"], "ov_F": len(top & T), "ov_H": len(top & H), "valid": bool(ok),
                         "test_acc": r["final_test_acc"], "gen95": r["gen_step_test95"],
                         "top5": r["final_top5"], "F": sorted(T), "H": sorted(H),
                         "ov_2F": len(top & {fold(2 * t) for t in T}), "ov_other_m_mean": float(np.mean(ov_m)),
                         "ov_raw_H": len(set(r["final_top5_raw"]) & H), "ov_raw_F": len(set(r["final_top5_raw"]) & T),
                         "ov_out_H": len(set(r["final_top5_out"]) & H), "ov_out_F": len(set(r["final_top5_out"]) & T)})
        v = [x for x in rows if x["valid"]]
        d = [x["ov_H"] - x["ov_F"] for x in v]
        res = {"n_valid": len(v), "ov_F_mean": float(np.mean([x["ov_F"] for x in v])) if v else None,
               "ov_H_mean": float(np.mean([x["ov_H"] for x in v])) if v else None,
               "d_mean": float(np.mean(d)) if v else None, "p_sign": sign_test(d),
               "n_informative": sum(x != 0 for x in d),
               "secondary": {k: float(np.mean([x[k] for x in v])) if v else None for k in
                             ("ov_2F", "ov_other_m_mean", "ov_raw_H", "ov_raw_F", "ov_out_H", "ov_out_F")},
               "test_acc_mean": float(np.mean([x["test_acc"] for x in v])) if v else None, "rows": rows}
        if act == "quad":
            if len(v) < 12 or res["n_informative"] < 8:
                res["verdict"] = "nicht auswertbar"
            elif res["d_mean"] <= 0:
                res["verdict"] = "widerspricht"
            elif res["p_sign"] < 0.05 and res["ov_H_mean"] >= 2:
                res["verdict"] = "bestätigt"
            else:
                res["verdict"] = "richtungsgleich, n. s."
        if act == "relu":   # Nachtrag b: directional secondary prediction F > H
            dr = [-x for x in d]
            res["p_sign_F_gt_H"] = sign_test(dr)
            if len(v) < 12 or sum(x != 0 for x in dr) < 8:
                res["verdict_R"] = "nicht auswertbar"
            elif np.mean(dr) <= 0:
                res["verdict_R"] = "widerspricht"
            elif res["p_sign_F_gt_H"] < 0.05 and res["ov_F_mean"] >= 2:
                res["verdict_R"] = "bestätigt"
            else:
                res["verdict_R"] = "richtungsgleich, n. s."
        out[act] = res
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for act, res in out.items():
        print(act, json.dumps({k: v for k, v in res.items() if k != "rows"}))


if __name__ == "__main__":
    main()
