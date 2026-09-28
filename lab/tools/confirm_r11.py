"""R11 confirmation (FINDINGS limit 2: lock-in K4 only confirmed at add 113; pilot EXP-044): does the early choice lock in
between 25 and 50 steps also for add mod 97 and mul mod 113? Session 43, UNTESTED BEYOND --selftest.

Registration: lab/confirm/R11_REGISTRATION_DRAFT.md. Protocol as EXP-044 (per task and seed: common held-out test set, two
engineered train sets F and G with disjoint target sets, EXP-043 construction in group coordinates, eps = 2, independent keys;
runs: pure F, pure G, F -> G at t = 25 and at t = 50, each followed by BUDGET = 2000 default steps). pi(t) = (L(t) - L(G)) /
(L(F) - L(G)), L = log[P(F targets) / P(G targets)] of the final W_E group power (EXP-044 pi_persistence definition).
Primary family (Holm over 6 = 2 tasks x 3, alpha 0.05), per task:
  H1  d = pi(50) - pi(25); one-sided t-test d > 0; 'bestätigt' = Holm p < 0.05 and bootstrap CI lower bound of d > 0
  H2  pi(50) - 0.5; one-sided t-test > 0 (at 50 more than half of the F bias persists); same criterion
  H3  0.5 - pi(25); one-sided t-test > 0 (at 25 the second split wins the larger part); same criterion
Validity: any technical failure -> whole block 'nicht auswertbar'. Seeds with L(F) - L(G) < 2 are excluded per task and counted;
more than MAX_EXCLUDED in a task -> that task's three hypotheses 'nicht auswertbar' (they leave the Holm family).

  python lab/tools/confirm_r11.py --hash-code | --splits M | --jobs M | --run M -- <cmd> | --analyze M | --selftest
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
sys.path.insert(0, str(LAB / "experiments/EXP-044-generalize-lockin"))
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
import confirm_p1 as c1  # noqa: E402  (read-only reuse: interp, t-test, bootstrap, holm)
from bound_block import Block, selftest_binding, sha  # noqa: E402
import make_splits as m44  # noqa: E402  (EXP-044 build: test / F / G per seed and task)
from make_split import target_set  # noqa: E402  (EXP-043 target sets)
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "r11_raw"
BIND = LAB / "confirm" / "r11_bindings"
SPL = LAB / "confirm" / "r11_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
BUDGET, ALPHA, HALF = 2000, 0.05, 0.5
MIN_LFLG, MAX_EXCLUDED = 2.0, 4
TASKS = (("add", 97), ("mul", 113))
SWITCH = (25, 50)
HYP = ("H1", "H2", "H3")
REGISTERED = {"seeds": list(range(3620, 3650)), "budget": 2000, "device": "cuda", "threads": 1,
              "tasks": [list(t) for t in TASKS], "switch_steps": list(SWITCH)}
CODE_FILES = ("lab/tools/confirm_r11.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_p2.py",
              "lab/tools/confirm_splits.py", "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py",
              "lab/experiments/EXP-001-freq-ban/freq_ban.py",
              "lab/experiments/EXP-044-generalize-lockin/make_splits.py",
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py")


# ---------------------------------------------------------------- splits and jobs
def stem(task: str, p: int, s: int, arm: str) -> str:
    return f"r11_{task}{p}_seed{s}_{'test' if arm == 'test' else 'train_' + arm}"


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(t, p, s, a)}.npy" for t, p in man["tasks"] for s in man["seeds"] for a in ("test", "F", "G")]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("R11 splits exist already: never overwrite")
    for task, p in man["tasks"]:
        for s in man["seeds"]:
            d = m44.build(s, task, p)
            assert len(d["F"]) == len(d["G"]) and not np.intersect1d(d["test"], np.union1d(d["F"], d["G"])).size
            for a in ("test", "F", "G"):
                with open(SPL / f"{stem(task, p, s, a)}.npy", "xb") as f:
                    np.save(f, d[a].astype(np.int64))
            meta = {"seed": s, "task": task, "p": p, "targets": {a: target_set(s, task, p, a) for a in "FG"},
                    "overlap_FG_train": int(np.intersect1d(d["F"], d["G"]).size), "manifest_commit": man["commit"]}
            with open(SPL / f"r11_{task}{p}_seed{s}.json", "x", encoding="utf-8") as f:
                json.dump(meta, f, indent=1)


def split_mismatch(task: str, p: int, s: int) -> str | None:
    d = m44.build(s, task, p)
    files = {a: SPL / f"{stem(task, p, s, a)}.npy" for a in ("test", "F", "G")}
    meta_f = SPL / f"r11_{task}{p}_seed{s}.json"
    if not meta_f.exists() or not all(f.exists() for f in files.values()):
        return f"{task}{p} seed {s}: split file missing"
    meta = json.loads(meta_f.read_text(encoding="utf-8"))
    if (not all(np.array_equal(np.load(f), d[a].astype(np.int64)) for a, f in files.items())
            or meta.get("targets") != {a: target_set(s, task, p, a) for a in "FG"}):
        return f"{task}{p} seed {s}: splits differ from the deterministic rebuild"
    return None


def trainer_jobs(man: dict) -> list[str]:
    pure, switch, bud = [], [], man["budget"]
    for task, p in man["tasks"]:
        for s in man["seeds"]:
            base = (f"{c1.interp(man)} {FB} --seed {s} --condition baseline --threads {man['threads']} --device {man['device']} "
                    f"--p {p} --task {task} --test-file lab/confirm/r11_splits/{stem(task, p, s, 'test')}.npy --out-root lab/confirm/r11_raw")
            f_, g_ = (f"lab/confirm/r11_splits/{stem(task, p, s, a)}.npy" for a in "FG")
            for first in (f_, g_):
                pure.append(f"{base} --steps {bud} --split-file {first} --spectra-at 50,250,{bud}")
            for t in man["switch_steps"]:
                switch.append(f"{base} --steps {t + bud} --split-file {f_} --switch-split-file {g_} --switch-step {t} "
                              f"--spectra-at {t},{t + 250},{t + bud}")
    return pure + switch


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban ids for p/task != 113/add: EXP-043 (split file) or EXP-044 (switch), '_{task}{p}', then _dev."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    if g("--switch-split-file") is None:
        rid = f"EXP-043_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}"
    else:
        rid = (f"EXP-044_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}_to_"
               f"{Path(g('--switch-split-file')).stem}_at{g('--switch-step')}")
    rid += f"_{g('--task')}{g('--p')}"
    dev = g("--device") or "cpu"
    return rid + ("" if dev == "cpu" else f"_dev{dev.replace(':', '')}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r11", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_r11.py")


# ---------------------------------------------------------------- analysis
_a43 = None


def a43():
    global _a43
    if _a43 is None:
        spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
        _a43 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_a43)
    return _a43


def one_run(man: dict, task: str, p: int, s: int, kind: str) -> np.ndarray | str:
    """Final W_E group power of one run (kind 'F', 'G' or a switch step as str) through the shared loader + R11 binding."""
    switch = kind not in ("F", "G")
    t = int(kind) if switch else 0
    first = "G" if kind == "G" else "F"
    sp, te = SPL / f"{stem(task, p, s, first)}.npy", SPL / f"{stem(task, p, s, 'test')}.npy"
    sw = SPL / f"{stem(task, p, s, 'G')}.npy" if switch else None
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--p", str(p), "--task", task,
           "--split-file", str(sp)] + (["--switch-split-file", str(sw), "--switch-step", str(t)] if switch else [])
    d, steps, tag = run_dir(cmd), man["budget"] + t, f"{task}{p}:{s}:{kind}"
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=steps, split_file=sp, test_file=te, switch_file=sw,
                           config={"p": p, "task": task, "arch": "transformer", "lr": 1e-3, "weight_decay": 1.0, "train_frac": 0.3,
                                   "beta1": 0.9, "beta2": 0.98, "lr_scale": 1.0, "pre_switch_betas": None},
                           snapshots_at=(steps,)))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(sp):
        return f"{tag}: defekt after load: {why or 'split bytes differ'}"
    if switch and L.res.get("switch_step") != t:
        return f"{tag}: defekt: switch_step does not match"
    if L.res.get("pre_switch_grad_every", 1) != 1 or L.res.get("pre_switch_update", "adam") != "adam":
        return f"{tag}: defekt: unexpected pre-switch option"
    try:
        end = a43().group_power(L.snapshot(steps), task, p)[0]
    except Exception as ex:   # any load/transform failure is technical, never an abort
        return f"{tag}: defekt: {type(ex).__name__}: {ex}"
    if not np.isfinite(end).all():
        return f"{tag}: defekt: non-finite values"
    return end


def seed_row(man: dict, task: str, p: int, s: int) -> dict:
    meta = json.loads((SPL / f"r11_{task}{p}_seed{s}.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["F"], meta["targets"]["G"]
    pw = {k: one_run(man, task, p, s, k) for k in ("F", "G") + tuple(str(t) for t in man["switch_steps"])}
    bad = [v for v in pw.values() if isinstance(v, str)]
    if bad:
        return {"seed": s, "valid": False, "technical": True, "reason": "; ".join(bad[:4])}
    lr = lambda x: float(np.log(x[[k - 1 for k in F]].sum() / x[[k - 1 for k in G]].sum()))   # noqa: E731
    LF, LG = lr(pw["F"]), lr(pw["G"])
    r: dict = {"seed": s, "technical": False, "LF_minus_LG": LF - LG, "valid": bool(LF - LG >= MIN_LFLG)}
    if r["valid"]:
        for t in man["switch_steps"]:
            r[f"pi_{t}"] = (lr(pw[str(t)]) - LG) / (LF - LG)
    return r


def stats(rows: list[dict]) -> dict[str, np.ndarray]:
    p25, p50 = np.array([r["pi_25"] for r in rows]), np.array([r["pi_50"] for r in rows])
    return {"H1": p50 - p25, "H2": p50 - HALF, "H3": HALF - p25}


def verdict(by_task: dict[str, list[dict]], n_planned: int, rng: np.random.Generator) -> dict:
    n_tech = sum(1 for rows in by_task.values() for r in rows if r.get("technical"))
    if n_tech > 0 or any(len(rows) != n_planned for rows in by_task.values()):
        return {"n_technical": n_tech, "verdict": "nicht auswertbar"}
    out: dict = {"n_technical": 0, "tasks": {}}
    X, p = {}, {}
    for task, rows in by_task.items():
        ok = [r for r in rows if r.get("valid")]
        n_excl = len(rows) - len(ok)
        info = {"n": len(ok), "n_excluded": n_excl}
        if n_excl > MAX_EXCLUDED or len(ok) < 3:
            info["verdict"] = "nicht auswertbar"
        else:
            st = stats(ok)
            for h in HYP:
                X[(task, h)] = st[h]
                p[f"{task}:{h}"] = c1.t_test_secondary(st[h])["p_one_sided"]
            info["pi_means"] = {t: float(np.mean([r[f"pi_{t}"] for r in ok])) for t in SWITCH}
        out["tasks"][task] = info
    ph = c1.holm(p) if p else {}
    for (task, h), x in X.items():
        ci = c1.boot_ci(x, rng)
        key = f"{task}:{h}"
        ok = ph[key] < ALPHA and ci[0] > 0
        out["tasks"][task][h] = {"mean": float(x.mean()), "sd": float(x.std(ddof=1)), "ci95": ci, "n_positive": int((x > 0).sum()),
                                 "p": p[key], "p_holm": ph[key], "verdict": "bestätigt" if ok else "nicht bestätigt"}
    conf = [f"{t}:{h}" for t in by_task for h in HYP if out["tasks"][t].get(h, {}).get("verdict") == "bestätigt"]
    out["reading"] = ("K4 verallgemeinert bestätigt (alle 6)" if len(conf) == 2 * len(HYP)
                      else ("teilweise: " + ", ".join(conf)) if conf else "nicht bestätigt")
    return out


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "R11_summary.json"
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(t, p, s) for t, p in man["tasks"] for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"R11 splits differ from the registered construction, confirmation void: {bad[:3]}")
    by_task = {f"{t}{p}": [seed_row(man, t, p, s) for s in man["seeds"]] for t, p in man["tasks"]}
    out = {"manifest_commit": man["commit"], "n_planned_per_task": len(man["seeds"]),
           "hypotheses": verdict(by_task, len(man["seeds"]), np.random.default_rng(11)), "rows": by_task}
    (LAB / "confirm" / "R11_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    for bad in ({"seeds": list(range(3620, 3649))}, {"budget": 2000.0}, {"threads": True}, {"tasks": [["add", 97]]},
                {"switch_steps": [25, 150]}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    assert len(tj) == 2 * 30 * 4 and len(set(tj)) == len(tj) and all("r11_raw" in j and "\\" not in j for j in tj)
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert len(set(ids)) == len(ids)
    assert ids[0] == "EXP-043_baseline_seed3620_thr1_r11_add97_seed3620_train_F_add97_devcuda", ids[0]
    sw = [i for i in ids if i.startswith("EXP-044_")]
    assert len(sw) == 120 and sw[0] == ("EXP-044_baseline_seed3620_thr1_r11_add97_seed3620_train_F_to_r11_add97_seed3620_train_G"
                                       "_at25_add97_devcuda"), sw[0]
    assert sum(i.endswith("_at50_mul113_devcuda") for i in ids) == 30
    assert all(j.startswith("python lab/tools/confirm_r11.py --run M -- ") for j in BLOCK.jobs(man, "M"))
    BLOCK.check_job(man, shlex.split(tj[0]))
    for foreign in (shlex.split(tj[0]) + ["--force"], [x if x != "3620" else "3621" for x in shlex.split(tj[0])]):
        try:
            BLOCK.check_job(man, foreign)
            raise AssertionError("foreign command accepted")
        except SystemExit:
            pass

    jit = lambda i: 0.02 * ((i * 7) % 5 - 2)   # noqa: E731
    mk = lambda p25, p50, i, valid=True: {"seed": i, "valid": valid, "technical": False, "pi_25": p25 + jit(i), "pi_50": p50 + jit(i + 2)}   # noqa: E731
    rng = np.random.default_rng(0)
    yes = {t: [mk(0.3, 0.8, i) for i in range(20)] for t in ("add97", "mul113")}
    v = verdict(yes, 20, rng)
    assert v["reading"] == "K4 verallgemeinert bestätigt (alle 6)", v
    no = {t: [mk(0.6, 0.45, i) for i in range(20)] for t in ("add97", "mul113")}
    v = verdict(no, 20, rng)
    assert v["reading"] == "nicht bestätigt", v
    part = {"add97": [mk(0.3, 0.8, i) for i in range(20)], "mul113": [mk(0.55, 0.9, i) for i in range(20)]}
    v = verdict(part, 20, rng)
    assert v["tasks"]["mul113"]["H3"]["verdict"] == "nicht bestätigt" and v["tasks"]["mul113"]["H1"]["verdict"] == "bestätigt", v
    assert v["reading"].startswith("teilweise:") and "mul113:H3" not in v["reading"], v
    excl = {"add97": [mk(0.3, 0.8, i) for i in range(15)] + [mk(0.3, 0.8, i, valid=False) for i in range(15, 20)],
            "mul113": [mk(0.3, 0.8, i) for i in range(20)]}
    v = verdict(excl, 20, rng)
    assert v["tasks"]["add97"]["verdict"] == "nicht auswertbar" and v["tasks"]["mul113"]["H1"]["verdict"] == "bestätigt", v
    assert verdict({"add97": yes["add97"][:19], "mul113": yes["mul113"]}, 20, rng)["verdict"] == "nicht auswertbar"
    tech = {"add97": yes["add97"][:19] + [{"seed": 1, "valid": False, "technical": True}], "mul113": yes["mul113"]}
    assert verdict(tech, 20, rng)["verdict"] == "nicht auswertbar"
    for task, p in TASKS:                                   # EXP-044 construction: disjoint targets, disjoint test set
        F, G = target_set(3620, task, p, "F"), target_set(3620, task, p, "G")
        d = m44.build(3620, task, p)
        assert not set(F) & set(G) and len(F) == len(G) == 5
        assert not np.intersect1d(d["test"], np.union1d(d["F"], d["G"])).size and len(d["F"]) == len(d["G"])
    selftest_binding(BLOCK, tj[0], tj[2], tj[3])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    src = (ROOT / FB).read_text(encoding="utf-8")
    assert 'exp_id = "EXP-044" if a.switch_split_file is not None else "EXP-043"' in src
    a43()
    loaded = {Path(m.__file__).resolve().relative_to(ROOT.resolve()).as_posix() for m in list(sys.modules.values())
              if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to((ROOT / "lab").resolve())}
    assert loaded <= set(CODE_FILES), sorted(loaded - set(CODE_FILES))
    print("[confirm_r11] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
