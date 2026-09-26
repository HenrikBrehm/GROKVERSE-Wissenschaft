"""EXP-027 analysis (pre-registered in README.md, Nachtrag a after Codex review, before any run).

Widths 32/64/128/256 from raw/, width 512 from EXP-026 arm t_s = 0 (identical computation). Units: EXP-016 seeds 10-14 F.
Per run: q_H, q_F = percentile of share(H), share(F) among 20 000 random 5-sets of frequencies of the same normalised
h = 2 spectrum at step 5000 (calibrated: uniform under 'no H/F preference' whatever the concentration); u = q_H - q_F.
Primary: Spearman(rank of -w, u), permutation of widths within each split. Fidelity gate: every run needs final train
accuracy >= 0.99 and test accuracy >= 0.90, else the grid is not evaluable. Provenance: all registered arguments checked.
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

WIDTHS = (512, 256, 128, 64, 32)          # rank order = narrower is higher
SEEDS = (10, 11, 12, 13, 14)
REG = {"steps": 5000, "arm": "F", "init_seed": None, "lr": 1e-3, "wd": 1.0, "init_scale": 0.1, "random_split": False}
N_RAND = 20_000


def path(w: int, s: int) -> Path:
    if w == 512:
        return E26 / "raw" / f"EXP-026_a3_sw0to0_seed{s}_F" / "result.json"
    return HERE / "raw" / f"EXP-026_a0_w{w}_seed{s}_F" / "result.json"


def percentile(sh: np.ndarray, S: set[int], rng: np.random.Generator) -> float:
    target = sh[[k - 1 for k in S]].sum()
    rand = np.array([sh[rng.choice(56, size=len(S), replace=False)].sum() for _ in range(N_RAND)])
    return float((rand < target).mean() + 0.5 * (rand == target).mean())


def valid(r: dict, w: int, s: int) -> bool:
    a = r["args"]
    alpha_end = a["alpha_after"] if a["switch_step"] == 0 else a["alpha"]
    return (bool(r.get("complete")) and all(a.get(k) == v for k, v in REG.items()) and a["seed"] == s
            and alpha_end == 0.0 and a.get("width", 512) == w and a["split_dir"].replace("\\", "/").endswith(
                "EXP-016-engineered-split/splits"))


def main() -> None:
    rng = np.random.default_rng(27)
    rows, bad = [], []
    for w in WIDTHS:
        for s in SEEDS:
            f = path(w, s)
            if not f.exists():
                bad.append((w, s, "missing")); continue
            r = json.loads(f.read_text())
            if not valid(r, w, s):
                bad.append((w, s, "provenance/incomplete")); continue
            T = set(r["targets"]); H = {fold(57 * t) for t in T}
            sp = np.array(r["spectra"]["5000"]["weighted"]); sh = sp / sp.sum()
            top = set(int(k) for k in np.argsort(-sp)[:5] + 1)
            qH, qF = percentile(sh, H, rng), percentile(sh, T, rng)
            rows.append({"w": w, "seed": s, "q_H": qH, "q_F": qF, "u": qH - qF,
                         "ds_H": float(sh[[k - 1 for k in H]].sum() - sh[[k - 1 for k in T]].sum()),
                         "ov_H": len(top & H), "ov_F": len(top & T),
                         "n_eff": float(np.exp(-(sh * np.log(sh + 1e-300)).sum())),
                         "train_acc": r["final_train_acc"], "test_acc": r["final_test_acc"], "gen95": r["gen_step_test95"]})
    out = {"n_valid": len(rows), "invalid": bad, "rows": rows}
    low = [(x["w"], x["seed"]) for x in rows if x["train_acc"] < 0.99 or x["test_acc"] < 0.90]
    out["fidelity_fail"] = low
    if len(rows) != len(WIDTHS) * len(SEEDS):
        out["verdict"] = "nicht auswertbar (Raster unvollständig)"
    elif low:
        out["verdict"] = "nicht auswertbar (Güte-Schwelle verfehlt)"
    else:
        rank = np.array([WIDTHS.index(x["w"]) for x in rows], float)
        d = np.array([x["u"] for x in rows])
        seed = np.array([x["seed"] for x in rows])
        rho = spearman(rank, d)
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
    if rows:
        out["by_width"] = {str(w): {k: float(np.mean([x[k] for x in rows if x["w"] == w]))
                                    for k in ("u", "q_H", "q_F", "ds_H", "ov_H", "ov_F", "n_eff", "test_acc")}
                           for w in WIDTHS if any(x["w"] == w for x in rows)}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
