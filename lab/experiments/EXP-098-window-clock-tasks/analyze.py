"""EXP-098 (pilot, exploration): R9 cells at Lambda = 25 in add mod 97 and mul mod 113. Definition, predictions and readings:
README.md (fixed before any EXP-098 run). Run under guarded_run.py with the global python. Session 43, UNTESTED.

pi per seed and cell as EXP-044 pi_persistence: L = log[P(F targets) / P(G targets)] of the final W_E group power (EXP-043 basis),
pi = (L(switch) - L(only G)) / (L(only F) - L(only G)). Valid seed: all 5 runs ok through the shared loader (seed, device, steps,
split/test/switch hashes, p, task, lr_scale, pre-switch betas; switch runs: switch_step, recorded beta switch), L(F) - L(G) >= 1.
Per task, paired over seeds, 95 % percentile bootstrap (10 000, rng 98):
  e1 = pi(l100) - pi(l100b)   (Adam windows fixed in steps vs matched in Lambda; R9 H1 at add 113: +0.161)
  d1 = pi(l100b) - pi(n25)    (Lambda clock with matched windows; R9 H2 at add 113: +0.015, equivalence +-0.1)
Readings per task (fewer than 10 valid seeds -> 'nicht auswertbar'), in this order:
  'verallgemeinert'        e1 CI lower > 0 and d1 CI inside [-0.1, +0.1]
  'nur Richtung'           e1 CI lower > 0, d1 CI not inside
  'nicht verallgemeinert'  e1 CI upper < 0.03
  else 'unklar'.
Descriptive: cell means of pi, target share and norm of the W_E displacement at the switch (group basis of the task).
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
MIN_VALID, N_BOOT, NULL_HI, EQ, MIN_LFLG = 10, 10_000, 0.03, 0.1, 1.0


def load(task: str, p: int, s: int, kind: str):
    """kind 'F' / 'G' (pure) or a cell name. Returns (final group power, W_E at t, W_E at 0) or an error string."""
    st = D.stem(task, p, s)
    switch = kind in D.CELLS
    c, t, psb = D.CELLS.get(kind, (1.0, 0, None))
    steps = D.BUDGET + t
    pat = (f"EXP-044_baseline_seed{s}_thr*_{st}_train_F_to_{st}_train_G_at{t}_{task}{p}" + (f"_lrs{c:g}" if c != 1.0 else "")
           + (f"_psb{psb[0]!r}_{psb[1]!r}" if psb else "") + SUF
           if switch else f"EXP-043_baseline_seed{s}_thr*_{st}_train_{kind}_{task}{p}{SUF}")
    L = load_run(find_run(RAW, pat),
                 Expect(seed=s, device="cuda", max_steps=steps, split_file=SPL / f"{st}_train_{'G' if kind == 'G' else 'F'}.npy",
                        test_file=SPL / f"{st}_test.npy", switch_file=SPL / f"{st}_train_G.npy" if switch else None,
                        config={"p": p, "task": task, "beta1": 0.9, "beta2": 0.98, "lr_scale": c,
                                "pre_switch_betas": list(psb) if psb else None},
                        snapshots_at=(steps,) + ((t, 0) if switch else ())))
    tag = f"{task}{p} seed {s} {kind}"
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if switch and (L.res.get("switch_step") != t or int(L.res.get("lr_scale_until", -1)) < t):
        return f"{tag}: switch_step/lr_scale_until do not match the cell"
    if psb and L.res.get("events", {}).get("pre_switch_betas", {}).get("check") is not True:
        return f"{tag}: beta switch not recorded"
    if L.res.get("pre_switch_grad_every", 1) != 1:
        return f"{tag}: unexpected gradient schedule"
    end = _a43.group_power(L.snapshot(steps), task, p)[0]
    return (end, L.snapshot(t), L.snapshot(0)) if switch else (end, None, None)


def seed_row(task: str, p: int, s: int) -> dict:
    meta = json.loads((SPL / f"{D.stem(task, p, s)}.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["F"], meta["targets"]["G"]
    runs = {k: load(task, p, s, k) for k in ("F", "G", *D.CELLS)}
    bad = [v for v in runs.values() if isinstance(v, str)]
    if bad:
        return {"seed": s, "valid": False, "reason": "; ".join(bad)}
    lr = lambda pw: float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))   # noqa: E731
    lf, lg = lr(runs["F"][0]), lr(runs["G"][0])
    if not lf - lg >= MIN_LFLG:
        return {"seed": s, "valid": False, "reason": f"L(F) - L(G) = {lf - lg:.2f} < {MIN_LFLG}"}
    r = {"seed": s, "valid": True}
    for c in D.CELLS:
        end, Wt, W0 = runs[c]
        r[f"pi_{c}"] = (lr(end) - lg) / (lf - lg)
        pw = _a43.group_power(Wt - W0, task, p)[0]
        r[f"fsel_{c}"] = float(pw[[k - 1 for k in F]].sum() / pw.sum())
        r[f"dnorm_{c}"] = float(np.linalg.norm((Wt - W0)[:p]))
    return r


def boot_ci(x: np.ndarray, seed: int = 98) -> list[float]:
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), size=(N_BOOT, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def verdict(pis: dict[str, np.ndarray]) -> dict:
    n = len(pis["n25"])
    if n < MIN_VALID:
        return {"n": n, "verdict": "nicht auswertbar"}
    d = {"e1": pis["l100"] - pis["l100b"], "d1": pis["l100b"] - pis["n25"]}
    ci = {k: boot_ci(v) for k, v in d.items()}
    if ci["e1"][0] > 0:
        v = "verallgemeinert" if -EQ <= ci["d1"][0] and ci["d1"][1] <= EQ else "nur Richtung"
    elif ci["e1"][1] < NULL_HI:
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
            res["cell_means"] = {k: {c: float(col(f"{k}_{c}").mean()) for c in D.CELLS} for k in ("pi", "fsel", "dnorm")}
        else:
            res["primary"] = {"verdict": "nicht auswertbar"}
        res["rows"] = rows
        out[f"{task}{p}"] = res
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({t: {k: v for k, v in r.items() if k != "rows"} for t, r in out.items()}, indent=1))


def selftest() -> None:
    j = D.jobs()
    assert len(j) == len(D.SEEDS) * len(D.TASKS) * 5 and len(set(j)) == len(j) and len(D.smoke()) == 3
    assert sum("--pre-switch-betas 0.975,0.995" in x for x in j) == 32 and sum("--lr-scale 0.25" in x for x in j) == 64
    for c, t, psb in D.CELLS.values():                 # Lambda = 25 in every cell; beta' = 1 - c (1 - beta) where given
        assert c * t == 25 and t <= 250
        if psb:
            assert abs(psb[0] - (1 - c * 0.1)) < 1e-12 and abs(psb[1] - (1 - c * 0.02)) < 1e-12
    rng = np.random.default_rng(0)
    nz = lambda: rng.normal(0, 0.02, 16)   # noqa: E731
    base = 0.35 + nz()
    w = lambda e1, d1: {"n25": base, "l100b": base + d1 + nz(), "l100": base + d1 + e1 + nz()}   # noqa: E731
    assert verdict(w(0.16, 0.01))["verdict"] == "verallgemeinert"
    assert verdict(w(0.16, 0.3))["verdict"] == "nur Richtung"
    assert verdict(w(-0.02, 0.0))["verdict"] == "nicht verallgemeinert"
    wide = {"n25": base, "l100b": base, "l100": base + 0.015 + rng.normal(0, 0.06, 16)}   # CI straddles 0 and 0.03
    assert verdict(wide)["verdict"] == "unklar", verdict(wide)
    assert verdict({k: v[:9] for k, v in w(0.1, 0.0).items()})["verdict"] == "nicht auswertbar"
    print("[exp098] selftest ok", flush=True)


def smoke_check() -> None:
    """Loader status of the three smoke runs only (seed 3660); prints ok/error, no values, writes nothing."""
    bad = 0
    for task, p, kind in (("add", 97, "F"), ("add", 97, "l100b"), ("mul", 113, "l100b")):
        r = load(task, p, D.SEEDS[0], kind)
        bad += isinstance(r, str)
        print(f"[exp098] smoke {task}{p} {kind}: {r if isinstance(r, str) else 'ok'}", flush=True)
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    {"--selftest": selftest, "--smoke-check": smoke_check}.get(sys.argv[1] if sys.argv[1:] else "", main)()
