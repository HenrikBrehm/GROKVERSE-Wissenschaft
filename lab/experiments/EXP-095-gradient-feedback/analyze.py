"""EXP-095 (pilot, exploration): fewer gradient evaluations at the same 24 Adam steps. Definition, predictions and readings:
README.md (fixed before any EXP-095 run). Run under guarded_run.py with the global python.

pi, validity, loading and displacement selectivity as EXP-092/094 (functions imported from EXP-092's analyze.py, pointed at this
experiment's design; the run lookup additionally knows the '_ge{k}' suffix and checks the recorded gradient schedule).
Paired over seeds, 95 % percentile bootstrap (10 000, rng 95):
  e4, e8, e24 = pi(n24) - pi(gk)     (deficit from sampling the gradient only every k steps, same Adam steps)
  d8 = pi(n24) - pi(c8b)             (deficit of 3 large steps with matched windows; replication of EXP-094, +0.174)
  r8 = pi(g8) - pi(c8b)              (same 3 evaluations: coarse Adam step on top of coarse sampling)
Readings (in this order):
  'nicht trennbar'           d8 CI lower <= 0.03 (the EXP-094 deficit does not replicate)
  'Auswertungen zaehlen'     e8 CI lower > 0.03 and mean e8 >= 0.5 mean d8
  'Adam-Schritt'             e8 CI inside [-0.05, +0.05]
  else 'teilweise'. Fewer than 10 valid seeds -> 'nicht auswertbar'.
Secondary (descriptive): e4, e24, r8, order of e4 <= e8 <= e24, cell means of pi, selectivity f and norm N at the switch;
prospective check of the post hoc line pi = -1.389 + 9.428 f (EXP-093 posthoc_state_s41.json): MAE over the five cell means.
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
E.D, E.SPL, E.RAW = D, HERE / "splits", HERE / "raw"

MIN_VALID, N_BOOT, HI, EQ = 10, 10_000, 0.03, 0.05
LINE = (-1.3894541968592156, 9.428517843120291)      # pi on f, EXP-092/093 cell means (post hoc, session 41)


def load(s: int, kind: str, cell: str | None = None):
    """As EXP-092 load, plus the gradient schedule: run id suffix '_ge{k}', recorded k and pre-switch evaluation steps."""
    first, second = kind[0], kind[1:] or None
    c, t, psb, k = D.CELLS[cell] if cell else (1.0, 0, None, 1)
    steps = D.BUDGET + (t if second else 0)
    pat = (f"EXP-0*_baseline_seed{s}_thr*_{D.stem(s, first)}" + (f"_to_{D.stem(s, second)}_at{t}" if second else "")
           + (f"_lrs{c:g}" if c != 1.0 else "") + (f"_psb{psb[0]!r}_{psb[1]!r}" if psb else "") + (f"_ge{k}" if k != 1 else "")
           + E.SUF)
    L = load_run(find_run(E.RAW, pat),
                 Expect(seed=s, device="cuda", max_steps=steps, split_file=E.SPL / f"{D.stem(s, first)}.npy",
                        test_file=E.SPL / f"seed{s}_test.npy", switch_file=E.SPL / f"{D.stem(s, second)}.npy" if second else None,
                        config={"p": 113, "task": "add", "lr_scale": c, "pre_switch_betas": list(psb) if psb else None,
                                "beta1": 0.9, "beta2": 0.98},
                        snapshots_at=(steps,) + ((t, 0) if second else ())))
    tag = f"{cell or 'pure'}:{kind}"
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if psb and L.res.get("events", {}).get("pre_switch_betas", {}).get("check") is not True:
        return f"{tag}: beta switch not recorded"
    if k != 1:
        ev = L.res.get("events", {}).get("pre_switch_grad_every", {})
        if (L.res.get("pre_switch_grad_every") != k or ev.get("k") != k
                or ev.get("eval_steps_pre_switch") != list(range(1, t + 1, k))):
            return f"{tag}: gradient schedule not recorded as k = {k}"
    end = E.A._a43.group_power(L.snapshot(steps), "add", 113)[0]
    return (end, L.snapshot(t), L.snapshot(0)) if second else (end, None, None)


E.load = load        # seed_row looks load up in its module at call time


def boot_ci(x: np.ndarray, seed: int = 95) -> list[float]:
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), size=(N_BOOT, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def verdict(pis: dict[str, np.ndarray]) -> dict:
    n = len(pis["n24"])
    if n < MIN_VALID:
        return {"n": n, "verdict": "nicht auswertbar"}
    d = {f"e{k}": pis["n24"] - pis[f"g{k}"] for k in (4, 8, 24)}
    d["d8"] = pis["n24"] - pis["c8b"]
    d["r8"] = pis["g8"] - pis["c8b"]
    ci = {k: boot_ci(v) for k, v in d.items()}
    if ci["d8"][0] <= HI:
        v = "nicht trennbar"
    elif ci["e8"][0] > HI and d["e8"].mean() >= 0.5 * d["d8"].mean():
        v = "Auswertungen zaehlen"
    elif -EQ <= ci["e8"][0] and ci["e8"][1] <= EQ:
        v = "Adam-Schritt"
    else:
        v = "teilweise"
    m = {k: float(x.mean()) for k, x in d.items()}
    return {"n": n, "mean": m, "ci95": ci, "pos": {k: int((x > 0).sum()) for k, x in d.items()},
            "order_e4_e8_e24": bool(m["e4"] <= m["e8"] <= m["e24"]), "verdict": v}


def main() -> None:
    rows = [E.seed_row(s) for s in D.SEEDS]
    ok = [r for r in rows if r["valid"]]
    col = lambda k: np.array([r[k] for r in ok])   # noqa: E731
    out: dict = {"n_valid": len(ok)}
    if ok:
        pis = {c: col(f"pi_{c}") for c in D.CELLS}
        out["primary"] = verdict(pis)
        f = {c: float(col(f"fsel_{c}").mean()) for c in D.CELLS}
        pm = {c: float(p.mean()) for c, p in pis.items()}
        out["secondary"] = {"pi_means": pm, "fsel_means": f, "dnorm_means": {c: float(col(f"dnorm_{c}").mean()) for c in D.CELLS},
                            "line_pred": {c: LINE[0] + LINE[1] * f[c] for c in D.CELLS},
                            "line_mae": float(np.mean([abs(LINE[0] + LINE[1] * f[c] - pm[c]) for c in D.CELLS]))}
    else:
        out["primary"] = {"verdict": "nicht auswertbar"}
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert len(D.jobs()) == len(D.SEEDS) * 12 and len(D.smoke()) == 3 and E.D is D and E.load is load
    assert all("--pre-switch-grad-every 24" in x and "--switch-step 24" in x for x in D.smoke()[1:])
    assert sum("--pre-switch-grad-every" in x for x in D.jobs()) == len(D.SEEDS) * 6
    for c, (cc, t, psb, k) in D.CELLS.items():
        assert cc * t == 24 and t % k == 0
        if psb:
            assert abs((1 - psb[0]) - cc * 0.1) < 1e-12 and abs((1 - psb[1]) - cc * 0.02) < 1e-12
    rng = np.random.default_rng(0)
    nz = lambda: rng.normal(0, 0.02, 16)   # noqa: E731
    base = 0.33 + nz()
    w = lambda e4, e8, e24, d8: {"n24": base, "g4": base - e4 + nz(), "g8": base - e8 + nz(), "g24": base - e24 + nz(),   # noqa: E731
                                 "c8b": base - d8 + nz()}
    assert verdict(w(0.05, 0.15, 0.25, 0.17))["verdict"] == "Auswertungen zaehlen"
    assert verdict(w(0.0, 0.0, 0.02, 0.17))["verdict"] == "Adam-Schritt"
    assert verdict(w(0.0, 0.06, 0.1, 0.17))["verdict"] == "teilweise"
    assert verdict(w(0.05, 0.15, 0.25, 0.0))["verdict"] == "nicht trennbar"
    assert verdict({k: v[:9] for k, v in w(0, 0, 0, 0.17).items()})["verdict"] == "nicht auswertbar"
    print("[exp095] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
