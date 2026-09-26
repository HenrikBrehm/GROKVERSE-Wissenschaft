"""EXP-027 analysis (pre-registered in README.md): does the tilt towards the half targets H grow as width shrinks?

Widths 32/64/128 from raw/, width 512 from EXP-026 arm t_s = 0 (identical computation). Units: EXP-016 seeds 10-14 F.
Primary: Spearman(rank of -w, ds_H) with ds_H = share(H) - share(F) of the normalised h = 2 spectrum at step 5000,
within-split permutation test. Fails closed unless the full 4 x 5 grid is complete.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
E26 = HERE.parents[0] / "EXP-026-parity-crossover"
sys.path.insert(0, str(E26))
from analyze import fold, spearman  # noqa: E402

WIDTHS = (512, 128, 64, 32)          # rank order = narrower is higher
SEEDS = (10, 11, 12, 13, 14)


def path(w: int, s: int) -> Path:
    if w == 512:
        return E26 / "raw" / f"EXP-026_a3_sw0to0_seed{s}_F" / "result.json"
    return HERE / "raw" / f"EXP-026_a0_w{w}_seed{s}_F" / "result.json"


def main() -> None:
    rows = []
    for w in WIDTHS:
        for s in SEEDS:
            f = path(w, s)
            if not f.exists():
                continue
            r = json.loads(f.read_text())
            a = r["args"]
            alpha_end = a["alpha_after"] if a["switch_step"] == 0 else a["alpha"]
            if not (r.get("complete") and a["steps"] == 5000 and alpha_end == 0.0 and a.get("width", 512) == w
                    and a["arm"] == "F" and a["init_seed"] is None):
                continue
            T = set(r["targets"]); H = {fold(57 * t) for t in T}
            sp = np.array(r["spectra"]["5000"]["weighted"]); sh = sp / sp.sum()
            top = set(int(k) for k in np.argsort(-sp)[:5] + 1)
            rows.append({"w": w, "seed": s, "ds_H": float(sh[[k - 1 for k in H]].sum() - sh[[k - 1 for k in T]].sum()),
                         "ov_H": len(top & H), "ov_F": len(top & T), "n_eff": float(np.exp(-(sh * np.log(sh + 1e-300)).sum())),
                         "test_acc": r["final_test_acc"], "gen95": r["gen_step_test95"]})
    out = {"n_valid": len(rows), "rows": rows}
    if len(rows) != len(WIDTHS) * len(SEEDS):
        out["verdict"] = "nicht auswertbar (Raster unvollständig)"
    else:
        rank = np.array([WIDTHS.index(x["w"]) for x in rows], float)
        d = np.array([x["ds_H"] for x in rows])
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
        out.update(rho=rho, p_perm=float(p),
                   verdict="bestätigt" if p < 0.05 and rho > 0 else "widerspricht" if rho <= 0 else "richtungsgleich, n. s.")
        out["by_width"] = {str(w): {k: float(np.mean([x[k] for x in rows if x["w"] == w]))
                                    for k in ("ds_H", "ov_H", "ov_F", "n_eff", "test_acc")} for w in WIDTHS}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
