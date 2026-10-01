"""R14 confirmation (session 67): does split steering (K2) hold at a larger modulus with sparse data, measured AFTER generalization?
Addition mod 307 with 10 % training data (9425 pairs), fresh seeds and splits. Registration: lab/confirm/R14_REGISTRATION.md.
Pilot: EXP-137 (3 seeds; 6/6 runs generalized at 6125-11500 steps; Delta_pow after generalization 8.2-10.9, placebo q99 3.8-5.7).

Unit = seed with an F/G pair (same init for F and G, as P1). Splits: P1 construction (confirm_splits) with experiment id 14 and the
train fraction 0.1 (confirm_splits.TRAIN_FRAC is overridden only inside build(), and restored). Trainer: freq_ban.py (unchanged),
--p 307 --task add --train-frac 0.1, at most 30 000 steps, stop 2000 steps after generalization, W_E snapshots every 1000 steps.
Per arm: generalization step g = transitions.primary.generalization.first_crossing_step; read the first snapshot >= g + 1000.
Per seed: Delta_pow at these two snapshots (P1 formula on the W_E group power, k = 1..153) and the 99 % quantile q99 of |placebo
Delta_pow| (2000 random disjoint 5+5 frequency sets outside F u G, same two snapshots, stream SeedSequence([14, seed])).
Primary statistic per seed: D = Delta_pow - q99; a seed with an arm that never generalizes (or no snapshot >= g + 1000) enters as
D = -1 (counts against the claim; reported). Test: exact one-sided sign-flip test of mean D > 0 (n = 12, 2^12 patterns), single
hypothesis (no Holm), 95 % bootstrap CI of mean D. "bestaetigt" if p < 0.05 AND CI lower bound > 0 AND D > 0 in >= 10 of 12 seeds
(added in the selftest before freezing: otherwise half the seeds failing could still pass on the mean); technical failure of any run
(missing, unbound, config, non-finite) -> "nicht auswertbar".
Descriptive: Delta_pow, q99, generalization steps, Delta_pow at 2000 and at the last snapshot before generalization, top-5 overlap.

  python lab/tools/confirm_r14.py --selftest
  python lab/tools/confirm_r14.py --splits|--jobs|--analyze lab/confirm/R14_manifest.json
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
import confirm_p1 as c1  # noqa: E402  (read-only reuse: sign_flip_p, boot_ci, interp)
import confirm_splits as cs  # noqa: E402
from bound_block import Block, selftest_binding, sha  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "r14_raw"
BIND = LAB / "confirm" / "r14_bindings"
SPL = LAB / "confirm" / "r14_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
P, ALPHA, EPS, EXPERIMENT, FRAC = 307, 0.05, 2.0, 14, 0.1
N_SEEDS, SEEDS = 12, list(range(4430, 4442))
MIN_POSITIVE = 10                 # >= 10/12 seeds with D > 0 (one-sided binomial p = 0.019): a mean carried by half the seeds is not enough
STEPS, STOP_AFTER_GEN, POST, N_PLACEBO = 30_000, 2000, 1000, 2000
SNAPS = [50, 250, 500, *range(1000, STEPS + 1, 1000)]
REGISTERED = {"experiment": EXPERIMENT, "p": P, "eps": EPS, "train_frac": FRAC, "device": "cuda", "threads": 1, "steps": STEPS,
              "stop_after_gen": STOP_AFTER_GEN}
CODE_FILES = ("lab/tools/confirm_r14.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py",
              "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py", FB,
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py")


# ---------------------------------------------------------------- splits
def build(s: int, arm: str) -> tuple[np.ndarray, dict[str, list[int]]]:
    old = cs.TRAIN_FRAC
    cs.TRAIN_FRAC = FRAC
    try:
        idx, _ = cs.build(EXPERIMENT, "add", P, s, arm, EPS)
    finally:
        cs.TRAIN_FRAC = old
    return idx, cs.target_sets(EXPERIMENT, "add", P, s)


def check_design(man: dict) -> None:
    s = man.get("seeds")
    if not isinstance(s, list) or s != SEEDS or not all(type(x) is int for x in s):
        raise SystemExit(f"R14 manifest: seeds must be exactly {SEEDS[0]}-{SEEDS[-1]}")


def stem(s: int, arm: str) -> str:
    return f"r14_add{P}_seed{s}_{arm}"


def write_splits(man: dict) -> None:
    check_design(man)
    SPL.mkdir(parents=True, exist_ok=True)
    if any((SPL / f"{stem(s, a)}{e}").exists() for s in SEEDS for a in "FG" for e in (".npy", ".json")):
        raise SystemExit("R14 splits exist already: never overwrite")
    for s in SEEDS:
        for a in "FG":
            idx, T = build(s, a)
            if len(idx) != int(round(FRAC * P * P)) or len(np.unique(idx)) != len(idx):
                raise SystemExit(f"R14 split {stem(s, a)}: bad size")
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, idx.astype(np.int64))
            with open(SPL / f"{stem(s, a)}.json", "x", encoding="utf-8") as f:
                json.dump({"seed": s, "arm": a, "targets": T[a], "other_targets": T["G" if a == "F" else "F"], "eps": EPS,
                           "train_frac": FRAC, "n": int(len(idx)), "manifest_commit": man["commit"]}, f, indent=1)


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
def job(man: dict, s: int, a: str) -> str:
    return (f"{c1.interp(man)} {FB} --seed {s} --condition baseline --steps {man['steps']} --stop-after-gen {man['stop_after_gen']} "
            f"--threads {man['threads']} --device {man['device']} --p {P} --task add --train-frac {man['train_frac']!r} "
            f"--split-file lab/confirm/r14_splits/{stem(s, a)}.npy --spectra-at {','.join(str(x) for x in SNAPS)} "
            f"--out-root lab/confirm/r14_raw")


def trainer_jobs(man: dict) -> list[str]:
    return [job(man, s, a) for s in man["seeds"] for a in "FG"]


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban.py rule as observed in EXP-137: EXP-043_baseline_seed<s>_thr<t>_<stem>_add<p>_tf<frac!r>_dev<dev>."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    sp, s, dev = Path(g("--split-file")).stem, g("--seed"), (g("--device") or "cpu").replace(":", "")
    if not sp.startswith("r14_") or g("--p") != str(P) or g("--train-frac") is None:
        raise SystemExit(f"R14: command does not match the R14 trainer call: {' '.join(cmd)[:120]}")
    return f"EXP-043_baseline_seed{s}_thr{g('--threads')}_{sp}_add{P}_tf{float(g('--train-frac'))!r}" + ("" if dev == "cpu" else f"_dev{dev}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r14", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_r14.py")


# ---------------------------------------------------------------- analysis
def group_power(W: np.ndarray) -> np.ndarray:
    sq = (np.abs(np.fft.fft(W[:P], axis=0)) ** 2).sum(axis=1)
    return 2.0 * sq[1:(P - 1) // 2 + 1] / P


def delta_pow(a: np.ndarray, b: np.ndarray, F: list[int], G: list[int]) -> float | None:
    S = lambda pw, K: float(pw[[k - 1 for k in K]].sum())   # noqa: E731
    v = [S(a, F), S(a, G), S(b, G), S(b, F)]
    if not all(np.isfinite(x) and x > 0 for x in v):
        return None
    return float(np.log(v[0] / v[1]) + np.log(v[2] / v[3]))


def placebo_q99(a: np.ndarray, b: np.ndarray, F: list[int], G: list[int], seed: int) -> float:
    rng = np.random.default_rng(np.random.SeedSequence([EXPERIMENT, seed]))
    pool = np.array([k for k in range(1, len(a) + 1) if k not in set(F) | set(G)])
    v = [delta_pow(a, b, list(c[:5]), list(c[5:])) for c in (rng.choice(pool, 10, replace=False) for _ in range(N_PLACEBO))]
    return float(np.quantile(np.abs([x for x in v if x is not None]), 0.99))


def top5(pw: np.ndarray) -> set[int]:
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:5]}


def run_info(man: dict, s: int, arm: str) -> dict | str:
    split = SPL / f"{stem(s, arm)}.npy"
    d = run_dir(shlex.split(job(man, s, arm)))
    if not d.exists():
        return "fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"defekt: {why}"
    e = dict(seed=s, device=man["device"], max_steps=man["steps"], min_steps_completed=1, split_file=split,
             config={"p": P, "task": "add", "arch": "transformer", "train_frac": FRAC})
    L = load_run(d, Expect(**e))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    if L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(split):
        return "defekt: split bytes differ"
    steps = [int(x) for x in np.load(io.BytesIO(BLOCK.bound_bytes(man, d / "we_snapshot_steps.npy")))]
    gen = ((L.res.get("transitions") or {}).get("primary") or {}).get("generalization", {}).get("first_crossing_step")
    post = [t for t in steps if gen is not None and t >= gen + POST]
    pre = [t for t in steps if gen is not None and t < gen]
    want = tuple(sorted({t for t in (post[:1] + pre[-1:] + [2000]) if t in steps}))
    L2 = load_run(d, Expect(**e, snapshots_at=want))
    if L2.status != "ok":
        return f"{L2.status}: {L2.reason}"
    if (why := BLOCK.unbound(man, d)):
        return f"defekt after load: {why}"
    gp = {t: group_power(L2.snapshot(t)) for t in want}
    return {"gen": gen, "post_step": post[0] if post else None, "pre_step": pre[-1] if pre else None, "power": gp,
            "test_acc": (L.res.get("final_acc") or {}).get("test")}


def seed_row(man: dict, s: int) -> dict:
    T = {a: json.loads((SPL / f"{stem(s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
    R = {a: run_info(man, s, a) for a in "FG"}
    bad = [f"{a}: {v}" for a, v in R.items() if isinstance(v, str)]
    if bad:
        return {"seed": s, "technical": True, "reason": "; ".join(bad)}
    F, G = R["F"], R["G"]
    row = {"seed": s, "technical": False, "gen": [F["gen"], G["gen"]], "test_acc": [F["test_acc"], G["test_acc"]],
           "Delta_pow_2000": delta_pow(F["power"][2000], G["power"][2000], T["F"], T["G"]) if 2000 in F["power"] and 2000 in G["power"] else None}
    if F["post_step"] is None or G["post_step"] is None:
        return {**row, "evaluable": False, "D": -1.0}
    a, b = F["power"][F["post_step"]], G["power"][G["post_step"]]
    d = delta_pow(a, b, T["F"], T["G"])
    if d is None:
        return {"seed": s, "technical": True, "reason": "Delta_pow undefined"}
    q = placebo_q99(a, b, T["F"], T["G"], s)
    pre = (delta_pow(F["power"][F["pre_step"]], G["power"][G["pre_step"]], T["F"], T["G"])
           if F["pre_step"] is not None and G["pre_step"] is not None else None)
    return {**row, "evaluable": True, "post_step": [F["post_step"], G["post_step"]], "Delta_pow": d, "q99": q, "D": d - q,
            "Delta_pow_pre": pre, "top5_own": [len(top5(a) & set(T["F"])), len(top5(b) & set(T["G"]))]}


def verdict(rows: list[dict], rng: np.random.Generator) -> dict:
    if len(rows) != N_SEEDS or any(r.get("technical") for r in rows):
        return {"verdict": "nicht auswertbar", "n": len(rows), "n_technical": sum(bool(r.get("technical")) for r in rows)}
    D = np.array([r["D"] for r in rows])
    p = c1.sign_flip_p(D, rng)
    ci = c1.boot_ci(D, rng)
    ev = [r for r in rows if r["evaluable"]]
    return {"n": len(D), "n_evaluable": len(ev), "mean_D": float(D.mean()), "ci95_D": ci, "p": p, "n_positive": int((D > 0).sum()),
            "mean_Delta_pow": float(np.mean([r["Delta_pow"] for r in ev])) if ev else None,
            "mean_q99": float(np.mean([r["q99"] for r in ev])) if ev else None,
            "verdict": "bestätigt" if p < ALPHA and ci[0] > 0 and int((D > 0).sum()) >= MIN_POSITIVE else "nicht bestätigt"}


def analyze(manifest: Path) -> None:
    out_f = LAB / "confirm" / "R14_summary.json"
    if out_f.exists():
        out_f.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    check_design(man)
    bad = [m for m in (split_mismatch(s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"R14 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [seed_row(man, s) for s in man["seeds"]]
    out = {"manifest_commit": man["commit"], "result": verdict(rows, np.random.default_rng(14)), "rows": rows}
    out_f.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["result"], indent=1, ensure_ascii=False))


def selftest() -> None:
    for bad in ({"seeds": SEEDS[:11]}, {"seeds": list(range(4400, 4412))}, {"seeds": [float(x) for x in SEEDS]}):
        try:
            check_design(bad)
            raise AssertionError("bad seeds accepted")
        except SystemExit:
            pass
    man = {**REGISTERED, "python": "PY", "seeds": SEEDS}
    BLOCK.check_registered(man)
    check_design(man)
    tj = trainer_jobs(man)
    assert len(tj) == 24 and len(set(tj)) == 24 and all("r14_raw" in j and "\\" not in j for j in tj)
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert len(set(ids)) == 24
    assert ids[0] == "EXP-043_baseline_seed4430_thr1_r14_add307_seed4430_F_add307_tf0.1_devcuda", ids[0]
    assert "--train-frac 0.1 " in tj[0] and "--p 307 --task add" in tj[0] and "--stop-after-gen 2000" in tj[0]
    assert ",29000,30000 " in tj[0] and "--steps 30000" in tj[0]
    # splits: fraction 0.1 inside build only, restored afterwards; fresh streams (experiment 14)
    idx, T = build(4430, "F")
    assert cs.TRAIN_FRAC == 0.3 and len(idx) == 9425 and len(np.unique(idx)) == 9425
    assert not set(T["F"]) & set(T["G"]) and T != cs.target_sets(13, "add", P, 4430)
    pw = cs.m0(idx, "add", P)
    assert pw[[k - 1 for k in T["F"]]].sum() > pw[[k - 1 for k in T["G"]]].sum()
    # measure and verdict on synthetic data
    rng = np.random.default_rng(0)
    base = np.ones(153) + 0.1 * rng.random(153)
    a, b = base.copy(), base.copy()
    a[[0, 1, 2, 3, 4]] += 50
    b[[5, 6, 7, 8, 9]] += 50
    d = delta_pow(a, b, [1, 2, 3, 4, 5], [6, 7, 8, 9, 10])
    q = placebo_q99(a, b, [1, 2, 3, 4, 5], [6, 7, 8, 9, 10], 4430)
    assert d > 5 and q < 1, (d, q)
    ok = [{"seed": s, "technical": False, "evaluable": True, "D": 4.0 + 0.1 * i, "Delta_pow": 9.0, "q99": 5.0} for i, s in enumerate(SEEDS)]
    assert verdict(ok, rng)["verdict"] == "bestätigt" and verdict(ok, rng)["p"] == 1 / 2 ** 12
    mixed = ok[:6] + [{**r, "D": -1.0, "evaluable": False} for r in ok[6:]]
    assert verdict(mixed, rng)["verdict"] == "nicht bestätigt"
    ten = ok[:10] + [{**r, "D": -1.0, "evaluable": False} for r in ok[10:]]
    assert verdict(ten, rng)["verdict"] == "bestätigt"
    nine = ok[:9] + [{**r, "D": -1.0, "evaluable": False} for r in ok[9:]]
    assert verdict(nine, rng)["verdict"] == "nicht bestätigt"
    assert verdict(ok[:11], rng)["verdict"] == "nicht auswertbar"
    assert verdict(ok[:11] + [{"seed": 1, "technical": True}], rng)["verdict"] == "nicht auswertbar"
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    print("[confirm_r14] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
