"""EXP-089 (pilot, exploration): lock-in at fixed Lambda = 25 over 25, 50 and 100 pre-switch steps. Definition and
readings: README.md (fixed before any EXP-089 run). Run under guarded_run.py with the global python.

pi as EXP-056/059/081 against the pure (standard-lr) A/B runs of the seed. Validity per seed: all 12 runs ok through the
shared loader (incl. lr_scale in the stored config), L(A) - L(B) >= 2.
Primary: d100 = pi(l100) - pi(n25) per seed, paired; 95 % percentile bootstrap CI (10 000 resamples, rng 89).
  'Lambda-Uhr gestuetzt' if the CI lies inside [-0.1, +0.1]; 'Mischuhr gestuetzt' if CI lower bound > 0 and mean < 0.5;
  'nahe Schrittuhr' if CI lower bound > 0 and mean >= 0.5; else 'unklar'. Fewer than 8 valid seeds -> 'nicht auswertbar'.
Secondary (descriptive): d50 = pi(l50) - pi(n25); equivalent standard step t_eq of the cell means on the standard curve
(25, 33, 45; linear interpolation, nan outside) and the exponent 1 - a = log(t_eq / 25) / log(t / 25) of a mixed clock
Lambda^a * t^(1 - a).
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
MIN_VALID, N_BOOT = 8, 10_000
STD_T = (25, 33, 45)


def load(s: int, kind: str, cell: str | None = None) -> np.ndarray | str:
    first, second = kind[0], kind[1:] or None
    c, t = D.CELLS[cell] if cell else (1.0, 0)
    steps = D.BUDGET + (t if second else 0)
    pat = (f"EXP-0*_baseline_seed{s}_thr*_{D.stem(s, first)}" + (f"_to_{D.stem(s, second)}_at{t}" if second else "")
           + (f"_lrs{c:g}" if c != 1.0 else "") + SUF)
    L = load_run(find_run(RAW, pat),
                 Expect(seed=s, device="cuda", max_steps=steps, split_file=SPL / f"{D.stem(s, first)}.npy", test_file=SPL / f"seed{s}_test.npy",
                        switch_file=SPL / f"{D.stem(s, second)}.npy" if second else None,
                        config={"p": 113, "task": "add", "lr_scale": c}, snapshots_at=(steps,)))
    if L.status != "ok":
        return f"{cell or 'pure'}:{kind}: {L.status}: {L.reason}"
    return A._a43.group_power(L.snapshot(steps), "add", 113)[0]


def seed_row(s: int) -> dict:
    meta = json.loads((SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    pure = {k: load(s, k) for k in ("A", "B")}
    sw = {(cell, k): load(s, k, cell) for cell in D.CELLS for k in ("AB", "BA")}
    bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
    if bad:
        return {"seed": s, "valid": False, "n_bad": len(bad), "reason": "; ".join(bad[:3])}
    LA, LB = A.logratio(pure["A"], F, G), A.logratio(pure["B"], F, G)
    if not LA - LB >= 2.0:
        return {"seed": s, "valid": False, "reason": f"L(A) - L(B) = {LA - LB:.2f} < 2"}
    r = {"seed": s, "valid": True}
    for cell in D.CELLS:
        L = {"A": LA, "B": LB, "AB": A.logratio(sw[(cell, "AB")], F, G), "BA": A.logratio(sw[(cell, "BA")], F, G)}
        r[f"pi_{cell}"] = A.pi_of(L)["pi"]
    return r


def boot_ci(d: np.ndarray, seed: int = 89) -> list[float]:
    rng = np.random.default_rng(seed)
    m = d[rng.integers(0, len(d), size=(N_BOOT, len(d)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def verdict(d: np.ndarray) -> dict:
    if len(d) < MIN_VALID:
        return {"n": len(d), "verdict": "nicht auswertbar"}
    ci, mean = boot_ci(d), float(d.mean())
    if -0.1 <= ci[0] and ci[1] <= 0.1:
        v = "Lambda-Uhr gestuetzt"
    elif ci[0] > 0 and mean < 0.5:
        v = "Mischuhr gestuetzt"
    elif ci[0] > 0:
        v = "nahe Schrittuhr"
    else:
        v = "unklar"
    return {"n": len(d), "mean": mean, "sd": float(d.std(ddof=1)), "ci95": ci, "n_pos": int((d > 0).sum()), "verdict": v}


def t_equiv(y: float, curve: list[float]) -> float:
    for (t0, y0), (t1, y1) in zip(zip(STD_T, curve), zip(STD_T[1:], curve[1:])):
        if min(y0, y1) <= y <= max(y0, y1) and y1 != y0:
            return float(t0 + (y - y0) * (t1 - t0) / (y1 - y0))
    return float("nan")


def main() -> None:
    rows = [seed_row(s) for s in D.SEEDS]
    ok = [r for r in rows if r["valid"]]
    out = {"n_valid": len(ok), "primary": verdict(np.array([r["pi_l100"] - r["pi_n25"] for r in ok]))}
    if ok:
        means = {c: float(np.mean([r[f"pi_{c}"] for r in ok])) for c in D.CELLS}
        curve = [means[f"n{t}"] for t in STD_T]
        d50 = np.array([r["pi_l50"] - r["pi_n25"] for r in ok])
        sec = {"pi_means": means, "pi_sd": {c: float(np.std([r[f"pi_{c}"] for r in ok], ddof=1)) for c in D.CELLS},
               "d50_mean": float(d50.mean()), "d50_ci95": boot_ci(d50) if len(ok) > 1 else None}
        for c in ("l50", "l100"):
            te = t_equiv(means[c], curve)
            sec[f"t_eq_{c}"] = te
            sec[f"one_minus_a_{c}"] = float(np.log(te / 25) / np.log(D.CELLS[c][1] / 25)) if np.isfinite(te) else None
        out["secondary"] = sec
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert len(D.jobs()) == 120 and len(D.smoke()) == 3 and all("--lr-scale 0.25" in x for x in D.smoke()[1:])
    z = np.linspace(-0.04, 0.04, 10)
    assert verdict(z)["verdict"] == "Lambda-Uhr gestuetzt"
    assert verdict(z + 0.2)["verdict"] == "Mischuhr gestuetzt"
    assert verdict(z + 0.8)["verdict"] == "nahe Schrittuhr"
    assert verdict(np.linspace(-0.3, 0.4, 10))["verdict"] == "unklar"
    assert verdict(z[:7])["verdict"] == "nicht auswertbar"
    assert abs(t_equiv(0.4, [0.3, 0.5, 0.9]) - 29.0) < 1e-12 and np.isnan(t_equiv(1.0, [0.3, 0.5, 0.9]))
    print("[exp089] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
