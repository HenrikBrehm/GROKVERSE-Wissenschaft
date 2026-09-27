"""EXP-059 (pilot): is the momentum effect of EXP-058 just prolonged exposure to A? Definition: README.md (registered before any
EXP-059 run). Run under guarded_run.py.

Seeds 400-409, omega = 0 (EXP-056 splits; pure A/B runs from EXP-056, t = 25 arms from EXP-058). pi as EXP-056.
Curves: pi_normal(t) for t in 10, 15, 20, 25, 30, 35, 50 and pi_rom(t) (exp_avg zeroed at the switch) for t in 25, 30, 35, 40, 50.
Primary: D = pi_rom(35) - pi_normal(25) per seed (10 extra plain A steps against the momentum tail of 25 A steps).
Secondary: delta(t') = t' - t_eq with t_eq = the switch time at which the seed-mean normal curve (linear interpolation) reaches pi_rom(t').
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
E56 = LAB / "experiments/EXP-056-overlap-persistence"
E58 = LAB / "experiments/EXP-058-optim-part"
_spec = importlib.util.spec_from_file_location("exp056", E56 / "analyze.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

SEEDS, OM, ALPHA, MIN_VALID, MARGIN = tuple(range(400, 410)), 0.0, 0.05, 8, 0.05
T_NORMAL, T_ROM = (10, 15, 20, 25, 30, 35, 50), (25, 30, 35, 40, 50)
T90 = {7: 1.8946, 8: 1.8595, 9: 1.8331}


def load(root: Path, s: int, kind: str, t: int, suffix: str = "") -> np.ndarray | str:
    """kind 'A'/'B': pure EXP-056 run (2000 steps); 'AB'/'BA': switch at t, then 2000 steps."""
    first, second = kind[0], kind[1:] or None
    st1 = A.stem(s, OM, first)
    steps = 2000 + (t if second else 0)
    pat = f"EXP-0*_baseline_seed{s}_thr*_{st1}" + (f"_to_{A.stem(s, OM, second)}_at{t}" if second else "") + suffix + A.SUF
    L = A.load_run(A.find_run(root, pat),
                   A.Expect(seed=s, device=A.DEV, max_steps=steps, split_file=A.SPL / f"{st1}.npy", test_file=A.SPL / f"seed{s}_test.npy",
                            switch_file=A.SPL / f"{A.stem(s, OM, second)}.npy" if second else None,
                            config={"p": 113, "task": "add"}, snapshots_at=(steps,)))
    if L.status != "ok":
        return f"{kind}@{t}{suffix}: {L.status}: {L.reason}"
    if suffix == "_rom" and L.res.get("events", {}).get("reset_optim_part", {}).get("check") is not True:
        return f"{kind}@{t}{suffix}: partial reset not recorded"
    return A._a43.group_power(L.snapshot(steps), "add", 113)[0]


def root_for(t: int) -> Path:
    return E58 / "raw" if t == 25 else HERE / "raw"


def verdict(d: np.ndarray) -> dict:
    """D = pi_rom(35) - pi_normal(25). Prolonged exposure (M2) predicts D >= 0; an optimizer memory beyond exposure (M1) predicts D < 0."""
    if len(d) < MIN_VALID:
        return {"verdict": "nicht auswertbar"}
    tt = A.t_test(-d)                      # one-sided test of mean D < 0
    half = float(d.std(ddof=1) / np.sqrt(len(d)) * T90[len(d) - 1])
    ci90 = [float(d.mean() - half), float(d.mean() + half)]
    if d.mean() < 0 and tt["p_one_sided"] < ALPHA and ci90[1] < -MARGIN:
        v = "mehr als verlängerte Exposition"
    elif ci90[0] > -MARGIN:
        v = "verlängerte Exposition genügt"
    else:
        v = "unklar"
    return {"D_mean": float(d.mean()), "D_sd": float(d.std(ddof=1)), "t_neg": tt["t"], "p_D_below_0": tt["p_one_sided"], "ci90": ci90, "verdict": v}


def t_equiv(y: float, ts: tuple[int, ...], curve: list[float]) -> float:
    """Switch time on the (assumed increasing) mean normal curve with pi = y, linear interpolation; nan outside the measured range."""
    for (t0, y0), (t1, y1) in zip(zip(ts, curve), zip(ts[1:], curve[1:])):
        if min(y0, y1) <= y <= max(y0, y1) and y1 != y0:
            return float(t0 + (y - y0) * (t1 - t0) / (y1 - y0))
    return float("nan")


def main() -> None:
    rows = []
    for s in SEEDS:
        meta = json.loads((A.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        pure = {k: load(E56 / "raw", s, k, 0) for k in ("A", "B")}
        sw = {("n", t, k): load(root_for(t), s, k, t) for t in T_NORMAL for k in ("AB", "BA")}
        sw |= {("m", t, k): load(root_for(t), s, k, t, "_rom") for t in T_ROM for k in ("AB", "BA")}
        bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
        if bad:
            rows.append({"seed": s, "valid": False, "n_bad": len(bad), "reason": "; ".join(bad[:4])})
            continue
        LA, LB = A.logratio(pure["A"], F, G), A.logratio(pure["B"], F, G)
        if not LA - LB >= 2.0:
            rows.append({"seed": s, "valid": False, "reason": "L(A) - L(B) < 2"})
            continue
        r = {"seed": s, "valid": True}
        for arm, ts in (("n", T_NORMAL), ("m", T_ROM)):
            for t in ts:
                L = {"A": LA, "B": LB, "AB": A.logratio(sw[(arm, t, "AB")], F, G), "BA": A.logratio(sw[(arm, t, "BA")], F, G)}
                r[f"pi_{arm}{t}"] = A.pi_of(L)["pi"]
        r["D"] = r["pi_m35"] - r["pi_n25"]
        rows.append(r)
    ok = [r for r in rows if r["valid"]]
    out = {"n_valid": len(ok), **verdict(np.array([r["D"] for r in ok]))}
    if ok:
        cn = [float(np.mean([r[f"pi_n{t}"] for r in ok])) for t in T_NORMAL]
        cm = [float(np.mean([r[f"pi_m{t}"] for r in ok])) for t in T_ROM]
        out["pi_normal_mean"] = dict(zip(map(str, T_NORMAL), cn))
        out["pi_rom_mean"] = dict(zip(map(str, T_ROM), cm))
        out["pi_normal_sd"] = {str(t): float(np.std([r[f"pi_n{t}"] for r in ok], ddof=1)) for t in T_NORMAL}
        out["pi_rom_sd"] = {str(t): float(np.std([r[f"pi_m{t}"] for r in ok], ddof=1)) for t in T_ROM}
        out["delta_shift"] = {str(t): t - t_equiv(y, T_NORMAL, cn) for t, y in zip(T_ROM, cm)}
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert verdict(np.ones(7))["verdict"] == "nicht auswertbar"
    assert verdict(-np.linspace(0.1, 0.3, 10))["verdict"] == "mehr als verlängerte Exposition"
    assert verdict(np.linspace(-0.02, 0.1, 10))["verdict"] == "verlängerte Exposition genügt"
    assert verdict(np.linspace(-0.5, 0.4, 10))["verdict"] == "unklar"
    assert abs(t_equiv(0.25, (10, 20, 30), [0.1, 0.2, 0.3]) - 25.0) < 1e-12
    assert np.isnan(t_equiv(0.5, (10, 20, 30), [0.1, 0.2, 0.3]))
    print("[exp059] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
