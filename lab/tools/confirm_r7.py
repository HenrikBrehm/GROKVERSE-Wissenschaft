"""R7 confirmation (FINDINGS limit 3, paper rule 19a/b): does split steering (K2, Delta_pow of the W_E power) hold in a TWO-layer transformer
on fresh seeds? Session 33, UNTESTED (selftest in the window). Registration: lab/confirm/R7_REGISTRATION_DRAFT.md (Fassung 2 after the
Codex review of session 33: 1 blocker, 4 major, all taken over).

No gate on the pilot's reading (symmetric design, Codex s33 point 5): R7 is frozen after the EXP-078 pilot has run with all 10 units
valid, whatever its reading. The pilot only sets n: N_UNITS = n_rule(pilot), a pure function of the pilot summary, whose sha256 and
reading are bound in the manifest ("pilot") and re-checked at analysis (Codex s33 point 3).
Unit = seed with an F/G pair (same init for F and G, as P1). Experiment id 10 (confirm_splits streams; ids 1-9 and 98 are taken).
  2L   EXP-078 train2l.py (lean trainer + TwoLayerTransformer), add 113, P1 construction, 10 000 steps; primary Delta_pow at 2000,
       secondary at 10 000
  1L   lean trainer lab/paper/repro/train.py (one layer, same init order), same seeds and splits, 2000 steps; secondary only: paired
       difference D_2L - D_1L at 2000 (reported, no verdict)
Primary verdict: all n units valid, EXACT one-sided sign-flip p < 0.05 (full enumeration, n <= 20; Codex s33 blocker) AND bootstrap CI
lower bound >= MIN_EFFECT (1.0, as P1) -> "bestätigt"; else "nicht bestätigt"; any technical failure -> "nicht auswertbar".
Registered second reading (symmetric): EXACT one-sided sign-flip p of (LIMIT - D) < 0.05 AND bootstrap CI upper bound < LIMIT (0.5)
-> "keine Steuerung von Belang bestätigt" (session 34 review: same evidential standard as the positive reading).
Only the primary step (2000) is fatal: a missing/invalid 2L spectrum at 10 000 gives D10000 = None with a reason (session 34 review).
The trainer records the sha256 of the split bytes it loaded; the analysis requires it to equal the registered split (Codex s33 point 4).

  python lab/tools/confirm_r7.py --selftest
  python lab/tools/confirm_r7.py --n-rule lab/experiments/EXP-078-two-layer-steering/summary.json    # prints the manifest "pilot" block
  python lab/tools/confirm_r7.py --splits|--jobs|--analyze lab/confirm/R7_manifest.json
  python lab/tools/confirm_r7.py --smoke-check lab/confirm/R7_manifest.json    # after the 4 smoke jobs of the first seed: loader path, no values
"""
from __future__ import annotations

import functools
import io
import json
import shlex
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
import confirm_p1 as c1  # noqa: E402  (read-only reuse: interp, delta_pow_checked, boot_ci, N_BOOT)
import confirm_splits as cs  # noqa: E402
from bound_block import Block, selftest_binding, sha  # noqa: E402

RAW = LAB / "confirm" / "r7_raw"
BIND = LAB / "confirm" / "r7_bindings"
SPL = LAB / "confirm" / "r7_splits"
T2 = "lab/experiments/EXP-078-two-layer-steering/train2l.py"
T1 = "lab/paper/repro/train.py"
PILOT = "lab/experiments/EXP-078-two-layer-steering/summary.json"
PILOT_SEEDS = list(range(1000, 1010))
P, ALPHA, MIN_EFFECT, LIMIT, EPS, EXPERIMENT = 113, 0.05, 1.0, 0.5, 2.0, 10
N_UNITS: int | None = None                    # = n_rule(pilot), set after EXP-078, then selftest, then freeze
N_ALLOWED = (10, 15, 20)                      # exact sign-flip enumeration up to 2^20 (Codex s33 blocker)
N_SIM = 1000                                  # outer simulations of the n rule (Codex s33: 400 too coarse)
SEED_MIN, SEED_MAX = 2900, 2929
STEPS = {"2L": 10_000, "1L": 2000}
PRIMARY_STEP = 2000
MODEL_TAG = "EXP-078 TwoLayerTransformer"
REGISTERED = {"experiment": EXPERIMENT, "p": P, "eps": EPS, "device": "cuda", "threads": 1, "steps": dict(STEPS),
              "primary_step": PRIMARY_STEP}            # plus "seeds" and "pilot" (from --n-rule) at registration
CODE_FILES = ("lab/tools/confirm_r7.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py",
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/make_split.py",
              "lab/experiments/EXP-046-dihedral-steering/dihedral.py", T2, T1,
              "lab/experiments/EXP-078-two-layer-steering/two_layer.py", "lab/experiments/EXP-078-two-layer-steering/analyze.py",
              "lab/tools/result_loader.py", "lab/paper/repro/k2.py")                   # session 34 review: executed imports


# ---------------------------------------------------------------- statistics
def exact_sign_flip_p(d: np.ndarray) -> float:
    """Exact one-sided sign-flip p of the mean (all 2^n sign vectors, n <= 20), ties counted as extreme (as confirm_p1)."""
    n = len(d)
    if not 1 <= n <= 20:
        raise ValueError(f"exact sign flip needs 1 <= n <= 20, got {n}")
    return float(((_signs(n) @ d) / n >= d.mean() - 1e-12).mean())


@functools.lru_cache(maxsize=4)
def _signs(n: int) -> np.ndarray:
    return 1.0 - 2.0 * ((np.arange(2 ** n, dtype=np.int64)[:, None] >> np.arange(n)) & 1)


def ci_lower(x: np.ndarray, rng: np.random.Generator, n_boot: int) -> float:
    return float(np.quantile(x[rng.integers(0, len(x), size=(n_boot, len(x)))].mean(axis=1), 0.025))


def n_rule(pilot_D2000: list[float]) -> int:
    """Registered rule: effect = half the pilot mean (winner's curse), SD = pilot SD; smallest n in N_ALLOWED whose simulated power for
    the ACTUAL conjunctive verdict (exact sign-flip p < ALPHA and bootstrap lower bound >= MIN_EFFECT with c1.N_BOOT resamples) is >= 0.8
    over N_SIM normal draws; the largest n if none (Codex s33 point 2)."""
    d = np.asarray(pilot_D2000, dtype=np.float64)
    m, sd = d.mean() / 2, d.std(ddof=1)
    rng = np.random.default_rng(710)
    for n in N_ALLOWED:
        hits = 0
        for _ in range(N_SIM):
            x = rng.normal(m, sd, n)
            hits += ci_lower(x, rng, c1.N_BOOT) >= MIN_EFFECT and exact_sign_flip_p(x) < ALPHA   # bootstrap first; exact test skipped if it fails
        if hits / N_SIM >= 0.8:
            return n
    return N_ALLOWED[-1]


def pilot_block(path: Path) -> dict:
    """Validated pilot summary -> the manifest's "pilot" block. Requires all 10 pilot units valid with finite D2000."""
    raw = path.read_bytes()
    s = json.loads(raw.decode("utf-8"))
    rows = s.get("rows") or []
    D = [r.get("D2000") for r in rows]
    if (s.get("n_valid") != len(PILOT_SEEDS) or sorted(r.get("seed") for r in rows) != PILOT_SEEDS or s.get("problems")
            or not all(isinstance(x, float) and np.isfinite(x) for x in D)):
        raise SystemExit("R7: pilot summary not complete (10 valid units, seeds 1000-1009, finite D2000, no problems) -> R7 not freezable")
    return {"summary": PILOT, "summary_sha256": sha(path) if path.resolve() == (ROOT / PILOT).resolve() else None,
            "reading": s.get("reading"), "mean_D2000": float(np.mean(D)), "sd_D2000": float(np.std(D, ddof=1)), "n_units": n_rule(D)}


def check_pilot(man: dict) -> None:
    pb = man.get("pilot") or {}
    now = pilot_block(ROOT / PILOT)
    if pb != now or pb.get("summary_sha256") != sha(ROOT / PILOT) or pb.get("n_units") != N_UNITS:
        raise SystemExit("R7: manifest pilot block differs from the bound pilot summary or from N_UNITS")
    import hashlib
    import subprocess
    pc = str(man.get("pilot_commit", "")).strip()          # Fassung 3: summary committed together with its analysis log
    got = subprocess.run(["git", "show", f"{pc}:{PILOT}"], cwd=ROOT, capture_output=True) if pc else None
    if got is None or got.returncode != 0 or hashlib.sha256(got.stdout).hexdigest() != pb.get("summary_sha256"):
        raise SystemExit("R7: pilot_commit missing or its EXP-078 summary.json differs from the bound pilot summary")


# ---------------------------------------------------------------- design and splits
def check_design(man: dict, n: int | None = None) -> None:
    n = N_UNITS if n is None else n
    if n not in N_ALLOWED:
        raise SystemExit(f"R7: N_UNITS {n!r} not set by the registered rule (allowed {N_ALLOWED}); not freezable")
    seeds = man.get("seeds")
    if (not isinstance(seeds, list) or len(seeds) != n or not all(type(x) is int for x in seeds)
            or seeds != list(range(SEED_MIN, SEED_MIN + n))):
        raise SystemExit(f"R7 manifest: seeds must be exactly {SEED_MIN}..{SEED_MIN + n - 1} (reserved {SEED_MIN}-{SEED_MAX})")


def stem(s: int, arm: str) -> str:
    return f"r7_seed{s}_{arm}"


def split_arg(s: int, a: str) -> str:
    return f"lab/confirm/r7_splits/{stem(s, a)}.npy"


def build(s: int, arm: str) -> tuple[np.ndarray, dict[str, list[int]]]:
    idx, _ = cs.build(EXPERIMENT, "add", P, s, arm, EPS)
    return idx, cs.target_sets(EXPERIMENT, "add", P, s)


def write_splits(man: dict) -> None:
    check_design(man)
    check_pilot(man)
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, a)}{ext}" for s in man["seeds"] for a in "FG" for ext in (".npy", ".json")]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("R7 splits exist already: never overwrite")
    for s in man["seeds"]:
        for a in "FG":
            idx, T = build(s, a)
            if len(idx) != int(round(0.3 * P * P)) or len(np.unique(idx)) != len(idx):
                raise SystemExit(f"R7 split {stem(s, a)}: bad size")
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, idx.astype(np.int64))
            with open(SPL / f"{stem(s, a)}.json", "x", encoding="utf-8") as f:
                json.dump({"seed": s, "arm": a, "targets": T[a], "other_targets": T["G" if a == "F" else "F"], "eps": EPS,
                           "n": int(len(idx)), "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(s: int) -> str | None:
    for a in "FG":
        idx, T = build(s, a)
        f, j = SPL / f"{stem(s, a)}.npy", SPL / f"{stem(s, a)}.json"
        if not f.exists() or not j.exists():
            return f"{stem(s, a)}: split file missing"
        meta = json.loads(j.read_text(encoding="utf-8"))
        if not (np.array_equal(np.load(f), idx.astype(np.int64)) and meta.get("targets") == T[a] and meta.get("seed") == s):
            return f"{stem(s, a)}: differs from the deterministic rebuild"
    return None


# ---------------------------------------------------------------- jobs and binding
def out_dir(model: str, s: int, a: str) -> str:
    return f"lab/confirm/r7_raw/r7_{model}_seed{s}_{a}"


def job(man: dict, model: str, s: int, a: str) -> str:
    tr = T2 if model == "2L" else T1
    return (f"{c1.interp(man)} {tr} --seed {s} --split-file {split_arg(s, a)} --steps {man['steps'][model]} "
            f"--device {man['device']} --threads {man['threads']} --out {out_dir(model, s, a)}")


def trainer_jobs(man: dict) -> list[str]:
    return [job(man, m, s, a) for m in ("2L", "1L") for s in man["seeds"] for a in "FG"]


def run_dir(cmd: list[str]) -> Path:
    if "--out" not in cmd:
        raise SystemExit(f"R7: command without --out: {' '.join(cmd)[:120]}")
    d = (ROOT / cmd[cmd.index("--out") + 1]).resolve()
    if d.parent != RAW.resolve():
        raise SystemExit(f"R7: --out outside lab/confirm/r7_raw: {d}")
    return RAW / d.name


BLOCK = Block(name="confirm_r7", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_r7.py")


# ---------------------------------------------------------------- analysis
def check_result(r: dict, man: dict, model: str, s: int, sp: str) -> str | None:
    """Provenance of one result.json (sp = registered split path as in the job line); None = ok."""
    argv = r.get("argv", [])
    if (r.get("status") != "completed" or r.get("seed") != s or r.get("steps") != man["steps"][model] or r.get("device") != man["device"]
            or (model == "2L") != str(r.get("model", "")).startswith(MODEL_TAG)):
        return f"result.json fields {r.get('status')}/{r.get('seed')}/{r.get('steps')}/{r.get('device')}/{r.get('model')}"
    if "--split-file" not in argv or argv[argv.index("--split-file") + 1] != sp:
        return "split file in result.json does not match seed/arm"
    if (r.get("input_sha256") or {}).get(sp) != sha(ROOT / sp):
        return "bytes the trainer loaded differ from the registered split"
    return None


def spectra(man: dict, model: str, s: int, a: str) -> dict | str:
    """W_E power k = 1..56 at the needed steps from BOUND bytes, with provenance checks; a string = technical failure."""
    d = run_dir(shlex.split(job(man, model, s, a)))
    if not (d / "result.json").exists():
        return "fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"defekt: {why}"
    try:
        r = json.loads(BLOCK.bound_bytes(man, d / "result.json").decode("utf-8"))
        pw = np.load(io.BytesIO(BLOCK.bound_bytes(man, d / "spectra.npy"))).astype(np.float64)
        st = np.load(io.BytesIO(BLOCK.bound_bytes(man, d / "spectra_steps.npy"))).tolist()
    except (OSError, ValueError) as ex:
        return f"defekt: {ex}"
    if (why := check_result(r, man, model, s, split_arg(s, a))):
        return f"defekt: {why}"
    if len(pw) != len(st):
        return "defekt: spectra and steps differ in length"
    out: dict = {"test_acc": (r.get("final_acc") or {}).get("test"), "gen_step": r.get("generalization_step"), "bad_final": None}
    for step in sorted({PRIMARY_STEP, man["steps"][model]}):
        v = pw[st.index(step)] if step in st else None
        why = (f"no spectrum at {step}" if v is None else
               f"spectrum at {step} shape/values" if v.shape != (56,) or not np.all(np.isfinite(v)) or not np.all(v > 0) else None)
        if why and step == PRIMARY_STEP:
            return f"defekt: {why}"
        out[step] = None if why else v
        if why:                                      # session 34 review: only the primary step is fatal
            out["bad_final"] = why
    return out


def seed_row(man: dict, s: int) -> dict:
    T = {a: json.loads((SPL / f"{stem(s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
    runs = {(m, a): spectra(man, m, s, a) for m in ("2L", "1L") for a in "FG"}
    bad2 = [f"2L {a}: {runs[('2L', a)]}" for a in "FG" if isinstance(runs[("2L", a)], str)]
    if bad2:
        return {"seed": s, "technical": True, "reason": "; ".join(bad2)}
    D = lambda m, step: c1.delta_pow_checked(runs[(m, "F")][step], runs[(m, "G")][step], T["F"], T["G"])   # noqa: E731
    ok10 = all(runs[("2L", a)][STEPS["2L"]] is not None for a in "FG")
    row = {"seed": s, "technical": False, "D2000": D("2L", PRIMARY_STEP), "D10000": D("2L", STEPS["2L"]) if ok10 else None,
           "reason_10000": None if ok10 else "; ".join(f"{a}: {runs[('2L', a)]['bad_final']}" for a in "FG" if runs[("2L", a)]["bad_final"]),
           **{f"{k}_2L_{a}": runs[("2L", a)][k] for a in "FG" for k in ("test_acc", "gen_step")}}
    if row["D2000"] is None:
        return {"seed": s, "technical": True, "reason": "Delta_pow undefined"}
    ok1 = not any(isinstance(runs[("1L", a)], str) for a in "FG")
    row["D1L_2000"] = D("1L", PRIMARY_STEP) if ok1 else None
    row["reason_1L"] = None if ok1 else "; ".join(f"{a}: {runs[('1L', a)]}" for a in "FG" if isinstance(runs[("1L", a)], str))
    return row


def summarize(D: np.ndarray, rng: np.random.Generator) -> dict:
    return {"n": len(D), "mean": float(D.mean()), "sd": float(D.std(ddof=1)) if len(D) > 1 else None, "ci95": c1.boot_ci(D, rng),
            "p_one_sided_exact": exact_sign_flip_p(D) if len(D) <= 20 else None, "n_positive": int((D > 0).sum())}


def limit_ok(D: np.ndarray, ci95: list[float]) -> bool:
    """Symmetric second reading (session 34 review): exact one-sided sign-flip p of (LIMIT - D) < ALPHA AND CI upper bound < LIMIT."""
    return exact_sign_flip_p(LIMIT - D) < ALPHA and ci95[1] < LIMIT


def verdict(rows: list[dict], n_planned: int, rng: np.random.Generator) -> dict:
    n_tech = sum(1 for r in rows if r.get("technical"))
    if n_tech or len(rows) != n_planned or n_planned not in N_ALLOWED:
        return {"n": len(rows), "n_technical": n_tech, "verdict": "nicht auswertbar", "limit_reading": "nicht auswertbar"}
    prim = summarize(np.array([r["D2000"] for r in rows]), rng)
    out = {"primary_D2000": prim, "n_technical": 0,
           "verdict": "bestätigt" if prim["p_one_sided_exact"] < ALPHA and prim["ci95"][0] >= MIN_EFFECT else "nicht bestätigt",
           "limit_reading": "keine Steuerung von Belang bestätigt" if limit_ok(np.array([r["D2000"] for r in rows]), prim["ci95"])
           else "nicht belegt"}
    sec = [r["D10000"] for r in rows if r.get("D10000") is not None]
    out["secondary_D10000"] = summarize(np.array(sec), rng) if len(sec) > 1 else None
    pair = [r["D2000"] - r["D1L_2000"] for r in rows if r.get("D1L_2000") is not None]
    out["secondary_paired_2L_minus_1L_at2000"] = summarize(np.array(pair), rng) if len(pair) > 1 else None
    out["n_units_2L_generalised_both"] = int(sum(r.get("gen_step_2L_F") is not None and r.get("gen_step_2L_G") is not None for r in rows))
    return out


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "R7_summary.json"
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    check_design(man)
    check_pilot(man)
    bad = [m for m in (split_mismatch(s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"R7 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [seed_row(man, s) for s in man["seeds"]]
    out = {"manifest_commit": man["commit"], "min_effect": MIN_EFFECT, "limit": LIMIT, "pilot": man["pilot"],
           "result": verdict(rows, len(man["seeds"]), np.random.default_rng(10)), "rows": rows}
    stale.write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False, default=float))


def smoke_check(manifest: Path) -> None:
    """Session 34 review: after the 4 smoke jobs of the first seed (2L F/G, 1L F/G) run the REAL loader path (bound bytes, check_result,
    spectra, seed_row) for that seed and print only which fields are defined, never a value. Exit 1 if the row is not complete."""
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    check_design(man)
    check_pilot(man)
    s = man["seeds"][0]
    if (m := split_mismatch(s)):
        raise SystemExit(f"R7 smoke: {m}")
    row = seed_row(man, s)
    shown = {"seed": s, "technical": row.get("technical"), "reason": row.get("reason"),
             **{k: (row.get(k) is not None and bool(np.isfinite(row[k]))) for k in ("D2000", "D10000", "D1L_2000")},
             "reason_10000": row.get("reason_10000"), "reason_1L": row.get("reason_1L")}
    print(json.dumps(shown, indent=1, ensure_ascii=False))
    if row.get("technical") or not all(shown[k] for k in ("D2000", "D10000", "D1L_2000")):
        raise SystemExit(1)
    print("[confirm_r7] smoke check ok (loader path complete for the first seed; values not shown)", flush=True)


# ---------------------------------------------------------------- selftest
def selftest() -> None:
    n = 15
    seeds = list(range(SEED_MIN, SEED_MIN + n))
    for bad in (seeds[:14], seeds[1:] + [SEED_MIN + 15], [float(x) for x in seeds], [SEED_MIN] * n):
        try:
            check_design({"seeds": bad}, n)
            raise AssertionError("bad seed design accepted")
        except SystemExit:
            pass
    check_design({"seeds": seeds}, n)
    for illegal in (None if N_UNITS is None else 11, 25, 30):
        try:
            check_design({"seeds": seeds}, illegal)
            raise AssertionError(f"illegal n {illegal} accepted")
        except SystemExit:
            pass
    man = {**REGISTERED, "python": "PY", "seeds": seeds}
    BLOCK.check_registered(man)
    tj = trainer_jobs(man)
    assert len(tj) == 2 * n * 2 and len(set(tj)) == len(tj) and all("r7_raw" in j and "\\" not in j for j in tj)
    dirs = [run_dir(shlex.split(j)) for j in tj]
    assert len(set(dirs)) == len(dirs) and dirs[0] == RAW / f"r7_2L_seed{SEED_MIN}_F", dirs[0]
    assert T2 in tj[0] and "--steps 10000" in tj[0] and T1 in tj[2 * n] and "--steps 2000" in tj[2 * n]
    try:
        run_dir(["x", "--out", "lab/confirm/raw/elsewhere"])
        raise AssertionError("out dir outside r7_raw accepted")
    except SystemExit:
        pass
    # splits = the P1 construction with experiment 10, other streams than P1 (1), P4 (7), R1 (8/9)
    for a in "FG":
        idx, T = build(SEED_MIN, a)
        ref, Tr = cs.build(EXPERIMENT, "add", P, SEED_MIN, a, EPS)
        assert np.array_equal(idx, ref) and T[a] == Tr and len(idx) == 3831 and not set(T["F"]) & set(T["G"])
        for e in (1, 7, 8, 9):
            assert not np.array_equal(idx, cs.build(e, "add", P, SEED_MIN, a, EPS)[0]), e
    # trainers: options of the job lines, completed flag and input hash in the lean trainer (train2l passes both through)
    src = (ROOT / T1).read_text(encoding="utf-8")
    for opt in ("--seed", "--split-file", "--steps", "--device", "--threads", "--out"):
        assert f'"{opt}"' in src, opt
    assert '"status": "completed"' in src and '"input_sha256"' in src, "lean trainer must mark completed runs and hash its inputs"
    # provenance check on a fake result.json of a real split file of this repo (the P1 split of seed 1000)
    sp_real = "lab/confirm/splits/confirm_exp1_eps2.0_add113_seed1000_F.npy"
    good = {"status": "completed", "seed": 1000, "steps": 2000, "device": "cuda", "argv": ["t", "--split-file", sp_real],
            "input_sha256": {sp_real: sha(ROOT / sp_real)}}
    assert check_result(good, man, "1L", 1000, sp_real) is None
    assert "differ" in check_result({**good, "input_sha256": {sp_real: "0" * 64}}, man, "1L", 1000, sp_real)
    assert "fields" in check_result({**good, "model": MODEL_TAG}, man, "1L", 1000, sp_real)
    assert check_result({**good, "steps": 10000, "model": MODEL_TAG + " (x)"}, man, "2L", 1000, sp_real) is None
    assert "fields" in check_result({**good, "status": "running"}, man, "1L", 1000, sp_real)
    assert "does not match" in check_result(good, man, "1L", 1000, split_arg(1000, "F"))
    # exact sign flip agrees with confirm_p1 (exact for n <= 20) and is exact at n = 20
    rng = np.random.default_rng(0)
    for k in (5, 10, 15):
        x = rng.normal(0.3, 1.0, k)
        assert abs(exact_sign_flip_p(x) - c1.sign_flip_p(x, rng)) < 1e-12, k
    assert exact_sign_flip_p(np.arange(1.0, 21.0)) == 1 / 2 ** 20
    assert exact_sign_flip_p(np.array([9.0, 9.0, 9.0, 9.0, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5])) > ALPHA   # Codex s33 counterexample
    # verdict logic (primary and the symmetric limit reading)
    ok = [{"seed": i, "technical": False, "D2000": 4.0 + 0.1 * i, "D10000": 6.0, "D1L_2000": 5.0, "gen_step_2L_F": 900,
           "gen_step_2L_G": None} for i in range(n)]
    v = verdict(ok, n, rng)
    assert v["verdict"] == "bestätigt" and v["limit_reading"] == "nicht belegt" and v["n_units_2L_generalised_both"] == 0, v
    assert abs(v["secondary_paired_2L_minus_1L_at2000"]["mean"] - (4.0 + 0.1 * 7 - 5.0)) < 1e-9
    assert verdict(ok[:14], n, rng)["verdict"] == "nicht auswertbar"
    assert verdict(ok[:14] + [{"seed": 99, "technical": True}], n, rng)["verdict"] == "nicht auswertbar"
    weak = [{**r, "D2000": 0.5 + 0.05 * i} for i, r in enumerate(ok)]
    assert verdict(weak, n, rng)["verdict"] == "nicht bestätigt"
    null = [{**r, "D2000": 0.05 * ((-1) ** i)} for i, r in enumerate(ok)]
    vn = verdict(null, n, rng)
    assert vn["verdict"] == "nicht bestätigt" and vn["limit_reading"] == "keine Steuerung von Belang bestätigt", vn
    assert not limit_ok(np.array([0.45, 0.55] * 5), [0.3, 0.45]), "limit reading must need the exact test"
    assert limit_ok(np.array([0.05] * 10), [0.0, 0.1])
    mixed = [{**r, "D2000": (3.0 if i % 2 else -2.5)} for i, r in enumerate(ok)]
    assert verdict(mixed, n, rng)["verdict"] == "nicht bestätigt"
    assert verdict(ok[:11], 11, rng)["verdict"] == "nicht auswertbar"
    # n rule: a strong pilot needs the minimum, a weak/noisy one the maximum; pilot summary validation
    assert n_rule([8.0 + 0.3 * i for i in range(10)]) == 10
    assert n_rule([2.0, -1.0, 4.0, 0.5, 3.0, -0.5, 2.5, 1.0, 3.5, 0.0]) == 20
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "s.json"
        rows = [{"seed": s_, "D2000": 8.0 + 0.3 * i} for i, s_ in enumerate(PILOT_SEEDS)]
        f.write_text(json.dumps({"n_valid": 10, "problems": [], "reading": "x", "rows": rows}))
        pb = pilot_block(f)
        assert pb["n_units"] == 10 and pb["reading"] == "x" and pb["summary_sha256"] is None
        for broken in ({"n_valid": 9}, {"problems": ["seed 1003"]}, {"rows": rows[:9]}):
            f.write_text(json.dumps({"n_valid": 10, "problems": [], "reading": "x", "rows": rows, **broken}))
            try:
                pilot_block(f)
                raise AssertionError(f"incomplete pilot accepted: {broken}")
            except SystemExit:
                pass
    selftest_binding(BLOCK, tj[0], tj[1], tj[2 * n])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    print("[confirm_r7] selftest ok", flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--n-rule"]:
        print(json.dumps(pilot_block(Path(sys.argv[2])), indent=1, ensure_ascii=False))
    elif sys.argv[1:2] == ["--smoke-check"]:
        smoke_check(Path(sys.argv[2]))
    else:
        BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
