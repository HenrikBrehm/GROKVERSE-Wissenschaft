"""EXP-097 (pilot, exploration): sign steps vs staleness before the switch. Definition, predictions and readings: README.md
(fixed before any EXP-097 run). Run under guarded_run.py with the global python.

pi, validity, loading and displacement selectivity as EXP-092/095 (functions imported from EXP-092's analyze.py, pointed at this
experiment's design; the run lookup knows the '_ge{k}' and '_psu{update}' suffixes and checks the recorded schedule/update).
Paired over seeds, 95 % percentile bootstrap (10 000, rng 97):
  eA = pi(n24) - pi(g24)     (Adam: initial gradient only vs fresh; replication of EXP-095 e24 = +0.187)
  sA = pi(L24) - pi(g24)     (same stale gradient AND identical Adam state at the switch; only the pre-switch weight path differs:
                              linear vs sign steps) -> Q1: how much of eA is sign quantisation of the weight path?
  eL = pi(L1) - pi(L24)      (linear pre-switch weight path: fresh vs initial gradient only) -> Q2: staleness without sign
                              quantisation of the weight path (the post-switch momentum tail of L24 is still sign(g0)-like,
                              as in g24; so eL is an upper bound for pure staleness, review session 43)
Q1 readings (in this order): eA CI lower <= 0.03 -> 'nicht trennbar';
  'Quantisierung erklaert'    sA CI lower > 0.03 and mean sA >= 0.5 mean eA
  'Quantisierung teilweise'   sA CI lower > 0.03 and mean sA < 0.5 mean eA
  'Quantisierung nicht'       sA CI inside [-0.05, +0.05]
  else 'unklar'.
Q2 readings (in this order): eA CI lower <= 0.03 -> 'nicht trennbar';
  'Boden'                    mean pi(L1) < 0.5 mean pi(n24) (the fresh linear arm locks in much less; eL not comparable)
  'Veraltung zaehlt'         eL CI lower > 0.03 and mean eL / mean pi(L1) >= 0.5 mean eA / mean pi(n24)  (relative deficits)
  'Veraltung teilweise'      eL CI lower > 0.03, relative deficit smaller
  'erste Ordnung genuegt'    eL CI inside [-0.05, +0.05]
  'erste Ordnung besser'     eL CI upper < -0.03
  else 'unklar'. Fewer than 10 valid seeds -> 'nicht auswertbar' (both).
Secondary (descriptive): pi(L1) - pi(n24); cell means of pi, selectivity f and norm N at the switch; share q of W_E
displacement entries that are sign steps (|D| within 10 % of the unit).
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

MIN_VALID, N_BOOT, HI, EQ, FLOOR_REL = 10, 10_000, 0.03, 0.05, 0.5
LR, WD = 1e-3, 1.0
DECAY = (1 - LR * WD) ** D.T_SW
UNIT = LR * sum((1 - LR * WD) ** j for j in range(D.T_SW))


def load(s: int, kind: str, cell: str | None = None):
    """As EXP-095 load, plus '_psu{update}' and the recorded pre-switch update (mode, steps, shadowed Adam counter)."""
    first, second = kind[0], kind[1:] or None
    k, upd = D.CELLS[cell] if cell else (1, "adam")
    t = D.T_SW if second else 0
    steps = D.BUDGET + t
    pat = (f"EXP-0*_baseline_seed{s}_thr*_{D.stem(s, first)}" + (f"_to_{D.stem(s, second)}_at{t}" if second else "")
           + (f"_ge{k}" if k != 1 else "") + (f"_psu{upd}" if upd != "adam" else "") + E.SUF)
    L = load_run(find_run(E.RAW, pat),
                 Expect(seed=s, device="cuda", max_steps=steps, split_file=E.SPL / f"{D.stem(s, first)}.npy",
                        test_file=E.SPL / f"seed{s}_test.npy", switch_file=E.SPL / f"{D.stem(s, second)}.npy" if second else None,
                        config={"p": 113, "task": "add", "lr_scale": 1.0, "pre_switch_betas": None, "beta1": 0.9, "beta2": 0.98},
                        snapshots_at=(steps,) + ((t, 0) if second else ())))
    tag = f"{cell or 'pure'}:{kind}"
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    ev = L.res.get("events", {})
    if k != 1:
        g = ev.get("pre_switch_grad_every", {})
        if (L.res.get("pre_switch_grad_every") != k or g.get("k") != k
                or g.get("eval_steps_pre_switch") != list(range(1, t + 1, k))):
            return f"{tag}: gradient schedule not recorded as k = {k}"
    if second and L.res.get("switch_step") != t:
        return f"{tag}: switch_step {L.res.get('switch_step')!r} != {t}"
    if upd != "adam":
        u = ev.get("pre_switch_update", {})
        if (L.res.get("pre_switch_update") != upd or u.get("mode") != upd or u.get("steps") != t
                or u.get("adam_step_at_switch") != t):
            return f"{tag}: pre-switch update not recorded as {upd} with a shadowed Adam counter {t}"
    elif L.res.get("pre_switch_update", "adam") != "adam":
        return f"{tag}: unexpected pre-switch update {L.res.get('pre_switch_update')!r}"
    end = E.A._a43.group_power(L.snapshot(steps), "add", 113)[0]
    return (end, L.snapshot(t), L.snapshot(0)) if second else (end, None, None)


E.load = load        # seed_row looks load up in its module at call time


def sign_share(W_t: np.ndarray, W_0: np.ndarray) -> float:
    Dd = W_t.astype(np.float64) - DECAY * W_0.astype(np.float64)
    return float(np.mean(np.abs(np.abs(Dd) - UNIT) <= 0.1 * UNIT))


def seed_row(s: int) -> dict:
    r = E.seed_row(s)
    if r["valid"]:
        for cell in D.CELLS:
            q = [sign_share(*load(s, kind, cell)[1:]) for kind in ("AB", "BA")]
            r[f"q_{cell}"] = float(np.mean(q))
    return r


def boot_ci(x: np.ndarray, seed: int = 97) -> list[float]:
    rng = np.random.default_rng(seed)
    m = x[rng.integers(0, len(x), size=(N_BOOT, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def verdict(pis: dict[str, np.ndarray]) -> dict:
    n = len(pis["n24"])
    if n < MIN_VALID:
        return {"n": n, "Q1": "nicht auswertbar", "Q2": "nicht auswertbar"}
    d = {"eA": pis["n24"] - pis["g24"], "sA": pis["L24"] - pis["g24"], "eL": pis["L1"] - pis["L24"],
         "L1_minus_n24": pis["L1"] - pis["n24"]}
    ci = {k: boot_ci(v) for k, v in d.items()}
    m = {k: float(x.mean()) for k, x in d.items()}
    inside = lambda k: -EQ <= ci[k][0] and ci[k][1] <= EQ   # noqa: E731
    if ci["eA"][0] <= HI:
        q1 = q2 = "nicht trennbar"
    else:
        if ci["sA"][0] > HI:
            q1 = "Quantisierung erklaert" if m["sA"] >= 0.5 * m["eA"] else "Quantisierung teilweise"
        else:
            q1 = "Quantisierung nicht" if inside("sA") else "unklar"
        pL1, pn = float(pis["L1"].mean()), float(pis["n24"].mean())
        if pL1 < FLOOR_REL * pn:
            q2 = "Boden"
        elif ci["eL"][0] > HI:
            q2 = "Veraltung zaehlt" if m["eL"] / pL1 >= 0.5 * m["eA"] / pn else "Veraltung teilweise"
        elif inside("eL"):
            q2 = "erste Ordnung genuegt"
        elif ci["eL"][1] < -HI:
            q2 = "erste Ordnung besser"
        else:
            q2 = "unklar"
    return {"n": n, "mean": m, "ci95": ci, "pos": {k: int((x > 0).sum()) for k, x in d.items()}, "Q1": q1, "Q2": q2}


def main() -> None:
    rows = [seed_row(s) for s in D.SEEDS]
    ok = [r for r in rows if r["valid"]]
    col = lambda k: np.array([r[k] for r in ok])   # noqa: E731
    out: dict = {"n_valid": len(ok)}
    if ok:
        pis = {c: col(f"pi_{c}") for c in D.CELLS}
        out["primary"] = verdict(pis)
        out["secondary"] = {"pi_means": {c: float(p.mean()) for c, p in pis.items()},
                            "fsel_means": {c: float(col(f"fsel_{c}").mean()) for c in D.CELLS},
                            "dnorm_means": {c: float(col(f"dnorm_{c}").mean()) for c in D.CELLS},
                            "sign_share_means": {c: float(col(f"q_{c}").mean()) for c in D.CELLS}}
    else:
        out["primary"] = {"Q1": "nicht auswertbar", "Q2": "nicht auswertbar"}
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def smoke_check() -> None:
    """Loader status of the three smoke runs only (no values, writes nothing)."""
    s = D.SEEDS[0]
    got = [load(s, "A"), load(s, "AB", "L24"), load(s, "BA", "L24")]
    bad = [g for g in got if isinstance(g, str)]
    print(f"[exp097] smoke-check: {3 - len(bad)}/3 loaded" + ("" if not bad else " | " + " | ".join(bad)), flush=True)
    if bad:
        raise SystemExit(1)


def selftest() -> None:
    assert len(D.jobs()) == len(D.SEEDS) * 10 and len(D.smoke()) == 3 and E.D is D and E.load is load
    assert all("--pre-switch-grad-every 24 --pre-switch-update normgd" in x and "--switch-step 24" in x for x in D.smoke()[1:])
    assert sum("--pre-switch-update normgd" in x for x in D.jobs()) == len(D.SEEDS) * 4
    assert sum("--pre-switch-grad-every 24" in x for x in D.jobs()) == len(D.SEEDS) * 4
    assert abs(UNIT - 0.02372601341636975) < 1e-12        # same unit as EXP-095 posthoc_sign_s43
    rng = np.random.default_rng(0)
    nz = lambda: rng.normal(0, 0.02, 16)   # noqa: E731
    base = 0.30 + nz()
    w = lambda eA, sA, l1, eL: {"n24": base, "g24": base - eA + nz(), "L24": base - eA + sA + nz() * 0 if l1 is None   # noqa: E731
                                else l1 - eL + nz(), "L1": (base - eA + sA + eL if l1 is None else l1) + nz()}
    v = verdict(w(0.19, 0.15, None, 0.03))
    assert v["Q1"] == "Quantisierung erklaert", v
    assert verdict(w(0.19, 0.06, None, 0.1))["Q1"] == "Quantisierung teilweise"
    assert verdict(w(0.19, 0.0, None, 0.15))["Q1"] == "Quantisierung nicht"
    assert verdict(w(0.19, 0.0, 0.28, 0.15))["Q2"] == "Veraltung zaehlt"
    assert verdict(w(0.25, 0.0, 0.28, 0.06))["Q2"] == "Veraltung teilweise"   # margin: 0.06/0.28 vs 0.5 * 0.25/0.30
    assert verdict(w(0.19, 0.0, 0.28, 0.0))["Q2"] == "erste Ordnung genuegt"
    assert verdict(w(0.19, 0.0, 0.28, -0.12))["Q2"] == "erste Ordnung besser"
    assert verdict(w(0.19, 0.0, 0.10, 0.0))["Q2"] == "Boden"
    v = verdict(w(0.0, 0.1, 0.28, 0.15))
    assert v["Q1"] == v["Q2"] == "nicht trennbar", v
    v = verdict({k: x[:9] for k, x in w(0.19, 0.1, 0.28, 0.15).items()})
    assert v["Q1"] == v["Q2"] == "nicht auswertbar", v
    W0 = rng.normal(0, 1, (113, 128))
    assert sign_share(DECAY * W0 - UNIT * np.sign(rng.normal(0, 1, W0.shape)), W0) > 0.999
    assert sign_share(DECAY * W0 + UNIT * rng.normal(0, 1, W0.shape), W0) < 0.2
    print("[exp097] selftest ok", flush=True)


if __name__ == "__main__":
    arg = sys.argv[1:]
    if arg == ["--selftest"]:
        selftest()
    elif arg == ["--smoke-check"]:
        smoke_check()
    elif not arg:
        main()
    else:
        raise SystemExit(__doc__)
