"""EXP-075 (pilot): does the early lock-in (pi(t)) also happen in the shared-embedding MLP (no attention)? Definition: README.md (fixed
before any run). Protocol of EXP-059 (seeds 400-409, EXP-056 splits omega = 0, both directions, 2000 steps after the switch) with --arch mlp;
pure A/B references also with --arch mlp. pi as EXP-056/059. Run under guarded_run.py (imports torch via the shared loader).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
_spec = importlib.util.spec_from_file_location("exp059", LAB / "experiments/EXP-059-momentum-exposure/analyze.py")
E59 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E59)
A = E59.A
TS, MIN_VALID = (10, 25, 50, 100, 200), 8
T_HALF_TRANSFORMER = 33.28         # EXP-059 summary pi_normal_mean (0.387 at 30, 0.559 at 35), linear interpolation; seen before this definition


def load(s: int, kind: str, t: int) -> np.ndarray | str:
    """As EXP-059 load, but the runs carry the '_mlp' suffix and config.arch must be 'mlp'."""
    first, second = kind[0], kind[1:] or None
    st1 = A.stem(s, E59.OM, first)
    steps = 2000 + (t if second else 0)
    pat = f"EXP-0*_baseline_seed{s}_thr*_{st1}" + (f"_to_{A.stem(s, E59.OM, second)}_at{t}" if second else "") + "_mlp" + A.SUF
    L = A.load_run(A.find_run(HERE / "raw", pat),
                   A.Expect(seed=s, device=A.DEV, max_steps=steps, split_file=A.SPL / f"{st1}.npy", test_file=A.SPL / f"seed{s}_test.npy",
                            switch_file=A.SPL / f"{A.stem(s, E59.OM, second)}.npy" if second else None,
                            config={"p": 113, "task": "add", "arch": "mlp"}, snapshots_at=(steps,)))
    if L.status != "ok":
        return f"{kind}@{t}: {L.status}: {L.reason}"
    return A._a43.group_power(L.snapshot(steps), "add", 113)[0]


def t_half(curve: list[float]) -> float:
    """First switch time at which the mean pi curve reaches 0.5 (linear interpolation); inf if never within TS."""
    return E59.t_equiv(0.5, TS, curve) if max(curve) >= 0.5 and curve[0] < 0.5 else (float(TS[0]) if curve[0] >= 0.5 else float("inf"))


def reading(th: float, pi200: float) -> str:
    """Pre-registered (README)."""
    if th <= 2 * T_HALF_TRANSFORMER:
        return "ähnlich früh wie im Transformer"
    if th > 4 * T_HALF_TRANSFORMER or pi200 < 0.5:
        return "deutlich später oder keine Festlegung im Messbereich"
    return "unklar"


def main() -> None:
    rows = []
    for s in E59.SEEDS:
        meta = json.loads((A.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        pure = {k: load(s, k, 0) for k in ("A", "B")}
        sw = {(t, k): load(s, k, t) for t in TS for k in ("AB", "BA")}
        bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
        if bad:
            rows.append({"seed": s, "valid": False, "reason": "; ".join(bad[:3])})
            continue
        LA, LB = A.logratio(pure["A"], F, G), A.logratio(pure["B"], F, G)
        if not LA - LB >= 2.0:
            rows.append({"seed": s, "valid": False, "reason": "L(A) - L(B) < 2", "sep": LA - LB})
            continue
        r = {"seed": s, "valid": True, "sep": LA - LB}
        for t in TS:
            r[f"pi_{t}"] = A.pi_of({"A": LA, "B": LB, "AB": A.logratio(sw[(t, "AB")], F, G), "BA": A.logratio(sw[(t, "BA")], F, G)})["pi"]
        rows.append(r)
    ok = [r for r in rows if r["valid"]]
    out: dict = {"n_valid": len(ok), "t_half_transformer_ref": T_HALF_TRANSFORMER}
    if len(ok) >= MIN_VALID:
        curve = [float(np.mean([r[f"pi_{t}"] for r in ok])) for t in TS]
        out |= {"pi_mean": dict(zip(map(str, TS), curve)), "pi_sd": {str(t): float(np.std([r[f"pi_{t}"] for r in ok], ddof=1)) for t in TS},
                "t_half": t_half(curve)}
        out["reading"] = reading(out["t_half"], curve[-1])
    else:
        out["reading"] = "nicht auswertbar"
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert abs(t_half([0.1, 0.3, 0.7, 0.9, 1.0]) - 37.5) < 1e-9
    assert t_half([0.0, 0.1, 0.2, 0.3, 0.4]) == float("inf") and t_half([0.6, 0.7, 0.8, 0.9, 1.0]) == 10.0
    assert reading(40.0, 1.0).startswith("ähnlich") and reading(float("inf"), 0.3).startswith("deutlich") and reading(100.0, 0.9) == "unklar"
    print("[exp075] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
