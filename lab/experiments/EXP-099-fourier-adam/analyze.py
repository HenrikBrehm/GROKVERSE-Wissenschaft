"""EXP-099 (pilot, exploration; N49): token-basis vs Fourier-coordinate AdamW for W_E[:p]. Definition, competing predictions and
readings: README.md (fixed before any EXP-099 run). Run under guarded_run.py with the global python. Session 43, UNTESTED.

Per seed (technically ok = all 12 runs ok through the shared loader: seed, device, steps, split/test/switch hashes, p/task, betas;
Fourier runs: we_fourier_adam recorded and max_coord_dev < 1e-3; switch runs: switch_step and gradient schedule):
  f(cell)  target share of the group power of W_E(24) - W_E(0) on the first split's targets, both directions averaged (EXP-092)
  S(par)   steering of the pure runs: L(A) - L(B), L = log[P(A targets) / P(B targets)] of the final W_E group power (EXP-056)
  pi(cell) persistence against the pure runs of the SAME parametrisation (EXP-056 pi_of), only for seeds with S >= 2 in both
Paired over technically ok seeds, 95 % percentile bootstrap (10 000, rng 99):
  Q1 (primary, early selectivity): df = f(n24F) - f(n24)
     'V1 (Streuung)'        CI lower > 0      'V2 (Angleichung)'   CI upper < 0      else 'unentschieden'
  Q2 (steering): dS = S(four) - S(tok)
     'Steuerung staerker'   CI lower > 0      'Steuerung schwaecher' CI upper < 0    else 'unentschieden'
  Fewer than 10 technically ok seeds -> both 'nicht auswertbar'.
Descriptive: dpi = pi(n24F) - pi(n24); e24 = pi(n24) - pi(g24) and e24F = pi(n24F) - pi(g24F); f(g24), f(g24F); number of seeds
with S < 2 per parametrisation.
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
sys.path.insert(0, str(HERE))
from result_loader import Expect, find_run, load_run  # noqa: E402
import design as D  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp092", LAB / "experiments/EXP-092-momentum-lag-clock/analyze.py")
E = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(E)

SPL, RAW, SUF = HERE / "splits", HERE / "raw", "_devcuda"
MIN_VALID, N_BOOT, MIN_S, MAX_DEV = 10, 10_000, 2.0, 1e-3


def load(s: int, kind: str, cell: str | None = None, four: bool = False):
    """kind 'A'/'B' (pure; four selects the parametrisation) or 'AB'/'BA' with a cell. Returns (end power, W_t, W_0) or str."""
    first, second = kind[0], kind[1:] or None
    k, four = D.CELLS[cell] if cell else (1, four)
    t = D.T_SW if second else 0
    steps = D.BUDGET + t
    pat = (f"EXP-0*_baseline_seed{s}_thr*_{D.stem(s, first)}" + (f"_to_{D.stem(s, second)}_at{t}" if second else "")
           + (f"_ge{k}" if k != 1 else "") + ("_wef" if four else "") + SUF)
    L = load_run(find_run(RAW, pat),
                 Expect(seed=s, device="cuda", max_steps=steps, split_file=SPL / f"{D.stem(s, first)}.npy",
                        test_file=SPL / f"seed{s}_test.npy", switch_file=SPL / f"{D.stem(s, second)}.npy" if second else None,
                        config={"p": 113, "task": "add", "beta1": 0.9, "beta2": 0.98, "lr_scale": 1.0, "pre_switch_betas": None},
                        snapshots_at=(steps,) + ((t, 0) if second else ())))
    tag = f"{cell or 'pure'}{'F' if four and not cell else ''}:{kind}"
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    ev = L.res.get("events", {})
    if bool(L.res.get("we_fourier_adam", False)) != four:
        return f"{tag}: we_fourier_adam not recorded as {four}"
    if four and not (ev.get("we_fourier_adam", {}).get("max_coord_dev", np.inf) < MAX_DEV):
        return f"{tag}: W_E and its DFT coordinates diverged"
    if second and L.res.get("switch_step") != t:
        return f"{tag}: switch_step {L.res.get('switch_step')!r} != {t}"
    if k != 1:
        g = ev.get("pre_switch_grad_every", {})
        if L.res.get("pre_switch_grad_every") != k or g.get("eval_steps_pre_switch") != list(range(1, t + 1, k)):
            return f"{tag}: gradient schedule not recorded as k = {k}"
    end = E.A._a43.group_power(L.snapshot(steps), "add", 113)[0]
    return (end, L.snapshot(t), L.snapshot(0)) if second else (end, None, None)


def seed_row(s: int) -> dict:
    meta = json.loads((SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    pure = {(x, four): load(s, x, None, four) for x in "AB" for four in (False, True)}
    sw = {(c, k): load(s, k, c) for c in D.CELLS for k in ("AB", "BA")}
    bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
    if bad:
        return {"seed": s, "ok": False, "reason": "; ".join(bad)}
    lr = lambda pw: E.A.logratio(pw, F, G)   # noqa: E731
    r: dict = {"seed": s, "ok": True}
    L = {four: {"A": lr(pure[("A", four)][0]), "B": lr(pure[("B", four)][0])} for four in (False, True)}
    r["S_tok"], r["S_four"] = L[False]["A"] - L[False]["B"], L[True]["A"] - L[True]["B"]
    for c, (_k, four) in D.CELLS.items():
        fa, _ = E.selectivity(*sw[(c, "AB")][1:], F)
        fb, _ = E.selectivity(*sw[(c, "BA")][1:], G)
        r[f"f_{c}"] = (fa + fb) / 2
        LL = {**L[four], "AB": lr(sw[(c, "AB")][0]), "BA": lr(sw[(c, "BA")][0])}
        r[f"pi_{c}"] = E.A.pi_of(LL)["pi"]
    r["pi_valid"] = bool(r["S_tok"] >= MIN_S and r["S_four"] >= MIN_S)
    return r


def boot_ci(x: np.ndarray, seed: int = 99) -> list[float]:
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), size=(N_BOOT, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def reading(ci: list[float], pos: str, neg: str) -> str:
    return pos if ci[0] > 0 else neg if ci[1] < 0 else "unentschieden"


def verdict(rows: list[dict]) -> dict:
    ok = [r for r in rows if r.get("ok")]
    if len(ok) < MIN_VALID:
        return {"n": len(ok), "Q1": "nicht auswertbar", "Q2": "nicht auswertbar"}
    col = lambda k, rs=ok: np.array([r[k] for r in rs])   # noqa: E731
    df, dS = col("f_n24F") - col("f_n24"), col("S_four") - col("S_tok")
    ci = {"df": boot_ci(df), "dS": boot_ci(dS)}
    out = {"n": len(ok), "mean": {"df": float(df.mean()), "dS": float(dS.mean())}, "ci95": ci,
           "pos": {"df": int((df > 0).sum()), "dS": int((dS > 0).sum())},
           "Q1": reading(ci["df"], "V1 (Streuung)", "V2 (Angleichung)"),
           "Q2": reading(ci["dS"], "Steuerung staerker", "Steuerung schwaecher"),
           "f_means": {c: float(col(f"f_{c}").mean()) for c in D.CELLS},
           "S_means": {"tok": float(col("S_tok").mean()), "four": float(col("S_four").mean())},
           "n_S_below_2": {"tok": int((col("S_tok") < MIN_S).sum()), "four": int((col("S_four") < MIN_S).sum())}}
    pv = [r for r in ok if r["pi_valid"]]
    if pv:
        p = {c: col(f"pi_{c}", pv) for c in D.CELLS}
        out["pi_descriptive"] = {"n": len(pv), "means": {c: float(v.mean()) for c, v in p.items()},
                                 "dpi_n24": float((p["n24F"] - p["n24"]).mean()),
                                 "e24_tok": float((p["n24"] - p["g24"]).mean()), "e24_four": float((p["n24F"] - p["g24F"]).mean())}
    return out


def main() -> None:
    rows = [seed_row(s) for s in D.SEEDS]
    out = {"primary": verdict(rows), "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def smoke_check() -> None:
    """Loader status of the three smoke runs only (seed 3680); no values, writes nothing."""
    s = D.SEEDS[0]
    got = [load(s, "A", None, True), load(s, "AB", "n24F"), load(s, "BA", "n24F")]
    bad = [g for g in got if isinstance(g, str)]
    print(f"[exp099] smoke-check: {3 - len(bad)}/3 loaded" + ("" if not bad else " | " + " | ".join(bad)), flush=True)
    if bad:
        raise SystemExit(1)


def selftest() -> None:
    j = D.jobs()
    assert len(j) == len(D.SEEDS) * 12 and len(set(j)) == len(j) and len(D.smoke()) == 3 and E.A is not None
    assert sum(x.endswith("--we-fourier-adam") for x in j) == len(D.SEEDS) * 6
    assert all("--we-fourier-adam" in x for x in D.smoke())
    rng = np.random.default_rng(0)
    mk = lambda df, dS, i: {"seed": i, "ok": True, "pi_valid": True, "S_tok": 5.0 + rng.normal(0, 0.3), "S_four": 5.0 + dS + rng.normal(0, 0.3),   # noqa: E731
                            "f_n24": 0.18 + rng.normal(0, 0.01), "f_n24F": 0.18 + df + rng.normal(0, 0.01),
                            **{f"f_{c}": 0.15 for c in ("g24", "g24F")}, **{f"pi_{c}": 0.3 for c in D.CELLS}}
    assert verdict([mk(0.05, 0.0, i) for i in range(16)])["Q1"] == "V1 (Streuung)"
    v = verdict([mk(-0.05, -1.0, i) for i in range(16)])
    assert v["Q1"] == "V2 (Angleichung)" and v["Q2"] == "Steuerung schwaecher", v
    assert verdict([mk(0.0, 1.0, i) for i in range(16)])["Q2"] == "Steuerung staerker"
    v = verdict([mk(0.05, 0.0, i) for i in range(9)] + [{"seed": 99, "ok": False}] * 7)
    assert v["Q1"] == v["Q2"] == "nicht auswertbar", v
    print("[exp099] selftest ok", flush=True)


if __name__ == "__main__":
    {"--selftest": selftest, "--smoke-check": smoke_check}.get(sys.argv[1] if sys.argv[1:] else "", main)()
