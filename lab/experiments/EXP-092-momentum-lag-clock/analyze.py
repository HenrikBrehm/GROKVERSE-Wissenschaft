"""EXP-092 (pilot, exploration): momentum-lag clock. Definition, predictions and readings: README.md (fixed before any EXP-092 run).
Run under guarded_run.py with the global python.

pi as EXP-056/089/090 against the pure (standard) A/B runs of the seed. Validity per seed: all 16 runs ok through the shared
loader (lr_scale and pre_switch_betas as recorded; beta switch event check true), L(A) - L(B) >= 2. Fewer than 10 valid seeds
-> 'nicht auswertbar'.
Three clocks x(cell): steps t; Lambda = c t; lag clock Lambda_eff = c t - c lag(beta1', t), lag(b, t) = sum_k k b^k / sum_k b^k
(k = 0..t-1, the mean age of Adam's bias-corrected first moment at the switch). Each clock is calibrated on the pilot's own
n25/n30 mean pi (straight line) and predicts the five held-out cells n20, b08, b095, c05, c4.
Primary: (P1) MAE of each clock over the held-out cell means; delta_L = MAE_Lambda - MAE_lag, delta_S = MAE_steps - MAE_lag,
95 % percentile bootstrap over seeds (10 000, rng 92; calibration refitted in every resample). (P2) b_up = pi(b08) - pi(n25),
b_dn = pi(n25) - pi(b095), paired bootstrap CIs.
  'Lag-Uhr gestuetzt'   delta_L and delta_S CI lower > 0, b_up and b_dn CI lower > 0
  'Lag-Uhr widerlegt'   b_up or b_dn CI upper < 0, or both b CIs inside [-0.03, +0.03]
  'Lag-Uhr teilweise'   b_up and b_dn CI lower > 0, not both delta CIs > 0
  else 'unklar'.
Secondary (descriptive): MAE_lag itself, Spearman over the 7 cell means between pi and each clock; displacement selectivity at
the switch (share of the group power of W_E(t) - W_E(0) on the first split's targets, and its norm), per cell.
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
MIN_VALID, N_BOOT, EQ = 10, 10_000, 0.03
CAL, HELD = ("n25", "n30"), ("n20", "b08", "b095", "c05", "c4")


def lag(b: float, t: int) -> float:
    k = np.arange(t)
    w = b ** k
    return float((k * w).sum() / w.sum())


def clocks(cell: str) -> dict[str, float]:
    c, t, psb = D.CELLS[cell]
    b1 = psb[0] if psb else 0.9
    return {"steps": float(t), "lambda": c * t, "lag": c * t - c * lag(b1, t)}


def load(s: int, kind: str, cell: str | None = None) -> tuple[np.ndarray, np.ndarray | None, np.ndarray | None] | str:
    """Returns (group power at the end, W_E at the switch or None, W_E at step 0 or None)."""
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
                        snapshots_at=(steps,) + ((t, 0) if second else ())))
    tag = f"{cell or 'pure'}:{kind}"
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if psb and L.res.get("events", {}).get("pre_switch_betas", {}).get("check") is not True:
        return f"{tag}: beta switch not recorded"
    end = A._a43.group_power(L.snapshot(steps), "add", 113)[0]
    return (end, L.snapshot(t), L.snapshot(0)) if second else (end, None, None)


def selectivity(W_t: np.ndarray, W_0: np.ndarray, F: list[int]) -> tuple[float, float]:
    """Share of the displacement's group power on the targets F, and the displacement norm (rows 0..p-1)."""
    pw = A._a43.group_power(W_t - W_0, "add", 113)[0]
    return float(pw[[k - 1 for k in F]].sum() / pw.sum()), float(np.linalg.norm((W_t - W_0)[:113]))


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
        fa, na = selectivity(sw[(cell, "AB")][1], sw[(cell, "AB")][2], F)
        fb, nb = selectivity(sw[(cell, "BA")][1], sw[(cell, "BA")][2], G)
        r[f"fsel_{cell}"], r[f"dnorm_{cell}"] = (fa + fb) / 2, (na + nb) / 2
    return r


def mae(means: dict[str, float]) -> dict[str, float]:
    """Calibrate each clock on n25/n30 (straight line), MAE over the held-out cells."""
    out = {}
    for k in ("steps", "lambda", "lag"):
        x0, x1 = clocks(CAL[0])[k], clocks(CAL[1])[k]
        y0, y1 = means[CAL[0]], means[CAL[1]]
        pred = {c: y0 + (y1 - y0) * (clocks(c)[k] - x0) / (x1 - x0) for c in HELD}
        out[k] = float(np.mean([abs(pred[c] - means[c]) for c in HELD]))
        out[f"pred_{k}"] = pred
    return out


def boot_ci(x: np.ndarray, seed: int = 92) -> list[float]:
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), size=(N_BOOT, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def boot_delta(pis: dict[str, np.ndarray], seed: int = 92) -> dict[str, list[float]]:
    rng = np.random.default_rng(seed)
    n = len(next(iter(pis.values())))
    dL, dS = [], []
    for _ in range(N_BOOT):
        i = rng.integers(0, n, size=n)
        m = mae({c: float(v[i].mean()) for c, v in pis.items()})
        dL.append(m["lambda"] - m["lag"])
        dS.append(m["steps"] - m["lag"])
    ci = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]   # noqa: E731
    return {"delta_L_ci95": ci(dL), "delta_S_ci95": ci(dS)}


def verdict(pis: dict[str, np.ndarray]) -> dict:
    n = len(pis["n25"])
    if n < MIN_VALID:
        return {"n": n, "verdict": "nicht auswertbar"}
    means = {c: float(v.mean()) for c, v in pis.items()}
    m, bd = mae(means), boot_delta(pis)
    b_up, b_dn = pis["b08"] - pis["n25"], pis["n25"] - pis["b095"]
    cu, cd = boot_ci(b_up), boot_ci(b_dn)
    inside = lambda ci: -EQ <= ci[0] and ci[1] <= EQ   # noqa: E731
    if bd["delta_L_ci95"][0] > 0 and bd["delta_S_ci95"][0] > 0 and cu[0] > 0 and cd[0] > 0:
        v = "Lag-Uhr gestuetzt"
    elif cu[1] < 0 or cd[1] < 0 or (inside(cu) and inside(cd)):
        v = "Lag-Uhr widerlegt"
    elif cu[0] > 0 and cd[0] > 0:
        v = "Lag-Uhr teilweise"
    else:
        v = "unklar"
    return {"n": n, "mae": m, **bd, "b_up_mean": float(b_up.mean()), "b_up_ci95": cu, "b_up_pos": int((b_up > 0).sum()),
            "b_dn_mean": float(b_dn.mean()), "b_dn_ci95": cd, "b_dn_pos": int((b_dn > 0).sum()), "verdict": v}


def spearman(x: list[float], y: list[float]) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def main() -> None:
    rows = [seed_row(s) for s in D.SEEDS]
    ok = [r for r in rows if r["valid"]]
    col = lambda k: np.array([r[k] for r in ok])   # noqa: E731
    out: dict = {"n_valid": len(ok)}
    if ok:
        pis = {c: col(f"pi_{c}") for c in D.CELLS}
        out["primary"] = verdict(pis)
        means = {c: float(v.mean()) for c, v in pis.items()}
        cells = list(D.CELLS)
        out["secondary"] = {"pi_means": means, "clocks": {c: clocks(c) for c in cells},
                            "spearman": {k: spearman([clocks(c)[k] for c in cells], [means[c] for c in cells])
                                         for k in ("steps", "lambda", "lag")},
                            "fsel_means": {c: float(col(f"fsel_{c}").mean()) for c in cells},
                            "dnorm_means": {c: float(col(f"dnorm_{c}").mean()) for c in cells}}
    else:
        out["primary"] = {"verdict": "nicht auswertbar"}
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert len(D.jobs()) == len(D.SEEDS) * 16 and len(D.smoke()) == 3
    assert all("--pre-switch-betas 0.95,0.98" in x for x in D.smoke()[1:])
    assert abs(lag(0.9, 100) - 9.0) < 0.01 and lag(0.9, 1) == 0.0
    assert abs(clocks("c4")["lambda"] - 24) < 1e-12 and clocks("b095")["lag"] < clocks("n25")["lag"] < clocks("b08")["lag"]
    rng = np.random.default_rng(0)
    noise = lambda: rng.normal(0, 0.02, 16)   # noqa: E731
    lagw = {c: 0.33 + 0.024 * (clocks(c)["lag"] - clocks("n25")["lag"]) + noise() for c in D.CELLS}
    assert verdict(lagw)["verdict"] == "Lag-Uhr gestuetzt", verdict(lagw)
    lamw = {c: 0.33 + 0.02 * (clocks(c)["lambda"] - 25) + noise() for c in D.CELLS}
    assert verdict(lamw)["verdict"] == "Lag-Uhr widerlegt", verdict(lamw)
    assert verdict({c: v[:9] for c, v in lagw.items()})["verdict"] == "nicht auswertbar"
    m = mae({"n25": 0.3, "n30": 0.4, "n20": 0.2, "b08": 0.3, "b095": 0.3, "c05": 0.3, "c4": 0.28})
    assert m["lambda"] < 1e-12 and m["lag"] > 0
    W0 = np.zeros((114, 8))
    Wt = W0.copy()
    Wt[:113, 0] = np.cos(2 * np.pi * 5 * np.arange(113) / 113)
    f, nrm = selectivity(Wt, W0, [5, 6])
    assert abs(f - 1) < 1e-9 and nrm > 0
    print("[exp092] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
