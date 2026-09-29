"""EXP-107 analysis (N54, exploration; session 46, written BEFORE any EXP-107 run). README.md.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-107-lockin-epochs/analyze.py

pi(t) as EXP-100 switch_analyze.py / N28: L = log[P(T_F)/P(T_G)] of W_E group power at absolute step 5000;
pi(t) = ((L_FG(t) - L_G)/(L_F - L_G) + (L_GF(t) - L_F)/(L_G - L_F)) / 2 with the pure EXP-100 pilot iid256 runs (snapshot 5000).
Valid seed: all 10 switch runs and both pure runs load (shared loader), L_F - L_G >= 0.5; fewer than 6 -> 'nicht auswertbar'.
Reference (seen, from EXP-100 raw_switch at step 5000, post hoc s46): pi(25), pi(50) ~ 0 under iid256; full batch
pi(25) = 0.38, pi(50) = 0.87 (1 step = 1 epoch).
Readings (bootstrap 95 % CI over seeds, 10 000, rng 100):
  'Epochen-Uhr gestuetzt'    mean pi(375) < 0.5 < mean pi(750) and CI of pi(750) - pi(375) > 0
                             (the full-batch window at 25-50 epochs reappears at 25-50 epochs)
  'frueher als in Epochen'   mean pi(375) >= 0.5  (then the window lies between the last t with pi < 0.5 and 375)
  'spaeter als in Epochen'   mean pi(750) < 0.5 and mean pi(1500) >= 0.5
  'keine Festlegung bis 100 Epochen'   mean pi(1500) < 0.5
  else 'gemischt'.
Descriptive: pi per t with CI; the t at which the mean pi first exceeds 0.5 (linear interpolation), in steps and epochs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
E100 = LAB / "experiments/EXP-100-set-vs-order"
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(HERE))
import design as D  # noqa: E402  (EXP-107 design)
from result_loader import Expect, find_run, load_run  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
_a43 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_a43)


def boot_ci(x: np.ndarray, seed: int = 100, n_boot: int = 10_000) -> list[float]:
    """As EXP-100 analyze.boot_ci (percentile bootstrap over seeds)."""
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), size=(n_boot, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


SPL = E100 / "splits"
SPE = 3831 / 256


def logratio(pw: np.ndarray, F: list[int], G: list[int]) -> float:
    return float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))


def pi_pair(LF: float, LG: float, LFG: float, LGF: float) -> float:
    return ((LFG - LG) / (LF - LG) + (LGF - LF) / (LG - LF)) / 2


def power(root: Path, pat: str, s: int, first: str, second: str | None, total: int) -> np.ndarray | str:
    L = load_run(find_run(root, pat),
                 Expect(seed=s, device="cuda", max_steps=total, split_file=SPL / f"seed{s}_{first}.npy",
                        test_file=SPL / f"seed{s}_test.npy", switch_file=(SPL / f"seed{s}_{second}.npy") if second else None,
                        config={"p": 113, "task": "add"}, snapshots_at=(D.TOTAL,)))
    if L.status != "ok":
        return f"{pat}: {L.status}: {L.reason}"
    if L.res.get("batch_size") != 256:
        return f"{pat}: batch size differs"
    pw = _a43.group_power(L.snapshot(D.TOTAL), "add", 113)[0]
    return pw if np.isfinite(pw).all() else f"{pat}: non-finite"


def seed_row(s: int) -> dict:
    T = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
    F, G = T["F"], T["G"]
    pure = {x: power(E100 / "raw", f"EXP-018_baseline_seed{s}_thr*_seed{s}_{x}_bs256_devcuda", s, x, None, 30000) for x in "FG"}
    sw = {(a, b, t): power(HERE / "raw", f"EXP-020_baseline_seed{s}_thr*_seed{s}_{a}_to_seed{s}_{b}_at{t}_bs256_devcuda", s, a, b, D.TOTAL)
          for t in D.SWITCH_T for a, b in (("F", "G"), ("G", "F"))}
    bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
    if bad:
        return {"seed": s, "errors": bad}
    LF, LG = logratio(pure["F"], F, G), logratio(pure["G"], F, G)
    if LF - LG < 0.5:
        return {"seed": s, "errors": [f"pure runs not separated ({LF - LG:.2f})"]}
    row = {"seed": s, "errors": []}
    for t in D.SWITCH_T:
        row[f"pi_{t}"] = pi_pair(LF, LG, logratio(sw[("F", "G", t)], F, G), logratio(sw[("G", "F", t)], F, G))
    return row


def reading(rows: list[dict]) -> dict:
    ok = [r for r in rows if not r["errors"]]
    if len(ok) < 6:
        return {"n": len(ok), "reading": "nicht auswertbar", "errors": [e for r in rows for e in r["errors"]][:5]}
    col = lambda t: np.array([r[f"pi_{t}"] for r in ok])   # noqa: E731
    m = {t: float(col(t).mean()) for t in D.SWITCH_T}
    d = boot_ci(col(750) - col(375))
    if m[375] < 0.5 < m[750] and d[0] > 0:
        rd = "Epochen-Uhr gestuetzt"
    elif m[375] >= 0.5:
        rd = "frueher als in Epochen"
    elif m[750] < 0.5 <= m[1500]:
        rd = "spaeter als in Epochen"
    elif m[1500] < 0.5:
        rd = "keine Festlegung bis 100 Epochen"
    else:
        rd = "gemischt"
    ts = [0] + list(D.SWITCH_T)
    ms = [0.0] + [m[t] for t in D.SWITCH_T]
    cross = next((ts[i - 1] + (0.5 - ms[i - 1]) * (ts[i] - ts[i - 1]) / (ms[i] - ms[i - 1])
                  for i in range(1, len(ts)) if ms[i - 1] < 0.5 <= ms[i]), None)
    return {"n": len(ok), "reading": rd, "pi": {t: {"mean": m[t], "ci95": boot_ci(col(t)), "epochs": t / SPE} for t in D.SWITCH_T},
            "d_750_minus_375_ci95": d, "t_half_steps": cross, "t_half_epochs": None if cross is None else cross / SPE}


def main() -> None:
    rows = [seed_row(s) for s in D.SEEDS]
    out = {"primary": reading(rows), "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps(out["primary"], indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
