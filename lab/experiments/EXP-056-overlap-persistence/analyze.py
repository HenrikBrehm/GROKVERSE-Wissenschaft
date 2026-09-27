"""EXP-056 (P3 pilot): does persistence after a data switch at t = 25 depend on the overlap of the two splits? Definition: README.md
(registered before any EXP-056 run). Run under guarded_run.py (imports torch via the EXP-043 helpers).

Per seed s and overlap omega: L(run) = log[P(F) / P(G)] of the final W_E power (add 113 DFT, EXP-043 group_power), F = targets of A,
G = targets of B. pi_AB = (L(A->B) - L(B)) / (L(A) - L(B)), pi_BA = (L(B->A) - L(A)) / (L(B) - L(A)), pi = mean of both.
Level valid: all four runs ok (shared loader) and L(A) > L(B). Seed valid: all three levels valid. b_s = OLS slope of pi over omega.
Primary: one-sided one-sample t-test of mean b > 0 over valid seeds (< 8 valid: not evaluable).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
from result_loader import Expect, find_run, load_run  # noqa: E402
from confirm_p1 import t_test_secondary as t_test  # noqa: E402  (scipy-free one-sided t-test, selftested there)
sys.path.insert(0, str(HERE))
from make_splits import BUDGET, OMEGAS, SEEDS, T_SWITCH, lvl, stem  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
_a43 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_a43)

DEV, SUF, ALPHA, MIN_VALID, EQ_BOUND = "cuda", "_devcuda", 0.05, 8, 0.25   # slope 0.25 = delta-pi 0.1 over omega 0 -> 0.4
SPL = HERE / "splits"


def power(s: int, om: float, kind: str) -> np.ndarray | str:
    """kind: 'A', 'B' (pure runs, 2000 steps) or 'AB', 'BA' (switch at T_SWITCH, then 2000 steps)."""
    first, second = kind[0], kind[1:] or None
    st1 = stem(s, om, first)
    pat = f"EXP-0*_baseline_seed{s}_thr*_{st1}"          # freq_ban names pure runs EXP-018_, switch runs EXP-020_ (smoke 04:44) + (f"_to_{stem(s, om, second)}_at{T_SWITCH}" if second else "") + SUF
    steps = BUDGET + (T_SWITCH if second else 0)
    L = load_run(find_run(HERE / "raw", pat),
                 Expect(seed=s, device=DEV, max_steps=steps, split_file=SPL / f"{st1}.npy", test_file=SPL / f"seed{s}_test.npy",
                        switch_file=SPL / f"{stem(s, om, second)}.npy" if second else None,
                        config={"p": 113, "task": "add"}, snapshots_at=(steps,)))
    if L.status != "ok":
        return f"{kind}: {L.status}: {L.reason}"
    return _a43.group_power(L.snapshot(steps), "add", 113)[0]


def logratio(pw: np.ndarray, F: list[int], G: list[int]) -> float:
    return float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))


def pi_of(L: dict[str, float]) -> dict:
    ab = (L["AB"] - L["B"]) / (L["A"] - L["B"])
    ba = (L["BA"] - L["A"]) / (L["B"] - L["A"])
    return {"pi_AB": ab, "pi_BA": ba, "pi": (ab + ba) / 2}


def slope(y: list[float]) -> float:
    x = np.array(OMEGAS)
    return float(np.polyfit(x, np.array(y), 1)[0])


def verdict(b: np.ndarray) -> dict:
    if len(b) < MIN_VALID:
        return {"verdict": "nicht auswertbar"}
    tt = t_test(b)
    half = float(np.std(b, ddof=1) / np.sqrt(len(b)) * T90[len(b) - 1]) if len(b) - 1 in T90 else None
    ci90 = [float(b.mean() - half), float(b.mean() + half)] if half is not None else None
    if b.mean() > 0 and tt["p_one_sided"] < ALPHA:
        v = "Überlappung trägt Persistenz (ii)"
    elif ci90 is not None and -EQ_BOUND <= ci90[0] and ci90[1] <= EQ_BOUND:
        v = "Persistenz unabhängig von der Überlappung (i)"
    else:
        v = "unklar"
    return {"b_mean": float(b.mean()), "b_sd": float(np.std(b, ddof=1)), "t": tt["t"], "p": tt["p_one_sided"], "ci90": ci90,
            "verdict": v}


T90 = {7: 1.8946, 8: 1.8595, 9: 1.8331}                  # two-sided 90 % t quantiles (df 7-9), table values


def main() -> None:
    rows = []
    for s in SEEDS:
        r: dict = {"seed": s, "valid": False, "levels": {}}
        for om in OMEGAS:
            meta = json.loads((SPL / f"seed{s}_w{lvl(om)}.json").read_text(encoding="utf-8"))
            F, G = meta["targets"]["A"], meta["targets"]["B"]
            pw = {k: power(s, om, k) for k in ("A", "B", "AB", "BA")}
            bad = [v for v in pw.values() if isinstance(v, str)]
            if bad:
                r["levels"][str(om)] = {"valid": False, "reason": "; ".join(bad)}
                continue
            L = {k: logratio(v, F, G) for k, v in pw.items()}
            if not L["A"] > L["B"]:
                r["levels"][str(om)] = {"valid": False, "reason": "L(A) <= L(B)", "L": L}
                continue
            r["levels"][str(om)] = {"valid": True, "L": L, **pi_of(L)}
        if all(v["valid"] for v in r["levels"].values()) and len(r["levels"]) == len(OMEGAS):
            r["valid"] = True
            r["b"] = slope([r["levels"][str(om)]["pi"] for om in OMEGAS])
        rows.append(r)
    ok = [r for r in rows if r["valid"]]
    b = np.array([r["b"] for r in ok])
    per = {str(om): [r["levels"][str(om)]["pi"] for r in ok] for om in OMEGAS}
    out = {"n_valid": len(ok), **verdict(b),
           "pi_by_omega": {k: {"mean": float(np.mean(v)), "sd": float(np.std(v, ddof=1))} for k, v in per.items()} if len(ok) > 1 else None,
           "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert abs(slope([0.1, 0.2, 0.3]) - 0.5) < 1e-12
    p = pi_of({"A": 2.0, "B": -2.0, "AB": 0.0, "BA": 0.0})
    assert p["pi_AB"] == 0.5 and p["pi_BA"] == 0.5
    p = pi_of({"A": 2.0, "B": -2.0, "AB": 2.0, "BA": -2.0})
    assert p["pi"] == 1.0
    assert verdict(np.ones(7))["verdict"] == "nicht auswertbar"
    assert verdict(np.linspace(0.5, 1.5, 10))["verdict"].endswith("(ii)")
    assert verdict(np.linspace(-0.05, 0.05, 10))["verdict"].endswith("(i)")
    assert verdict(np.linspace(-2, 2, 10))["verdict"] == "unklar"
    print("[exp056] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
