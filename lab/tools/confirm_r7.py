"""R7 confirmation (FINDINGS limit 3, paper rule 19a/b): does split steering (K2, Delta_pow of the W_E power) hold in a TWO-layer transformer
on fresh seeds? Session 33, UNTESTED (selftest in the window; Codex before freezing). Registration: lab/confirm/R7_REGISTRATION_DRAFT.md.

Freeze ONLY after the EXP-078 pilot reads "Steuerung überträgt sich auf zwei Schichten (Pilot)"; N_UNITS is set from the pilot spread by
the rule in the registration BEFORE the selftest and the freeze (N_UNITS None = not freezable).
Unit = seed with an F/G pair (same init for F and G, as P1). Experiment id 10 (confirm_splits streams; ids 1-9 and 98 are taken).
  2L   EXP-078 train2l.py (lean trainer + TwoLayerTransformer), add 113, P1 construction, 10 000 steps; primary Delta_pow at 2000,
       secondary at 10 000
  1L   lean trainer lab/paper/repro/train.py (one layer, same init order), same seeds and splits, 2000 steps; secondary only: paired
       difference D_2L - D_1L at 2000 (reported, no verdict)
Verdict: all n units valid, exact one-sided sign-flip p < 0.05 AND bootstrap CI lower bound >= MIN_EFFECT (1.0, as P1); any technical
failure -> "nicht auswertbar". One primary hypothesis, no family correction.

  python lab/tools/confirm_r7.py --selftest
  python lab/tools/confirm_r7.py --splits|--jobs|--analyze lab/confirm/R7_manifest.json
"""
from __future__ import annotations

import io
import json
import shlex
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
import confirm_p1 as c1  # noqa: E402  (read-only reuse: interp, delta_pow_checked, sign_flip_p, boot_ci)
import confirm_splits as cs  # noqa: E402
from bound_block import Block, selftest_binding, sha  # noqa: E402

RAW = LAB / "confirm" / "r7_raw"
BIND = LAB / "confirm" / "r7_bindings"
SPL = LAB / "confirm" / "r7_splits"
T2 = "lab/experiments/EXP-078-two-layer-steering/train2l.py"
T1 = "lab/paper/repro/train.py"
P, ALPHA, MIN_EFFECT, EPS, EXPERIMENT = 113, 0.05, 1.0, 2.0, 10
N_UNITS: int | None = None                    # set from the EXP-078 pilot by the registered rule, then selftest, then freeze
N_ALLOWED = (10, 15, 20, 25, 30)
SEED_MIN, SEED_MAX = 2900, 2929
STEPS = {"2L": 10_000, "1L": 2000}
PRIMARY_STEP = 2000
MODEL_TAG = "EXP-078 TwoLayerTransformer"
REGISTERED = {"experiment": EXPERIMENT, "p": P, "eps": EPS, "device": "cuda", "threads": 1, "steps": dict(STEPS),
              "primary_step": PRIMARY_STEP}            # "seeds" (N_UNITS ints) is added at registration
CODE_FILES = ("lab/tools/confirm_r7.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py",
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/make_split.py",
              "lab/experiments/EXP-046-dihedral-steering/dihedral.py", T2, T1,
              "lab/experiments/EXP-078-two-layer-steering/two_layer.py")


# ---------------------------------------------------------------- design and splits
def check_design(man: dict, n: int | None = None) -> None:
    n = N_UNITS if n is None else n
    if n not in N_ALLOWED:
        raise SystemExit(f"R7: N_UNITS {n!r} not set by the registered rule (allowed {N_ALLOWED}); not freezable")
    seeds = man.get("seeds")
    if (not isinstance(seeds, list) or len(seeds) != n or len(set(seeds)) != n or not all(type(x) is int for x in seeds)
            or seeds != list(range(SEED_MIN, SEED_MIN + n))):
        raise SystemExit(f"R7 manifest: seeds must be exactly {SEED_MIN}..{SEED_MIN + n - 1} (reserved {SEED_MIN}-{SEED_MAX})")


def stem(s: int, arm: str) -> str:
    return f"r7_seed{s}_{arm}"


def build(s: int, arm: str) -> tuple[np.ndarray, dict[str, list[int]]]:
    idx, _ = cs.build(EXPERIMENT, "add", P, s, arm, EPS)
    return idx, cs.target_sets(EXPERIMENT, "add", P, s)


def write_splits(man: dict) -> None:
    check_design(man)
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
    return (f"{c1.interp(man)} {tr} --seed {s} --split-file lab/confirm/r7_splits/{stem(s, a)}.npy --steps {man['steps'][model]} "
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
    argv = r.get("argv", [])
    sp = SPL / f"{stem(s, a)}.npy"
    if (r.get("status") != "completed" or r.get("seed") != s or r.get("steps") != man["steps"][model] or r.get("device") != man["device"]
            or (model == "2L") != str(r.get("model", "")).startswith(MODEL_TAG)):
        return f"defekt: result.json fields {r.get('status')}/{r.get('seed')}/{r.get('steps')}/{r.get('device')}/{r.get('model')}"
    if "--split-file" not in argv or Path(argv[argv.index("--split-file") + 1]).name != sp.name:
        return "defekt: split file in result.json does not match seed/arm"
    if len(pw) != len(st):
        return "defekt: spectra and steps differ in length"
    out: dict = {"test_acc": (r.get("final_acc") or {}).get("test"), "gen_step": r.get("generalization_step"),
                 "split_sha256": sha(sp)}
    for step in sorted({PRIMARY_STEP, man["steps"][model]}):
        if step not in st:
            return f"defekt: no spectrum at {step}"
        v = pw[st.index(step)]
        if v.shape != (56,) or not np.all(np.isfinite(v)) or not np.all(v > 0):
            return f"defekt: spectrum at {step} shape/values"
        out[step] = v
    return out


def seed_row(man: dict, s: int) -> dict:
    T = {a: json.loads((SPL / f"{stem(s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
    runs = {(m, a): spectra(man, m, s, a) for m in ("2L", "1L") for a in "FG"}
    bad2 = [f"2L {a}: {runs[('2L', a)]}" for a in "FG" if isinstance(runs[("2L", a)], str)]
    if bad2:
        return {"seed": s, "technical": True, "reason": "; ".join(bad2)}
    D = lambda m, step: c1.delta_pow_checked(runs[(m, "F")][step], runs[(m, "G")][step], T["F"], T["G"])   # noqa: E731
    row = {"seed": s, "technical": False, "D2000": D("2L", PRIMARY_STEP), "D10000": D("2L", STEPS["2L"]),
           **{f"{k}_2L_{a}": runs[("2L", a)][k] for a in "FG" for k in ("test_acc", "gen_step")}}
    if row["D2000"] is None:
        return {"seed": s, "technical": True, "reason": "Delta_pow undefined"}
    ok1 = not any(isinstance(runs[("1L", a)], str) for a in "FG")
    row["D1L_2000"] = D("1L", PRIMARY_STEP) if ok1 else None
    row["reason_1L"] = None if ok1 else "; ".join(f"{a}: {runs[('1L', a)]}" for a in "FG" if isinstance(runs[("1L", a)], str))
    return row


def summarize(D: np.ndarray, rng: np.random.Generator) -> dict:
    return {"n": len(D), "mean": float(D.mean()), "sd": float(D.std(ddof=1)) if len(D) > 1 else None, "ci95": c1.boot_ci(D, rng),
            "p_one_sided": c1.sign_flip_p(D, rng), "n_positive": int((D > 0).sum())}


def verdict(rows: list[dict], n_planned: int, rng: np.random.Generator) -> dict:
    n_tech = sum(1 for r in rows if r.get("technical"))
    if n_tech or len(rows) != n_planned or n_planned not in N_ALLOWED:
        return {"n": len(rows), "n_technical": n_tech, "verdict": "nicht auswertbar"}
    prim = summarize(np.array([r["D2000"] for r in rows]), rng)
    out = {"primary_D2000": prim, "n_technical": 0,
           "verdict": "bestätigt" if prim["p_one_sided"] < ALPHA and prim["ci95"][0] >= MIN_EFFECT else "nicht bestätigt"}
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
    bad = [m for m in (split_mismatch(s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"R7 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [seed_row(man, s) for s in man["seeds"]]
    out = {"manifest_commit": man["commit"], "min_effect": MIN_EFFECT,
           "result": verdict(rows, len(man["seeds"]), np.random.default_rng(10)), "rows": rows}
    stale.write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False, default=float))


def n_rule(pilot_D2000: list[float]) -> int:
    """Registered rule (R7 draft): assume half the pilot mean (winner's curse) and the pilot SD; smallest n in N_ALLOWED whose simulated
    power (400 normal draws) for the CI criterion (bootstrap 95 % lower bound >= MIN_EFFECT, 1000 resamples) is >= 0.8; 30 if none.
    Surrogate: the sign-flip criterion is not simulated (with a lower bound >= 1 > 0 it is practically always met)."""
    d = np.asarray(pilot_D2000, dtype=np.float64)
    m, sd = d.mean() / 2, d.std(ddof=1)
    rng = np.random.default_rng(710)
    for n in N_ALLOWED:
        hits = 0
        for _ in range(400):
            x = rng.normal(m, sd, n)
            boot = x[rng.integers(0, n, size=(1000, n))].mean(axis=1)
            hits += np.quantile(boot, 0.025) >= MIN_EFFECT
        if hits / 400 >= 0.8:
            return n
    return N_ALLOWED[-1]


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
    try:
        check_design({"seeds": seeds}, None if N_UNITS is None else 11)
        raise AssertionError("unset or illegal N_UNITS accepted")
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
    # the two trainers accept every option of the job lines (argparse of the lean trainer; train2l passes through)
    src = (ROOT / T1).read_text(encoding="utf-8")
    for opt in ("--seed", "--split-file", "--steps", "--device", "--threads", "--out"):
        assert f'"{opt}"' in src, opt
    assert '"status": "completed"' in src, "lean trainer must mark completed runs (bound_block)"
    # measure and verdict logic
    pF, pG = np.ones(56), np.ones(56)
    pF[[0, 1, 2, 3, 4]] = np.e
    assert abs(c1.delta_pow_checked(pF, pG, [1, 2, 3, 4, 5], [6, 7, 8, 9, 10]) - 1.0) < 1e-12
    rng = np.random.default_rng(0)
    ok = [{"seed": i, "technical": False, "D2000": 4.0 + 0.1 * i, "D10000": 6.0, "D1L_2000": 5.0, "gen_step_2L_F": 900,
           "gen_step_2L_G": None} for i in range(n)]
    v = verdict(ok, n, rng)
    assert v["verdict"] == "bestätigt" and v["n_units_2L_generalised_both"] == 0, v
    assert abs(v["secondary_paired_2L_minus_1L_at2000"]["mean"] - (4.0 + 0.1 * 7 - 5.0)) < 1e-9
    assert verdict(ok[:14], n, rng)["verdict"] == "nicht auswertbar"
    assert verdict(ok[:14] + [{"seed": 99, "technical": True}], n, rng)["verdict"] == "nicht auswertbar"
    weak = [{**r, "D2000": 0.5 + 0.05 * i} for i, r in enumerate(ok)]
    assert verdict(weak, n, rng)["verdict"] == "nicht bestätigt"
    mixed = [{**r, "D2000": (3.0 if i % 2 else -2.5)} for i, r in enumerate(ok)]
    assert verdict(mixed, n, rng)["verdict"] == "nicht bestätigt"
    assert verdict(ok[:11], 11, rng)["verdict"] == "nicht auswertbar"
    # n rule: a strong pilot needs the minimum, a weak and noisy one the maximum
    assert n_rule([8.0 + 0.3 * i for i in range(10)]) == 10
    assert n_rule([2.0, -1.0, 4.0, 0.5, 3.0, -0.5, 2.5, 1.0, 3.5, 0.0]) == 30
    selftest_binding(BLOCK, tj[0], tj[1], tj[2 * n])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    print("[confirm_r7] selftest ok", flush=True)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--n-rule"]:          # python lab/tools/confirm_r7.py --n-rule lab/experiments/EXP-078-two-layer-steering/summary.json
        rows = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))["rows"]
        print(json.dumps({"n_units": n_rule([r["D2000"] for r in rows]), "pilot_n": len(rows)}))
    else:
        BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
