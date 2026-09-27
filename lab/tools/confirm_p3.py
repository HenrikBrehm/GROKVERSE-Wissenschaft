"""P3 confirmation (FINDINGS programme B, persistence): splits, job list, run binding and frozen analysis. Session 21, UNTESTED.

Registration: lab/confirm/P3_REGISTRATION_DRAFT.md. Own manifest (lab/confirm/P3_manifest.json), own code-hash list (CODE_FILES_P3), own raw
directory and bindings, so the running P1 block (bound to the P1 hashes) is never touched. The binding logic is the one of confirm_p1
(session 21, Codex-reviewed) with one difference: the run directory is derived EXACTLY from the command (freq_ban run-id rules), because a
switch run contains the stems of both splits.

Per seed s and overlap omega: runs only-A, only-B (2000 steps), A->B, B->A (t = 25, then 2000). L = log[P(F)/P(G)] of the final W_E power
(add 113 DFT, EXP-043 group_power); pi = mean of pi_AB, pi_BA (EXP-056). pi_trace(c) replaces the switch run's final W_E by
W_E(pure second run, end) + c * (W_E(switch run, 25) - W_E(switch run, 0)); after the Codex review (s21) the control is the MAXIMUM over
c in C_GRID (0, 0.05, ..., 1): a STATIC ADDITIVE W_E trace, no dynamics (the claim is worded accordingly). Level valid only if
L(A) - L(B) >= MIN_SEP (normalisation guard, pilot minimum 5.7). PRIMARY: D_s = pi_s(0) - max_c pi_trace_s(0; c); one-sided t-test of mean D > 0,
worst-case Holm over P1-P3 (3p); "bestätigt" = all planned seeds valid, Holm-p < 0.05 and lower 95 % bootstrap bound >= MIN_EFFECT (0.05).
Secondary (descriptive): pi(0.4) - pi(0) with CI, pi per omega, pi_trace with the AdamW decay c = 0.999^2000.

  python lab/tools/confirm_p3.py --hash-code                                 # code_sha256 for the manifest
  python lab/tools/confirm_p3.py --splits lab/confirm/P3_manifest.json       # after freezing; never overwrites
  python lab/tools/confirm_p3.py --jobs lab/confirm/P3_manifest.json > lab/confirm/P3_jobs.txt
  python lab/tools/confirm_p3.py --run lab/confirm/P3_manifest.json -- <trainer command>     # one job line
  python lab/tools/confirm_p3.py --analyze lab/confirm/P3_manifest.json      # under guarded_run.py
  python lab/tools/confirm_p3.py --selftest
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "experiments/EXP-053-p3-overlap-design"))
import confirm_p1 as c1  # noqa: E402  (read-only reuse: _state, _sha, _bindable, t-test, bootstrap, holm)
import overlap_split as ov  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "p3_raw"
BIND = LAB / "confirm" / "p3_bindings"
SPL = LAB / "confirm" / "p3_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"
T_SWITCH, BUDGET, ALPHA, MIN_EFFECT, SEED_RANGE, POLL_S, MIN_SEP = 25, 2000, 0.05, 0.05, (1050, 1099), 2.0, 2.0
C_DECAY = 0.999 ** BUDGET
C_GRID = tuple(round(0.05 * i, 2) for i in range(21))
REGISTERED = {"seeds": list(range(1050, 1080)), "omegas": [0.0, 0.4], "device": "cuda", "threads": 1}
CODE_FILES_P3 = ("lab/tools/confirm_p3.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py", "lab/tools/result_loader.py",
                 "lab/tools/paket_a_device.py", "lab/experiments/EXP-001-freq-ban/freq_ban.py",
                 "lab/experiments/EXP-053-p3-overlap-design/overlap_split.py", "lab/experiments/EXP-053-p3-overlap-design/calibration.json",
                 "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
                 "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py")

_a43 = None


def a43():
    global _a43
    if _a43 is None:
        spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
        _a43 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_a43)
    return _a43


# ---------------------------------------------------------------- freezing
def code_hashes() -> dict[str, str]:
    files = list(CODE_FILES_P3) + sorted(q.relative_to(ROOT).as_posix() for q in (ROOT / "training/grokverse").rglob("*.py")
                                         if "__pycache__" not in q.parts)
    return {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in files}


def check_code(man: dict) -> None:
    want, have = man.get("code_sha256") or {}, code_hashes()
    if not want:
        raise SystemExit("P3 manifest has no code_sha256")
    diff = sorted(set(want) ^ set(have)) + sorted(f for f in set(want) & set(have) if want[f] != have[f])
    if diff:
        raise SystemExit(f"executed code differs from the frozen P3 manifest: {diff[:5]}")


def check_manifest(manifest: Path, man: dict) -> None:
    c = str(man.get("commit", "")).strip()
    if not c:
        raise SystemExit("P3 manifest has no 'commit'")
    rel = manifest.resolve().relative_to(ROOT.resolve()).as_posix()
    got = subprocess.run(["git", "show", f"{c}:{rel}"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if got.returncode != 0:
        raise SystemExit(f"P3 manifest not found at commit {c}")
    strip = lambda d: {k: v for k, v in d.items() if k != "commit"}   # noqa: E731
    if strip(json.loads(got.stdout)) != strip(man):
        raise SystemExit("P3 manifest differs from its frozen version")
    check_registered(man)
    check_code(man)


def check_registered(man: dict) -> None:
    """Codex review s21: the manifest must be exactly the registered design."""
    for k, v in REGISTERED.items():
        got = man.get(k)
        same_types = (type(got) is type(v) and (not isinstance(v, list) or
                      (len(got) == len(v) and all(type(x) is type(y) for x, y in zip(got, v)))))
        if got != v or not same_types:            # Codex recheck s21: type-strict (1050.0, 0, True must not pass)
            raise SystemExit(f"P3 manifest field {k!r} differs from the registration: {got!r} != {v!r}")


# ---------------------------------------------------------------- splits and jobs
def lvl(om: float) -> int:
    return int(round(om * 1000))


def stem(s: int, om: float, arm: str) -> str:
    return f"p3_seed{s}_w{lvl(om)}_{arm}"


def write_splits(man: dict) -> None:
    cal = json.loads(CAL.read_text(encoding="utf-8"))["levels"]
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, om, a)}.npy" for s in man["seeds"] for om in man["omegas"] for a in "AB"] + [f"p3_seed{s}_test.npy" for s in man["seeds"]]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("P3 splits exist already: never overwrite")
    for s in man["seeds"]:
        F, G = ov.targets(s)
        tests = []
        for om in man["omegas"]:
            d = ov.build(s, om, cal[str(om)]["eps"])
            tests.append(d["test"])
            assert len(d["A"]) == len(d["B"]) == ov.N_TRAIN and len(np.intersect1d(d["A"], d["B"])) == len(d["S"])
            assert not np.intersect1d(d["test"], np.union1d(d["A"], d["B"])).size
            for a in "AB":
                with open(SPL / f"{stem(s, om, a)}.npy", "xb") as f:
                    np.save(f, d[a].astype(np.int64))
            with open(SPL / f"p3_seed{s}_w{lvl(om)}.json", "x", encoding="utf-8") as f:
                json.dump({"seed": s, "omega": om, "targets": {"A": F, "B": G}, "n_shared": int(len(d["S"])),
                           "share_A_F": ov.share(d["A"], F), "share_B_G": ov.share(d["B"], G), "manifest_commit": man["commit"]}, f, indent=1)
        assert all(np.array_equal(tests[0], t) for t in tests)
        with open(SPL / f"p3_seed{s}_test.npy", "xb") as f:
            np.save(f, tests[0].astype(np.int64))


def interp(man: dict) -> str:
    return c1.interp(man)


def trainer_jobs(man: dict) -> list[str]:
    out = []
    for s in man["seeds"]:
        base = (f"{interp(man)} {FB} --seed {s} --condition baseline --threads {man['threads']} --device {man['device']} "
                f"--test-file lab/confirm/p3_splits/p3_seed{s}_test.npy --out-root lab/confirm/p3_raw")
        for om in man["omegas"]:
            a, b = (f"lab/confirm/p3_splits/{stem(s, om, x)}.npy" for x in "AB")
            for first in (a, b):
                out.append(f"{base} --steps {BUDGET} --split-file {first} --spectra-at 50,250,{BUDGET}")
            for first, second in ((a, b), (b, a)):
                out.append(f"{base} --steps {T_SWITCH + BUDGET} --split-file {first} --switch-split-file {second} "
                           f"--switch-step {T_SWITCH} --spectra-at {T_SWITCH},{T_SWITCH + 250},{T_SWITCH + BUDGET}")
    return out


def jobs(man: dict, manifest: str) -> list[str]:
    return [f"python lab/tools/confirm_p3.py --run {manifest} -- {j}" for j in trainer_jobs(man)]


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban run-id rules for add 113 with --split-file and --test-file (EXP-018), plus --switch-split-file (EXP-020)."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    s, thr, dev, sp, sw = g("--seed"), g("--threads"), g("--device") or "cpu", g("--split-file"), g("--switch-split-file")
    rid = f"EXP-018_baseline_seed{s}_thr{thr}_{Path(sp).stem}"
    if sw is not None:
        rid = f"EXP-020_baseline_seed{s}_thr{thr}_{Path(sp).stem}_to_{Path(sw).stem}_at{g('--switch-step')}"
    return rid + ("" if dev == "cpu" else f"_dev{dev}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


# ---------------------------------------------------------------- binding (as confirm_p1, own code list and paths)
def code_digest(man: dict) -> str:
    return hashlib.sha256(json.dumps(man["code_sha256"], sort_keys=True).encode()).hexdigest()


def check_job(man: dict, cmd: list[str]) -> None:
    if cmd not in [shlex.split(j) for j in trainer_jobs(man)]:
        raise SystemExit(f"not a job of the frozen P3 manifest: {' '.join(cmd)[:120]}")


_BOUND: dict[str, set[tuple[str, str]]] = {}


def bound_files(man: dict) -> set[tuple[str, str]]:
    key = f"{man['commit']}:{code_digest(man)}"
    if key not in _BOUND:
        ok: set[tuple[str, str]] = set()
        for b in sorted(BIND.glob("*.json")) if BIND.exists() else []:
            r = json.loads(b.read_text(encoding="utf-8"))
            if r.get("exit") == 0 and r.get("code_digest") == code_digest(man) and r.get("manifest_commit") == man["commit"]:
                ok |= set(r.get("files", {}).items())
        _BOUND[key] = ok
    return _BOUND[key]


def unbound(man: dict, d: Path) -> str | None:
    ok = bound_files(man)
    bad = [q.name for q in sorted(d.rglob("*")) if c1._bindable(q) and (q.relative_to(ROOT).as_posix(), c1._sha(q)) not in ok]
    return f"not bound to the frozen P3 code: {bad[:3]}" if bad else None


def _run_gated(man: dict, cmd: list[str]) -> tuple[int, str | None]:
    pyc = str(Path(tempfile.gettempdir()) / f"confirm_pyc_{code_digest(man)[:16]}")
    proc = subprocess.Popen(cmd, cwd=ROOT, env={**os.environ, "PYTHONPYCACHEPREFIX": pyc})
    try:
        while True:
            try:
                rc = proc.wait(timeout=POLL_S)
                break
            except subprocess.TimeoutExpired:
                try:
                    check_code(man)
                except SystemExit as ex:
                    proc.kill()
                    return proc.wait(), str(ex)
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
    try:
        check_code(man)
    except SystemExit as ex:
        return rc, str(ex)
    return rc, None


def run_bound(manifest: Path, cmd: list[str]) -> int:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    check_manifest(manifest, man)
    check_job(man, cmd)
    d = run_dir(cmd)
    if (d / "result.json").exists():
        if unbound(man, d) is None:
            print(f"[confirm_p3] {d.name} already bound, skipped", flush=True)
            return 0
        try:
            done = json.loads((d / "result.json").read_text(encoding="utf-8")).get("status") == "completed"
        except (OSError, ValueError):
            done = False
        if done:
            print(f"[confirm_p3] {d.name}: completed but not bound; refused", file=sys.stderr, flush=True)
            return 4
    if (d / "run.lock").exists():                         # Codex recheck s21: a (possibly live) trainer holds this run id
        print(f"[confirm_p3] {d.name}: run.lock present (live or crashed trainer); refused, check by hand", file=sys.stderr, flush=True)
        return 4
    if d.exists():                                        # Codex review s21: never bind on top of leftovers, run in a clean dir
        aside = d.with_name(f"{d.name}.stale_{time.time_ns()}")
        d.rename(aside)
        print(f"[confirm_p3] unfinished/unbound leftover moved to {aside.name}", file=sys.stderr, flush=True)
    pre: dict[str, str] = {}
    t0 = time.time_ns()
    rc, changed = _run_gated(man, cmd)
    if changed:
        print(f"[confirm_p3] code changed during the run, no binding: {changed}", file=sys.stderr, flush=True)
        return 4
    post = c1._state([d]) if rc == 0 and d.exists() else {}
    files = {k: v for k, v in post.items() if pre.get(k) != v}
    if rc == 0 and not any(k.endswith("/result.json") for k in files):
        print(f"[confirm_p3] {d.name}: no new result.json, nothing usable bound", file=sys.stderr, flush=True)
        rc = 4
    BIND.mkdir(parents=True, exist_ok=True)
    rec = {"code_digest": code_digest(man), "manifest_commit": man["commit"], "cmd": cmd, "exit": rc, "t0_ns": t0,
           "t1_ns": time.time_ns(), "run_dir": d.name, "files": files if rc == 0 else {}}
    with open(BIND / f"{hashlib.sha256(' '.join(cmd).encode()).hexdigest()[:16]}_{t0}_{os.getpid()}.json", "x", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    return rc


# ---------------------------------------------------------------- analysis
def logratio(pw: np.ndarray, F: list[int], G: list[int]) -> float:
    return float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))


def pi_pair(L: dict[str, float], LAB_: float, LBA: float) -> float:
    """Mean of pi_AB = (L_AB - L_B) / (L_A - L_B) and pi_BA = (L_BA - L_A) / (L_B - L_A)."""
    return ((LAB_ - L["B"]) / (L["A"] - L["B"]) + (LBA - L["A"]) / (L["B"] - L["A"])) / 2


def load_level(man: dict, s: int, om: float) -> dict | str:
    """W_E snapshots of the four runs of (s, om), each through the shared loader + P3 binding (hash -> load -> hash)."""
    dev, snaps = man["device"], {}
    test = SPL / f"p3_seed{s}_test.npy"
    for kind in ("A", "B", "AB", "BA"):
        first, second = kind[0], kind[1:] or None
        cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", dev,
               "--split-file", str(SPL / f"{stem(s, om, first)}.npy")]
        if second:
            cmd += ["--switch-split-file", str(SPL / f"{stem(s, om, second)}.npy"), "--switch-step", str(T_SWITCH)]
        d = run_dir(cmd)
        steps = BUDGET + (T_SWITCH if second else 0)
        if not d.exists():
            return f"{kind}: fehlt"
        if (why := unbound(man, d)):
            return f"{kind}: defekt: {why}"
        split = SPL / f"{stem(s, om, first)}.npy"
        L = load_run(d, Expect(seed=s, device=dev, max_steps=steps, split_file=split, test_file=test,
                               switch_file=SPL / f"{stem(s, om, second)}.npy" if second else None, config={"p": 113, "task": "add"},
                               snapshots_at=(0, T_SWITCH, steps) if second else (steps,)))
        if L.status != "ok":
            return f"{kind}: {L.status}: {L.reason}"
        if (why := unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != c1._sha(split):
            return f"{kind}: defekt after load: {why or 'split bytes differ'}"
        snaps[kind] = {t: np.asarray(L.snapshot(t), dtype=np.float64) for t in ((0, T_SWITCH, steps) if second else (steps,))}
    return snaps


def level_row(man: dict, s: int, om: float) -> dict:
    meta = json.loads((SPL / f"p3_seed{s}_w{lvl(om)}.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    sn = load_level(man, s, om)
    if isinstance(sn, str):
        return {"valid": False, "reason": sn}
    gp = lambda W: a43().group_power(W, "add", 113)[0]   # noqa: E731
    L = {"A": logratio(gp(sn["A"][BUDGET]), F, G), "B": logratio(gp(sn["B"][BUDGET]), F, G),
         "AB": logratio(gp(sn["AB"][T_SWITCH + BUDGET]), F, G), "BA": logratio(gp(sn["BA"][T_SWITCH + BUDGET]), F, G)}
    if not all(np.isfinite(v) for v in L.values()):
        return {"valid": False, "reason": "non-finite L", "L": L}
    if not L["A"] - L["B"] >= MIN_SEP:
        return {"valid": False, "reason": f"L(A) - L(B) < {MIN_SEP}", "L": L}
    tr = lambda c: pi_pair(L, logratio(gp(sn["B"][BUDGET] + c * (sn["AB"][T_SWITCH] - sn["AB"][0])), F, G),   # noqa: E731
                           logratio(gp(sn["A"][BUDGET] + c * (sn["BA"][T_SWITCH] - sn["BA"][0])), F, G))
    grid = {str(c): tr(c) for c in C_GRID}
    if not all(np.isfinite(v) for v in grid.values()):
        return {"valid": False, "reason": "non-finite trace", "L": L}
    return {"valid": True, "L": L, "pi": pi_pair(L, L["AB"], L["BA"]), "pi_trace_max": max(grid.values()),
            "pi_trace_c1": grid["1.0"], "pi_trace_decay": tr(C_DECAY), "pi_trace_grid": grid}


def verdict(D: np.ndarray, n_planned: int, rng: np.random.Generator) -> dict:
    if len(D) != n_planned:
        return {"verdict": "nicht auswertbar"}
    tt = c1.t_test_secondary(D)
    ph = c1.holm({"P3": tt["p_one_sided"], "_P1": 1.0, "_P2": 1.0})["P3"]
    ci = c1.boot_ci(D, rng)
    ok = ph < ALPHA and ci[0] >= MIN_EFFECT
    return {"mean": float(D.mean()), "sd": float(D.std(ddof=1)), "t": tt["t"], "p": tt["p_one_sided"], "p_holm_worstcase": ph,
            "ci95": ci, "n_positive": int((D > 0).sum()), "verdict": "bestätigt" if ok else "nicht bestätigt"}


def analyze(manifest: Path) -> None:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    check_manifest(manifest, man)
    rows = []
    for s in man["seeds"]:
        rows.append({"seed": s, "levels": {str(om): level_row(man, s, om) for om in man["omegas"]}})
    prim = [r["levels"]["0.0"] for r in rows]
    D = np.array([x["pi"] - x["pi_trace_max"] for x in prim if x["valid"]])
    rng = np.random.default_rng(3)
    out = {"manifest_commit": man["commit"], "min_effect": MIN_EFFECT, "n_valid": int(len(D)), "n_planned": len(man["seeds"]),
           **verdict(D, len(man["seeds"]), rng)}
    both = [r for r in rows if all(v["valid"] for v in r["levels"].values())]
    if len(both) > 1 and "0.4" in both[0]["levels"]:
        dd = np.array([r["levels"]["0.4"]["pi"] - r["levels"]["0.0"]["pi"] for r in both])
        out["secondary_dpi_0.4_minus_0"] = {"n": len(dd), "mean": float(dd.mean()), "ci95": c1.boot_ci(dd, rng)}
    out["pi_by_omega"] = {k: float(np.mean([r["levels"][k]["pi"] for r in rows if r["levels"][k]["valid"]] or [np.nan]))
                          for k in rows[0]["levels"]} if rows else {}
    out["pi_trace_decay_mean_omega0"] = float(np.mean([x["pi_trace_decay"] for x in prim if x["valid"]] or [np.nan]))
    out["pi_trace_max_mean_omega0"] = float(np.mean([x["pi_trace_max"] for x in prim if x["valid"]] or [np.nan]))
    out["rows"] = rows
    (LAB / "confirm" / "P3_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    man = {"seeds": [1050], "omegas": [0.0, 0.4], "device": "cuda", "python": "PY", "threads": 1}
    try:
        check_registered(man)
        raise AssertionError("unregistered seed list accepted")
    except SystemExit:
        pass
    check_registered({**man, "seeds": list(range(1050, 1080))})
    for bad in ({"seeds": [float(x) for x in range(1050, 1080)]}, {"omegas": [0, 0.4]}, {"threads": True}):
        try:
            check_registered({**man, "seeds": list(range(1050, 1080)), **bad})
            raise AssertionError(f"type-sloppy manifest accepted: {bad}")
        except SystemExit:
            pass
    assert C_GRID[0] == 0.0 and C_GRID[-1] == 1.0 and len(C_GRID) == 21
    tj = trainer_jobs(man)
    assert len(tj) == 8 and all("p3_raw" in j and "\\" not in j for j in tj)
    assert all(j.startswith("python lab/tools/confirm_p3.py --run M -- ") for j in jobs(man, "M"))
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert ids[0] == "EXP-018_baseline_seed1050_thr1_p3_seed1050_w0_A_devcuda", ids[0]
    assert ids[2] == "EXP-020_baseline_seed1050_thr1_p3_seed1050_w0_A_to_p3_seed1050_w0_B_at25_devcuda", ids[2]
    assert ids[3] == "EXP-020_baseline_seed1050_thr1_p3_seed1050_w0_B_to_p3_seed1050_w0_A_at25_devcuda", ids[3]
    assert len(set(ids)) == 8
    check_job(man, shlex.split(tj[0]))
    try:
        check_job(man, shlex.split(tj[0]) + ["--force"])
        raise AssertionError("foreign command accepted")
    except SystemExit:
        pass
    L = {"A": 2.0, "B": -2.0}
    assert pi_pair(L, 0.0, 0.0) == 0.5 and pi_pair(L, 2.0, -2.0) == 1.0 and pi_pair(L, -2.0, 2.0) == 0.0
    rng = np.random.default_rng(0)
    assert verdict(np.full(29, 0.3), 30, rng)["verdict"] == "nicht auswertbar"
    v = verdict(np.linspace(0.1, 0.4, 30), 30, rng)
    assert v["verdict"] == "bestätigt" and abs(v["p_holm_worstcase"] - 3 * v["p"]) < 1e-12, v
    assert verdict(np.linspace(0.0, 0.06, 30), 30, rng)["verdict"] == "nicht bestätigt"      # significant, below MIN_EFFECT
    global RAW, BIND
    keep = RAW, BIND
    try:
        with tempfile.TemporaryDirectory(dir=LAB / "confirm") as tmp:
            RAW, BIND = Path(tmp) / "raw", Path(tmp) / "b"
            m2 = {"commit": "c0", "code_sha256": {"a": "1"}}
            g = globals()
            gates = g["check_manifest"], g["check_code"], g["check_job"]
            g["check_manifest"], g["check_code"], g["check_job"] = (lambda *_: None), (lambda *_: None), (lambda *_: None)
            try:
                mf = Path(tmp) / "m.json"
                mf.write_text(json.dumps(m2))
                cmd = shlex.split(tj[2])
                d = run_dir(cmd).as_posix()
                fake = [sys.executable, "-c", "import pathlib, sys; d = pathlib.Path(sys.argv[1]); d.mkdir(parents=True); "
                        "(d / 'result.json').write_text('{}')", d] + cmd[2:]
                assert expected_run_id(fake) == expected_run_id(cmd)
                assert run_bound(mf, fake) == 0
                _BOUND.clear()
                assert unbound(m2, Path(d)) is None
                assert run_bound(mf, fake) == 0                                  # already bound -> skipped
                (Path(d) / "result.json").write_text('{"status": "completed", "x": 1}')
                _BOUND.clear()
                assert "result.json" in unbound(m2, Path(d)) and run_bound(mf, fake) == 4   # altered completed run refused
                nothing = [sys.executable, "-c", "pass"] + shlex.split(tj[1])[2:]
                assert run_bound(mf, nothing) == 4                              # exit 0 without a result.json
                last = max(BIND.glob("*.json"), key=lambda q: int(q.name.split("_")[1]))   # t0 in the name (mtime is coarse on Windows)
                assert json.loads(last.read_text())["exit"] == 4
                left = run_dir(shlex.split(tj[3]))                              # unfinished leftover -> moved aside, clean rerun
                left.mkdir(parents=True)
                (left / "result.json").write_text('{"status": "running"}')
                redo = [sys.executable, "-c", "import pathlib, sys; d = pathlib.Path(sys.argv[1]); d.mkdir(parents=True); "
                        "(d / 'result.json').write_text('{}')", left.as_posix()] + shlex.split(tj[3])[2:]
                assert run_bound(mf, redo) == 0 and list(RAW.glob(left.name + ".stale_*"))
                _BOUND.clear()
                assert unbound(m2, left) is None
                locked = run_dir(shlex.split(tj[5]))                            # run.lock present -> refused, nothing renamed
                locked.mkdir(parents=True)
                (locked / "run.lock").write_text("{}")
                assert run_bound(mf, [sys.executable, "-c", "pass"] + shlex.split(tj[5])[2:]) == 4 and locked.exists()
            finally:
                g["check_manifest"], g["check_code"], g["check_job"] = gates
    finally:
        RAW, BIND = keep
        _BOUND.clear()
    assert set(CODE_FILES_P3) <= set(code_hashes())
    print("[confirm_p3] selftest ok", flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
    elif a == ["--hash-code"]:
        print(json.dumps(code_hashes(), indent=1))
    elif len(a) == 2 and a[0] in ("--splits", "--jobs", "--analyze"):
        m = json.loads(Path(a[1]).read_text(encoding="utf-8"))
        if a[0] == "--analyze":
            analyze(Path(a[1]))
        else:
            check_manifest(Path(a[1]), m)
            if a[0] == "--splits":
                write_splits(m)
            else:
                print("\n".join(jobs(m, Path(a[1]).resolve().relative_to(ROOT.resolve()).as_posix())))
    elif len(a) >= 4 and a[0] == "--run" and a[2] == "--":
        raise SystemExit(run_bound(Path(a[1]), a[3:]))
    else:
        raise SystemExit(__doc__)
