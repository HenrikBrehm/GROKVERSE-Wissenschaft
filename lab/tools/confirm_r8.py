"""R8 confirmation (FINDINGS programme B, time signature of the lock-in): does only a switch to OTHER target frequencies cost
grokking time? Session 37; selftest green (session 37), independent read-only review without blocker (session 37).

Registration: lab/confirm/R8_REGISTRATION_DRAFT.md (pilot EXP-086, seeds 400-409, seen).
Per seed s: A, B, test exactly as N28/R6 (EXP-053 overlap_split, omega = 0, calibrated eps); A2 = the EXP-086 construction (same target
set F as A, fresh phases and keys, disjoint from A, eps bisected so that the M0 share of A2 on F matches A within 0.005), own streams
SeedSequence([88_001, seed, purpose]). Runs: A, B, A2 alone (2000 steps); A->B, B->A, A->A2, A2->A at t = 25 (2025 steps, AdamW kept).
Time: b = min(first test >= 0.95 [trainer event], CAP = 2000) from step 0. C_XY = mean over both directions of
log2 b(switch) - log2 b(destination only).
Primary (one hypothesis): H1 D = C_AB - C_AA2 > 0; p = max(p_flip exact, p_sign) as R6; "bestätigt" at p < 0.05.
Secondary S1 (not in the verdict): mean C_AA2 < 0.5 * mean C_AB ("gestützt" if the 95 % bootstrap CI upper bound of
C_AA2 - 0.5 C_AB per seed is < 0). Any missing/unbound/broken run of any seed -> "nicht auswertbar".

  python lab/tools/confirm_r8.py --hash-code
  python lab/tools/confirm_r8.py --splits lab/confirm/R8_manifest.json        # after freezing; never overwrites
  python lab/tools/confirm_r8.py --jobs lab/confirm/R8_manifest.json > lab/confirm/R8_jobs.txt   # plain, NOT through guarded_run
  python lab/tools/confirm_r8.py --run lab/confirm/R8_manifest.json -- <trainer command>
  python lab/tools/confirm_r8.py --analyze lab/confirm/R8_manifest.json       # under guarded_run.py
  python lab/tools/confirm_r8.py --selftest                                   # under guarded_run.py
"""
from __future__ import annotations

import json
import math
import shlex
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "experiments/EXP-053-p3-overlap-design"))
import confirm_n28 as n28  # noqa: E402  (read-only reuse: expected_run_id)
import confirm_p1 as c1  # noqa: E402  (read-only reuse: interp, boot_ci)
import confirm_r6 as r6  # noqa: E402  (read-only reuse: p_flip, p_sign)
from bound_block import Block, selftest_binding, sha  # noqa: E402
import overlap_split as ov  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "r8_raw"
BIND = LAB / "confirm" / "r8_bindings"
SPL = LAB / "confirm" / "r8_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"
BUDGET, CAP, T_SW, ALPHA, OMEGA, SALT, SHARE_TOL = 2000, 2000, 25, 0.05, 0.0, 88_001, 0.005
TIE = 1e-9
PURPOSE = {"phases": 0, "keys": 1}
N_UNITS = 25                                      # power rule (R8_pilot_power.json, bootstrap AND normal model at half effect)
REGISTERED = {"seeds": list(range(3100, 3100 + N_UNITS)), "switch_step": T_SW, "device": "cuda", "threads": 1}
CODE_FILES = ("lab/tools/confirm_r8.py", "lab/tools/confirm_r6.py", "lab/tools/confirm_n28.py", "lab/tools/confirm_p1.py",
              "lab/tools/confirm_splits.py", "lab/tools/result_loader.py", "lab/tools/paket_a_device.py", FB,
              "lab/experiments/EXP-053-p3-overlap-design/overlap_split.py", "lab/experiments/EXP-053-p3-overlap-design/calibration.json",
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py")
ARMS = ("A", "B", "A2")
SWITCHES = (("A", "B"), ("B", "A"), ("A", "A2"), ("A2", "A"))


# ---------------------------------------------------------------- splits
def stem(s: int, arm: str) -> str:
    return f"r8_seed{s}_{arm}"


def rng_for(seed: int, purpose: str) -> np.random.Generator:
    return np.random.default_rng(np.random.SeedSequence([SALT, seed, PURPOSE[purpose]]))


def weighted_draw(cands: np.ndarray, q: np.ndarray, keys: np.ndarray, n: int) -> np.ndarray:
    """Weighted sampling without replacement (Efraimidis-Spirakis, as overlap_split / EXP-086): top n of u^(1/q)."""
    return np.sort(cands[np.argsort(-(keys ** (1.0 / q[cands])), kind="stable")[:n]])


def build(seed: int) -> dict:
    """A, B, test as R6; A2 as EXP-086 (same F, fresh phases/keys, eps bisected on the realised share)."""
    eps = json.loads(CAL.read_text(encoding="utf-8"))["levels"][str(OMEGA)]["eps"]
    d = ov.build(seed, OMEGA, eps)
    A, test = d["A"], d["test"]
    F, G = ov.targets(seed)
    cand = np.setdiff1d(np.setdiff1d(np.arange(113 * 113), test), A)
    goal = ov.share(A, F)
    ph, keys = rng_for(seed, "phases"), rng_for(seed, "keys").random(len(cand))
    state = ph.bit_generator.state
    lo, hi = 0.5, 80.0
    for _ in range(40):                                   # share rises monotonically in eps for fixed phases and keys
        mid = (lo * hi) ** 0.5
        ph.bit_generator.state = state                    # identical phases for every eps
        A2 = weighted_draw(cand, ov.weights(F, mid, ph), keys, ov.N_TRAIN)
        s_ = ov.share(A2, F)
        if abs(s_ - goal) <= 0.002:
            break
        lo, hi = (mid, hi) if s_ < goal else (lo, mid)
    assert len(A2) == ov.N_TRAIN and not np.intersect1d(A2, A).size and not np.intersect1d(A2, test).size
    assert len(d["A"]) == len(d["B"]) == ov.N_TRAIN and not np.intersect1d(d["A"], d["B"]).size
    assert not np.intersect1d(test, np.union1d(d["A"], d["B"])).size
    meta = {"seed": seed, "omega": OMEGA, "targets": {"A": F, "B": G}, "eps_A2": float(mid), "share_A_F": goal,
            "share_A2_F": ov.share(A2, F), "share_B_G": ov.share(d["B"], G), "share_A2_G": ov.share(A2, G),
            "overlap_A2_B": int(np.intersect1d(A2, d["B"]).size)}
    return {"A": A, "B": d["B"], "A2": A2, "test": test, "meta": meta}


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, a)}.npy" for s in man["seeds"] for a in ARMS + ("test",)]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("R8 splits exist already: never overwrite")
    for s in man["seeds"]:
        d = build(s)
        if abs(d["meta"]["share_A2_F"] - d["meta"]["share_A_F"]) > SHARE_TOL:
            raise SystemExit(f"R8 seed {s}: A2 share {d['meta']['share_A2_F']:.4f} not within {SHARE_TOL} of A: design failure")
        for a in ARMS + ("test",):
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, d[a].astype(np.int64))
        with open(SPL / f"r8_seed{s}.json", "x", encoding="utf-8") as f:
            json.dump({**d["meta"], "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(s: int) -> str | None:
    files = {a: SPL / f"{stem(s, a)}.npy" for a in ARMS + ("test",)}
    if not all(f.exists() for f in files.values()) or not (SPL / f"r8_seed{s}.json").exists():
        return f"seed {s}: split file missing"
    d = build(s)
    if not all(np.array_equal(np.load(f), d[a].astype(np.int64)) for a, f in files.items()):
        return f"seed {s}: splits differ from the deterministic rebuild"
    return None


# ---------------------------------------------------------------- jobs
def trainer_jobs(man: dict) -> list[str]:
    """Seed by seed: A, B, A2 alone, then the four switches at t."""
    out, t = [], man["switch_step"]
    for s in man["seeds"]:
        base = (f"{c1.interp(man)} {FB} --seed {s} --condition baseline --threads {man['threads']} --device {man['device']} "
                f"--test-file lab/confirm/r8_splits/{stem(s, 'test')}.npy --out-root lab/confirm/r8_raw")
        path = {a: f"lab/confirm/r8_splits/{stem(s, a)}.npy" for a in ARMS}
        for a in ARMS:
            out.append(f"{base} --steps {BUDGET} --stop-after-gen {BUDGET} --split-file {path[a]} --spectra-at 250,{BUDGET}")
        for x, y in SWITCHES:
            out.append(f"{base} --steps {t + BUDGET} --stop-after-gen {t + BUDGET} --split-file {path[x]} --switch-split-file {path[y]} "
                       f"--switch-step {t} --spectra-at {t},{t + BUDGET}")
    return out


def expected_run_id(cmd: list[str]) -> str:
    return n28.expected_run_id(cmd)


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r8", raw=RAW, bind=BIND, code_files=CODE_FILES + ("lab/tools/bound_block.py",), registered=REGISTERED,
              trainer_jobs=trainer_jobs, run_dir=run_dir, script="lab/tools/confirm_r8.py")


# ---------------------------------------------------------------- loading
def load_one(man: dict, s: int, first: str, second: str | None) -> dict | str:
    """Bounded time of one run through the shared loader + R8 binding (hash -> load -> hash)."""
    dev, t = man["device"], man["switch_step"]
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", dev, "--split-file", str(SPL / f"{stem(s, first)}.npy")]
    if second:
        cmd += ["--switch-split-file", str(SPL / f"{stem(s, second)}.npy"), "--switch-step", str(t)]
    d = run_dir(cmd)
    steps = BUDGET + (t if second else 0)
    tag = first + (f">{second}" if second else "")
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    split = SPL / f"{stem(s, first)}.npy"
    L = load_run(d, Expect(seed=s, device=dev, max_steps=steps, split_file=split, test_file=SPL / f"{stem(s, 'test')}.npy",
                           switch_file=SPL / f"{stem(s, second)}.npy" if second else None, config={"p": 113, "task": "add"},
                           snapshots_at=(steps,)))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(split):
        return f"{tag}: defekt after load: {why or 'split bytes differ'}"
    if L.res["steps_completed"] != steps:
        return f"{tag}: defekt: stopped at {L.res['steps_completed']} != {steps}"
    g = (L.res.get("events") or {}).get("generalization_step")
    if g is not None and not (isinstance(g, int) and 0 < g):
        return f"{tag}: defekt: generalization_step {g!r}"
    return {"b": float(min(g, CAP)) if g is not None else float(CAP), "event": g is not None and g <= CAP,
            "init": L.res.get("init_checksum_shared")}


# ---------------------------------------------------------------- analysis
def cost(b: dict, x: str, y: str) -> float:
    """C_XY = mean over both directions of log2 b(switch) - log2 b(destination only); b bounded at CAP."""
    return ((math.log2(b[f"{x}>{y}"]) - math.log2(b[y])) + (math.log2(b[f"{y}>{x}"]) - math.log2(b[x]))) / 2


def seed_row(man: dict, s: int) -> dict:
    R = {a: load_one(man, s, a, None) for a in ARMS}
    for x, y in SWITCHES:
        R[f"{x}>{y}"] = load_one(man, s, x, y)
    bad = [v for v in R.values() if isinstance(v, str)]
    if bad:
        return {"seed": s, "valid": False, "reason": "; ".join(bad[:4]), "n_bad": len(bad)}
    inits = {v["init"] for v in R.values()}
    if len(inits) != 1 or not all(inits):
        return {"seed": s, "valid": False, "reason": "init checksums differ within the seed", "n_bad": 1}
    b = {k: v["b"] for k, v in R.items()}
    cab, caa = cost(b, "A", "B"), cost(b, "A", "A2")
    return {"seed": s, "valid": True, "C_AB": cab, "C_AA2": caa, "D": cab - caa,
            "events": {k: v["event"] for k, v in R.items()}}


def verdict(rows: list[dict], n_planned: int, rng: np.random.Generator) -> dict:
    ok = [r for r in rows if r["valid"]]
    if len(ok) != n_planned:
        return {"n_valid": len(ok), "verdict": "nicht auswertbar"}
    D = np.array([r["D"] for r in ok])
    cab, caa = np.array([r["C_AB"] for r in ok]), np.array([r["C_AA2"] for r in ok])
    p = max(r6.p_flip(D, rng), r6.p_sign(D))
    s1d = caa - 0.5 * cab
    s1_ci = c1.boot_ci(s1d, rng)
    return {"n_valid": len(ok),
            "H1": {"mean": float(D.mean()), "sd": float(D.std(ddof=1)), "ci95": c1.boot_ci(D, rng), "p_flip_sign_max": p,
                   "n_positive": int((D > TIE).sum()), "n_negative": int((D < -TIE).sum()),
                   "verdict": "bestätigt" if p < ALPHA else "nicht bestätigt"},
            "S1": {"mean_C_AA2_minus_half_C_AB": float(s1d.mean()), "ci95": s1_ci,
                   "verdict": "gestützt" if s1_ci[1] < 0 else "nicht gestützt"},
            "descriptive": {"C_AB": {"mean": float(cab.mean()), "n_positive": int((cab > TIE).sum())},
                            "C_AA2": {"mean": float(caa.mean()), "n_positive": int((caa > TIE).sum())},
                            "events_by_arm": {k: sum(r["events"][k] for r in ok) for k in ok[0]["events"]}}}


def analyze(manifest: Path) -> None:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"R8 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [seed_row(man, s) for s in man["seeds"]]
    out = {"manifest_commit": man["commit"], "n_planned": len(man["seeds"]),
           "result": verdict(rows, len(man["seeds"]), np.random.default_rng(8)), "rows": rows}
    (LAB / "confirm" / "R8_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


# ---------------------------------------------------------------- selftest
def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    for bad in ({"seeds": REGISTERED["seeds"][:-1]}, {"switch_step": 25.0}, {"threads": True}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"type-sloppy or unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    assert len(tj) == N_UNITS * 7 and all("r8_raw" in j and "\\" not in j for j in tj)
    assert all(j.startswith("python lab/tools/confirm_r8.py --run M -- ") for j in BLOCK.jobs(man, "M"))
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert len(set(ids)) == len(ids), "run ids collide"
    assert ids[0] == "EXP-018_baseline_seed3100_thr1_r8_seed3100_A_devcuda", ids[0]
    assert ids[5] == "EXP-020_baseline_seed3100_thr1_r8_seed3100_A_to_r8_seed3100_A2_at25_devcuda", ids[5]
    assert "--steps 2025 --stop-after-gen 2025" in tj[3] and "--steps 2000 --stop-after-gen 2000" in tj[0]
    BLOCK.check_job(man, shlex.split(tj[0]))
    try:
        BLOCK.check_job(man, shlex.split(tj[0]) + ["--force"])
        raise AssertionError("foreign command accepted")
    except SystemExit:
        pass
    # splits: deterministic, disjoint, matched share (pure numpy; two seeds outside the block)
    for s in (3190, 3191):
        d1, d2 = build(s), build(s)
        assert all(np.array_equal(d1[k], d2[k]) for k in ARMS + ("test",)), "build not deterministic"
        assert abs(d1["meta"]["share_A2_F"] - d1["meta"]["share_A_F"]) <= SHARE_TOL, d1["meta"]
        assert not np.intersect1d(d1["A2"], d1["A"]).size and not np.intersect1d(d1["A2"], d1["test"]).size
    # cost and verdict arithmetic
    b = {"A": 500.0, "B": 400.0, "A2": 500.0, "A>B": 800.0, "B>A": 1000.0, "A>A2": 500.0, "A2>A": 500.0}
    assert abs(cost(b, "A", "B") - 1.0) < 1e-12 and cost(b, "A", "A2") == 0.0
    rng = np.random.default_rng(0)
    ev = {k: True for k in ("A", "B", "A2", "A>B", "B>A", "A>A2", "A2>A")}
    rows = [{"seed": i, "valid": True, "C_AB": 0.6, "C_AA2": -0.2 + 0.01 * i, "D": 0.8 - 0.01 * i, "events": ev} for i in range(N_UNITS)]
    v = verdict(rows, N_UNITS, rng)
    assert v["H1"]["verdict"] == "bestätigt" and v["S1"]["verdict"] == "gestützt", v
    assert verdict(rows[:-1], N_UNITS, rng)["verdict"] == "nicht auswertbar"
    flat = [{**r, "D": (0.3 if i % 2 else -0.3)} for i, r in enumerate(rows)]
    assert verdict(flat, N_UNITS, rng)["H1"]["verdict"] == "nicht bestätigt"
    worse = [{**r, "C_AA2": 0.5} for r in rows]
    assert verdict(worse, N_UNITS, rng)["S1"]["verdict"] == "nicht gestützt"
    selftest_binding(BLOCK, tj[4], tj[1], tj[5])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    print("[confirm_r8] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
