"""P2e confirmation (FINDINGS programme A, generalisation of P2d to mul 113 and add 97): splits, jobs, binding, frozen analysis. Session 23 (selftest ok; revised after Codex review s23).

Registration: lab/confirm/P2e_REGISTRATION.md. As confirm_p2d (experiment id 5, fresh seeds 2270-2289, one split pair F/G per task and seed),
but for the tasks mul 113 and add 97, STEPS = 8000 with --stop-after-gen 8000 (EXP-066: 24/50 add-97 P1 models below 0.9 at 2000 steps).
Measure (EXP-066, the P2d measure in the group basis): number rows X of W_E in group order (add 97: a = 0..96; mul 113: g^i, i = 0..111);
u_S = P_S X / ||P_S X||, X' = X - delta * u_S, delta = REL_DELTA * ||X|| for every S; drop_S = mean correct-class logit margin on the pairs in
neither split before minus after. N_CTRL control sets of 5 frequencies (EXP-066 pool, RNG [5, task, p, seed, arm]).
PRIMARY per task and seed: D_s = mean over the two arms of (drop_own - mean drop_ctrl). One family {mul113, add97}, Holm, one-sided t-test,
95 % bootstrap CI; per task "bestätigt" = no technical failure (incl. load/forward exceptions), Holm p < 0.05 and CI lower bound
>= MIN_EFFECT (0.05 logit units). Primary sample = ALL planned seeds (as N29, Codex s23: an accuracy gate is outcome-related); the subset with
base accuracy >= 0.9 in both arms is reported descriptively without a verdict label.
"""
from __future__ import annotations

import importlib.util
import json
import shlex
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
import confirm_p1 as c1  # noqa: E402  (read-only reuse: interp, t-test, bootstrap, holm)
import confirm_splits as cs  # noqa: E402
from bound_block import Block, selftest_binding, sha  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "p2e_raw"
BIND = LAB / "confirm" / "p2e_bindings"
SPL = LAB / "confirm" / "p2e_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
E66_FILE = "lab/experiments/EXP-066-p2d-other-tasks/analyze.py"
ACC_MIN, ALPHA, MIN_EFFECT, REL_DELTA, N_CTRL = 0.9, 0.05, 0.05, 0.02, 4
REGISTERED = {"experiment": 5, "eps": 2.0, "seeds": list(range(2270, 2290)), "tasks": [["mul", 113], ["add", 97]], "steps": 8000,
              "device": "cuda", "threads": 1}
CODE_FILES = ("lab/tools/confirm_p2e.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py",
              "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py", E66_FILE,
              "lab/experiments/EXP-001-freq-ban/freq_ban.py", "lab/experiments/EXP-043-generalize-steering/make_split.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py")

_e66 = None


def e66():
    global _e66
    if _e66 is None:
        spec = importlib.util.spec_from_file_location("exp066", ROOT / E66_FILE)
        _e66 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_e66)
    return _e66


def stem(task: str, p: int, s: int, arm: str) -> str:
    return f"p2e_{task}{p}_seed{s}_{arm}"


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(t, p, s, a)}.npy" for t, p in man["tasks"] for s in man["seeds"] for a in "FG"]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("P2e splits exist already: never overwrite")
    for task, p in man["tasks"]:
        for s in man["seeds"]:
            T = cs.target_sets(man["experiment"], task, p, s)
            for a in "FG":
                idx, targ = cs.build(man["experiment"], task, p, s, a, man["eps"])
                assert targ == T[a]
                with open(SPL / f"{stem(task, p, s, a)}.npy", "xb") as f:
                    np.save(f, idx.astype(np.int64))
                with open(SPL / f"{stem(task, p, s, a)}.json", "x", encoding="utf-8") as f:
                    json.dump({"seed": s, "task": task, "p": p, "arm": a, "targets": T[a], "other_targets": T["G" if a == "F" else "F"],
                               "n": int(len(idx)), "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(man: dict, task: str, p: int, s: int) -> str | None:
    T = cs.target_sets(man["experiment"], task, p, s)
    for a in "FG":
        idx, targ = cs.build(man["experiment"], task, p, s, a, man["eps"])
        f, j = SPL / f"{stem(task, p, s, a)}.npy", SPL / f"{stem(task, p, s, a)}.json"
        if not f.exists() or not j.exists():
            return f"{stem(task, p, s, a)}: split file missing"
        meta = json.loads(j.read_text(encoding="utf-8"))
        if not (np.array_equal(np.load(f), idx.astype(np.int64)) and meta.get("targets") == targ == T[a]
                and meta.get("other_targets") == T["G" if a == "F" else "F"] and meta.get("seed") == s):
            return f"{stem(task, p, s, a)}: differs from the deterministic rebuild"
    return None


def trainer_jobs(man: dict) -> list[str]:
    st = man["steps"]
    return [f"{c1.interp(man)} {FB} --seed {s} --condition baseline --steps {st} --threads {man['threads']} --device {man['device']} "
            f"--p {p} --task {task} --split-file lab/confirm/p2e_splits/{stem(task, p, s, a)}.npy "
            f"--spectra-at 500,1000,2000,4000,{st} --stop-after-gen {st} --save-model --out-root lab/confirm/p2e_raw"
            for task, p in man["tasks"] for s in man["seeds"] for a in "FG"]


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban: --split-file without --test-file and (p, task) != (113, add) -> EXP-043 with task suffix; GPU suffix."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    dev = g("--device") or "cpu"
    return (f"EXP-043_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}_{g('--task')}{g('--p')}"
            + ("" if dev == "cpu" else f"_dev{dev}"))


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_p2e", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_p2e.py")


# ---------------------------------------------------------------- analysis
def arm_row(man: dict, task: str, p: int, s: int, arm: str, T: dict, common: np.ndarray) -> dict | str:
    split = SPL / f"{stem(task, p, s, arm)}.npy"
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--p", str(p), "--task", task,
           "--split-file", str(split)]
    d = run_dir(cmd)
    if not d.exists():
        return "fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"defekt: {why}"
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=man["steps"], split_file=split, config={"p": p, "task": task},
                           files=("model_final.pt",)))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(split):
        return f"defekt after load: {why or 'split bytes differ'}"
    try:
        return measure(task, p, s, arm, T, common, BLOCK.bound_bytes(man, L.path / "model_final.pt"))
    except Exception as ex:                    # Codex s23 point 1: any load/forward failure is technical, never an abort
        return f"defekt: {type(ex).__name__}: {ex}"


def measure(task: str, p: int, s: int, arm: str, T: dict, common: np.ndarray, data: bytes) -> dict:
    m = e66().load_model(task, p, data)
    n, elem = e66().group(task, p)
    elem = np.arange(p) if elem is None else elem
    X = m.W_E.detach().numpy().astype(np.float64)[elem]
    other = "G" if arm == "F" else "F"
    ctrl = e66().control_sets(T[arm], T[other], n, [5, ord(task[0]), p, s, ord(arm)])
    base = e66().evaluate(m, task, p, None, elem, common)
    delta = REL_DELTA * float(np.linalg.norm(X))
    dr = {}
    for k, S in {"own": T[arm]} | {f"c{i}": c for i, c in enumerate(ctrl)}.items():
        PS = e66().proj(X, S)
        dr[k] = base["margin"] - e66().evaluate(m, task, p, X - delta * PS / np.linalg.norm(PS), elem, common)["margin"]
    return {"base": base, "drop_own": dr["own"], "drop_ctrl": [dr[f"c{i}"] for i in range(N_CTRL)], "ctrl_sets": ctrl}


def validity(arms: dict) -> dict:
    vals = [v["drop_own"] for v in arms.values()] + [x for v in arms.values() for x in v["drop_ctrl"]] + [v["base"]["margin"] for v in arms.values()]
    if not all(np.isfinite(x) for x in vals):
        return {"valid": False, "technical": True, "reason": "non-finite margin"}
    D = float(np.mean([v["drop_own"] - np.mean(v["drop_ctrl"]) for v in arms.values()]))
    return {"valid": True, "technical": False, "D": D, "generalised": all(v["base"]["acc"] >= ACC_MIN for v in arms.values())}


def seed_row(man: dict, task: str, p: int, s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    T = {a: json.loads((SPL / f"{stem(task, p, s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
    trains = [np.load(SPL / f"{stem(task, p, s, a)}.npy") for a in "FG"]
    common = np.setdiff1d(np.arange(p * p), np.union1d(*trains))
    arms = {}
    for arm in "FG":
        a = arm_row(man, task, p, s, arm, T, common)
        if isinstance(a, str):
            return {**r, "reason": f"{arm}: {a}", "technical": True}
        arms[arm] = a
    return {**r, "arms": arms, **validity(arms)}


def stats(D: np.ndarray, rng: np.random.Generator) -> dict:
    tt = c1.t_test_secondary(D)
    return {"n": int(len(D)), "mean": float(D.mean()), "sd": float(D.std(ddof=1)), "t": tt["t"], "p": tt["p_one_sided"],
            "ci95": c1.boot_ci(D, rng), "n_positive": int((D > 0).sum())}


def verdict(rows_by_task: dict[str, list[dict]], n_planned: int, rng: np.random.Generator) -> dict:
    out, ps = {}, {}
    for k, rows in rows_by_task.items():
        n_tech = sum(1 for r in rows if r.get("technical"))
        if n_tech > 0 or len(rows) != n_planned or n_planned < 3:
            out[k] = {"n": len(rows), "n_technical": n_tech, "verdict": "nicht auswertbar"}
            ps[k] = 1.0                                   # counts in the family as a worst-case placeholder
            continue
        out[k] = {**stats(np.array([r["D"] for r in rows]), rng), "n_technical": 0}
        g = np.array([r["D"] for r in rows if r["generalised"]])
        out[k]["n_generalised"] = int(len(g))
        out[k]["descriptive_generalised_only"] = stats(g, rng) if len(g) >= 3 else None     # no verdict label
        ps[k] = out[k]["p"]
    ph = c1.holm(ps)
    for k in out:
        if "p" in out[k]:
            out[k]["p_holm"] = ph[k]
            out[k]["verdict"] = "bestätigt" if ph[k] < ALPHA and out[k]["ci95"][0] >= MIN_EFFECT else "nicht bestätigt"
    return out


def analyze(manifest: Path) -> None:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for t, p in man["tasks"] for m in (split_mismatch(man, t, p, s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"P2e splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = {f"{t}{p}": [seed_row(man, t, p, s) for s in man["seeds"]] for t, p in man["tasks"]}
    out = {"manifest_commit": man["commit"], "min_effect": MIN_EFFECT, "rel_delta": REL_DELTA, "n_planned": len(man["seeds"]),
           "tasks": verdict(rows, len(man["seeds"]), np.random.default_rng(5)),
           "rows": rows}
    (LAB / "confirm" / "P2e_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    for bad in ({"seeds": list(range(2270, 2289))}, {"steps": 8000.0}, {"experiment": 4}, {"tasks": [["mul", 113]]}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    assert len(tj) == 80 and len(set(tj)) == 80 and all("p2e_raw" in j and "--save-model" in j and "\\" not in j for j in tj)
    for j in tj:
        c = shlex.split(j)
        assert int(c[c.index("--stop-after-gen") + 1]) >= int(c[c.index("--steps") + 1]), j
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert ids[0] == "EXP-043_baseline_seed2270_thr1_p2e_mul113_seed2270_F_mul113_devcuda", ids[0]
    assert ids[40] == "EXP-043_baseline_seed2270_thr1_p2e_add97_seed2270_F_add97_devcuda", ids[40]
    assert len(set(ids)) == 80
    for task, p in REGISTERED["tasks"]:
        T = cs.target_sets(5, task, p, 2270)
        assert T != cs.target_sets(4, task, p, 2270) and not set(T["F"]) & set(T["G"])
    assert cs.target_sets(5, "mul", 113, 2270) != cs.target_sets(5, "add", 113, 2270)
    good = {a: {"base": {"acc": 1.0, "margin": 5.0}, "drop_own": 0.3, "drop_ctrl": [0.0, 0.01, -0.01, 0.0]} for a in "FG"}
    v = validity(good)
    assert v["valid"] and v["generalised"] and abs(v["D"] - 0.3) < 1e-12
    assert validity({**good, "F": {**good["F"], "drop_own": float("nan")}})["technical"]
    ng = validity({**good, "G": {**good["G"], "base": {"acc": 0.5, "margin": 1.0}}})
    assert ng["valid"] and not ng["generalised"] and abs(ng["D"] - 0.3) < 1e-12
    rng = np.random.default_rng(0)
    mk = lambda D, g=True: {"valid": True, "technical": False, "D": D, "generalised": g}   # noqa: E731
    good_rows = [mk(0.15 + 0.005 * i) for i in range(20)]
    w = verdict({"mul113": good_rows, "add97": good_rows}, 20, rng)
    assert w["mul113"]["verdict"] == "bestätigt" and w["add97"]["verdict"] == "bestätigt", w
    w = verdict({"mul113": good_rows, "add97": good_rows[:15] + [mk(0.0, False)] * 5}, 20, rng)   # non-generalised seeds stay in
    assert w["add97"]["n"] == 20 and w["add97"]["n_generalised"] == 15 and "verdict" not in w["add97"]["descriptive_generalised_only"]
    assert w["add97"]["mean"] < w["add97"]["descriptive_generalised_only"]["mean"]
    w = verdict({"mul113": good_rows, "add97": good_rows[:19]}, 20, rng)
    assert w["add97"]["verdict"] == "nicht auswertbar" and w["mul113"]["verdict"] == "bestätigt"
    assert abs(w["mul113"]["p_holm"] - min(1.0, 2 * w["mul113"]["p"])) < 1e-12        # placeholder p = 1 keeps the family at two
    w = verdict({"mul113": [mk(0.0 + 0.004 * i) for i in range(20)], "add97": good_rows}, 20, rng)
    assert w["mul113"]["verdict"] == "nicht bestätigt"
    w = verdict({"mul113": good_rows[:19] + [{"seed": 1, "valid": False, "technical": True}], "add97": good_rows}, 20, rng)
    assert w["mul113"]["verdict"] == "nicht auswertbar"
    # semantics of the imported measure (Codex s23 point 5): discrete-log order, projection, Nyquist-free pool
    n, elem = e66().group("mul", 113)
    assert n == 112 and elem[0] == 1 and elem[1] == 3 and sorted(elem.tolist()) == list(range(1, 113))
    j = np.arange(n)
    X = np.stack([np.cos(2 * np.pi * 55 * j / n), np.sin(2 * np.pi * 7 * j / n)], 1)
    assert np.allclose(e66().proj(X, [55]), X * [1, 0], atol=1e-10) and np.allclose(e66().proj(X, [7]), X * [0, 1], atol=1e-10)
    cs5 = e66().control_sets([1, 2, 3, 4, 5], [6, 7, 8, 9, 10], 112, [5, 1])
    assert all(max(c) <= 55 and not set(c) & {1, 2, 3, 4, 5, 6, 7, 8, 9, 10} for c in cs5)
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    loaded = {Path(m.__file__).resolve().relative_to(ROOT.resolve()).as_posix() for m in list(sys.modules.values())
              if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to((ROOT / "lab").resolve())}
    assert loaded <= set(CODE_FILES), sorted(loaded - set(CODE_FILES))
    print("[confirm_p2e] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
