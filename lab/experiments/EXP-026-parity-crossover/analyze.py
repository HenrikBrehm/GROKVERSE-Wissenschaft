"""EXP-026 analysis (pre-registered in README.md): parity crossover alpha* and its position relative to r(0), r(5000)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
P = 113
ALPHAS = (0.0, 0.003, 0.03, 0.3, 3.0)
SEEDS = (10, 11, 12, 13, 14)


def fold(k: int) -> int:
    k %= P
    return min(k, P - k)


def main() -> None:
    rows = []
    for al in ALPHAS:
        for s in SEEDS:
            f = HERE / "raw" / f"EXP-026_a{al:g}_seed{s}_F" / "result.json"
            if not f.exists():
                continue
            r = json.loads(f.read_text())
            if not r.get("complete") or r["args"]["steps"] != 5000:
                continue
            T = set(r["targets"]); H = {fold(57 * t) for t in T}
            top = set(r["final_top5"])
            amps = {int(k): v["amp"]["median"] for k, v in r["spectra"].items()}
            rows.append({"alpha": al, "seed": s, "ov_F": len(top & T), "ov_H": len(top & H),
                         "d": len(top & T) - len(top & H), "test_acc": r["final_test_acc"],
                         "gen95": r["gen_step_test95"], "r": amps})
    n = len(rows)
    out = {"n_valid": n, "rows": rows}
    if n < 20:
        out["verdict"] = "nicht auswertbar"
    else:
        rank = np.array([ALPHAS.index(x["alpha"]) for x in rows], float)
        d = np.array([x["d"] for x in rows], float)
        seed = np.array([x["seed"] for x in rows])
        rho = spearmanr(rank, d).statistic
        rng = np.random.default_rng(0)
        cnt = 0
        for _ in range(10_000):
            pr = rank.copy()
            for s in SEEDS:
                m = seed == s
                pr[m] = rng.permutation(pr[m])
            rp = spearmanr(pr, d).statistic
            cnt += (np.nan_to_num(rp, nan=-1) >= rho)
        p = (cnt + 1) / 10_001
        out.update(rho=float(rho), p_perm=float(p), verdict="Umschlag bestätigt" if p < 0.05 and rho > 0
                   else "kein Umschlag nachgewiesen")
        md = {al: float(np.mean([x["d"] for x in rows if x["alpha"] == al])) for al in ALPHAS
              if any(x["alpha"] == al for x in rows)}
        out["mean_d"] = {f"{k:g}": v for k, v in md.items()}
        neg = [al for al, v in md.items() if v < 0]
        pos = [al for al, v in md.items() if v > 0]
        r0 = float(np.median([x["r"][0] for x in rows]))
        out["r0_median"] = r0
        out["r_median_by_step"] = {int(t): float(np.median([x["r"][t] for x in rows if t in x["r"]]))
                                   for t in sorted(rows[0]["r"])}
        if neg and pos and max(neg) < min(pos):
            lo, hi = max(max(neg), 0.001), min(pos)
            a_star = float(np.sqrt(lo * hi))
            near = [al for al in ALPHAS if al in (max(neg), min(pos))]
            r_end = float(np.median([x["r"][5000] for x in rows if x["alpha"] in near]))
            A, B = a_star <= 3 * r0, a_star >= r_end / 3
            out.update(alpha_star=a_star, r_end_near=r_end, A_start=bool(A), B_end=bool(B),
                       when="nicht unterscheidbar" if A and B else "A (Start)" if A else "B (Ende)" if B
                       else "Zwischenlage")
            if not A and not B:
                steps = sorted(out["r_median_by_step"])
                out["t_star"] = next((t for t in steps if out["r_median_by_step"][t] >= a_star), None)
        else:
            out["alpha_star"] = None
            out["when"] = "kein eindeutiger Vorzeichenwechsel der mittleren d"
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
