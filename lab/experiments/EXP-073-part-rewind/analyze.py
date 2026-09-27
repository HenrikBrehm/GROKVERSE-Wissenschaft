"""EXP-073 (pilot): how sensitive is the time dependence of the lock-in (t = 25 vs 50) to rewinding one part of the network?
Definition: README.md (fixed before any run; revised after the Codex review of session 24, still before any run). pi as EXP-056/059
(pure A/B runs from EXP-056). Run under guarded_run.py.

Arms (switch A->B and B->A, 2000 steps after the switch): ref25 (switch at 25), ref50 (switch at 50), and rw<X> = switch at 50 with part X
(weights + AdamW state) rewound to its state after step 25, X in all / we / attn / vo / rest.
Per seed q_X = (pi_X - pi_25) / (pi_50 - pi_25); reported: median q over seeds and the seed-mean position.
Technical gate (Codex s24: per direction, not averaged): rwall must reproduce ref25 in BOTH directions (|pi_dir(rwall) - pi_dir(ref25)| <= SANITY
for dir in AB, BA, every valid seed), otherwise the pilot is technically void.
Diagnostic (descriptive): loss jump on the new split caused by the rewind itself (diag_after - diag_before, from the trainer event).
Secondary (descriptive, fixed before any run): functional contrast R per arm (EXP-067 function(), see function_R).
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
PARTS, R, T, SANITY, MIN_VALID, MIN_GAP = ("all", "we", "attn", "vo", "rest"), 25, 50, 0.05, 8, 0.2


def arm_pi(s: int, F: list[int], G: list[int], LA: float, LB: float, t: int, part: str | None) -> dict | str:
    suffix = f"_rw{part}{R}" if part else ""
    L, jump = {"A": LA, "B": LB}, []
    for k in ("AB", "BA"):
        v = E59.load(HERE / "raw", s, k, t, suffix)          # loader checks seed, device, steps, split/test/switch hashes, snapshot
        if isinstance(v, str):
            return v
        if part:                                             # the rewind itself must be recorded and self-checked by the trainer
            d = A.find_run(HERE / "raw", f"EXP-0*_baseline_seed{s}_thr*_{A.stem(s, E59.OM, k[0])}_to_{A.stem(s, E59.OM, k[1])}_at{t}{suffix}{A.SUF}")
            ev = json.loads((d / "result.json").read_text(encoding="utf-8")).get("events", {}).get("rewind_at_switch", {})
            if ev.get("check") is not True or ev.get("from_step") != R or ev.get("which") != part:
                return f"{k}{suffix}: rewind not recorded"
            jump.append(ev["diag_after"]["new"][0] - ev["diag_before"]["new"][0])
        L[k] = A.logratio(v, F, G)
    return {**A.pi_of(L), "loss_jump_new": float(np.mean(jump)) if jump else 0.0}


_x67 = None


def function_R(s: int, t: int, part: str | None, F: list[int], G: list[int]) -> float | str:
    """Descriptive secondary (fixed before any run): R = mean over both directions of (acc with the NEW targets removed from W_E
    minus acc with the OLD targets removed), held-out EXP-056 test set, EXP-067 function(); R > 0 = the model relies more on the old choice."""
    global _x67
    if _x67 is None:
        spec = importlib.util.spec_from_file_location("exp067", LAB / "experiments/EXP-067-exclusion-part/analyze.py")
        _x67 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_x67)
    suffix = f"_rw{part}{R}" if part else ""
    test = np.load(A.SPL / f"seed{s}_test.npy")
    vals = []
    for k, old, new in (("AB", F, G), ("BA", G, F)):
        d = A.find_run(HERE / "raw", f"EXP-0*_baseline_seed{s}_thr*_{A.stem(s, E59.OM, k[0])}_to_{A.stem(s, E59.OM, k[1])}_at{t}{suffix}{A.SUF}")
        try:
            f = _x67.function(d, old, new, test) if d is not None else None
        except Exception as ex:                       # descriptive only: a failure is reported, never an abort
            return f"{k}{suffix}: {type(ex).__name__}"
        if f is None:
            return f"{k}{suffix}: model missing"
        vals.append(f["acc_new"] - f["acc_old"])
    return float(np.mean(vals))


def classify(q: dict[str, float]) -> str:
    """Pre-registered readings from the median q of the W_E and rest arms (README); sensitivity labels, not carriers (Codex s24)."""
    we, rest = q["we"], q["rest"]
    lo, hi = 0.3, 0.7
    if we <= lo and rest >= hi:
        return "empfindlich nur für W_E-Rückspulen"
    if rest <= lo and we >= hi:
        return "empfindlich nur für Rest-Rückspulen"
    if we <= lo and rest <= lo:
        return "empfindlich für beide (jedes Rückspulen nimmt die Zusatzfestigkeit)"
    if we >= hi and rest >= hi:
        return "unempfindlich für beide einzeln (jeder Teil allein hält)"
    return "gemischt"


def main() -> None:
    rows = []
    for s in E59.SEEDS:
        meta = json.loads((A.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        pure = {k: E59.load(LAB / "experiments/EXP-056-overlap-persistence/raw", s, k, 0) for k in ("A", "B")}
        if any(isinstance(v, str) for v in pure.values()):
            rows.append({"seed": s, "valid": False, "reason": "pure run missing"})
            continue
        LA, LB = A.logratio(pure["A"], F, G), A.logratio(pure["B"], F, G)
        arms = {"25": arm_pi(s, F, G, LA, LB, R, None), "50": arm_pi(s, F, G, LA, LB, T, None)}
        arms |= {x: arm_pi(s, F, G, LA, LB, T, x) for x in PARTS}
        bad = [v for v in arms.values() if isinstance(v, str)]
        r: dict = {"seed": s}
        if bad:
            rows.append({**r, "valid": False, "reason": "; ".join(bad[:3])})
            continue
        r |= {f"pi_{k}": v["pi"] for k, v in arms.items()} | {f"jump_{x}": arms[x]["loss_jump_new"] for x in PARTS}
        r["sanity"] = max(abs(arms["all"][d] - arms["25"][d]) for d in ("pi_AB", "pi_BA"))
        r["valid"] = LA - LB >= 2.0 and r["pi_50"] - r["pi_25"] >= MIN_GAP
        if not r["valid"]:
            r["reason"] = "L(A) - L(B) < 2 or pi_50 - pi_25 < MIN_GAP"
        else:
            r["q"] = {x: (r[f"pi_{x}"] - r["pi_25"]) / (r["pi_50"] - r["pi_25"]) for x in PARTS}
        rows.append(r)
    ok = [r for r in rows if r["valid"]]
    out: dict = {"n_valid": len(ok)}
    if len(ok) < MIN_VALID:
        out["verdict"] = "nicht auswertbar"
    else:
        out["sanity_max_abs_diff_per_direction"] = float(max(r["sanity"] for r in ok))
        m25, m50 = np.mean([r["pi_25"] for r in ok]), np.mean([r["pi_50"] for r in ok])
        out["pi_mean"] = {k: float(np.mean([r[f"pi_{k}"] for r in ok])) for k in ("25", "50") + PARTS}
        out["q_median"] = {x: float(np.median([r["q"][x] for r in ok])) for x in PARTS}
        out["q_of_means"] = {x: float((out["pi_mean"][x] - m25) / (m50 - m25)) for x in PARTS}
        out["loss_jump_new_median"] = {x: float(np.median([r[f"jump_{x}"] for r in ok])) for x in PARTS}
        out["verdict"] = ("technisch ungültig (rwall != ref25)" if out["sanity_max_abs_diff_per_direction"] > SANITY
                          else classify(out["q_median"]))
        fr = {}                                             # descriptive functional secondary, no verdict
        for r in ok:
            meta = json.loads((A.SPL / f"seed{r['seed']}_w0.json").read_text(encoding="utf-8"))
            F, G = meta["targets"]["A"], meta["targets"]["B"]
            fr[r["seed"]] = {"25": function_R(r["seed"], R, None, F, G), "50": function_R(r["seed"], T, None, F, G)} |                             {x: function_R(r["seed"], T, x, F, G) for x in PARTS}
        good = [v for v in fr.values() if not any(isinstance(x, str) for x in v.values())]
        out["function_R_median"] = {k: float(np.median([v[k] for v in good])) for k in ("25", "50") + PARTS} if good else None
        out["function_n"] = len(good)
        out["function_rows"] = fr
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert classify({"we": 0.1, "rest": 0.9}) == "empfindlich nur für W_E-Rückspulen"
    assert classify({"we": 0.9, "rest": 0.1}) == "empfindlich nur für Rest-Rückspulen"
    assert classify({"we": 0.2, "rest": 0.2}).startswith("empfindlich für beide")
    assert classify({"we": 0.8, "rest": 0.8}).startswith("unempfindlich")
    assert classify({"we": 0.5, "rest": 0.9}) == "gemischt"
    print("[exp073] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
