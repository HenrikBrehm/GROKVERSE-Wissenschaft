"""R6 confirmation (FINDINGS programme B, functional signature of the lock-in): does a data switch in the middle of the lock-in
window delay grokking, and more than a switch after it? Session 32, UNTESTED (selftest only inside the run window).

Registration: lab/confirm/R6_REGISTRATION_DRAFT.md (hypotheses came from post hoc reads of N28/P3/EXP-020/EXP-041 in session 32).
Construction exactly as N28 (EXP-053 overlap_split, omega = 0, matched steering strength, common test set per seed); fresh seeds.
Per seed s: pure A, pure B (2000 steps) and switches A->B, B->A at every t in SWITCH_STEPS (t + 2000 steps, AdamW state kept).
Time: b = min(first test >= 0.95 [trainer event], CAP) counted from step 0, CAP = 2000 for every arm (common horizon, so a pair
censored on both sides gives exactly 0). Cost C(t) per seed = mean over both directions of log2 b(switch@t) - log2 b(destination only).
Primary family (Holm over 2 at 0.05; per hypothesis p = max(p_flip, p_sign)):
  H1  C(25) > 0            (a switch at 25 steps delays grokking against training on the destination split alone)
  H2  C(25) - C(50) > 0    (the delay is larger at 25 than at 50 steps)
Secondary (outside the family, "gestützt" / "nicht gestützt"): S1 the t in SWITCH_STEPS with the largest mean C lies within 10 steps
of t_pi, the first t at which the median persistence pi(t) (N28 definition, final W_E) reaches 0.5 (linear interpolation).
Descriptive: mean / median C(t) for every t, share of arms with an event, pi(t).

  python lab/tools/confirm_r6.py --hash-code
  python lab/tools/confirm_r6.py --splits lab/confirm/R6_manifest.json        # after freezing; never overwrites
  python lab/tools/confirm_r6.py --jobs lab/confirm/R6_manifest.json > lab/confirm/R6_jobs.txt   # plain, NOT through guarded_run
  python lab/tools/confirm_r6.py --run lab/confirm/R6_manifest.json -- <trainer command>
  python lab/tools/confirm_r6.py --analyze lab/confirm/R6_manifest.json       # under guarded_run.py
  python lab/tools/confirm_r6.py --selftest                                   # under guarded_run.py
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
import confirm_n28 as n28  # noqa: E402  (read-only reuse: logratio, pi_pair, a43 group power)
import confirm_p1 as c1  # noqa: E402  (read-only reuse: interp, bootstrap, holm)
from bound_block import Block, selftest_binding, sha  # noqa: E402
import overlap_split as ov  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "r6_raw"
BIND = LAB / "confirm" / "r6_bindings"
SPL = LAB / "confirm" / "r6_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"
BUDGET, CAP, ALPHA, OMEGA, MIN_SEP = 2000, 2000, 0.05, 0.0, 2.0
N_FLIP, TIE = 100_000, 1e-9
REGISTERED = {"seeds": list(range(2800, 2830)), "switch_steps": [10, 20, 25, 30, 40, 50, 75], "device": "cuda", "threads": 1}
CODE_FILES = ("lab/tools/confirm_r6.py", "lab/tools/confirm_n28.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py",
              "lab/tools/result_loader.py", "lab/tools/paket_a_device.py", "lab/experiments/EXP-001-freq-ban/freq_ban.py",
              "lab/experiments/EXP-053-p3-overlap-design/overlap_split.py", "lab/experiments/EXP-053-p3-overlap-design/calibration.json",
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py")


# ---------------------------------------------------------------- splits and jobs
def stem(s: int, arm: str) -> str:
    return f"r6_seed{s}_w0_{arm}"


def write_splits(man: dict) -> None:
    eps = json.loads(CAL.read_text(encoding="utf-8"))["levels"][str(OMEGA)]["eps"]
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, a)}.npy" for s in man["seeds"] for a in "AB"] + [f"r6_seed{s}_test.npy" for s in man["seeds"]]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("R6 splits exist already: never overwrite")
    for s in man["seeds"]:
        F, G = ov.targets(s)
        d = ov.build(s, OMEGA, eps)
        assert len(d["A"]) == len(d["B"]) == ov.N_TRAIN and not np.intersect1d(d["A"], d["B"]).size
        assert not np.intersect1d(d["test"], np.union1d(d["A"], d["B"])).size
        for a in "AB":
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, d[a].astype(np.int64))
        with open(SPL / f"r6_seed{s}_test.npy", "xb") as f:
            np.save(f, d["test"].astype(np.int64))
        with open(SPL / f"r6_seed{s}_w0.json", "x", encoding="utf-8") as f:
            json.dump({"seed": s, "omega": OMEGA, "targets": {"A": F, "B": G}, "share_A_F": ov.share(d["A"], F),
                       "share_B_G": ov.share(d["B"], G), "manifest_commit": man["commit"]}, f, indent=1)


def trainer_jobs(man: dict) -> list[str]:
    """Seed by seed (a partly finished night leaves whole seeds, not whole arms)."""
    out = []
    for s in man["seeds"]:
        base = (f"{c1.interp(man)} {FB} --seed {s} --condition baseline --threads {man['threads']} --device {man['device']} "
                f"--test-file lab/confirm/r6_splits/r6_seed{s}_test.npy --out-root lab/confirm/r6_raw")
        a, b = (f"lab/confirm/r6_splits/{stem(s, x)}.npy" for x in "AB")
        for first in (a, b):
            out.append(f"{base} --steps {BUDGET} --stop-after-gen {BUDGET} --split-file {first} --spectra-at 50,250,{BUDGET}")
        for t in man["switch_steps"]:
            for first, second in ((a, b), (b, a)):
                out.append(f"{base} --steps {t + BUDGET} --stop-after-gen {t + BUDGET} --split-file {first} --switch-split-file {second} --switch-step {t} "
                           f"--spectra-at {t},{t + 250},{t + BUDGET}")
    return out


def expected_run_id(cmd: list[str]) -> str:
    return n28.expected_run_id(cmd)


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r6", raw=RAW, bind=BIND, code_files=CODE_FILES + ("lab/tools/bound_block.py",), registered=REGISTERED,
              trainer_jobs=trainer_jobs, run_dir=run_dir, script="lab/tools/confirm_r6.py")


# ---------------------------------------------------------------- loading
def load_one(man: dict, s: int, first: str, second: str | None, t: int | None) -> dict | str:
    """Bounded time and final W_E of one run through the shared loader + R6 binding (hash -> load -> hash)."""
    dev = man["device"]
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", dev, "--split-file", str(SPL / f"{stem(s, first)}.npy")]
    if second:
        cmd += ["--switch-split-file", str(SPL / f"{stem(s, second)}.npy"), "--switch-step", str(t)]
    d = run_dir(cmd)
    steps = BUDGET + (t if second else 0)
    tag = f"{first}{second or ''}{'' if not second else '@' + str(t)}"
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    split = SPL / f"{stem(s, first)}.npy"
    L = load_run(d, Expect(seed=s, device=dev, max_steps=steps, split_file=split, test_file=SPL / f"r6_seed{s}_test.npy",
                           switch_file=SPL / f"{stem(s, second)}.npy" if second else None, config={"p": 113, "task": "add"},
                           snapshots_at=(steps,)))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(split):
        return f"{tag}: defekt after load: {why or 'split bytes differ'}"
    if L.res["steps_completed"] != steps:                       # Codex s32: full end step (pi snapshot), not only the cap
        return f"{tag}: defekt: stopped at {L.res['steps_completed']} != {steps}"
    g = (L.res.get("events") or {}).get("generalization_step")
    if g is not None and not (isinstance(g, int) and 0 < g):
        return f"{tag}: defekt: generalization_step {g!r}"
    return {"b": float(min(g, CAP)) if g is not None else float(CAP), "event": g is not None and g <= CAP,
            "W": np.asarray(L.snapshot(steps), dtype=np.float64)}


def split_mismatch(man: dict, s: int) -> str | None:
    eps = json.loads(CAL.read_text(encoding="utf-8"))["levels"][str(OMEGA)]["eps"]
    F, G = ov.targets(s)
    d = ov.build(s, OMEGA, eps)
    meta_f = SPL / f"r6_seed{s}_w0.json"
    if not meta_f.exists():
        return f"seed {s}: split metadata missing"
    meta = json.loads(meta_f.read_text(encoding="utf-8"))
    files = {"A": SPL / f"{stem(s, 'A')}.npy", "B": SPL / f"{stem(s, 'B')}.npy", "test": SPL / f"r6_seed{s}_test.npy"}
    if not all(f.exists() for f in files.values()):
        return f"seed {s}: split file missing"
    if not all(np.array_equal(np.load(f), d[k].astype(np.int64)) for k, f in files.items()) or meta.get("targets") != {"A": F, "B": G}:
        return f"seed {s}: splits differ from the deterministic rebuild"
    return None


# ---------------------------------------------------------------- analysis
def cost(b: dict, t: int) -> float:
    """C(t) = mean over directions of log2 b(switch) - log2 b(destination only); b bounded at CAP."""
    return ((math.log2(b[("AB", t)]) - math.log2(b["B"])) + (math.log2(b[("BA", t)]) - math.log2(b["A"]))) / 2


def seed_row(man: dict, s: int) -> dict:
    meta = json.loads((SPL / f"r6_seed{s}_w0.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    R = {"A": load_one(man, s, "A", None, None), "B": load_one(man, s, "B", None, None)}
    for t in man["switch_steps"]:
        for first, second in (("A", "B"), ("B", "A")):
            R[(first + second, t)] = load_one(man, s, first, second, t)
    bad = [v for v in R.values() if isinstance(v, str)]
    if bad:
        return {"seed": s, "valid": False, "reason": "; ".join(bad[:4]), "n_bad": len(bad)}
    b = {k: v["b"] for k, v in R.items()}
    row = {"seed": s, "valid": True, "C": {str(t): cost(b, t) for t in man["switch_steps"]},
           "events": {("%s@%s" % k if isinstance(k, tuple) else k): v["event"] for k, v in R.items()}}
    gp = lambda W: n28.a43().group_power(W, "add", 113)[0]   # noqa: E731
    L = {"A": n28.logratio(gp(R["A"]["W"]), F, G), "B": n28.logratio(gp(R["B"]["W"]), F, G)}
    if all(np.isfinite(v) for v in L.values()) and L["A"] - L["B"] >= MIN_SEP:      # pi only where A and B separate (N28 rule)
        row["pi"] = {str(t): n28.pi_pair(L, n28.logratio(gp(R[("AB", t)]["W"]), F, G), n28.logratio(gp(R[("BA", t)]["W"]), F, G))
                     for t in man["switch_steps"]}
    return row


def p_sign(d: np.ndarray) -> float:
    nz = d[np.abs(d) > TIE]
    k, n = int((nz > 0).sum()), len(nz)
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0


def _half_sums(x: np.ndarray) -> np.ndarray:
    """All 2^len(x) signed sums of x (len(x) <= 20)."""
    m = len(x)
    signs = 1.0 - 2.0 * ((np.arange(2 ** m)[:, None] >> np.arange(m)[None, :]) & 1)
    return signs @ x


def p_flip(d: np.ndarray, rng: np.random.Generator) -> float:
    """One-sided sign-flip test of the sum, EXACT for n <= 40 by meet in the middle (Codex s32 recheck: n = 30 needs it):
    count sign vectors with left-half sum + right-half sum >= observed sum. Monte Carlo only above 40."""
    n = len(d)
    if n <= 40:
        left, right = _half_sums(d[: n // 2]), np.sort(_half_sums(d[n // 2:]))
        need = d.sum() - 1e-12 - left                                        # right sum must be >= need
        hits = int((len(right) - np.searchsorted(right, need, side="left")).sum())
        return hits / 2 ** n
    s = rng.choice(np.array([-1.0, 1.0]), size=(N_FLIP, n))
    return float(((s * d).mean(axis=1) >= d.mean() - 1e-12).sum() + 1) / (N_FLIP + 1)


def family(X: dict[str, np.ndarray], n_planned: int, rng: np.random.Generator) -> dict:
    if any(len(v) != n_planned for v in X.values()):
        return {"verdict": "nicht auswertbar"}
    p = {k: max(p_flip(v, rng), p_sign(v)) for k, v in X.items()}
    ph = c1.holm(p)
    return {k: {"mean": float(v.mean()), "factor_2^mean": float(2 ** v.mean()), "sd": float(v.std(ddof=1)), "p_flip_sign_max": p[k],
                "p_holm": ph[k], "ci95": c1.boot_ci(v, rng), "n_positive": int((v > TIE).sum()), "n_negative": int((v < -TIE).sum()),
                "verdict": "bestätigt" if ph[k] < ALPHA else "nicht bestätigt"} for k, v in X.items()}


def t_at_half(ts: list[int], med_pi: list[float]) -> float | None:
    """First t at which the median pi reaches 0.5 (linear interpolation between grid points); None if never."""
    for i, (t, v) in enumerate(zip(ts, med_pi)):
        if v >= 0.5:
            if i == 0:
                return float(t)
            t0, v0 = ts[i - 1], med_pi[i - 1]
            return float(t0 + (0.5 - v0) * (t - t0) / (v - v0))
    return None


MIN_PI_SEEDS = 10


def secondary(rows: list[dict], ts: list[int]) -> dict:
    """S1 edge rules (Codex s32, fixed before any run): all grid points tied for the largest mean C (|diff| <= 1e-9) must lie within
    10 steps of t_pi; t_pi left-censored (median pi >= 0.5 already at the first grid point) or never reached -> 'nicht auswertbar';
    fewer than MIN_PI_SEEDS seeds with a defined pi -> 'nicht auswertbar'."""
    mc = {t: float(np.mean([r["C"][str(t)] for r in rows])) for t in ts}
    top = max(mc.values())
    t_star = [t for t in ts if mc[t] >= top - TIE]
    with_pi = [r for r in rows if "pi" in r]
    med_pi = [float(np.median([r["pi"][str(t)] for r in with_pi])) for t in ts] if with_pi else []
    t_pi = t_at_half(ts, med_pi) if with_pi else None
    left_cens = bool(med_pi) and med_pi[0] >= 0.5
    if len(with_pi) < MIN_PI_SEEDS or t_pi is None or left_cens:
        s1 = "nicht auswertbar"
    else:
        s1 = "gestützt" if all(abs(t - t_pi) <= 10 for t in t_star) else "nicht gestützt"
    return {"mean_C": {str(t): mc[t] for t in ts}, "median_C": {str(t): float(np.median([r["C"][str(t)] for r in rows])) for t in ts},
            "t_star": t_star, "n_with_pi": len(with_pi), "median_pi": dict(zip(map(str, ts), med_pi)), "t_pi": t_pi,
            "t_pi_left_censored": left_cens, "S1": s1, "S2": s2_rule(ts, mc, med_pi, len(with_pi))}


def s2_rule(ts: list[int], mc: dict[int, float], med_pi: list[float], n_pi: int) -> str:
    """S2 (added before freezing, session 32, from the post hoc block-level picture): the delay vanishes once the choice has
    persisted. 'gestützt' if mean C(t) <= 0 for every grid t with median pi(t) >= 0.9 AND mean C(t) > 0 for every grid t with
    0.2 <= median pi(t) <= 0.8 (pi < 0.2 excluded a priori: C must go to 0 as t -> 0); needs >= 1 grid point in each class and
    >= MIN_PI_SEEDS seeds with pi, else 'nicht auswertbar'."""
    if n_pi < MIN_PI_SEEDS:
        return "nicht auswertbar"
    hi = [t for t, v in zip(ts, med_pi) if v >= 0.9]
    mid = [t for t, v in zip(ts, med_pi) if 0.2 <= v <= 0.8]
    if not hi or not mid:
        return "nicht auswertbar"
    return "gestützt" if all(mc[t] <= 0 for t in hi) and all(mc[t] > 0 for t in mid) else "nicht gestützt"


def analyze(manifest: Path) -> None:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(man, s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"R6 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [seed_row(man, s) for s in man["seeds"]]
    ok = [r for r in rows if r["valid"]]
    X = {"H1": np.array([r["C"]["25"] for r in ok]), "H2": np.array([r["C"]["25"] - r["C"]["50"] for r in ok])}
    out = {"manifest_commit": man["commit"], "n_valid": len(ok), "n_planned": len(man["seeds"]),
           "hypotheses": family(X, len(man["seeds"]), np.random.default_rng(6))}
    if len(ok) == len(man["seeds"]):
        out["secondary"] = secondary(ok, man["switch_steps"])
    out["rows"] = rows
    (LAB / "confirm" / "R6_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


# ---------------------------------------------------------------- selftest
def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    for bad in ({"seeds": list(range(2800, 2829))}, {"switch_steps": [10, 20, 25.0, 30, 40, 50, 75]}, {"threads": True}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"type-sloppy or unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    assert len(tj) == 30 * (2 + 2 * 7) and all("r6_raw" in j and "\\" not in j for j in tj)
    assert all(j.startswith("python lab/tools/confirm_r6.py --run M -- ") for j in BLOCK.jobs(man, "M"))
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert ids[0] == "EXP-018_baseline_seed2800_thr1_r6_seed2800_w0_A_devcuda", ids[0]
    assert ids[2] == "EXP-020_baseline_seed2800_thr1_r6_seed2800_w0_A_to_r6_seed2800_w0_B_at10_devcuda", ids[2]
    assert ids[7] == "EXP-020_baseline_seed2800_thr1_r6_seed2800_w0_B_to_r6_seed2800_w0_A_at25_devcuda", ids[7]
    assert len(set(ids)) == len(ids)
    assert "--steps 2025 --stop-after-gen 2025" in tj[6] and "--spectra-at 25,275,2025" in tj[6] and "--reset-optim" not in tj[6]
    assert "--steps 2000 --stop-after-gen 2000" in tj[0]
    BLOCK.check_job(man, shlex.split(tj[0]))
    try:
        BLOCK.check_job(man, shlex.split(tj[0]) + ["--force"])
        raise AssertionError("foreign command accepted")
    except SystemExit:
        pass
    # cost: both censored -> 0; switch twice as slow in both directions -> 1
    b = {"A": 2000.0, "B": 2000.0, ("AB", 25): 2000.0, ("BA", 25): 2000.0}
    assert cost(b, 25) == 0.0
    b = {"A": 500.0, "B": 400.0, ("AB", 25): 800.0, ("BA", 25): 1000.0}
    assert abs(cost(b, 25) - 1.0) < 1e-12
    rng = np.random.default_rng(0)
    assert family({"H1": np.full(19, 0.5), "H2": np.full(20, 0.5)}, 20, rng)["verdict"] == "nicht auswertbar"
    pos = np.linspace(0.1, 0.9, 20)
    v = family({"H1": pos, "H2": np.linspace(-0.4, 0.4, 20)}, 20, rng)
    assert v["H1"]["verdict"] == "bestätigt" and v["H2"]["verdict"] == "nicht bestätigt", v
    assert abs(p_sign(pos) - 0.5 ** 20) < 1e-15 and p_sign(np.zeros(5)) == 1.0
    assert v["H1"]["p_flip_sign_max"] >= p_sign(pos)
    assert t_at_half([10, 20, 30], [0.1, 0.3, 0.7]) == 25.0 and t_at_half([10, 20], [0.1, 0.2]) is None
    assert t_at_half([10, 20], [0.6, 0.9]) == 10.0
    rows = [{"C": {"10": 0.1, "25": 0.6, "50": -0.3}, "pi": {"10": 0.1, "25": 0.4, "50": 0.9}} for _ in range(10)]
    sec = secondary(rows, [10, 25, 50])
    assert sec["t_star"] == [25] and abs(sec["t_pi"] - 30.0) < 1e-9 and sec["S1"] == "gestützt", sec
    assert sec["S2"] == "gestützt", sec                    # pi 0.1 (excluded), 0.4 -> C 0.6 > 0, 0.9 -> C -0.3 <= 0
    assert s2_rule([10, 25, 50], {10: 0.1, 25: 0.6, 50: 0.1}, [0.1, 0.4, 0.9], 10) == "nicht gestützt"
    assert s2_rule([10, 25, 50], {10: 0.1, 25: 0.6, 50: -0.1}, [0.1, 0.4, 0.85], 10) == "nicht auswertbar"   # no pi >= 0.9
    assert s2_rule([10, 25, 50], {10: 0.1, 25: 0.6, 50: -0.1}, [0.1, 0.4, 0.95], 9) == "nicht auswertbar"
    assert secondary(rows[:9], [10, 25, 50])["S1"] == "nicht auswertbar"                       # too few pi seeds
    left = [{"C": r["C"], "pi": {"10": 0.6, "25": 0.8, "50": 0.9}} for r in rows]
    assert secondary(left, [10, 25, 50])["S1"] == "nicht auswertbar"                           # left-censored t_pi
    tied = [{"C": {"10": 0.6, "25": 0.6, "50": -0.3}, "pi": r["pi"]} for r in rows]
    s_t = secondary(tied, [10, 25, 50])
    assert s_t["t_star"] == [10, 25] and s_t["S1"] == "nicht gestützt", s_t                    # 10 is 20 steps from t_pi = 30
    d = np.array([0.5, -0.2, 0.3])                                                             # exact flip p by hand: sums >= 0.6
    assert abs(p_flip(d, rng) - 2 / 8) < 1e-12, p_flip(d, rng)
    for m in (1, 7, 10):                                                                       # meet in the middle == brute force
        x = np.random.default_rng(m).normal(0.2, 1.0, m)
        brute = float((_half_sums(x) >= x.sum() - 1e-12).mean())
        assert abs(p_flip(x, rng) - brute) < 1e-12, (m, p_flip(x, rng), brute)
    assert abs(p_flip(np.linspace(0.1, 0.9, 30), rng) - 0.5 ** 30) < 1e-18                     # all positive: only the identity
    selftest_binding(BLOCK, tj[4], tj[1], tj[5])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    print("[confirm_r6] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
