"""EXP-057 (pilot): does the persistence after a switch at t = 25 (P3, EXP-056) live in the AdamW state or in the weights?
Definition: README.md (registered before any EXP-057 run). Run under guarded_run.py.

Seeds 400-409, omega = 0 (EXP-056 splits). Reused from EXP-056 (bound by its loader): only-A, only-B (2000), A->B, B->A (25 + 2000).
New here (lab/experiments/EXP-057-optim-reset/raw): A->B and B->A with --reset-optim-at-switch (AdamW state of all parameters cleared at
step 25, weights kept), and only-A / only-B with 2025 steps (same-length references, descriptive).
pi as EXP-056 (normalised between the 2000-step pure runs). Primary: Delta_s = pi_normal - pi_ro; one-sided t-test Delta > 0.
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

SEEDS, OM, ALPHA, MIN_VALID, EQ, RO_LOW = tuple(range(400, 410)), 0.0, 0.05, 8, 0.1, 0.1
T90 = {7: 1.8946, 8: 1.8595, 9: 1.8331}


def power(root: Path, s: int, kind: str, steps: int, ro: bool = False) -> np.ndarray | str:
    first, second = kind[0], kind[1:] or None
    st1 = A.stem(s, OM, first)
    pat = (f"EXP-0*_baseline_seed{s}_thr*_{st1}" + (f"_to_{A.stem(s, OM, second)}_at{A.T_SWITCH}" if second else "")
           + ("_ro" if ro else "") + A.SUF)
    L = A.load_run(A.find_run(root, pat),
                   A.Expect(seed=s, device=A.DEV, max_steps=steps, split_file=A.SPL / f"{st1}.npy", test_file=A.SPL / f"seed{s}_test.npy",
                            switch_file=A.SPL / f"{A.stem(s, OM, second)}.npy" if second else None,
                            config={"p": 113, "task": "add"}, snapshots_at=(steps,)))
    if L.status != "ok":
        return f"{kind}{'_ro' if ro else ''}@{steps}: {L.status}: {L.reason}"
    if ro and not (L.res.get("events", {}).get("reset_optim_at_switch", {}).get("check") is True):
        return f"{kind}_ro: reset not recorded"
    return A._a43.group_power(L.snapshot(steps), "add", 113)[0]


def share(pw: np.ndarray, T: list[int]) -> float:
    return float(pw[[k - 1 for k in T]].sum() / pw.sum())


def verdict(d: np.ndarray, pi_ro_mean: float) -> dict:
    if len(d) < MIN_VALID:
        return {"verdict": "nicht auswertbar"}
    tt = A.t_test(d)
    half = float(d.std(ddof=1) / np.sqrt(len(d)) * T90[len(d) - 1])
    ci90 = [float(d.mean() - half), float(d.mean() + half)]
    sig = d.mean() > 0 and tt["p_one_sided"] < ALPHA
    if sig and pi_ro_mean <= RO_LOW:
        v = "Optimiererzustand trägt die Persistenz"
    elif sig:
        v = "teilweise: Optimiererzustand trägt einen Teil, Gewichte den Rest"
    elif -EQ <= ci90[0] and ci90[1] <= EQ:
        v = "Gewichte tragen die Persistenz (Optimiererzustand unwesentlich)"
    else:
        v = "unklar"
    return {"delta_mean": float(d.mean()), "delta_sd": float(d.std(ddof=1)), "t": tt["t"], "p": tt["p_one_sided"], "ci90": ci90,
            "pi_ro_mean": pi_ro_mean, "verdict": v}


def main() -> None:
    rows = []
    for s in SEEDS:
        meta = json.loads((A.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        pw = {"A": power(E56 / "raw", s, "A", 2000), "B": power(E56 / "raw", s, "B", 2000),
              "AB": power(E56 / "raw", s, "AB", 2025), "BA": power(E56 / "raw", s, "BA", 2025),
              "ABro": power(HERE / "raw", s, "AB", 2025, True), "BAro": power(HERE / "raw", s, "BA", 2025, True),
              "A2025": power(HERE / "raw", s, "A", 2025), "B2025": power(HERE / "raw", s, "B", 2025)}
        bad = [v for v in pw.values() if isinstance(v, str)]
        if bad:
            rows.append({"seed": s, "valid": False, "reason": "; ".join(bad)})
            continue
        L = {k: A.logratio(v, F, G) for k, v in pw.items()}
        if not L["A"] - L["B"] >= 2.0:
            rows.append({"seed": s, "valid": False, "reason": "L(A) - L(B) < 2", "L": L})
            continue
        pn = A.pi_of({k: L[k] for k in ("A", "B", "AB", "BA")})["pi"]
        pr = A.pi_of({"A": L["A"], "B": L["B"], "AB": L["ABro"], "BA": L["BAro"]})["pi"]
        pl = A.pi_of({"A": L["A2025"], "B": L["B2025"], "AB": L["AB"], "BA": L["BA"]})["pi"]
        first_share_ro = (share(pw["ABro"], F) + share(pw["BAro"], G)) / 2
        rows.append({"seed": s, "valid": True, "L": L, "pi_normal": pn, "pi_ro": pr, "pi_normal_samelength": pl,
                     "first_target_share_ro": first_share_ro, "delta": pn - pr})
    ok = [r for r in rows if r["valid"]]
    d = np.array([r["delta"] for r in ok])
    out = {"n_valid": len(ok), **verdict(d, float(np.mean([r["pi_ro"] for r in ok])) if ok else float("nan")),
           "pi_normal_mean": float(np.mean([r["pi_normal"] for r in ok])) if ok else None,
           "pi_normal_samelength_mean": float(np.mean([r["pi_normal_samelength"] for r in ok])) if ok else None,
           "first_target_share_ro_mean": float(np.mean([r["first_target_share_ro"] for r in ok])) if ok else None,
           "chance_share": 5 / 56, "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert verdict(np.ones(7), 0.0)["verdict"] == "nicht auswertbar"
    assert verdict(np.linspace(0.2, 0.4, 10), 0.05)["verdict"] == "Optimiererzustand trägt die Persistenz"
    assert verdict(np.linspace(0.1, 0.2, 10), 0.2)["verdict"].startswith("teilweise")
    assert verdict(np.linspace(-0.03, 0.03, 10), 0.3)["verdict"].startswith("Gewichte")
    assert verdict(np.linspace(-0.5, 0.5, 10), 0.3)["verdict"] == "unklar"
    print("[exp057] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
