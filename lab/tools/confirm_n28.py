"""N28 confirmation (FINDINGS programme B, mechanism of persistence): splits, job list, run binding and frozen analysis. Session 22, UNTESTED.

Registration: lab/confirm/N28_REGISTRATION.md. Own manifest (lab/confirm/N28_manifest.json), own code-hash list, own raw directory,
splits and bindings. Binding and gating as confirm_p3 (session 21, Codex-reviewed), copied rather than imported so that confirm_p3.py
(frozen with P3) stays unchanged and its globals are never patched.

Per seed s (fresh block, omega = 0, EXP-053 splits with matched steering strength): pure A, pure B (2000 steps) and the switch runs
A->B, B->A at t for every registered arm (t, part): part "normal" (AdamW state kept) or "m" (exp_avg zeroed at the switch, step and
exp_avg_sq kept; freq_ban --reset-optim-part m). pi(arm) = mean of pi_AB, pi_BA of the final W_E power (EXP-056 / P3 definition).
Primary and secondary quantities: see PRIMARY in the registration and verdict() below.

  python lab/tools/confirm_n28.py --hash-code
  python lab/tools/confirm_n28.py --splits lab/confirm/N28_manifest.json       # after freezing; never overwrites
  python lab/tools/confirm_n28.py --jobs lab/confirm/N28_manifest.json > lab/confirm/N28_jobs.txt
  python lab/tools/confirm_n28.py --run lab/confirm/N28_manifest.json -- <trainer command>
  python lab/tools/confirm_n28.py --analyze lab/confirm/N28_manifest.json      # under guarded_run.py
  python lab/tools/confirm_n28.py --selftest
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
import confirm_p1 as c1  # noqa: E402  (read-only reuse: _state, _sha, _bindable, interp, t-test, bootstrap, holm)
import overlap_split as ov  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "n28_raw"
BIND = LAB / "confirm" / "n28_bindings"
SPL = LAB / "confirm" / "n28_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"
BUDGET, ALPHA, POLL_S, MIN_SEP, OMEGA = 2000, 0.05, 2.0, 2.0, 0.0
MIN_EFFECT = {"H1": 0.05, "H2": 0.05}
REGISTERED = {"seeds": list(range(2200, 2230)), "arms": [["normal", 25], ["m", 25], ["m", 35]], "device": "cuda", "threads": 1}
CODE_FILES = ("lab/tools/confirm_n28.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py", "lab/tools/result_loader.py",
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
    files = list(CODE_FILES) + sorted(q.relative_to(ROOT).as_posix() for q in (ROOT / "training/grokverse").rglob("*.py")
                                      if "__pycache__" not in q.parts)
    return {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in files}


def check_code(man: dict) -> None:
    want, have = man.get("code_sha256") or {}, code_hashes()
    if not want:
        raise SystemExit("N28 manifest has no code_sha256")
    diff = sorted(set(want) ^ set(have)) + sorted(f for f in set(want) & set(have) if want[f] != have[f])
    if diff:
        raise SystemExit(f"executed code differs from the frozen N28 manifest: {diff[:5]}")


def check_registered(man: dict) -> None:
    """Type-strict equality with the registered design (as confirm_p3)."""
    def same(a, b) -> bool:
        if type(a) is not type(b):
            return False
        if isinstance(a, list):
            return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
        return a == b
    for k, v in REGISTERED.items():
        if not same(man.get(k), v):
            raise SystemExit(f"N28 manifest field {k!r} differs from the registration: {man.get(k)!r} != {v!r}")


def check_manifest(manifest: Path, man: dict) -> None:
    c = str(man.get("commit", "")).strip()
    if not c:
        raise SystemExit("N28 manifest has no 'commit'")
    rel = manifest.resolve().relative_to(ROOT.resolve()).as_posix()
    got = subprocess.run(["git", "show", f"{c}:{rel}"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if got.returncode != 0:
        raise SystemExit(f"N28 manifest not found at commit {c}")
    strip = lambda d: {k: v for k, v in d.items() if k != "commit"}   # noqa: E731
    if strip(json.loads(got.stdout)) != strip(man):
        raise SystemExit("N28 manifest differs from its frozen version")
    check_registered(man)
    check_code(man)


# ---------------------------------------------------------------- splits and jobs
def stem(s: int, arm: str) -> str:
    return f"n28_seed{s}_w0_{arm}"


def write_splits(man: dict) -> None:
    eps = json.loads(CAL.read_text(encoding="utf-8"))["levels"][str(OMEGA)]["eps"]
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, a)}.npy" for s in man["seeds"] for a in "AB"] + [f"n28_seed{s}_test.npy" for s in man["seeds"]]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("N28 splits exist already: never overwrite")
    for s in man["seeds"]:
        F, G = ov.targets(s)
        d = ov.build(s, OMEGA, eps)
        assert len(d["A"]) == len(d["B"]) == ov.N_TRAIN and not np.intersect1d(d["A"], d["B"]).size
        assert not np.intersect1d(d["test"], np.union1d(d["A"], d["B"])).size
        for a in "AB":
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, d[a].astype(np.int64))
        with open(SPL / f"n28_seed{s}_test.npy", "xb") as f:
            np.save(f, d["test"].astype(np.int64))
        with open(SPL / f"n28_seed{s}_w0.json", "x", encoding="utf-8") as f:
            json.dump({"seed": s, "omega": OMEGA, "targets": {"A": F, "B": G}, "share_A_F": ov.share(d["A"], F),
                       "share_B_G": ov.share(d["B"], G), "manifest_commit": man["commit"]}, f, indent=1)


def switch_args(first: str, second: str, t: int, part: str) -> str:
    return (f"--steps {t + BUDGET} --split-file {first} --switch-split-file {second} --switch-step {t} "
            f"--spectra-at {t},{t + 250},{t + BUDGET} --log-update-norms 10" + (" --reset-optim-part m" if part == "m" else ""))


def trainer_jobs(man: dict) -> list[str]:
    out = []
    for s in man["seeds"]:
        base = (f"{c1.interp(man)} {FB} --seed {s} --condition baseline --threads {man['threads']} --device {man['device']} "
                f"--test-file lab/confirm/n28_splits/n28_seed{s}_test.npy --out-root lab/confirm/n28_raw")
        a, b = (f"lab/confirm/n28_splits/{stem(s, x)}.npy" for x in "AB")
        for first in (a, b):
            out.append(f"{base} --steps {BUDGET} --split-file {first} --spectra-at 50,250,{BUDGET}")
        for part, t in man["arms"]:
            for first, second in ((a, b), (b, a)):
                out.append(f"{base} {switch_args(first, second, t, part)}")
    return out


def jobs(man: dict, manifest: str) -> list[str]:
    return [f"python lab/tools/confirm_n28.py --run {manifest} -- {j}" for j in trainer_jobs(man)]


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban run-id rules: --split-file + --test-file (EXP-018), --switch-split-file (EXP-020), --reset-optim-part (EXP-058)."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    s, thr, dev, sp, sw, part = g("--seed"), g("--threads"), g("--device") or "cpu", g("--split-file"), g("--switch-split-file"), g("--reset-optim-part")
    rid = f"EXP-018_baseline_seed{s}_thr{thr}_{Path(sp).stem}"
    if sw is not None:
        rid = f"EXP-020_baseline_seed{s}_thr{thr}_{Path(sp).stem}_to_{Path(sw).stem}_at{g('--switch-step')}"
    if part is not None:
        rid += f"_ro{part}"
    return rid + ("" if dev == "cpu" else f"_dev{dev}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


# ---------------------------------------------------------------- binding (as confirm_p3, own paths and code list)
def code_digest(man: dict) -> str:
    return hashlib.sha256(json.dumps(man["code_sha256"], sort_keys=True).encode()).hexdigest()


def check_job(man: dict, cmd: list[str]) -> None:
    if cmd not in [shlex.split(j) for j in trainer_jobs(man)]:
        raise SystemExit(f"not a job of the frozen N28 manifest: {' '.join(cmd)[:120]}")


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
    return f"not bound to the frozen N28 code: {bad[:3]}" if bad else None


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
            print(f"[confirm_n28] {d.name} already bound, skipped", flush=True)
            return 0
        try:
            done = json.loads((d / "result.json").read_text(encoding="utf-8")).get("status") == "completed"
        except (OSError, ValueError):
            done = False
        if done:
            print(f"[confirm_n28] {d.name}: completed but not bound; refused", file=sys.stderr, flush=True)
            return 4
    if (d / "run.lock").exists():
        print(f"[confirm_n28] {d.name}: run.lock present (live or crashed trainer); refused, check by hand", file=sys.stderr, flush=True)
        return 4
    if d.exists():
        aside = d.with_name(f"{d.name}.stale_{time.time_ns()}")
        d.rename(aside)
        print(f"[confirm_n28] unfinished/unbound leftover moved to {aside.name}", file=sys.stderr, flush=True)
    t0 = time.time_ns()
    rc, changed = _run_gated(man, cmd)
    if changed:
        print(f"[confirm_n28] code changed during the run, no binding: {changed}", file=sys.stderr, flush=True)
        return 4
    files = c1._state([d]) if rc == 0 and d.exists() else {}
    if rc == 0 and not any(k.endswith("/result.json") for k in files):
        print(f"[confirm_n28] {d.name}: no new result.json, nothing usable bound", file=sys.stderr, flush=True)
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
    return ((LAB_ - L["B"]) / (L["A"] - L["B"]) + (LBA - L["A"]) / (L["B"] - L["A"])) / 2


def arm_key(part: str, t: int) -> str:
    return f"{part}{t}"


def load_final(man: dict, s: int, first: str, second: str | None, t: int | None, part: str | None) -> np.ndarray | str:
    """Final W_E of one run through the shared loader + N28 binding (hash -> load -> hash)."""
    dev = man["device"]
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", dev, "--split-file", str(SPL / f"{stem(s, first)}.npy")]
    if second:
        cmd += ["--switch-split-file", str(SPL / f"{stem(s, second)}.npy"), "--switch-step", str(t)]
        if part == "m":
            cmd += ["--reset-optim-part", "m"]
    d = run_dir(cmd)
    steps = BUDGET + (t if second else 0)
    tag = f"{first}{second or ''}{'' if not second else '@' + arm_key(part, t)}"
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := unbound(man, d)):
        return f"{tag}: defekt: {why}"
    split = SPL / f"{stem(s, first)}.npy"
    L = load_run(d, Expect(seed=s, device=dev, max_steps=steps, split_file=split, test_file=SPL / f"n28_seed{s}_test.npy",
                           switch_file=SPL / f"{stem(s, second)}.npy" if second else None, config={"p": 113, "task": "add"},
                           snapshots_at=(steps,)))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if (why := unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != c1._sha(split):
        return f"{tag}: defekt after load: {why or 'split bytes differ'}"
    if part == "m" and L.res.get("events", {}).get("reset_optim_part", {}).get("check") is not True:
        return f"{tag}: defekt: partial reset not recorded"
    return np.asarray(L.snapshot(steps), dtype=np.float64)


def seed_row(man: dict, s: int) -> dict:
    meta = json.loads((SPL / f"n28_seed{s}_w0.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    gp = lambda W: a43().group_power(W, "add", 113)[0]   # noqa: E731
    W = {"A": load_final(man, s, "A", None, None, None), "B": load_final(man, s, "B", None, None, None)}
    for part, t in man["arms"]:
        for first, second in (("A", "B"), ("B", "A")):
            W[(arm_key(part, t), first + second)] = load_final(man, s, first, second, t, part)
    bad = [v for v in W.values() if isinstance(v, str)]
    if bad:
        return {"seed": s, "valid": False, "reason": "; ".join(bad[:4]), "n_bad": len(bad)}
    L = {"A": logratio(gp(W["A"]), F, G), "B": logratio(gp(W["B"]), F, G)}
    pis = {}
    for part, t in man["arms"]:
        k = arm_key(part, t)
        lab_, lba = logratio(gp(W[(k, "AB")]), F, G), logratio(gp(W[(k, "BA")]), F, G)
        if not (np.isfinite(lab_) and np.isfinite(lba)):
            return {"seed": s, "valid": False, "reason": f"non-finite L in {k}"}
        pis[k] = pi_pair(L, lab_, lba)
    if not all(np.isfinite(v) for v in L.values()):
        return {"seed": s, "valid": False, "reason": "non-finite L", "L": L}
    if not L["A"] - L["B"] >= MIN_SEP:
        return {"seed": s, "valid": False, "reason": f"L(A) - L(B) < {MIN_SEP}", "L": L}
    return {"seed": s, "valid": True, "L": L, "pi": pis}


def contrasts(pi: dict[str, float]) -> dict[str, float]:
    """H1: pi_normal(25) - pi_m(25) (zeroing m lowers persistence). H2: see registration (filled in after EXP-059)."""
    return {"H1": pi["normal25"] - pi["m25"], "H2": pi["normal25"] - pi["m35"]}


def verdict(X: dict[str, np.ndarray], n_planned: int, rng: np.random.Generator) -> dict:
    if any(len(v) != n_planned for v in X.values()):
        return {"verdict": "nicht auswertbar"}
    tt = {k: c1.t_test_secondary(v) for k, v in X.items()}
    ph = c1.holm({k: t["p_one_sided"] for k, t in tt.items()})
    out = {}
    for k, v in X.items():
        ci = c1.boot_ci(v, rng)
        out[k] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)), "t": tt[k]["t"], "p": tt[k]["p_one_sided"], "p_holm": ph[k],
                  "ci95": ci, "n_positive": int((v > 0).sum()),
                  "verdict": "bestätigt" if ph[k] < ALPHA and ci[0] >= MIN_EFFECT[k] else "nicht bestätigt"}
    return out


def analyze(manifest: Path) -> None:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    check_manifest(manifest, man)
    rows = [seed_row(man, s) for s in man["seeds"]]
    ok = [r for r in rows if r["valid"]]
    X = {k: np.array([contrasts(r["pi"])[k] for r in ok]) for k in MIN_EFFECT}
    out = {"manifest_commit": man["commit"], "min_effect": MIN_EFFECT, "n_valid": len(ok), "n_planned": len(man["seeds"]),
           "hypotheses": verdict(X, len(man["seeds"]), np.random.default_rng(28))}
    out["pi_mean"] = {arm_key(p, t): float(np.mean([r["pi"][arm_key(p, t)] for r in ok])) for p, t in man["arms"]} if ok else {}
    out["rows"] = rows
    (LAB / "confirm" / "N28_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    man = {**REGISTERED, "seeds": [2200], "python": "PY"}
    try:
        check_registered(man)
        raise AssertionError("unregistered seed list accepted")
    except SystemExit:
        pass
    check_registered({**man, "seeds": list(range(2200, 2230))})
    for bad in ({"seeds": [float(x) for x in range(2200, 2230)]}, {"arms": [["normal", 25.0], ["m", 25], ["m", 35]]}, {"threads": True}):
        try:
            check_registered({**man, "seeds": list(range(2200, 2230)), **bad})
            raise AssertionError(f"type-sloppy manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    assert len(tj) == 2 + 2 * len(REGISTERED["arms"]) and all("n28_raw" in j and "\\" not in j for j in tj)
    assert all(j.startswith("python lab/tools/confirm_n28.py --run M -- ") for j in jobs(man, "M"))
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert ids[0] == "EXP-018_baseline_seed2200_thr1_n28_seed2200_w0_A_devcuda", ids[0]
    assert ids[2] == "EXP-020_baseline_seed2200_thr1_n28_seed2200_w0_A_to_n28_seed2200_w0_B_at25_devcuda", ids[2]
    assert ids[5] == "EXP-020_baseline_seed2200_thr1_n28_seed2200_w0_B_to_n28_seed2200_w0_A_at25_rom_devcuda", ids[5]
    assert ids[6] == "EXP-020_baseline_seed2200_thr1_n28_seed2200_w0_A_to_n28_seed2200_w0_B_at35_rom_devcuda", ids[6]
    assert len(set(ids)) == len(ids)
    assert "--steps 2035" in tj[6] and "--spectra-at 35,285,2035" in tj[6] and tj[6].endswith("--reset-optim-part m")
    assert "--reset-optim" not in tj[2] and "--reset-optim" not in tj[0]
    check_job(man, shlex.split(tj[0]))
    try:
        check_job(man, shlex.split(tj[0]) + ["--force"])
        raise AssertionError("foreign command accepted")
    except SystemExit:
        pass
    L = {"A": 2.0, "B": -2.0}
    assert pi_pair(L, 0.0, 0.0) == 0.5 and pi_pair(L, 2.0, -2.0) == 1.0 and pi_pair(L, -2.0, 2.0) == 0.0
    c = contrasts({"normal25": 0.3, "m25": 0.1, "m35": 0.2})
    assert abs(c["H1"] - 0.2) < 1e-12 and abs(c["H2"] - 0.1) < 1e-12
    rng = np.random.default_rng(0)
    assert verdict({"H1": np.full(29, 0.3), "H2": np.full(30, 0.3)}, 30, rng)["verdict"] == "nicht auswertbar"
    v = verdict({"H1": np.linspace(0.1, 0.4, 30), "H2": np.linspace(0.0, 0.06, 30)}, 30, rng)
    assert v["H1"]["verdict"] == "bestätigt" and v["H2"]["verdict"] == "nicht bestätigt", v
    assert v["H1"]["p"] < v["H2"]["p"] and abs(v["H1"]["p_holm"] - 2 * v["H1"]["p"]) < 1e-12, v
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
                cmd = shlex.split(tj[4])
                d = run_dir(cmd).as_posix()
                fake = [sys.executable, "-c", "import pathlib, sys; d = pathlib.Path(sys.argv[1]); d.mkdir(parents=True); "
                        "(d / 'result.json').write_text('{}')", d] + cmd[2:]
                assert expected_run_id(fake) == expected_run_id(cmd)
                assert run_bound(mf, fake) == 0
                _BOUND.clear()
                assert unbound(m2, Path(d)) is None
                assert run_bound(mf, fake) == 0
                (Path(d) / "result.json").write_text('{"status": "completed", "x": 1}')
                _BOUND.clear()
                assert "result.json" in unbound(m2, Path(d)) and run_bound(mf, fake) == 4
                nothing = [sys.executable, "-c", "pass"] + shlex.split(tj[1])[2:]
                assert run_bound(mf, nothing) == 4
                locked = run_dir(shlex.split(tj[5]))
                locked.mkdir(parents=True)
                (locked / "run.lock").write_text("{}")
                assert run_bound(mf, [sys.executable, "-c", "pass"] + shlex.split(tj[5])[2:]) == 4 and locked.exists()
            finally:
                g["check_manifest"], g["check_code"], g["check_job"] = gates
    finally:
        RAW, BIND = keep
        _BOUND.clear()
    assert set(CODE_FILES) <= set(code_hashes())
    print("[confirm_n28] selftest ok", flush=True)


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
