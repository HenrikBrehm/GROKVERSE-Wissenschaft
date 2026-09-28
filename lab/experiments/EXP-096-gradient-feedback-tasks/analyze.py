"""EXP-096 (pilot, exploration): EXP-095 cells n24 / g8 / g24 in add mod 97 and mul mod 113. Definition, predictions and readings:
README.md (fixed before any EXP-096 run). Run under guarded_run.py with the global python. Session 42, UNTESTED.

pi per seed and cell as EXP-044 pi_persistence: L = log[P(F targets) / P(G targets)] of the final W_E group power (EXP-043 basis),
pi = (L(switch) - L(only G)) / (L(only F) - L(only G)). Valid seed: all 5 runs ok through the shared loader (seed, device, steps,
split/test/switch hashes, p, task; switch runs: recorded gradient schedule), L(F) - L(G) >= 1. Per task, paired over seeds,
95 % percentile bootstrap (10 000, rng 96):  e8 = pi(n24) - pi(g8),  e24 = pi(n24) - pi(g24).
Readings per task (fewer than 10 valid seeds -> 'nicht auswertbar'):
  'verallgemeinert'        e8 and e24 CI lower > 0
  'nicht verallgemeinert'  e8 and e24 CI upper < 0.03
  else 'unklar'.
Descriptive: cell means of pi, target share and norm of the W_E displacement at the switch (group basis of the task), T/R split.
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

_spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
_a43 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_a43)

SPL, RAW, SUF = HERE / "splits", HERE / "raw", "_devcuda"
MIN_VALID, N_BOOT, NULL_HI, MIN_LFLG = 10, 10_000, 0.03, 1.0


def load(task: str, p: int, s: int, kind: str):
    """kind 'F' / 'G' (pure) or a cell name. Returns (final group power, W_E at t, W_E at 0) or an error string."""
    st = D.stem(task, p, s)
    switch = kind in D.CELLS
    k = D.CELLS.get(kind, 1)
    steps = D.BUDGET + (D.T_SWITCH if switch else 0)
    pat = (f"EXP-044_baseline_seed{s}_thr*_{st}_train_F_to_{st}_train_G_at{D.T_SWITCH}_{task}{p}" + (f"_ge{k}" if k != 1 else "") + SUF
           if switch else f"EXP-043_baseline_seed{s}_thr*_{st}_train_{kind}_{task}{p}{SUF}")
    L = load_run(find_run(RAW, pat),
                 Expect(seed=s, device="cuda", max_steps=steps, split_file=SPL / f"{st}_train_{'G' if kind == 'G' else 'F'}.npy",
                        test_file=SPL / f"{st}_test.npy", switch_file=SPL / f"{st}_train_G.npy" if switch else None,
                        config={"p": p, "task": task, "beta1": 0.9, "beta2": 0.98},
                        snapshots_at=(steps,) + ((D.T_SWITCH, 0) if switch else ())))
    tag = f"{task}{p} seed {s} {kind}"
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if switch:
        ev = L.res.get("events", {}).get("pre_switch_grad_every")
        if k != 1 and (L.res.get("pre_switch_grad_every") != k or not ev
                       or ev.get("eval_steps_pre_switch") != list(range(1, D.T_SWITCH + 1, k))):
            return f"{tag}: gradient schedule not recorded as k = {k}"
        if k == 1 and (L.res.get("pre_switch_grad_every", 1) != 1 or ev is not None):
            return f"{tag}: unexpected gradient schedule"
    end = _a43.group_power(L.snapshot(steps), task, p)[0]
    return (end, L.snapshot(D.T_SWITCH), L.snapshot(0)) if switch else (end, None, None)


def seed_row(task: str, p: int, s: int) -> dict:
    meta = json.loads((SPL / f"{D.stem(task, p, s)}.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["F"], meta["targets"]["G"]
    runs = {k: load(task, p, s, k) for k in ("F", "G", *D.CELLS)}
    bad = [v for v in runs.values() if isinstance(v, str)]
    if bad:
        return {"seed": s, "valid": False, "reason": "; ".join(bad[:3])}
    lr = lambda pw: float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))   # noqa: E731
    lf, lg = lr(runs["F"][0]), lr(runs["G"][0])
    if not lf - lg >= MIN_LFLG:
        return {"seed": s, "valid": False, "reason": f"L(F) - L(G) = {lf - lg:.2f} < {MIN_LFLG}"}
    r = {"seed": s, "valid": True}
    for c in D.CELLS:
        end, Wt, W0 = runs[c]
        r[f"pi_{c}"] = (lr(end) - lg) / (lf - lg)
        pw = _a43.group_power(Wt - W0, task, p)[0]
        T = float(pw[[k - 1 for k in F]].sum())
        r[f"T_{c}"], r[f"R_{c}"], r[f"fsel_{c}"] = T, float(pw.sum() - T), T / float(pw.sum())
        r[f"dnorm_{c}"] = float(np.linalg.norm((Wt - W0)[:p]))
    return r


def boot_ci(x: np.ndarray, seed: int = 96) -> list[float]:
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), size=(N_BOOT, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def verdict(pis: dict[str, np.ndarray]) -> dict:
    n = len(pis["n24"])
    if n < MIN_VALID:
        return {"n": n, "verdict": "nicht auswertbar"}
    d = {"e8": pis["n24"] - pis["g8"], "e24": pis["n24"] - pis["g24"]}
    ci = {k: boot_ci(v) for k, v in d.items()}
    if ci["e8"][0] > 0 and ci["e24"][0] > 0:
        v = "verallgemeinert"
    elif ci["e8"][1] < NULL_HI and ci["e24"][1] < NULL_HI:
        v = "nicht verallgemeinert"
    else:
        v = "unklar"
    return {"n": n, "mean": {k: float(x.mean()) for k, x in d.items()}, "ci95": ci,
            "pos": {k: int((x > 0).sum()) for k, x in d.items()}, "verdict": v}


def main() -> None:
    out: dict = {}
    for task, p in D.TASKS:
        rows = [seed_row(task, p, s) for s in D.SEEDS]
        ok = [r for r in rows if r["valid"]]
        col = lambda k: np.array([r[k] for r in ok])   # noqa: E731
        res: dict = {"n_valid": len(ok)}
        if ok:
            res["primary"] = verdict({c: col(f"pi_{c}") for c in D.CELLS})
            res["cell_means"] = {k: {c: float(col(f"{k}_{c}").mean()) for c in D.CELLS} for k in ("pi", "fsel", "dnorm", "T", "R")}
        else:
            res["primary"] = {"verdict": "nicht auswertbar"}
        res["rows"] = rows
        out[f"{task}{p}"] = res
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({t: {k: v for k, v in r.items() if k != "rows"} for t, r in out.items()}, indent=1))


def selftest() -> None:
    j = D.jobs()
    assert len(j) == len(D.SEEDS) * len(D.TASKS) * 5 and len(set(j)) == len(j) and len(D.smoke()) == 3
    assert sum("--pre-switch-grad-every 8" in x for x in j) == sum("--pre-switch-grad-every 24" in x for x in j) == 32
    assert all(D.T_SWITCH % k == 0 for k in D.CELLS.values())
    rng = np.random.default_rng(0)
    nz = lambda: rng.normal(0, 0.02, 16)   # noqa: E731
    base = 0.4 + nz()
    w = lambda e8, e24: {"n24": base, "g8": base - e8 + nz(), "g24": base - e24 + nz()}   # noqa: E731
    assert verdict(w(0.14, 0.19))["verdict"] == "verallgemeinert"
    assert verdict(w(0.0, -0.02))["verdict"] == "nicht verallgemeinert"
    assert verdict(w(0.14, 0.0))["verdict"] == "unklar"
    assert verdict({k: v[:9] for k, v in w(0.1, 0.1).items()})["verdict"] == "nicht auswertbar"
    print("[exp096] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
