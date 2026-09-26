"""EXP-025 analysis (pre-registered in README.md).

For each seed s (study random split) and arm A in {quad, relu}: K_A,s = final top-5 of the trained two-hot net.
Predictors on the same mask: U_quad, U_relu (exact AGF utility, 16 x 16 phases), M0 (EXP-015).
Primary (architecture specificity): d = rbar(U_other, K_A) - rbar(U_own, K_A) over all 20 (seed, arm) units,
one-sided exact sign-flip test (EXP-012 sign_flip_p) on mean d > 0. Co-primary: rbar(U_own) over the 20 units
against the Monte-Carlo chance null (EXP-012 mc_null_p). Secondary: foreign-mask rbar, M0.
Nachtrag a (session 7, before any run): continuous secondary rho_own - rho_other, Spearman of the utility with the
whole final weighted spectrum (the two-hot spectra are nearly flat, EXP-024 post hoc), sign-flip test.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[0]
sys.path.insert(0, str(EXP / "EXP-012-init-gradient"))
sys.path.insert(0, str(EXP / "EXP-015-mask-spectrum"))
sys.path.insert(0, str(EXP / "EXP-024-quadratic-agf-mask"))
import predict as p12  # noqa: E402
from mask_spectrum import m0, mask_matrix  # noqa: E402
from utility_relu import utility  # noqa: E402

SEEDS, ACTS = range(10, 20), ("quad", "relu")


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))   # spectra and utilities are continuous: no ties
    return float(np.corrcoef(rx, ry)[0, 1])


def main() -> None:
    cache = HERE / "utilities.json"
    if cache.exists():
        U = {tuple(k.split("|")): np.array(v) for k, v in json.loads(cache.read_text()).items()}
    else:
        U = {}
        for s in SEEDS:
            M = mask_matrix(s)
            for act in ACTS:
                U[(str(s), act)] = np.array([utility(M, k, act) for k in range(1, 57)])
        cache.write_text(json.dumps({"|".join(k): v.tolist() for k, v in U.items()}), encoding="utf-8")
    rows, d, own, dc = [], [], [], []
    for act in ACTS:
        other = "relu" if act == "quad" else "quad"
        for s in SEEDS:
            f = HERE / "raw" / f"EXP-025_{act}_seed{s}_random" / "result.json"
            if not f.exists():
                rows.append({"seed": s, "act": act, "valid": False, "reason": "missing"}); continue
            r = json.loads(f.read_text())
            if not r.get("complete"):
                rows.append({"seed": s, "act": act, "valid": False, "reason": "incomplete"}); continue
            K = r["final_top5"]
            ro, rx = p12.rbar(U[(str(s), act)], K), p12.rbar(U[(str(s), other)], K)
            foreign = float(np.mean([p12.rbar(U[(str(t), act)], K) for t in SEEDS if t != s]))
            rows.append({"seed": s, "act": act, "valid": True, "K": K, "test_acc": r["final_test_acc"],
                         "rbar_own": ro, "rbar_other": rx, "rbar_foreign_own": foreign,
                         "rbar_M0": p12.rbar(m0(mask_matrix(s)), K)})
            w = np.array(r["spectra"]["5000"]["weighted"])
            rows[-1].update(rho_own=spearman(U[(str(s), act)], w), rho_other=spearman(U[(str(s), other)], w))
            d.append(rx - ro); own.append(ro); dc.append(rows[-1]["rho_own"] - rows[-1]["rho_other"])
    v = [x for x in rows if x["valid"]]
    out = {"n_valid": len(v), "rows": rows}
    if len(v) >= 16:
        dd = np.array(d)
        out.update({"d_mean": float(dd.mean()), "p_specificity": p12.sign_flip_p(dd),
                    "rbar_own_mean": float(np.mean(own)), "p_own_vs_chance": p12.mc_null_p(float(np.mean(own)), len(own)),
                    "rbar_foreign_own_mean": float(np.mean([x["rbar_foreign_own"] for x in v])),
                    "rbar_M0_mean": float(np.mean([x["rbar_M0"] for x in v])),
                    "secondary_rho_diff_mean": float(np.mean(dc)), "secondary_p_rho_diff": p12.sign_flip_p(np.array(dc))})
        for act in ACTS:
            va = [x for x in v if x["act"] == act]
            out[act] = {k: float(np.mean([x[k] for x in va])) for k in
                        ("rbar_own", "rbar_other", "rbar_foreign_own", "rbar_M0", "test_acc", "rho_own", "rho_other")}
        spec = out["p_specificity"] < 0.05 and out["d_mean"] > 0
        chance = out["p_own_vs_chance"] < 0.05
        out["verdict"] = ("bestätigt" if spec and chance else "teilweise" if spec or chance else
                          "widerspricht" if out["d_mean"] <= 0 else "richtungsgleich, n. s.")
    else:
        out["verdict"] = "nicht auswertbar"
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
