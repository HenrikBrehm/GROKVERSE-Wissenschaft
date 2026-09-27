"""P2d confirmation DRAFT (FINDINGS programme A, functional use; successor of P2c): splits, jobs, binding, frozen analysis. Session 22, UNTESTED,
NOT FROZEN. Registration draft: lab/confirm/P2d_REGISTRATION.md. Splits, jobs and binding as confirm_p2c (experiment id 4, fresh seeds 2230-2249,
4000 steps with --stop-after-gen 4000, model saved). Measure (EXP-065 exploration, Codex proposal s22): local sensitivity per EQUAL parameter
step. For S = own targets and N_CTRL control sets of 5 frequencies drawn from the P2 control pool (fixed RNG per seed and arm):
u_S = P_S W / ||P_S W|| with W = W_E[:113]; W' = W - delta * u_S, delta = REL_DELTA * ||W|| for every S. drop_S = mean correct-class logit margin
on the common test set before minus after. PRIMARY per seed: D_s = mean over the two arms of (drop_own - mean drop_ctrl) (always defined).
One-sided t-test of mean D > 0; "bestätigt" = no technical failure, >= 90 % eligible (base accuracy >= 0.9 in both arms), p < 0.05 and lower
95 % bootstrap bound of mean D >= MIN_EFFECT (0.05 logit units). Multiplicity: own family (P2d alone) unless the registration says otherwise.
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

RAW = LAB / "confirm" / "p2d_raw"
BIND = LAB / "confirm" / "p2d_bindings"
SPL = LAB / "confirm" / "p2d_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
TASK, ACC_MIN, ALPHA, MIN_VALID_FRAC = {"task": "add", "p": 113}, 0.9, 0.05, 0.9
MIN_EFFECT, REL_DELTA, N_CTRL, P = 0.05, 0.02, 4, 113          # logit-margin units; step = 2 % of ||W_E[:113]|| (EXP-065)
REGISTERED = {"experiment": 4, "eps": 2.0, "seeds": list(range(2230, 2250)), "steps": 4000, "device": "cuda", "threads": 1}
CODE_FILES = ("lab/tools/confirm_p2d.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_p2.py",
              "lab/tools/confirm_splits.py", "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py",
              "lab/experiments/EXP-001-freq-ban/freq_ban.py", "lab/experiments/EXP-043-generalize-steering/make_split.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py",
              "lab/experiments/EXP-051-functional-ablation/analyze.py", "lab/experiments/EXP-055-ablation-dose/analyze.py",
              "lab/experiments/EXP-061-grad-alignment/analyze.py", "lab/experiments/EXP-059-momentum-exposure/analyze.py",
              "lab/experiments/EXP-056-overlap-persistence/analyze.py")


def stem(s: int, arm: str) -> str:
    return f"p2d_seed{s}_{arm}"


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, a)}.npy" for s in man["seeds"] for a in "FG"]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("P2d splits exist already: never overwrite")
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
            f"--split-file lab/confirm/p2d_splits/{stem(s, a)}.npy --spectra-at 250,500,1000,2000,{st} --stop-after-gen {st} --save-model "
            f"--out-root lab/confirm/p2d_raw"
            for s in man["seeds"] for a in "FG"]


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban: --split-file without --test-file, add 113 -> EXP-016 (no task suffix); GPU suffix."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    dev = g("--device") or "cpu"
    return f"EXP-016_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}" + ("" if dev == "cpu" else f"_dev{dev}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_p2d", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_p2d.py")


# ---------------------------------------------------------------- analysis
_g61 = None


def g61():
    global _g61
    if _g61 is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("exp061", LAB / "experiments/EXP-061-grad-alignment/analyze.py")
        _g61 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_g61)
    return _g61


def control_sets(pool: list[int], s: int, arm: str) -> list[list[int]]:
    rng = np.random.default_rng([4, s, ord(arm)])
    return [sorted(int(k) for k in rng.choice(sorted(pool), 5, replace=False)) for _ in range(N_CTRL)]


def drops(m, W: np.ndarray, sets: dict[str, list[int]], test: np.ndarray, delta: float) -> dict[str, float]:
    base = p2.e55.evaluate(m, None, test)["margin"]
    out = {}
    for k, S in sets.items():
        PS = g61().project(W, S)
        out[k] = base - p2.e55.evaluate(m, W - delta * PS / np.linalg.norm(PS), test)["margin"]
    return out


def arm_row(man: dict, s: int, arm: str, T: dict, common: np.ndarray) -> dict | str:
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
    W = m.W_E.detach().numpy().astype(np.float64)[:P]
    other = "G" if arm == "F" else "F"
    sets = {"own": T[arm]} | {f"c{i}": c for i, c in enumerate(control_sets(p2.e51.control_set(T[arm], T[other]), s, arm))}
    dr = drops(m, W, sets, common, REL_DELTA * float(np.linalg.norm(W)))
    base = p2.e55.evaluate(m, None, common)
    return {"base": base, "drop_own": dr["own"], "drop_ctrl": [dr[f"c{i}"] for i in range(N_CTRL)], "ctrl_sets": [sets[f"c{i}"] for i in range(N_CTRL)]}


def seed_row(man: dict, s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    T = {a: json.loads((SPL / f"{stem(s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
    trains = [np.load(SPL / f"{stem(s, a)}.npy") for a in "FG"]
    common = np.setdiff1d(np.arange(TASK["p"] ** 2), np.union1d(*trains))
    arms = {}
    for arm in "FG":
        a = arm_row(man, s, arm, T, common)
        if isinstance(a, str):
            r.update({"reason": f"{arm}: {a}", "technical": True})
            return r
        arms[arm] = a
    r["arms"] = arms
    return {**r, **validity(arms)}


def validity(arms: dict) -> dict:
    vals = [v["drop_own"] for v in arms.values()] + [x for v in arms.values() for x in v["drop_ctrl"]] + [v["base"]["margin"] for v in arms.values()]
    if not all(np.isfinite(x) for x in vals):
        return {"valid": False, "technical": True, "reason": "non-finite margin"}
    D = float(np.mean([v["drop_own"] - np.mean(v["drop_ctrl"]) for v in arms.values()]))
    if not all(v["base"]["acc"] >= ACC_MIN for v in arms.values()):
        return {"valid": False, "technical": False, "reason": f"base accuracy < {ACC_MIN}", "D_all": D}
    return {"valid": True, "technical": False, "D": D, "D_all": D}


def verdict(D: np.ndarray, n_planned: int, rng: np.random.Generator, n_technical: int = 0) -> dict:
    if n_technical > 0 or len(D) < MIN_VALID_FRAC * n_planned or len(D) < 3:
        return {"n_valid": int(len(D)), "n_technical": n_technical, "verdict": "nicht auswertbar"}
    tt = c1.t_test_secondary(D)
    ci = c1.boot_ci(D, rng)
    ok = tt["p_one_sided"] < ALPHA and ci[0] >= MIN_EFFECT
    return {"n_valid": int(len(D)), "mean": float(D.mean()), "sd": float(D.std(ddof=1)), "t": tt["t"], "p": tt["p_one_sided"], "ci95": ci,
            "n_positive": int((D > 0).sum()), "verdict": "bestätigt" if ok else "nicht bestätigt"}


def analyze(manifest: Path) -> None:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(man, s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"P2d splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [seed_row(man, s) for s in man["seeds"]]
    D = np.array([r["D"] for r in rows if r["valid"]])
    D_all = np.array([r["D_all"] for r in rows if "D_all" in r])
    n_tech = sum(1 for r in rows if r.get("technical"))
    out = {"manifest_commit": man["commit"], "min_effect": MIN_EFFECT, "rel_delta": REL_DELTA, "n_planned": len(man["seeds"]),
           "n_technical": n_tech, **verdict(D, len(man["seeds"]), np.random.default_rng(42), n_tech),
           "sensitivity_D_all_seeds": {"n": int(len(D_all)), "mean": float(D_all.mean()) if len(D_all) else None}, "rows": rows}
    (LAB / "confirm" / "P2d_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    for bad in ({"seeds": list(range(2230, 2249))}, {"steps": 4000.0}, {"experiment": 3}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    assert len(tj) == 40 and len(set(tj)) == 40 and all("p2d_raw" in j and "--save-model" in j for j in tj)
    for j in tj:
        c = shlex.split(j)
        assert int(c[c.index("--stop-after-gen") + 1]) >= int(c[c.index("--steps") + 1]), j
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert ids[0] == "EXP-016_baseline_seed2230_thr1_p2d_seed2230_F_devcuda" and len(set(ids)) == 40
    T = cs.target_sets(4, "add", 113, 2230)
    assert T != cs.target_sets(3, "add", 113, 2230) and not set(T["F"]) & set(T["G"])
    pool = p2.e51.control_set(T["F"], T["G"])
    cs1 = control_sets(pool, 2230, "F")
    assert cs1 == control_sets(pool, 2230, "F") and cs1 != control_sets(pool, 2230, "G") and all(len(x) == 5 and set(x) <= set(pool) for x in cs1)
    good = {a: {"base": {"acc": 1.0, "margin": 5.0}, "drop_own": 0.3, "drop_ctrl": [0.0, 0.01, -0.01, 0.0]} for a in "FG"}
    v = validity(good)
    assert v["valid"] and abs(v["D"] - 0.3) < 1e-12
    assert validity({**good, "F": {**good["F"], "drop_own": float("nan")}})["technical"]
    ng = validity({**good, "G": {**good["G"], "base": {"acc": 0.5, "margin": 1.0}}})
    assert not ng["valid"] and not ng["technical"]
    rng = np.random.default_rng(0)
    assert verdict(np.full(17, 0.3), 20, rng)["verdict"] == "nicht auswertbar"
    assert verdict(np.linspace(0.2, 0.3, 20), 20, rng, n_technical=1)["verdict"] == "nicht auswertbar"
    assert verdict(np.linspace(0.2, 0.3, 20), 20, rng)["verdict"] == "bestätigt"
    assert verdict(np.linspace(0.0, 0.06, 20), 20, rng)["verdict"] == "nicht bestätigt"
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    print("[confirm_p2d] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
