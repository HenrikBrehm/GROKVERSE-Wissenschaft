"""EXP-090 (pilot, exploration): EMA windows in Lambda vs. extra lock-in of small steps. Definition and readings: README.md
(fixed before any EXP-090 run). Run under guarded_run.py with the global python.

pi as EXP-056/089 against the pure (standard) A/B runs of the seed. Validity per seed: all 14 runs ok through the shared
loader (lr_scale and pre_switch_betas as recorded; beta switch event check true), L(A) - L(B) >= 2.
Primary: e = pi(l100) - pi(l100b) and d_b = pi(l100b) - pi(n25), paired; 95 % percentile bootstrap CIs (10 000, rng 90).
  'H-beta gestuetzt'        e CI lower > 0 and d_b CI inside [-0.1, +0.1]
  'Fenster erklaeren Teil'  e CI lower > 0 and d_b CI lower > 0
  'Fenster erklaeren nichts' e CI inside [-0.1, +0.1]
  else 'unklar'. Fewer than 10 valid seeds -> 'nicht auswertbar'.
Secondary (descriptive): d100 = pi(l100) - pi(n25) (replication of EXP-089), f1 = pi(l100) - pi(l100b1) (first-moment window
alone), t_eq of the cell means on the standard curve 25/33/45, separation at the switch from the W_E snapshot at t.
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

_spec = importlib.util.spec_from_file_location("exp056", LAB / "experiments/EXP-056-overlap-persistence/analyze.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

SPL, RAW, SUF = HERE / "splits", HERE / "raw", "_devcuda"
MIN_VALID, N_BOOT = 10, 10_000
STD_T = (25, 33, 45)


def load(s: int, kind: str, cell: str | None = None) -> tuple[np.ndarray, np.ndarray | None] | str:
    """Returns (group power at the end, group power at the switch or None)."""
    first, second = kind[0], kind[1:] or None
    c, t, psb = D.CELLS[cell] if cell else (1.0, 0, None)
    steps = D.BUDGET + (t if second else 0)
    pat = (f"EXP-0*_baseline_seed{s}_thr*_{D.stem(s, first)}" + (f"_to_{D.stem(s, second)}_at{t}" if second else "")
           + (f"_lrs{c:g}" if c != 1.0 else "") + (f"_psb{psb[0]!r}_{psb[1]!r}" if psb else "") + SUF)
    L = load_run(find_run(RAW, pat),
                 Expect(seed=s, device="cuda", max_steps=steps, split_file=SPL / f"{D.stem(s, first)}.npy", test_file=SPL / f"seed{s}_test.npy",
                        switch_file=SPL / f"{D.stem(s, second)}.npy" if second else None,
                        config={"p": 113, "task": "add", "lr_scale": c, "pre_switch_betas": list(psb) if psb else None,
                                "beta1": 0.9, "beta2": 0.98},
                        snapshots_at=(steps,) + ((t,) if second else ())))
    tag = f"{cell or 'pure'}:{kind}"
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if psb and L.res.get("events", {}).get("pre_switch_betas", {}).get("check") is not True:
        return f"{tag}: beta switch not recorded"
    gp = lambda st: A._a43.group_power(L.snapshot(st), "add", 113)[0]   # noqa: E731
    return gp(steps), (gp(t) if second else None)


def seed_row(s: int) -> dict:
    meta = json.loads((SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    pure = {k: load(s, k) for k in ("A", "B")}
    sw = {(cell, k): load(s, k, cell) for cell in D.CELLS for k in ("AB", "BA")}
    bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
    if bad:
        return {"seed": s, "valid": False, "n_bad": len(bad), "reason": "; ".join(bad[:3])}
    LA, LB = A.logratio(pure["A"][0], F, G), A.logratio(pure["B"][0], F, G)
    if not LA - LB >= 2.0:
        return {"seed": s, "valid": False, "reason": f"L(A) - L(B) = {LA - LB:.2f} < 2"}
    r = {"seed": s, "valid": True}
    for cell in D.CELLS:
        L = {"A": LA, "B": LB, "AB": A.logratio(sw[(cell, "AB")][0], F, G), "BA": A.logratio(sw[(cell, "BA")][0], F, G)}
        r[f"pi_{cell}"] = A.pi_of(L)["pi"]
        r[f"sep_{cell}"] = (A.logratio(sw[(cell, "AB")][1], F, G) - A.logratio(sw[(cell, "BA")][1], F, G)) / (LA - LB)
    return r


def boot_ci(d: np.ndarray, seed: int = 90) -> list[float]:
    rng = np.random.default_rng(seed)
    m = d[rng.integers(0, len(d), size=(N_BOOT, len(d)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def verdict(e: np.ndarray, db: np.ndarray) -> dict:
    if len(e) < MIN_VALID:
        return {"n": len(e), "verdict": "nicht auswertbar"}
    ce, cb = boot_ci(e), boot_ci(db)
    inside = lambda ci: -0.1 <= ci[0] and ci[1] <= 0.1   # noqa: E731
    if ce[0] > 0 and inside(cb):
        v = "H-beta gestuetzt"
    elif ce[0] > 0 and cb[0] > 0:
        v = "Fenster erklaeren Teil"
    elif inside(ce):
        v = "Fenster erklaeren nichts"
    else:
        v = "unklar"
    return {"n": len(e), "e_mean": float(e.mean()), "e_ci95": ce, "e_pos": int((e > 0).sum()),
            "d_b_mean": float(db.mean()), "d_b_ci95": cb, "verdict": v}


def t_equiv(y: float, curve: list[float]) -> float:
    for (t0, y0), (t1, y1) in zip(zip(STD_T, curve), zip(STD_T[1:], curve[1:])):
        if min(y0, y1) <= y <= max(y0, y1) and y1 != y0:
            return float(t0 + (y - y0) * (t1 - t0) / (y1 - y0))
    return float("nan")


def main() -> None:
    rows = [seed_row(s) for s in D.SEEDS]
    ok = [r for r in rows if r["valid"]]
    col = lambda k: np.array([r[k] for r in ok])   # noqa: E731
    out = {"n_valid": len(ok)}
    if ok:
        out["primary"] = verdict(col("pi_l100") - col("pi_l100b"), col("pi_l100b") - col("pi_n25"))
        means = {c: float(col(f"pi_{c}").mean()) for c in D.CELLS}
        curve = [means[f"n{t}"] for t in STD_T]
        d100, f1 = col("pi_l100") - col("pi_n25"), col("pi_l100") - col("pi_l100b1")
        out["secondary"] = {"pi_means": means, "sep_means": {c: float(col(f"sep_{c}").mean()) for c in D.CELLS},
                            "d100_mean": float(d100.mean()), "d100_ci95": boot_ci(d100) if len(ok) > 1 else None,
                            "f1_mean": float(f1.mean()), "f1_ci95": boot_ci(f1) if len(ok) > 1 else None,
                            "t_eq": {c: t_equiv(means[c], curve) for c in ("l100", "l100b", "l100b1")}}
    else:
        out["primary"] = {"verdict": "nicht auswertbar"}
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert len(D.jobs()) == len(D.SEEDS) * 14 and len(D.smoke()) == 3
    assert all("--pre-switch-betas 0.975,0.995" in x and "--lr-scale 0.25" in x for x in D.smoke()[1:])
    z = np.linspace(-0.04, 0.04, 16)
    assert verdict(z + 0.24, z)["verdict"] == "H-beta gestuetzt"
    assert verdict(z + 0.12, z + 0.12)["verdict"] == "Fenster erklaeren Teil"
    assert verdict(z, z + 0.24)["verdict"] == "Fenster erklaeren nichts"
    assert verdict(np.linspace(-0.3, 0.4, 16), z)["verdict"] == "unklar"
    assert verdict(z[:9], z[:9])["verdict"] == "nicht auswertbar"
    assert abs(t_equiv(0.4, [0.3, 0.5, 0.9]) - 29.0) < 1e-12
    print("[exp090] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
