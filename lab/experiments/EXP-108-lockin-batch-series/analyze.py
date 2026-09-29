"""EXP-108 analysis (N54b; session 46, written after the launch but before any EXP-108 result was read; implements the readings
fixed in README.md). Global python, under the guard:
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-108-lockin-batch-series/analyze.py

Per seed and batch size B: pi(t) at absolute step 5000 (as EXP-107), t_half by linear interpolation from (0, 0) over the grid;
censored at t_max if pi(t_max) < 0.5. B = 256 from EXP-107's summary rows (same seeds). Exponent alpha per seed = least-squares
slope of log t_half against log(N/B) over the points (1, 31) [full batch, fixed], B = 1024, 256, 64. Mean alpha with a bootstrap
95 % CI over seeds (10 000, rng 100). Readings (README): CI within [0.3, 0.7] 'Wurzel-Uhr gestuetzt'; within [0.8, 1.2]
'Epochen-Uhr'; within [-0.2, 0.2] 'Schritt-Uhr'; else 'gemischt/andere'. More than 2 censored seeds at B = 64 ->
't_half(64) > 700, gegen Wurzel-Uhr'.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
E100, E107 = LAB / "experiments/EXP-100-set-vs-order", LAB / "experiments/EXP-107-lockin-epochs"
sys.path.insert(0, str(LAB / "tools"))
from result_loader import Expect, find_run, load_run  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
_a43 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_a43)
_spec = importlib.util.spec_from_file_location("exp108_design", HERE / "design.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)

SPL = E100 / "splits"
N, T_FB = 3831, 31.0


def boot_ci(x: np.ndarray, seed: int = 100, n_boot: int = 10_000) -> list[float]:
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), size=(n_boot, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def logratio(pw: np.ndarray, F: list[int], G: list[int]) -> float:
    return float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))


def power(root: Path, pat: str, s: int, first: str, second: str | None, total: int, bs: int) -> np.ndarray | str:
    L = load_run(find_run(root, pat),
                 Expect(seed=s, device="cuda", max_steps=total, split_file=SPL / f"seed{s}_{first}.npy",
                        test_file=SPL / f"seed{s}_test.npy", switch_file=(SPL / f"seed{s}_{second}.npy") if second else None,
                        config={"p": 113, "task": "add"}, snapshots_at=(D.TOTAL,)))
    if L.status != "ok":
        return f"{pat}: {L.status}: {L.reason}"
    if L.res.get("batch_size") != bs:
        return f"{pat}: batch size differs"
    pw = _a43.group_power(L.snapshot(D.TOTAL), "add", 113)[0]
    return pw if np.isfinite(pw).all() else f"{pat}: non-finite"


def pis(s: int, bs: int) -> dict | str:
    T = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
    F, G = T["F"], T["G"]
    if bs == 64:
        pure = {x: power(E100 / "raw", f"EXP-018_baseline_seed{s}_thr*_seed{s}_{x}_bs64_devcuda", s, x, None, 30000, 64) for x in "FG"}
    else:
        pure = {x: power(HERE / "raw", f"EXP-018_baseline_seed{s}_thr*_seed{s}_{x}_bs{bs}_devcuda", s, x, None, D.TOTAL, bs) for x in "FG"}
    sw = {(a, b, t): power(HERE / "raw", f"EXP-020_baseline_seed{s}_thr*_seed{s}_{a}_to_seed{s}_{b}_at{t}_bs{bs}_devcuda", s, a, b, D.TOTAL, bs)
          for t in D.SWITCH_T[bs] for a, b in (("F", "G"), ("G", "F"))}
    bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
    if bad:
        return bad[0]
    LF, LG = logratio(pure["F"], F, G), logratio(pure["G"], F, G)
    if LF - LG < 0.5:
        return f"seed {s} B {bs}: pure runs not separated"
    return {t: ((logratio(sw[("F", "G", t)], F, G) - LG) / (LF - LG) + (logratio(sw[("G", "F", t)], F, G) - LF) / (LG - LF)) / 2
            for t in D.SWITCH_T[bs]}


def t_half(pi: dict) -> tuple[float, bool]:
    ts = [0] + sorted(pi)
    ms = [0.0] + [pi[t] for t in sorted(pi)]
    for i in range(1, len(ts)):
        if ms[i - 1] < 0.5 <= ms[i]:
            return ts[i - 1] + (0.5 - ms[i - 1]) * (ts[i] - ts[i - 1]) / (ms[i] - ms[i - 1]), False
    return float(ts[-1]), True


def main() -> None:
    r107 = {r["seed"]: r for r in json.loads((E107 / "summary.json").read_text(encoding="utf-8"))["rows"] if not r["errors"]}
    rows, errors = [], []
    for s in D.SEEDS:
        row = {"seed": s}
        for bs in (64, 1024):
            p = pis(s, bs)
            if isinstance(p, str):
                errors.append(p)
                break
            row[f"pi_{bs}"] = p
            row[f"th_{bs}"], row[f"cens_{bs}"] = t_half(p)
        if s in r107:
            row["th_256"], row["cens_256"] = t_half({t: r107[s][f"pi_{t}"] for t in (100, 200, 375, 750, 1500)})
        if all(f"th_{b}" in row for b in (64, 256, 1024)):
            x = np.log([1.0, N / 1024, N / 256, N / 64])
            y = np.log([T_FB, row["th_1024"], row["th_256"], row["th_64"]])
            row["alpha"] = float(np.polyfit(x, y, 1)[0])
            rows.append(row)
    out: dict = {"n": len(rows), "errors": errors[:5]}
    if len(rows) >= 6:
        a = np.array([r["alpha"] for r in rows])
        ci = boot_ci(a)
        n_cens64 = sum(r["cens_64"] for r in rows)
        if n_cens64 > 2:
            rd = "t_half(64) > 700, gegen Wurzel-Uhr"
        elif 0.3 <= ci[0] and ci[1] <= 0.7:
            rd = "Wurzel-Uhr gestuetzt"
        elif 0.8 <= ci[0] and ci[1] <= 1.2:
            rd = "Epochen-Uhr"
        elif -0.2 <= ci[0] and ci[1] <= 0.2:
            rd = "Schritt-Uhr"
        else:
            rd = "gemischt/andere"
        out.update({"reading": rd, "alpha": {"mean": float(a.mean()), "ci95": ci}, "n_censored": {b: int(sum(r[f"cens_{b}"] for r in rows)) for b in (64, 256, 1024)},
                    "t_half_mean": {b: float(np.mean([r[f"th_{b}"] for r in rows])) for b in (64, 256, 1024)},
                    "pi_mean": {b: {t: float(np.mean([r[f"pi_{b}"][t] for r in rows])) for t in D.SWITCH_T[b]} for b in (64, 1024)}})
    else:
        out["reading"] = "nicht auswertbar"
    (HERE / "summary.json").write_text(json.dumps({"primary": out, "rows": rows}, indent=1, default=float), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
