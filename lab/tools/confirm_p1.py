"""P1 confirmation (FINDINGS "Programm"): job list and frozen analysis for the reserved block. Session 14, UNTESTED.

P1: engineered splits raise the target power in W_E, Delta_pow > 0 on fresh seeds and splits, minimum effect Delta_pow >= 1.
Primary per task in the manifest: mean Delta_pow over seeds, one-sided sign-flip test of mean > 0 (exact for n <= 20, else
Monte Carlo), 95 % bootstrap CI of the mean; with manifest 'primary_task' only that task enters the P1-P3 Holm family (FAMILY = 3,
missing members p = 1) and the other tasks form a secondary Holm family (session 20, Codex B2; see family_adjust).
"confirmed" for a task needs ALL planned pairs valid, Holm-p < 0.05 AND the lower CI bound >= MIN_EFFECT (session 20, Codex B4/H3).
Runs: transformer of the study (freq_ban.py, add/mul) or group_train.py (D_n), 2000 steps, device from the manifest.

  python lab/tools/confirm_p1.py --jobs lab/confirm/P1_manifest.json > lab/confirm/P1_jobs.txt     # for parallel_queue.py
  python lab/tools/confirm_p1.py --analyze lab/confirm/P1_manifest.json                             # under guarded_run.py
  python lab/tools/confirm_p1.py --selftest
  python lab/tools/confirm_p1.py --run lab/confirm/P1_manifest.json -- <trainer command>             # one job line (see run_bound)
Session 21 (Codex B1, UNTESTED): every job runs through --run, which checks the frozen manifest and code before and after the
trainer and writes a binding (code digest + sha256 of every file the run wrote) to lab/confirm/bindings/. --analyze accepts a run
only if every file in its directory is covered by a binding with the manifest's code digest; runs made outside --run are rejected.
Extra manifest fields: "device": "cuda"|"cpu", "python": ".venv-gpu/Scripts/python.exe", "threads": 1.

Optional "cross": {"task": "add", "p": 113, "seeds": [...], "inits_per_seed": 2} (Astra point 5, session 16, UNTESTED): the SAME
F/G split files of these seeds are trained again with extra inits cross_init(s, r) = s + 200 + 100 r (reserved 1200-1399).
Secondary and descriptive only, not in the Holm family; the primary P1 test keeps one Delta per seed (repeated inits of the same
split are no independent split replications). Reading, fixed before any run: see cross_block().
"""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
from confirm_splits import OUT as SPLITS, build, check_code, check_manifest  # noqa: E402
from result_loader import Expect, find_run, load_run  # noqa: E402

STEP, ALPHA, FAMILY, MIN_EFFECT, N_BOOT, N_MC = 2000, 0.05, 3, 1.0, 10_000, 200_000
RAW = LAB / "confirm" / "raw"
BIND = LAB / "confirm" / "bindings"
UNBOUND_NAMES = ("run.lock",)                             # trainer lock files are removed or stale, never results
POLL_S = 2.0                                              # code gate interval while the trainer runs (Codex B1 review, s21)
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
GT = "lab/experiments/EXP-046-dihedral-steering/group_train.py"


def stem(man: dict, t: dict, s: int, arm: str) -> str:
    return f"confirm_exp{int(man['experiment'])}_eps{float(man['eps'])}_{t['task']}{t['p']}_seed{s}_{arm}"


def cross_init(s: int, r: int) -> int:
    return s + 200 + 100 * r


def cross_spec(man: dict) -> dict | None:
    c = man.get("cross")
    if c is None:
        return None
    t = {"task": c["task"], "p": int(c["p"])}
    if t not in [{"task": x["task"], "p": int(x["p"])} for x in man["tasks"]] or t["task"] == "D":
        raise SystemExit("cross: task must be a non-D task of the manifest")
    if not set(c["seeds"]) <= set(man["seeds"]) or not all(1000 <= s <= 1099 for s in c["seeds"]):
        raise SystemExit("cross: seeds must be manifest seeds in 1000-1099")
    if not 1 <= int(c["inits_per_seed"]) <= 2:            # keeps cross_init inside the reserved 1200-1399
        raise SystemExit("cross: inits_per_seed must be 1 or 2")
    return {"t": t, "seeds": list(c["seeds"]), "R": int(c["inits_per_seed"])}


def interp(man: dict) -> str:
    """Session 20: Windows CreateProcess cannot find a RELATIVE path with forward slashes (.venv-gpu/Scripts/python.exe);
    an absolute forward-slash path works and survives parallel_queue's no-backslash rule for job lines."""
    py = str(man["python"])
    if ("/" in py or "\\" in py) and not Path(py).is_absolute():
        return (LAB.parent / py).as_posix()
    return py


def fb_job(man: dict, t: dict, init: int, sp: str, save_model: bool = False) -> str:
    """save_model (session 21): the primary add/mul runs keep model_final.pt for a LATER, separately registered functional test
    (P2). It does not change training or the run id, and the P1 analysis does not read it."""
    return (f"{interp(man)} {FB} --seed {init} --condition baseline --steps {STEP} --threads {man['threads']} "
            f"--device {man['device']} --p {t['p']} --task {t['task']} --split-file {sp} "
            f"--spectra-at 250,500,1000,{STEP}{' --save-model' if save_model else ''} --out-root lab/confirm/raw")


def jobs(man: dict, manifest: str) -> list[str]:
    """Every line runs through --run (session 21, Codex B1); manifest is the repo-relative manifest path."""
    return [f"python lab/tools/confirm_p1.py --run {manifest} -- {j}" for j in trainer_jobs(man)]


def trainer_jobs(man: dict) -> list[str]:
    out = []
    for t in man["tasks"]:
        for s in man["seeds"]:
            for arm in "FG":
                sp = f"lab/confirm/splits/{stem(man, t, s, arm)}.npy"
                if t["task"] == "D":
                    out.append(f"{interp(man)} {GT} --seed {s} --n {t['p']} --steps {STEP} --device {man['device']} --split-file {sp} "
                               f"--out-root lab/confirm/raw")
                else:
                    out.append(fb_job(man, t, s, sp, save_model=True))
    c = cross_spec(man)
    if c is not None:
        for s in c["seeds"]:
            for r in range(c["R"]):
                for arm in "FG":
                    out.append(fb_job(man, c["t"], cross_init(s, r), f"lab/confirm/splits/{stem(man, c['t'], s, arm)}.npy"))
    return out


def code_digest(man: dict) -> str:
    return hashlib.sha256(json.dumps(man["code_sha256"], sort_keys=True).encode()).hexdigest()


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _bindable(p: Path) -> bool:
    return p.is_file() and p.name not in UNBOUND_NAMES and not p.name.endswith(".tmp")


def run_dir_for(cmd: list[str]) -> list[Path]:
    """Run directories of this job: the split stem occurs in the name and 'seed<seed>_' occurs BEFORE it (freq_ban and group_train
    run ids both look like that). Before the stem, because the stem itself contains the unit seed: the cross runs (init 1200+) on
    the split of unit 1000 must not match the primary job of seed 1000."""
    seed, split = cmd[cmd.index("--seed") + 1], Path(cmd[cmd.index("--split-file") + 1]).stem
    return [d for d in RAW.glob("*") if d.is_dir() and split in d.name and f"seed{seed}_" in d.name.split(split)[0]] if RAW.exists() else []


def check_job(man: dict, cmd: list[str]) -> None:
    """Codex B1 review (s21): --run executes only commands of the frozen job list, nothing else."""
    if cmd not in [shlex.split(j) for j in trainer_jobs(man)]:
        raise SystemExit(f"not a job of the frozen manifest: {' '.join(cmd)[:120]}")


def _state(dirs: list[Path]) -> dict[str, str]:
    return {q.relative_to(LAB.parent).as_posix(): _sha(q) for d in dirs for q in sorted(d.rglob("*")) if _bindable(q)}


def _run_gated(man: dict, cmd: list[str]) -> tuple[int, str | None]:
    """Trainer with a fresh bytecode cache (no stale or foreign .pyc can run) and the code gate every POLL_S seconds;
    a change kills the trainer. Returns (exit code, reason if the code changed)."""
    pyc = tempfile.mkdtemp(prefix="confirm_pyc_")
    try:
        proc = subprocess.Popen(cmd, cwd=LAB.parent, env={**os.environ, "PYTHONPYCACHEPREFIX": pyc})
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
        try:
            check_code(man)
        except SystemExit as ex:
            return rc, str(ex)
        return rc, None
    finally:
        shutil.rmtree(pyc, ignore_errors=True)


def run_bound(manifest: Path, cmd: list[str]) -> int:
    """Session 21 (Codex B1 + its review): gates -> trainer (polled gate) -> gate -> binding. The binding lists the files of the
    job's own run directory that are NEW or CHANGED against the state before the start (no timestamps). Before the start: an
    already bound run is skipped (exit 0), an unbound COMPLETED run is refused (exit 4; never bind work of unknown code).
    Exit code = trainer's; 4 if a gate fails, the code changes, or a successful run leaves no new result.json."""
    man = json.loads(manifest.read_text(encoding="utf-8"))
    check_manifest(manifest, man)
    check_job(man, cmd)
    pre_dirs = run_dir_for(cmd)
    if len(pre_dirs) == 1 and (pre_dirs[0] / "result.json").exists() and unbound(man, pre_dirs[0]) is None:
        print(f"[confirm_p1] {pre_dirs[0].name} already bound, skipped", flush=True)
        return 0
    for d in pre_dirs:
        try:
            done = json.loads((d / "result.json").read_text(encoding="utf-8")).get("status") == "completed"
        except (OSError, ValueError):
            done = False
        if done:
            print(f"[confirm_p1] {d.name}: completed but not bound to the frozen code; refused (move it away)", file=sys.stderr, flush=True)
            return 4
    pre = _state(pre_dirs)
    t0 = time.time_ns()
    rc, changed = _run_gated(man, cmd)
    if changed:
        print(f"[confirm_p1] code changed during the run, no binding: {changed}", file=sys.stderr, flush=True)
        return 4
    dirs = run_dir_for(cmd)
    post = _state(dirs) if rc == 0 and len(dirs) == 1 else {}
    files = {k: v for k, v in post.items() if pre.get(k) != v}
    BIND.mkdir(parents=True, exist_ok=True)
    rec = {"code_digest": code_digest(man), "manifest_commit": man["commit"], "cmd": cmd, "exit": rc, "t0_ns": t0,
           "t1_ns": time.time_ns(), "run_dirs": [d.name for d in dirs], "files": files}
    name = f"{hashlib.sha256(' '.join(cmd).encode()).hexdigest()[:16]}_{t0}_{os.getpid()}.json"
    with open(BIND / name, "x", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    if rc == 0 and (len(dirs) != 1 or not any(k.endswith("/result.json") for k in files)):
        print(f"[confirm_p1] {len(dirs)} run directories / no new result.json: nothing usable bound", file=sys.stderr, flush=True)
        return 4
    return rc


def post_load_check(man: dict, d: Path, res: dict, split: Path) -> str | None:
    """Codex B1 review (s21): re-check the binding AFTER loading (hash -> load -> hash) and pin the exact split bytes the trainer
    used (fingerprint_fields.split_file_sha256 of freq_ban and group_train) to the current split file."""
    if (why := unbound(man, d)):
        return f"defekt: {why}"
    if res.get("fingerprint_fields", {}).get("split_file_sha256") != _sha(split):
        return "defekt: split bytes differ from the ones the trainer used"
    return None


_BOUND: dict[str, set[tuple[str, str]]] = {}


def bound_files(man: dict) -> set[tuple[str, str]]:
    """(relpath, sha256) of every file bound by a successful --run with this manifest's code digest and commit."""
    key = f"{man['commit']}:{code_digest(man)}"
    if key not in _BOUND:
        ok: set[tuple[str, str]] = set()
        for b in sorted(BIND.glob("*.json")) if BIND.exists() else []:
            r = json.loads(b.read_text(encoding="utf-8"))
            if r.get("exit") == 0 and r.get("code_digest") == code_digest(man) and r.get("manifest_commit") == man["commit"]:
                ok |= set(r.get("files", {}).items())
        _BOUND[key] = ok
    return _BOUND[key]


def unbound(man: dict, d: Path | None) -> str | None:
    """None if every bindable file of run directory d is covered by a binding (Codex B1), else the reason."""
    if d is None:
        return None                                       # load_run reports the missing run itself
    ok = bound_files(man)
    bad = [q.name for q in sorted(d.rglob("*")) if _bindable(q) and (q.relative_to(LAB.parent).as_posix(), _sha(q)) not in ok]
    return f"not bound to the frozen code: {bad[:3]}" if bad else None


def power_at(man: dict, t: dict, s: int, arm: str, init: int | None = None) -> np.ndarray | str:
    """W_E group power at STEP of the run on the split of (seed s, arm); init defaults to s (primary runs)."""
    st = stem(man, t, s, arm)
    init = s if init is None else init
    split = SPLITS / f"{st}.npy"
    dev = man["device"]
    if t["task"] == "D":
        d = find_run(RAW, f"EXP-046_seed{s}_{st}_dev{dev}")
        if (why := unbound(man, d)):
            return f"defekt: {why}"
        L = load_run(d,
                     Expect(seed=s, device=dev, max_steps=STEP, split_file=split, config={"p": 2 * t["p"], "group": f"D{t['p']}"},
                            at=(STEP,)))
        if L.status != "ok":
            return f"{L.status}: {L.reason}"
        return post_load_check(man, d, L.res, split) or L.spectrum(STEP)
    suffix = "" if (t["task"], t["p"]) == ("add", 113) else f"_{t['task']}{t['p']}"
    devsuf = "" if dev == "cpu" else f"_dev{dev}"            # freq_ban: CPU run-ids carry no device suffix
    d = find_run(RAW, f"EXP-0*_baseline_seed{init}_thr*_{st}{suffix}{devsuf}")
    if (why := unbound(man, d)):
        return f"defekt: {why}"
    L = load_run(d,
                 Expect(seed=init, device=dev, max_steps=STEP, split_file=split, config={"p": t["p"], "task": t["task"]},
                        snapshots_at=(STEP,)))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    if (why := post_load_check(man, d, L.res, split)):
        return why
    sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
    from analyze import group_power                       # EXP-043 group-basis power (add 113 = plain DFT, k = 1..56)
    return group_power(L.snapshot(STEP), t["task"], t["p"])[0]


def delta_pow(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float:
    s = lambda pw, S: float(pw[[k - 1 for k in S]].sum())   # noqa: E731
    return float(np.log(s(pF, F) / s(pF, G)) + np.log(s(pG, G) / s(pG, F)))


def delta_pow_checked(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float | None:
    """Session 20 (Codex B4): None if a target sum is not positive or the result is not finite (row then invalid)."""
    sums = [float(pw[[k - 1 for k in S]].sum()) for pw in (pF, pG) for S in (F, G)]
    if not all(np.isfinite(x) and x > 0 for x in sums):
        return None
    d = delta_pow(pF, pG, F, G)
    return d if np.isfinite(d) else None


def split_mismatch(man: dict, t: dict, s: int, arm: str) -> str | None:
    """Session 20 (Codex H6): rebuild the split deterministically and require exact equality of indices and targets."""
    st = stem(man, t, s, arm)
    idx, T = build(int(man["experiment"]), t["task"], t["p"], s, arm, float(man["eps"]))
    meta = json.loads((SPLITS / f"{st}.json").read_text(encoding="utf-8"))
    if not np.array_equal(np.load(SPLITS / f"{st}.npy"), idx):
        return f"{arm}: split indices differ from build()"
    if list(meta["targets"]) != list(T) or meta.get("arm") != arm or int(meta.get("seed", -1)) != s:
        return f"{arm}: split metadata differs from build()"
    return None


def family_adjust(ps: dict[str, float], primary: str | None) -> dict[str, float]:
    """Session 20 (Codex B2). With 'primary_task' (e.g. "add113"): that task is P1 and enters the P1-P3 Holm family
    (FAMILY = 3, P2/P3 as p = 1 placeholders until they exist); all other tasks form a separate SECONDARY Holm family (P1b).
    Without it (old behaviour): every task plus FAMILY - 1 placeholders in one family."""
    if primary is None:
        return holm({**ps, **{f"_other{i}": 1.0 for i in range(FAMILY - 1)}})
    if primary not in ps:
        raise SystemExit(f"primary_task {primary} is not a manifest task")
    main_ = holm({primary: ps[primary], **{f"_other{i}": 1.0 for i in range(FAMILY - 1)}})
    sec = {k: v for k, v in ps.items() if k != primary}
    return {primary: main_[primary], **(holm(sec) if sec else {})}


def task_verdict(v: dict) -> str:
    """Session 20 (Codex B4/H3): all planned pairs valid, Holm-p < ALPHA AND the CI lower bound >= MIN_EFFECT."""
    if "p" not in v:
        return "nicht auswertbar"
    return "bestätigt" if v["p_holm_worstcase"] < ALPHA and v["ci95"][0] >= MIN_EFFECT else "nicht bestätigt"


def sign_flip_p(d: np.ndarray, rng: np.random.Generator) -> float:
    if len(d) <= 20:
        flips = np.array(list(itertools.product((1.0, -1.0), repeat=len(d))))
        return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())
    flips = rng.choice((1.0, -1.0), size=(N_MC, len(d)))
    return float((np.sum((flips * d).mean(axis=1) >= d.mean() - 1e-12) + 1) / (N_MC + 1))


def boot_ci(d: np.ndarray, rng: np.random.Generator) -> list[float]:
    m = np.array([rng.choice(d, len(d)).mean() for _ in range(N_BOOT)])
    return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]


def holm(ps: dict[str, float]) -> dict[str, float]:
    order = sorted(ps, key=ps.get)
    adj, run = {}, 0.0
    for i, k in enumerate(order):
        run = max(run, min(1.0, (len(order) - i) * ps[k]))
        adj[k] = run
    return adj


def var_components(D: np.ndarray) -> dict:
    """One-way random effects on D [units x inits]: sigma2_between (split pair + targets of the unit) and sigma2_within
    (init, incl. init x split interaction, not separable here); ICC = share of the unit."""
    n, k = D.shape
    msw = float(D.var(axis=1, ddof=1).mean())
    msb = float(k * D.mean(axis=1).var(ddof=1))
    sb = max(0.0, (msb - msw) / k)
    tot = sb + msw
    return {"sigma2_between_unit": sb, "sigma2_within_init": msw, "icc_unit": sb / tot if tot > 0 else float("nan")}


def cross_reading(D: np.ndarray) -> str:
    """Fixed session 16 (before any run): stable if >= 90 % of all (unit, init) Delta > 0 and the init SD < mean/2;
    init-dependent if < 75 % positive or init SD >= mean; else mixed. Descriptive, no test."""
    frac, m = float((D > 0).mean()), float(D.mean())
    sw = var_components(D)["sigma2_within_init"] ** 0.5
    if frac >= 0.9 and m > 0 and sw < m / 2:
        return "stabil über Inits"
    if frac < 0.75 or m <= 0 or sw >= m:
        return "init-abhängig"
    return "gemischt"


def cross_block(man: dict) -> dict | None:
    c = cross_spec(man)
    if c is None:
        return None
    t, rows = c["t"], []
    for s in c["seeds"]:
        T = {a: json.loads((SPLITS / f"{stem(man, t, s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
        inits = [s] + [cross_init(s, r) for r in range(c["R"])]
        pw = {(i, a): power_at(man, t, s, a, i) for i in inits for a in "FG"}
        bad = [f"init {i} {a}: {v}" for (i, a), v in pw.items() if isinstance(v, str)]
        rows.append({"seed": s, "inits": inits, "valid": not bad, "reason": "; ".join(bad)} if bad else
                    {"seed": s, "inits": inits, "valid": True,
                     "Delta_pow": [delta_pow(pw[(i, "F")], pw[(i, "G")], T["F"], T["G"]) for i in inits]})
    ok = [r for r in rows if r["valid"]]
    res: dict = {"task": f"{t['task']}{t['p']}", "rows": rows, "n_valid_units": len(ok)}
    if len(ok) < 4:
        res["reading"] = "nicht auswertbar"
        return res
    D = np.array([r["Delta_pow"] for r in ok])
    res.update(var_components(D))
    res.update({"mean": float(D.mean()), "frac_positive": float((D > 0).mean()),
                "min_per_unit": D.min(axis=1).tolist(), "reading": cross_reading(D)})
    return res


def analyze(manifest: Path) -> None:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    check_manifest(manifest, man)
    rng = np.random.default_rng(1)
    out: dict = {"manifest_commit": man["commit"], "tasks": {}}
    for t in man["tasks"]:
        rows = []
        for s in man["seeds"]:
            T = {a: json.loads((SPLITS / f"{stem(man, t, s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
            pw = {a: power_at(man, t, s, a) for a in "FG"}
            bad = [f"{a}: {v}" for a, v in pw.items() if isinstance(v, str)]
            bad += [m for m in (split_mismatch(man, t, s, a) for a in "FG") if m]
            dp = None if bad else delta_pow_checked(pw["F"], pw["G"], T["F"], T["G"])
            if not bad and dp is None:
                bad = ["Delta_pow not finite or target power <= 0"]
            rows.append({"seed": s, "valid": False, "reason": "; ".join(bad)} if bad else
                        {"seed": s, "valid": True, "Delta_pow": dp})
        d = np.array([r["Delta_pow"] for r in rows if r["valid"]])
        res: dict = {"rows": rows, "n_valid": int(len(d)), "n_planned": len(man["seeds"])}
        if len(d) == len(man["seeds"]):   # session 20 (Codex B4): every planned pair, no complete-case deletion
            res.update({"mean": float(d.mean()), "sd": float(d.std(ddof=1)), "n_positive": int((d > 0).sum()),
                        "ci95": boot_ci(d, rng), "p": sign_flip_p(d, rng)})
        out["tasks"][f"{t['task']}{t['p']}"] = res
    adj = family_adjust({k: v.get("p", 1.0) for k, v in out["tasks"].items()}, man.get("primary_task"))
    out["primary_task"] = man.get("primary_task")
    for k, v in out["tasks"].items():
        v["p_holm_worstcase"] = adj[k]
        v["verdict"] = task_verdict(v)
        if "ci95" in v:
            v["min_effect_met"] = v["ci95"][0] >= MIN_EFFECT
    cb = cross_block(man)
    if cb is not None:
        out["cross_secondary"] = cb
        print(json.dumps({k: v for k, v in cb.items() if k != "rows"}, indent=1))
    (LAB / "confirm" / "P1_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: {x: y for x, y in v.items() if x != "rows"} for k, v in out["tasks"].items()}, indent=1))


def selftest() -> None:
    rng = np.random.default_rng(0)
    assert abs(delta_pow(np.array([4.0, 1.0]), np.array([1.0, 4.0]), [1], [2]) - 2 * np.log(4)) < 1e-12
    assert sign_flip_p(np.ones(10), rng) == 1 / 1024
    assert sign_flip_p(np.array([1.0, -1.0] * 5), rng) > 0.5
    lo, hi = boot_ci(np.full(10, 2.0), rng)
    assert lo == hi == 2.0
    man = {"experiment": 1, "eps": 2.0, "seeds": [1000], "device": "cuda", "python": "PY", "threads": 1,
           "tasks": [{"task": "add", "p": 113}, {"task": "D", "p": 59}]}
    j = trainer_jobs(man)
    assert all(x.startswith("python lab/tools/confirm_p1.py --run M.json -- ") for x in jobs(man, "M.json"))
    assert len(j) == 4 and "--task add" in j[0] and "group_train.py" in j[2] and all("\\" not in x for x in j), j
    assert "confirm_exp1_eps2.0_add113_seed1000_F.npy" in j[0] and "--n 59" in j[2]
    assert "--save-model" in j[0] and "--save-model" not in j[2]
    h = holm({"a": 0.01, "b": 0.04, "c": 1.0})
    assert abs(h["a"] - 0.03) < 1e-12 and abs(h["b"] - 0.08) < 1e-12 and h["c"] == 1.0
    # cross block (session 16): extra inits reuse the unit's split files, D tasks rejected
    mc = {**man, "seeds": [1000, 1001], "cross": {"task": "add", "p": 113, "seeds": [1001], "inits_per_seed": 2}}
    jc = trainer_jobs(mc)
    assert len(jc) == 8 + 4 and "--seed 1201 " in jc[8] and "--seed 1301 " in jc[10], jc[8:]
    assert "--save-model" not in jc[8]
    assert "confirm_exp1_eps2.0_add113_seed1001_F.npy" in jc[8] and "confirm_exp1_eps2.0_add113_seed1001_G.npy" in jc[9]
    for bad in ({"task": "D", "p": 59, "seeds": [1000], "inits_per_seed": 1},
                {"task": "add", "p": 113, "seeds": [999], "inits_per_seed": 1},
                {"task": "add", "p": 113, "seeds": [1000], "inits_per_seed": 3}):
        try:
            trainer_jobs({**mc, "cross": bad})
            raise AssertionError(bad)
        except SystemExit:
            pass
    vc = var_components(np.array([[1.0, 1.0, 1.0], [3.0, 3.0, 3.0]]))
    assert vc["sigma2_within_init"] == 0 and abs(vc["sigma2_between_unit"] - 2.0) < 1e-12 and vc["icc_unit"] == 1.0
    vc = var_components(np.array([[1.0, 3.0], [1.0, 3.0]]))
    assert vc["sigma2_between_unit"] == 0 and abs(vc["sigma2_within_init"] - 2.0) < 1e-12 and vc["icc_unit"] == 0.0
    assert cross_reading(np.full((5, 3), 8.0) + np.linspace(-1, 1, 15).reshape(5, 3)) == "stabil über Inits"
    assert cross_reading(np.array([[8.0, -1.0, 8.0]] * 5)) == "init-abhängig"
    # session 20 (Codex B4/H3)
    assert delta_pow_checked(np.array([4.0, 0.0]), np.array([1.0, 4.0]), [1], [2]) is None
    assert delta_pow_checked(np.array([4.0, np.nan]), np.array([1.0, 4.0]), [1], [2]) is None
    assert abs(delta_pow_checked(np.array([4.0, 1.0]), np.array([1.0, 4.0]), [1], [2]) - 2 * np.log(4)) < 1e-12
    import tempfile                                      # session 20 (Codex H6): split re-validation
    global SPLITS
    keep = SPLITS
    try:
        with tempfile.TemporaryDirectory() as tmp:
            SPLITS = Path(tmp)
            m1, t1 = {"experiment": 1, "eps": 2.0}, {"task": "add", "p": 113}
            idx, T = build(1, "add", 113, 1000, "F", 2.0)
            st = stem(m1, t1, 1000, "F")
            np.save(SPLITS / f"{st}.npy", idx)
            (SPLITS / f"{st}.json").write_text(json.dumps({"targets": T, "arm": "F", "seed": 1000}), encoding="utf-8")
            assert split_mismatch(m1, t1, 1000, "F") is None
            (SPLITS / f"{st}.json").write_text(json.dumps({"targets": T[::-1] if T != T[::-1] else [0], "arm": "F", "seed": 1000}), encoding="utf-8")
            assert "metadata" in split_mismatch(m1, t1, 1000, "F")
            np.save(SPLITS / f"{st}.npy", idx[1:])
            assert "indices" in split_mismatch(m1, t1, 1000, "F")
    finally:
        SPLITS = keep
    fa = family_adjust({"add113": 0.001, "mul113": 0.01, "add97": 0.02, "D59": 0.03}, "add113")
    assert abs(fa["add113"] - 0.003) < 1e-12 and abs(fa["mul113"] - 0.03) < 1e-12 and abs(fa["add97"] - 0.04) < 1e-12 and abs(fa["D59"] - 0.04) < 1e-12, fa   # Holm is monotone
    assert abs(family_adjust({"a": 0.01, "b": 0.02}, None)["a"] - 0.04) < 1e-12
    assert task_verdict({"n_valid": 49}) == "nicht auswertbar"
    assert task_verdict({"p": 0.001, "p_holm_worstcase": 0.003, "ci95": [0.5, 2.0]}) == "nicht bestätigt"
    assert task_verdict({"p": 0.001, "p_holm_worstcase": 0.003, "ci95": [1.2, 2.0]}) == "bestätigt"
    assert task_verdict({"p": 0.001, "p_holm_worstcase": 0.06, "ci95": [1.2, 2.0]}) == "nicht bestätigt"
    _selftest_binding()
    print("[confirm_p1] selftest ok", flush=True)


def _selftest_binding() -> None:
    """Session 21 (B1): bound files pass; unbound, altered, extra, wrong-digest/commit and failed-run files do not."""
    import tempfile
    global RAW, BIND
    keep = RAW, BIND
    try:
        with tempfile.TemporaryDirectory(dir=LAB / "confirm") as tmp:
            RAW, BIND = Path(tmp) / "raw", Path(tmp) / "bindings"
            man = {"commit": "c0", "code_sha256": {"a.py": "1" * 64}}
            d = RAW / "EXP-001_baseline_seed1000_thr1_confirm_x_F"
            d.mkdir(parents=True)
            (d / "result.json").write_text("{}")
            (d / "run.lock").write_text("x")
            assert run_dir_for(["py", "t.py", "--seed", "1000", "--split-file", "s/confirm_x_F.npy"]) == [d]
            assert run_dir_for(["py", "t.py", "--seed", "1001", "--split-file", "s/confirm_x_F.npy"]) == []
            st = "confirm_exp1_eps2.0_add113_seed1000_F"                 # primary and cross run on the same split
            prim, cross = RAW / f"EXP-001_baseline_seed1000_thr1_{st}_devcuda", RAW / f"EXP-001_baseline_seed1200_thr1_{st}_devcuda"
            prim.mkdir(), cross.mkdir()
            assert run_dir_for(["py", "t.py", "--seed", "1000", "--split-file", f"s/{st}.npy"]) == [prim]
            assert run_dir_for(["py", "t.py", "--seed", "1200", "--split-file", f"s/{st}.npy"]) == [cross]
            prim.rmdir(), cross.rmdir()
            _BOUND.clear()
            assert "not bound" in unbound(man, d)
            BIND.mkdir()
            rel = (d / "result.json").relative_to(LAB.parent).as_posix()
            rec = {"code_digest": code_digest(man), "manifest_commit": "c0", "exit": 0, "files": {rel: _sha(d / "result.json")}}
            for i, bad in enumerate(({"exit": 1}, {"code_digest": "0" * 64}, {"manifest_commit": "c1"})):
                (BIND / f"bad{i}.json").write_text(json.dumps({**rec, **bad}))
            _BOUND.clear()
            assert "not bound" in unbound(man, d)
            (BIND / "ok.json").write_text(json.dumps(rec))
            _BOUND.clear()
            assert unbound(man, d) is None and unbound(man, None) is None
            (d / "result.json").write_text('{"x": 1}')
            _BOUND.clear()
            assert "result.json" in unbound(man, d)
            (d / "result.json").write_text("{}")
            (d / "extra.npy").write_bytes(b"1")
            _BOUND.clear()
            assert "extra.npy" in unbound(man, d)
            # run_bound end to end with a fake trainer; gates stubbed (they need a committed manifest)
            g = globals()
            gates = g["check_manifest"], g["check_code"], g["check_job"]
            g["check_manifest"], g["check_code"], g["check_job"] = (lambda *_: None), (lambda *_: None), (lambda *_: None)
            try:
                mf = Path(tmp) / "m.json"
                mf.write_text(json.dumps(man))
                d2 = (RAW / "EXP-001_baseline_seed1002_thr1_confirm_y_G").as_posix()
                fake = ("import pathlib, sys; d = pathlib.Path(sys.argv[1]); d.mkdir(); (d / 'result.json').write_text('{}'); "
                        "(d / 'run.lock').write_text('x')")
                cmd = [sys.executable, "-c", fake, d2, "--seed", "1002", "--split-file", "s/confirm_y_G.npy"]
                assert run_bound(mf, cmd) == 0
                _BOUND.clear()
                assert unbound(man, Path(d2)) is None
                assert run_bound(mf, cmd) == 0                            # already bound -> skipped (mkdir would fail)
                d3 = RAW / "EXP-001_baseline_seed1005_thr1_confirm_w_G"   # unbound completed run from elsewhere -> refused
                d3.mkdir()
                (d3 / "result.json").write_text('{"status": "completed"}')
                assert run_bound(mf, [sys.executable, "-c", "pass", "--seed", "1005", "--split-file", "s/confirm_w_G.npy"]) == 4
                d4 = RAW / "EXP-001_baseline_seed1006_thr1_confirm_v_G"   # trainer exits 0 without writing -> nothing bound
                d4.mkdir()
                (d4 / "result.json").write_text('{"status": "running"}')
                assert run_bound(mf, [sys.executable, "-c", "pass", "--seed", "1006", "--split-file", "s/confirm_v_G.npy"]) == 4
                _BOUND.clear()
                assert "result.json" in unbound(man, d4)
                def gate_trips(*_):                                        # code changes while the trainer sleeps -> killed
                    raise SystemExit("changed")
                g["check_code"], g["POLL_S"] = gate_trips, 0.2
                t_start = time.time()
                assert run_bound(mf, [sys.executable, "-c", "import time; time.sleep(30)", "--seed", "1007",
                                      "--split-file", "s/confirm_u_G.npy"]) == 4
                assert time.time() - t_start < 10
                g["check_code"], g["POLL_S"] = (lambda *_: None), 2.0
                assert run_bound(mf, [sys.executable, "-c", "raise SystemExit(3)", "--seed", "1003", "--split-file", "s/z.npy"]) == 3
                assert run_bound(mf, [sys.executable, "-c", "pass", "--seed", "1004", "--split-file", "s/none.npy"]) == 4
            finally:
                g["check_manifest"], g["check_code"], g["check_job"] = gates
            man_j = {"experiment": 1, "eps": 2.0, "seeds": [1000], "device": "cuda", "python": "PY", "threads": 1,
                     "tasks": [{"task": "add", "p": 113}]}
            check_job(man_j, shlex.split(trainer_jobs(man_j)[0]))
            try:
                check_job(man_j, shlex.split(trainer_jobs(man_j)[0]) + ["--force"])
                raise AssertionError("foreign command accepted")
            except SystemExit:
                pass
            sp = Path(tmp) / "s.npy"
            sp.write_bytes(b"x")
            (d / "extra.npy").unlink()
            _BOUND.clear()
            assert post_load_check(man, d, {"fingerprint_fields": {"split_file_sha256": _sha(sp)}}, sp) is None
            assert "split bytes" in post_load_check(man, d, {"fingerprint_fields": {"split_file_sha256": "0"}}, sp)
    finally:
        RAW, BIND = keep
        _BOUND.clear()


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
    elif len(a) == 2 and a[0] == "--jobs":
        m = json.loads(Path(a[1]).read_text(encoding="utf-8"))
        check_manifest(Path(a[1]), m)
        print("\n".join(jobs(m, Path(a[1]).resolve().relative_to(LAB.parent.resolve()).as_posix())))
    elif len(a) >= 4 and a[0] == "--run" and a[2] == "--":
        raise SystemExit(run_bound(Path(a[1]), a[3:]))
    elif len(a) == 2 and a[0] == "--analyze":
        analyze(Path(a[1]))
    else:
        raise SystemExit(__doc__)
