"""P2 confirmation (FINDINGS "Programm", functional use): frozen analysis on the saved P1 add-113 models. Session 21, UNTESTED.

Registration: lab/confirm/P2_REGISTRATION_DRAFT.md (frozen together with the P1 manifest; this file is in its code_sha256).
Per seed s of the P1 manifest and arm a in {F, G}: remove E = 0.5 * E_ctrl of W_E energy from the own targets and, separately, from the
control set (EXP-051/055 helpers, unchanged), measure the test-loss change on the pairs in neither split. D_s = mean over the two arms of
dL_own - dL_ctrl. One-sided sign-flip test of mean D > 0 (Monte Carlo as P1), Holm in the P1-P3 family (FAMILY = 3, P1 and P3 as p = 1
placeholders here; the joint table is P1_summary + P2_summary). "bestätigt" = all planned seeds valid, Holm-p < 0.05 and the lower
95 % bootstrap bound of mean D > 0. Runs are accepted only through the P1 loader + binding (confirm_p1.unbound).

  python lab/tools/confirm_p2.py --analyze lab/confirm/P1_manifest.json     # under guarded_run.py, only after P1 jobs finished
  python lab/tools/confirm_p2.py --selftest
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
import confirm_p1 as c1  # noqa: E402
from result_loader import Expect, find_run, load_run  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp055", LAB / "experiments/EXP-055-ablation-dose/analyze.py")
e55 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e55)
e51 = e55.e51

TASK, F_PRIMARY, DOSES, ACC_MIN, ALPHA = {"task": "add", "p": 113}, 0.5, (0.1, 0.25, 0.5, 0.75, 1.0), 0.9, 0.05


def arm_row(man: dict, s: int, arm: str, other: str, T: dict, common: np.ndarray, B: np.ndarray) -> dict | str:
    st, dev = c1.stem(man, TASK, s, arm), man["device"]
    d = find_run(c1.RAW, f"EXP-0*_baseline_seed{s}_thr*_{st}{'' if dev == 'cpu' else f'_dev{dev}'}")
    if (why := c1.unbound(man, d)):
        return f"defekt: {why}"
    L = load_run(d, Expect(seed=s, device=dev, max_steps=c1.STEP, split_file=c1.SPLITS / f"{st}.npy",
                           config={"p": TASK["p"], "task": TASK["task"]}, files=("model_final.pt",)))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    m = e51.load_model(L.path)
    W = m.W_E.detach().numpy().astype(np.float64)[:e51.P]
    base = e55.evaluate(m, None, common)
    ctrl = e51.control_set(T[arm], T[other])
    e_own, e_ctrl = e51.energy(W, B, T[arm]), e51.energy(W, B, ctrl)
    if e_own <= F_PRIMARY * e_ctrl:
        return f"E_own <= {F_PRIMARY} E_ctrl, primary dose infeasible"
    dose = {}
    for f in DOSES:
        E = f * e_ctrl
        if E > e_own:                                  # secondary doses only where feasible
            continue
        ev_o = e55.evaluate(m, e51.remove_energy(W, B, T[arm], E), common)
        ev_c = e55.evaluate(m, e51.remove_energy(W, B, ctrl, E), common)
        dose[str(f)] = {"E": E, "dL_own": ev_o["loss"] - base["loss"], "dL_ctrl": ev_c["loss"] - base["loss"],
                        "dacc_own": base["acc"] - ev_o["acc"], "dacc_ctrl": base["acc"] - ev_c["acc"],
                        "margin_own": ev_o["margin"], "margin_ctrl": ev_c["margin"]}
    return {"base": base, "energy_own": e_own, "energy_ctrl": e_ctrl, "dose": dose}


def seed_row(man: dict, s: int, B: np.ndarray) -> dict:
    r: dict = {"seed": s, "valid": False}
    bad = [m for m in (c1.split_mismatch(man, TASK, s, a) for a in "FG") if m]
    if bad:
        r["reason"] = "; ".join(bad)
        return r
    T = {a: json.loads((c1.SPLITS / f"{c1.stem(man, TASK, s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
    trains = [np.load(c1.SPLITS / f"{c1.stem(man, TASK, s, a)}.npy") for a in "FG"]
    common = np.setdiff1d(np.arange(e51.P * e51.P), np.union1d(*trains))
    arms = {}
    for arm, other in (("F", "G"), ("G", "F")):
        a = arm_row(man, s, arm, other, T, common, B)
        if isinstance(a, str):
            r["reason"] = f"{arm}: {a}"
            return r
        arms[arm] = a
    r.update({"arms": arms, "n_common_test": int(len(common))})
    if not all(v["base"]["acc"] >= ACC_MIN for v in arms.values()):
        r["reason"] = f"base accuracy < {ACC_MIN}"
        return r
    prim = [v["dose"][str(F_PRIMARY)] for v in arms.values()]
    if not np.all(np.isfinite([x[k] for x in prim for k in ("dL_own", "dL_ctrl")])):
        r["reason"] = "non-finite loss change at the primary dose"
        return r
    r["valid"] = True
    r["D"] = float(np.mean([x["dL_own"] - x["dL_ctrl"] for x in prim]))
    return r


def verdict(D: np.ndarray, n_planned: int, rng: np.random.Generator) -> dict:
    """All planned seeds valid (no complete-case deletion, as P1), Holm-p < ALPHA and CI lower bound > 0."""
    if len(D) != n_planned:
        return {"verdict": "nicht auswertbar"}
    p = c1.sign_flip_p(D, rng)
    ci = c1.boot_ci(D, rng)
    ph = c1.holm({"P2": p, "_P1": 1.0, "_P3": 1.0})["P2"]
    ok = ph < ALPHA and ci[0] > 0
    return {"p": p, "p_holm_worstcase": ph, "ci95": ci, "mean": float(D.mean()), "sd": float(D.std(ddof=1)),
            "d_z": float(D.mean() / D.std(ddof=1)) if D.std(ddof=1) > 0 else None,
            "n_positive": int((D > 0).sum()), "verdict": "bestätigt" if ok else "nicht bestätigt"}


def analyze(manifest: Path) -> None:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    c1.check_manifest(manifest, man)
    if TASK not in [{"task": t["task"], "p": int(t["p"])} for t in man["tasks"]]:
        raise SystemExit("P2 needs the add 113 task in the P1 manifest")
    B = e51.basis()
    rows = [seed_row(man, s, B) for s in man["seeds"]]
    D = np.array([r["D"] for r in rows if r["valid"]])
    out = {"manifest_commit": man["commit"], "f_primary": F_PRIMARY, "n_valid": int(len(D)), "n_planned": len(man["seeds"]),
           **verdict(D, len(man["seeds"]), np.random.default_rng(2)), "rows": rows}
    (LAB / "confirm" / "P2_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    rng = np.random.default_rng(0)
    assert verdict(np.ones(9), 10, rng)["verdict"] == "nicht auswertbar"
    v = verdict(np.linspace(0.5, 1.5, 10), 10, rng)
    assert v["verdict"] == "bestätigt" and abs(v["p_holm_worstcase"] - 3 / 1024) < 1e-12, v
    assert verdict(-np.linspace(0.5, 1.5, 10), 10, rng)["verdict"] == "nicht bestätigt"
    v = verdict(np.array([1.0, -0.9] * 5), 10, rng)
    assert v["verdict"] == "nicht bestätigt" and v["ci95"][0] <= 0
    assert F_PRIMARY in DOSES
    e55.selftest()
    print("[confirm_p2] selftest ok", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
    elif len(a) == 2 and a[0] == "--analyze":
        analyze(Path(a[1]))
    else:
        raise SystemExit(__doc__)
