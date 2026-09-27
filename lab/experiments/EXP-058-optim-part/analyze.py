"""EXP-058 (pilot): which part of the AdamW state carries the persistence after a switch at t = 25? Definition: README.md (registered
before any EXP-058 run). Run under guarded_run.py.

Seeds 400-409, omega = 0 (EXP-056 splits; pure A/B runs reused from EXP-056). New runs here, all with --log-update-norms 10:
A->B and B->A for four arms: normal, ro (full reset, as EXP-057), rom (zero exp_avg only, step kept), romoments (zero both, step kept).
pi as EXP-056. Primary: Delta_m = pi_normal - pi_rom (one-sided t-test). Early update norm = mean total update norm of the first 5 steps
after the switch (both directions averaged), reported per arm.
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
_spec = importlib.util.spec_from_file_location("exp056", E56 / "analyze.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

SEEDS, OM, ALPHA, MIN_VALID, EQ = tuple(range(400, 410)), 0.0, 0.05, 8, 0.1
ARMS = {"normal": "", "ro": "_ro", "rom": "_rom", "romoments": "_romoments"}
T90 = {7: 1.8946, 8: 1.8595, 9: 1.8331}


def load(root: Path, s: int, kind: str, steps: int, suffix: str = "") -> tuple[np.ndarray, list] | str:
    first, second = kind[0], kind[1:] or None
    st1 = A.stem(s, OM, first)
    pat = (f"EXP-0*_baseline_seed{s}_thr*_{st1}" + (f"_to_{A.stem(s, OM, second)}_at{A.T_SWITCH}" if second else "") + suffix + A.SUF)
    L = A.load_run(A.find_run(root, pat),
                   A.Expect(seed=s, device=A.DEV, max_steps=steps, split_file=A.SPL / f"{st1}.npy", test_file=A.SPL / f"seed{s}_test.npy",
                            switch_file=A.SPL / f"{A.stem(s, OM, second)}.npy" if second else None,
                            config={"p": 113, "task": "add"}, snapshots_at=(steps,)))
    if L.status != "ok":
        return f"{kind}{suffix}: {L.status}: {L.reason}"
    ev = L.res.get("events", {})
    if suffix == "_ro" and ev.get("reset_optim_at_switch", {}).get("check") is not True:
        return f"{kind}{suffix}: reset not recorded"
    if suffix in ("_rom", "_romoments") and ev.get("reset_optim_part", {}).get("check") is not True:
        return f"{kind}{suffix}: partial reset not recorded"
    un = ev.get("update_norms", [])
    return A._a43.group_power(L.snapshot(steps), "add", 113)[0], un


def early_norm(un: list) -> float:
    post = [x[1] for x in un if A.T_SWITCH < x[0] <= A.T_SWITCH + 5]
    return float(np.mean(post)) if len(post) == 5 else float("nan")


def verdict(d: np.ndarray) -> dict:
    if len(d) < MIN_VALID:
        return {"verdict": "nicht auswertbar"}
    tt = A.t_test(d)
    half = float(d.std(ddof=1) / np.sqrt(len(d)) * T90[len(d) - 1])
    ci90 = [float(d.mean() - half), float(d.mean() + half)]
    if d.mean() > 0 and tt["p_one_sided"] < ALPHA:
        v = "Momentum (m) trägt einen Teil der Persistenz"
    elif -EQ <= ci90[0] and ci90[1] <= EQ:
        v = "m trägt die Persistenz nicht"
    else:
        v = "unklar"
    return {"delta_m_mean": float(d.mean()), "delta_m_sd": float(d.std(ddof=1)), "t": tt["t"], "p": tt["p_one_sided"], "ci90": ci90, "verdict": v}


def main() -> None:
    rows = []
    for s in SEEDS:
        meta = json.loads((A.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        pure = {k: load(E56 / "raw", s, k, 2000) for k in ("A", "B")}
        sw = {(arm, k): load(HERE / "raw", s, k, 2025, suf) for arm, suf in ARMS.items() for k in ("AB", "BA")}
        bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
        if bad:
            rows.append({"seed": s, "valid": False, "reason": "; ".join(bad[:4])})
            continue
        LA, LB = A.logratio(pure["A"][0], F, G), A.logratio(pure["B"][0], F, G)
        if not LA - LB >= 2.0:
            rows.append({"seed": s, "valid": False, "reason": "L(A) - L(B) < 2"})
            continue
        r = {"seed": s, "valid": True}
        for arm in ARMS:
            L = {"A": LA, "B": LB, "AB": A.logratio(sw[(arm, "AB")][0], F, G), "BA": A.logratio(sw[(arm, "BA")][0], F, G)}
            r[f"pi_{arm}"] = A.pi_of(L)["pi"]
            r[f"early_norm_{arm}"] = (early_norm(sw[(arm, "AB")][1]) + early_norm(sw[(arm, "BA")][1])) / 2
        r["delta_m"] = r["pi_normal"] - r["pi_rom"]
        rows.append(r)
    ok = [r for r in rows if r["valid"]]
    out = {"n_valid": len(ok), **verdict(np.array([r["delta_m"] for r in ok])),
           "pi_mean": {arm: float(np.mean([r[f"pi_{arm}"] for r in ok])) for arm in ARMS} if ok else None,
           "early_update_norm_mean": {arm: float(np.mean([r[f"early_norm_{arm}"] for r in ok])) for arm in ARMS} if ok else None,
           "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert verdict(np.ones(7))["verdict"] == "nicht auswertbar"
    assert verdict(np.linspace(0.1, 0.3, 10))["verdict"].startswith("Momentum")
    assert verdict(np.linspace(-0.03, 0.03, 10))["verdict"] == "m trägt die Persistenz nicht"
    assert verdict(np.linspace(-0.5, 0.5, 10))["verdict"] == "unklar"
    un = [[s, 1.0 + s, 0.1] for s in range(21, 36)]
    assert abs(early_norm(un) - np.mean([1.0 + s for s in range(26, 31)])) < 1e-12
    print("[exp058] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
