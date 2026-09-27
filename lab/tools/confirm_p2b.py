"""P2b confirmation (FINDINGS programme A, functional use; successor of the non-evaluable P2): splits, jobs, binding, frozen analysis.
Session 22, UNTESTED.

Registration: lab/confirm/P2b_REGISTRATION.md. Own manifest (lab/confirm/P2b_manifest.json), fresh seeds, own splits (P1 construction,
confirm_splits.build with experiment id 2, so no stream is shared with P1), own raw directory and bindings (lab/tools/bound_block.py).
Per seed s: two models (arms F, G), add 113, 4000 steps (P2 failed because 3/50 G models had not generalised at 2000), model_final.pt saved.
Measure as P2 (EXP-051/055 helpers through confirm_p2, unchanged): remove E = 0.5 * E_ctrl of W_E energy from the own targets and,
separately, from the control set; loss on the common test set (pairs in neither split of the seed).
PRIMARY: R_s = mean over the two arms of log(L_after_own) - log(L_after_ctrl); one-sided one-sample t-test of mean R > 0; Holm in the
session-22 family {N28-H1, N28-H2, P2b} with the N28 hypotheses as p = 1 placeholders (worst case, 3p).
After the Codex review (s22): (a) every split and target set is rebuilt with confirm_splits.build and must match exactly, else the whole
analysis stops; (b) ANY technical failure (run missing, unbound, not loadable, non-finite loss/R/D) makes P2b "nicht auswertbar";
(c) the only scientific exclusion is base accuracy < ACC_MIN in either arm (the claim is conditional on it; an all-seed sensitivity
analysis is reported); (d) the dose is E = min(0.5 * E_ctrl, E_own), always feasible (capped cases are counted).
"nicht auswertbar" also if fewer than MIN_VALID_FRAC of the planned seeds are eligible; otherwise "bestätigt" = Holm-p < 0.05 and lower
95 % bootstrap bound of mean R >= log(1.05).

  python lab/tools/confirm_p2b.py --hash-code | --splits M | --jobs M | --run M -- <cmd> | --analyze M | --selftest
"""
from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
import confirm_p1 as c1  # noqa: E402  (read-only reuse: interp, t-test, bootstrap, holm)
import confirm_p2 as p2  # noqa: E402  (read-only reuse: EXP-051/055 helpers, load_model_bytes)
import confirm_splits as cs  # noqa: E402
from bound_block import Block, selftest_binding, sha  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "p2b_raw"
BIND = LAB / "confirm" / "p2b_bindings"
SPL = LAB / "confirm" / "p2b_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
TASK, F_PRIMARY, ACC_MIN, ALPHA, MIN_VALID_FRAC = {"task": "add", "p": 113}, 0.5, 0.9, 0.05, 0.9
MIN_EFFECT = float(np.log(1.05))
REGISTERED = {"experiment": 2, "eps": 2.0, "seeds": list(range(2000, 2100)), "steps": 4000, "device": "cuda", "threads": 1}
CODE_FILES = ("lab/tools/confirm_p2b.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_p2.py",
              "lab/tools/confirm_splits.py", "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py",
              "lab/experiments/EXP-001-freq-ban/freq_ban.py", "lab/experiments/EXP-043-generalize-steering/make_split.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py",
              "lab/experiments/EXP-051-functional-ablation/analyze.py", "lab/experiments/EXP-055-ablation-dose/analyze.py")


def stem(s: int, arm: str) -> str:
    return f"p2b_seed{s}_{arm}"


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, a)}.npy" for s in man["seeds"] for a in "FG"]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("P2b splits exist already: never overwrite")
    for s in man["seeds"]:
        T = cs.target_sets(man["experiment"], TASK["task"], TASK["p"], s)
        for a in "FG":
            idx, targ = cs.build(man["experiment"], TASK["task"], TASK["p"], s, a, man["eps"])
            assert targ == T[a]
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, idx.astype(np.int64))
            with open(SPL / f"{stem(s, a)}.json", "x", encoding="utf-8") as f:
                json.dump({"seed": s, "arm": a, "targets": T[a], "other_targets": T["G" if a == "F" else "F"], "n": int(len(idx)),
                           "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(man: dict, s: int) -> str | None:
    """Codex s22 blocker 1: rebuild both splits and target sets and compare with the files the analysis reads."""
    T = cs.target_sets(man["experiment"], TASK["task"], TASK["p"], s)
    for a in "FG":
        idx, targ = cs.build(man["experiment"], TASK["task"], TASK["p"], s, a, man["eps"])
        f, j = SPL / f"{stem(s, a)}.npy", SPL / f"{stem(s, a)}.json"
        if not f.exists() or not j.exists():
            return f"{stem(s, a)}: split file missing"
        meta = json.loads(j.read_text(encoding="utf-8"))
        same = (np.array_equal(np.load(f), idx.astype(np.int64)) and meta.get("targets") == targ == T[a]
                and meta.get("other_targets") == T["G" if a == "F" else "F"] and meta.get("seed") == s)
        if not same:
            return f"{stem(s, a)}: differs from the deterministic rebuild"
    return None


def trainer_jobs(man: dict) -> list[str]:
    st = man["steps"]
    return [f"{c1.interp(man)} {FB} --seed {s} --condition baseline --steps {st} --threads {man['threads']} --device {man['device']} "
            f"--split-file lab/confirm/p2b_splits/{stem(s, a)}.npy --spectra-at 250,500,1000,2000,{st} --save-model --out-root lab/confirm/p2b_raw"
            for s in man["seeds"] for a in "FG"]


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban: --split-file without --test-file, add 113 -> EXP-016 (no task suffix); GPU suffix."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    dev = g("--device") or "cpu"
    return f"EXP-016_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}" + ("" if dev == "cpu" else f"_dev{dev}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_p2b", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_p2b.py")


# ---------------------------------------------------------------- analysis
def arm_row(man: dict, s: int, arm: str, T: dict, common: np.ndarray, B: np.ndarray) -> dict | str:
    e51, e55 = p2.e51, p2.e55
    split = SPL / f"{stem(s, arm)}.npy"
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--split-file", str(split)]
    d = run_dir(cmd)
    if not d.exists():
        return "fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"defekt: {why}"
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=man["steps"], split_file=split,
                           config={"p": TASK["p"], "task": TASK["task"]}, files=("model_final.pt",)))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(split):
        return f"defekt after load: {why or 'split bytes differ'}"
    try:
        m = p2.load_model_bytes(BLOCK.bound_bytes(man, L.path / "model_final.pt"))
    except ValueError as ex:
        return f"defekt: {ex}"
    W = m.W_E.detach().numpy().astype(np.float64)[:e51.P]
    base = e55.evaluate(m, None, common)
    other = "G" if arm == "F" else "F"
    ctrl = e51.control_set(T[arm], T[other])
    e_own, e_ctrl = e51.energy(W, B, T[arm]), e51.energy(W, B, ctrl)
    E = min(F_PRIMARY * e_ctrl, e_own)                  # Codex s22 high 3: always feasible, no selection on the energy geometry
    row = {"base": base, "energy_own": e_own, "energy_ctrl": e_ctrl, "capped": bool(e_own < F_PRIMARY * e_ctrl)}
    ev_o = e55.evaluate(m, e51.remove_energy(W, B, T[arm], E), common)
    ev_c = e55.evaluate(m, e51.remove_energy(W, B, ctrl, E), common)
    return {**row, "E": E, "L_own": ev_o["loss"], "L_ctrl": ev_c["loss"],
            "dL_own": ev_o["loss"] - base["loss"], "dL_ctrl": ev_c["loss"] - base["loss"]}


def seed_row(man: dict, s: int, B: np.ndarray) -> dict:
    r: dict = {"seed": s, "valid": False}
    T = {a: json.loads((SPL / f"{stem(s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
    trains = [np.load(SPL / f"{stem(s, a)}.npy") for a in "FG"]
    common = np.setdiff1d(np.arange(TASK["p"] ** 2), np.union1d(*trains))
    arms = {}
    for arm in "FG":
        a = arm_row(man, s, arm, T, common, B)
        if isinstance(a, str):
            r.update({"reason": f"{arm}: {a}", "technical": True})
            return r
        arms[arm] = a
    r.update({"arms": arms, "n_common_test": int(len(common)), "base_acc": {a: v["base"]["acc"] for a, v in arms.items()}})
    return {**r, **validity(arms)}


def validity(arms: dict) -> dict:
    """Numerical failure is technical (Codex s22 medium 4); R is also computed for non-generalised seeds (sensitivity)."""
    losses = [v[k] for v in arms.values() for k in ("L_own", "L_ctrl")] + [v["base"]["loss"] for v in arms.values()]
    if not all(np.isfinite(x) and x > 0 for x in losses):
        return {"valid": False, "technical": True, "reason": "a loss is not finite and positive"}
    R = float(np.mean([np.log(v["L_own"]) - np.log(v["L_ctrl"]) for v in arms.values()]))
    D = float(np.mean([v["dL_own"] - v["dL_ctrl"] for v in arms.values()]))
    if not (np.isfinite(R) and np.isfinite(D)):
        return {"valid": False, "technical": True, "reason": "R or D not finite"}
    if not all(v["base"]["acc"] >= ACC_MIN for v in arms.values()):
        return {"valid": False, "technical": False, "reason": f"base accuracy < {ACC_MIN}", "R_all": R}
    return {"valid": True, "technical": False, "R": R, "R_all": R, "D": D}


def verdict(R: np.ndarray, n_planned: int, rng: np.random.Generator, min_effect: float = MIN_EFFECT, n_technical: int = 0) -> dict:
    if n_technical > 0 or len(R) < MIN_VALID_FRAC * n_planned or len(R) < 3:
        return {"n_valid": int(len(R)), "n_technical": n_technical, "verdict": "nicht auswertbar"}
    tt = c1.t_test_secondary(R)
    ph = c1.holm({"P2b": tt["p_one_sided"], "_N28H1": 1.0, "_N28H2": 1.0})["P2b"]
    ci = c1.boot_ci(R, rng)
    ok = ph < ALPHA and ci[0] >= min_effect
    return {"n_valid": int(len(R)), "mean": float(R.mean()), "sd": float(R.std(ddof=1)), "t": tt["t"], "p": tt["p_one_sided"],
            "p_holm_worstcase": ph, "ci95": ci, "n_positive": int((R > 0).sum()),
            "d_z": float(R.mean() / R.std(ddof=1)) if R.std(ddof=1) > 0 else None, "verdict": "bestätigt" if ok else "nicht bestätigt"}


def analyze(manifest: Path) -> None:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(man, s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"P2b splits differ from the registered construction, confirmation void: {bad[:3]}")
    B = p2.e51.basis()
    rows = [seed_row(man, s, B) for s in man["seeds"]]
    R = np.array([r["R"] for r in rows if r["valid"]])
    D = np.array([r["D"] for r in rows if r["valid"]])
    R_all = np.array([r["R_all"] for r in rows if "R_all" in r])
    n, n_tech = len(man["seeds"]), sum(1 for r in rows if r.get("technical"))
    out = {"manifest_commit": man["commit"], "f_primary": F_PRIMARY, "min_effect_R": MIN_EFFECT, "n_planned": n,
           "eligibility": {"n_valid": int(len(R)), "n_technical": n_tech,
                           "not_generalised": sum(1 for r in rows if r.get("reason", "").startswith("base accuracy")),
                           "n_capped_arms": sum(v["capped"] for r in rows for v in r.get("arms", {}).values())},
           **verdict(R, n, np.random.default_rng(22), n_technical=n_tech),
           "secondary_D_raw": {k: v for k, v in verdict(D, n, np.random.default_rng(23), 0.0, n_tech).items() if k != "verdict"},
           "sensitivity_R_all_seeds": {"n": int(len(R_all)), "mean": float(R_all.mean()) if len(R_all) else None,
                                       "ci95": c1.boot_ci(R_all, np.random.default_rng(24)) if len(R_all) > 1 else None},
           "rows": rows}
    (LAB / "confirm" / "P2b_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    for bad in ({"seeds": list(range(2000, 2099))}, {"steps": 4000.0}, {"eps": 2}, {"experiment": 1}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    assert len(tj) == 200 and len(set(tj)) == 200 and all("p2b_raw" in j and "--save-model" in j and "--steps 4000" in j for j in tj)
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert ids[0] == "EXP-016_baseline_seed2000_thr1_p2b_seed2000_F_devcuda" and ids[1].endswith("p2b_seed2000_G_devcuda"), ids[:2]
    assert len(set(ids)) == 200
    BLOCK.check_job(man, shlex.split(tj[0]))
    T = cs.target_sets(2, "add", 113, 2000)
    T1 = cs.target_sets(1, "add", 113, 2000)
    assert not set(T["F"]) & set(T["G"]) and T != T1           # own stream, not P1's
    base = {"acc": 1.0, "loss": 0.01}
    good = {a: {"base": base, "capped": False, "L_own": 0.02, "L_ctrl": 0.01, "dL_own": 0.01, "dL_ctrl": 0.0} for a in "FG"}
    v = validity(good)
    assert v["valid"] and abs(v["R"] - np.log(2)) < 1e-12 and not v["technical"]
    ng = validity({**good, "G": {**good["G"], "base": {"acc": 0.8, "loss": 1.0}}})
    assert not ng["valid"] and not ng["technical"] and "R_all" in ng
    nf = validity({**good, "F": {**good["F"], "L_own": float("inf")}})
    assert not nf["valid"] and nf["technical"]
    assert validity({**good, "F": {**good["F"], "base": {"acc": 1.0, "loss": float("nan")}}})["technical"]
    rng = np.random.default_rng(0)
    assert verdict(np.full(89, 0.2), 100, rng)["verdict"] == "nicht auswertbar"
    assert verdict(np.linspace(0.05, 0.25, 99), 100, rng, n_technical=1)["verdict"] == "nicht auswertbar"   # any technical failure
    x = verdict(np.linspace(0.05, 0.25, 90), 100, rng)
    assert x["verdict"] == "bestätigt" and abs(x["p_holm_worstcase"] - 3 * x["p"]) < 1e-12, x
    assert verdict(np.full(100, 0.03) + np.linspace(-0.01, 0.01, 100), 100, rng)["verdict"] == "nicht bestätigt"   # below log(1.05)
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    idx, targ = cs.build(2, "add", 113, 2000, "F", 2.0)
    assert len(idx) == int(round(0.3 * 113 * 113)) and targ == T["F"]
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    p2.e55.selftest()
    print("[confirm_p2b] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
