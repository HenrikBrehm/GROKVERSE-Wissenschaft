"""EXP-042 Nachtrag b (session 15, frozen before any EXP-042 run; DESCRIPTIVE, the pre-registered verdict in analyze.py is unchanged).

Why: under a pure clock with linear superposition inside an early integration window (EXP-020/posthoc_window_model.py, T* ~ 69 steps),
the top-5 crossover already moves with the strength of G (EXP-020/posthoc_clock_crossover.py: eps 8 -> t ~ 46-54, eps 1 -> ~ 14-24),
so 'later' does not separate H42 from a clock. The normalised persistence pi does: with linear superposition pi(t) = t / T* whatever G is.
  C (fixed clock): mean pi_eps(t) within 0.12 of the EXP-020 curve (window model min(1, t / 69)) in every cell.
  O (G strength moves the window): eps 8 at least 0.15 below the curve at t = 25 or 50; eps 1 at least 0.15 above it at t = 10 or 25.
pi = (D_switch - D_onlyG) / (D_onlyF - D_onlyG), D = beta_F - beta_G (log-log slope of W_E power on M0 of F resp. G_eps), pure runs at
step 2000, switch runs at their last step (t + 2000); per seed. Also pi at global step 250 (freeze check: |pi(250) - pi(end)| <= 0.1 expected).
UNTESTED (window closed). Usage: python pi_window.py [--selftest]
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[0]
sys.path.insert(0, str(LAB / "EXP-043-generalize-steering"))
from make_split import mask_power  # noqa: E402

T_STAR, TOL_C, DELTA_O, MIN_SEEDS = 69.0, 0.12, 0.15, 3   # MIN_SEEDS: Nachtrag c (review s15)


def curve(t: float) -> float:
    return min(1.0, t / T_STAR)


def beta(m0: np.ndarray, pw: np.ndarray) -> float:
    return float(np.polyfit(np.log(m0), np.log(pw), 1)[0])


def spectrum(run: Path, step: int | None) -> np.ndarray | None:
    st = [int(x) for x in np.load(run / "spectra_steps.npy")]
    pw = np.load(run / "spectra.npy")
    if step is None:
        return pw[-1]
    return pw[st.index(step)] if step in st else None


def need(run: Path, step: int | None) -> np.ndarray:
    pw = spectrum(run, step)
    if pw is None:                                   # Nachtrag c: a missing step marks the seed broken instead of a TypeError
        raise ValueError(f"spectrum step {step} missing: {run.name}")
    return pw


def analyze_mod():
    spec = importlib.util.spec_from_file_location("exp042_analyze", HERE / "analyze.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def pis(run_dir, split_dir: Path, s: int, grid) -> dict:
    M = {a: mask_power(np.load(split_dir / f"seed{s}_train_{a}.npy"), "add", 113) for a in "FG"}
    D = lambda pw: beta(M["F"], pw) - beta(M["G"], pw)  # noqa: E731
    for t in (0.0, math.inf, *grid):
        r = json.loads((run_dir(s, t) / "result.json").read_text(encoding="utf-8"))
        if r.get("status") != "completed":
            raise ValueError(f"run not completed: {run_dir(s, t).name}")
    ref = {k: {250: spectrum(run_dir(s, t), 250), 2000: need(run_dir(s, t), 2000)} for k, t in (("F", math.inf), ("G", 0.0))}
    out = {}
    for t in grid:
        dF, dG = D(ref["F"][2000]), D(ref["G"][2000])
        row = {"pi_end": (D(need(run_dir(s, t), None)) - dG) / (dF - dG), "curve": curve(t)}
        sw250 = spectrum(run_dir(s, t), 250)
        if t < 250 and sw250 is not None and ref["F"][250] is not None and ref["G"][250] is not None:
            f2, g2 = D(ref["F"][250]), D(ref["G"][250])
            row["pi_250"] = (D(sw250) - g2) / (f2 - g2)
        if not all(math.isfinite(v) for v in row.values()):
            raise ValueError(f"non-finite pi seed {s} t {t}")
        out[int(t)] = row
    return out


def reading(e: float, cells: dict[int, list[float]]) -> str:
    dev = {t: float(np.mean(v)) - curve(t) for t, v in cells.items() if len(v) >= MIN_SEEDS}
    if not dev:
        return "nicht auswertbar"
    if e == 8.0 and any(dev.get(t, 0) <= -DELTA_O for t in (25, 50)):
        return f"O (Fenster haengt von G ab), dev {dev}"
    if e == 1.0 and any(dev.get(t, 0) >= DELTA_O for t in (10, 25)):
        return f"O (Fenster haengt von G ab), dev {dev}"
    if all(abs(d) <= TOL_C for d in dev.values()):
        return f"C (fester Takt), dev {dev}"
    return f"weder C noch O, dev {dev}"


def main() -> None:
    A = analyze_mod()
    out = {}
    for e in A.GRIDS:
        m = A.load_mod(e)
        rows, cells = {}, {t: [] for t in A.GRIDS[e]}
        for s in A.SEEDS:
            try:
                rows[s] = pis(m.run_dir, HERE / f"eps{e:g}" / "splits", s, A.GRIDS[e])
                for t in cells:
                    cells[t].append(rows[s][t]["pi_end"])
            except (OSError, KeyError, ValueError) as ex:
                rows[s] = {"missing_or_broken": f"{type(ex).__name__}: {ex}"}
        out[f"eps{e:g}"] = {"rows": rows, "reading": reading(e, cells),
                            "mean_pi": {t: (float(np.mean(v)) if v else None) for t, v in cells.items()}}
        print(f"eps{e:g}", out[f"eps{e:g}"]["mean_pi"], out[f"eps{e:g}"]["reading"])
    (HERE / "summary_pi_window.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")


def selftest() -> None:
    assert curve(25) == 25 / 69 and curve(150) == 1.0
    assert reading(8.0, {25: [0.1] * 3, 50: [0.5] * 3}).startswith("O") and reading(8.0, {25: [0.37] * 3, 50: [0.7] * 3}).startswith("C")
    assert reading(1.0, {10: [0.4] * 3, 25: [0.4] * 3}).startswith("O") and reading(8.0, {}) == "nicht auswertbar"
    assert reading(8.0, {25: [0.1]}) == "nicht auswertbar"
    # EXP-020 regression: the same pi as posthoc_beta_persistence.json (eps 2, stored runs)
    spec = importlib.util.spec_from_file_location("e20", LAB / "EXP-020-data-switch" / "analyze.py")
    e20 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(e20)
    ref = json.loads((LAB / "EXP-020-data-switch" / "posthoc_beta_persistence.json").read_text(encoding="utf-8"))
    got = pis(e20.run_dir, LAB / "EXP-020-data-switch" / "splits", 30, (10, 25, 50, 150))
    for t in (10, 25, 50, 150):
        assert abs(got[t]["pi_end"] - ref["switch"][str(t)]["pi"]["30"]) < 1e-9, (t, got[t])
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
