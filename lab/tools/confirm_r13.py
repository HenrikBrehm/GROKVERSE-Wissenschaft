"""R13 confirmation (session 67): does split steering of the W_E spectrum (K2, Delta_pow at step 2000) hold WITHOUT Adam, under
full-batch SGD with momentum and global gradient-norm clipping, on fresh seeds and splits? Registration: lab/confirm/R13_REGISTRATION.md.

Motivation: paper limitation (i) "all results are AdamW results"; EXP-126 (plain SGDm) and EXP-128 (clipped SGDm) were "nicht auswertbar"
by their pre-set fit criterion, but post hoc (seen seeds 3704-3707) Delta_pow at step 2000 was 7.2-7.6 (clip 0.1) and 4.0-4.5 (clip 0.017)
in every seed, mostly WITHOUT fitting the training set. R13 tests this representation claim (like P4 integer addition: steering of the
W_E spectrum without generalization), not a claim about learned algorithms.
Two conditions (Holm over 2); unit = seed with an F/G pair (same init for F and G, as P1/P4); split construction = P1 (confirm_splits.build)
with experiment id 13; fresh seeds 4400-4414 (c01) and 4415-4429 (c0017), disjoint.
  c01    freq_ban_sgdclip.py (EXP-128 trainer copy) --optimizer sgdm --sgd-lr 0.1 --sgd-momentum 0.9 --sgd-clip 0.1, add 113, 2000 steps
  c0017  same with --sgd-clip 0.017
Primary per condition: Delta_pow of the W_E power (spectra.npy, additive DFT, k = 1..56) at step 2000; exact one-sided sign-flip test
(n = 15), Holm over 2, bootstrap CI; "bestätigt" if all 15 pairs valid, Holm-p < 0.05 AND CI lower bound >= MIN_EFFECT (1.0, as P1/P4);
any technical failure -> "nicht auswertbar" (p = 1 in the family).
Descriptive (no verdict): Delta_pow at 250; final train/test accuracy; arms with train >= 0.99; generalization step; clipped share;
any non-finite logged gradient norm.

  python lab/tools/confirm_r13.py --selftest
  python lab/tools/confirm_r13.py --splits|--jobs|--analyze lab/confirm/R13_manifest.json
"""
from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
import confirm_p1 as c1  # noqa: E402  (read-only reuse: delta_pow_checked, sign_flip_p, boot_ci, holm, interp)
import confirm_splits as cs  # noqa: E402
from bound_block import Block, selftest_binding, sha  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "r13_raw"
BIND = LAB / "confirm" / "r13_bindings"
SPL = LAB / "confirm" / "r13_splits"
FBS = "lab/experiments/EXP-128-sgd-clip/freq_ban_sgdclip.py"
P, ALPHA, MIN_EFFECT, EPS, EXPERIMENT = 113, 0.05, 1.0, 2.0, 13
N_PER_COND, SEED_MIN, SEED_MAX = 15, 4400, 4429
CONDS = ("c01", "c0017")
CLIP = {"c01": 0.1, "c0017": 0.017}
STEPS, SECONDARY_STEP, SGD_LR, SGD_MOM = 2000, 250, 0.1, 0.9
REGISTERED_SEEDS = {"c01": list(range(4400, 4415)), "c0017": list(range(4415, 4430))}
STOP_AFTER_GEN = 100_000                                 # never stop early: Delta_pow is read at 2000 in every run
REGISTERED = {"experiment": EXPERIMENT, "p": P, "eps": EPS, "device": "cuda", "threads": 1, "steps": STEPS,
              "stop_after_gen": STOP_AFTER_GEN, "sgd_lr": SGD_LR, "sgd_momentum": SGD_MOM, "clip": dict(CLIP)}
CODE_FILES = ("lab/tools/confirm_r13.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py",
              "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py", FBS,
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py")


# ---------------------------------------------------------------- splits
def build(s: int, arm: str) -> tuple[np.ndarray, dict[str, list[int]]]:
    idx, _ = cs.build(EXPERIMENT, "add", P, s, arm, EPS)
    return idx, cs.target_sets(EXPERIMENT, "add", P, s)


def check_design(man: dict) -> None:
    """Exactly N_PER_COND integer seeds per condition, globally distinct, inside the reserved block."""
    seeds = man.get("seeds") or {}
    if set(seeds) != set(CONDS) or any(not isinstance(v, list) or len(v) != N_PER_COND or len(set(v)) != N_PER_COND
                                       or not all(type(x) is int for x in v) for v in seeds.values()):
        raise SystemExit(f"R13 manifest: need exactly {N_PER_COND} distinct integer seeds per condition")
    flat = [x for v in seeds.values() for x in v]
    if len(set(flat)) != len(flat) or min(flat) < SEED_MIN or max(flat) > SEED_MAX:
        raise SystemExit(f"R13 manifest: seeds must be globally distinct and from the reserved block {SEED_MIN}-{SEED_MAX}")
    if seeds != REGISTERED_SEEDS:                         # pre-freeze review s67: the registration fixes the assignment
        raise SystemExit("R13 manifest: seeds differ from the registered assignment (c01 4400-4414, c0017 4415-4429)")


def stem(cond: str, s: int, arm: str) -> str:
    return f"r13_{cond}_seed{s}_{arm}"


def write_splits(man: dict) -> None:
    check_design(man)
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(c, s, a)}{ext}" for c in CONDS for s in man["seeds"][c] for a in "FG" for ext in (".npy", ".json")]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("R13 splits exist already: never overwrite")
    for c in CONDS:
        for s in man["seeds"][c]:
            for a in "FG":
                idx, T = build(s, a)
                if len(idx) != int(round(0.3 * P * P)) or len(np.unique(idx)) != len(idx):
                    raise SystemExit(f"R13 split {stem(c, s, a)}: bad size")
                with open(SPL / f"{stem(c, s, a)}.npy", "xb") as f:
                    np.save(f, idx.astype(np.int64))
                with open(SPL / f"{stem(c, s, a)}.json", "x", encoding="utf-8") as f:
                    json.dump({"cond": c, "seed": s, "arm": a, "targets": T[a], "other_targets": T["G" if a == "F" else "F"],
                               "eps": EPS, "n": int(len(idx)), "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(c: str, s: int) -> str | None:
    for a in "FG":
        idx, T = build(s, a)
        f, j = SPL / f"{stem(c, s, a)}.npy", SPL / f"{stem(c, s, a)}.json"
        if not f.exists() or not j.exists():
            return f"{stem(c, s, a)}: split file missing"
        meta = json.loads(j.read_text(encoding="utf-8"))
        if not (np.array_equal(np.load(f), idx.astype(np.int64)) and meta.get("targets") == T[a] and meta.get("seed") == s
                and meta.get("cond") == c):
            return f"{stem(c, s, a)}: differs from the deterministic rebuild"
    return None


# ---------------------------------------------------------------- jobs and binding
def split_arg(c: str, s: int, a: str) -> str:
    return f"lab/confirm/r13_splits/{stem(c, s, a)}.npy"


def job(man: dict, c: str, s: int, a: str) -> str:
    py, th, dev = c1.interp(man), man["threads"], man["device"]
    return (f"{py} {FBS} --seed {s} --condition baseline --steps {man['steps']} --stop-after-gen {man['stop_after_gen']} "
            f"--threads {th} --device {dev} --split-file {split_arg(c, s, a)} --spectra-at {SECONDARY_STEP},{man['steps']} "
            f"--optimizer sgdm --sgd-lr {man['sgd_lr']!r} --sgd-momentum {man['sgd_momentum']!r} --sgd-clip {man['clip'][c]!r} "
            f"--out-root lab/confirm/r13_raw")


def trainer_jobs(man: dict) -> list[str]:
    return [job(man, c, s, a) for c in CONDS for s in man["seeds"][c] for a in "FG"]


def expected_run_id(cmd: list[str]) -> str:
    """Run-id rule of freq_ban_sgdclip.py (split file, no test file -> EXP-016; found by the smoke, s67): EXP-016_baseline_seed<s>_thr<t>_<split stem>_sgdm<lr!r>_<mom!r>_clip<c!r>_dev<dev>."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    sp, s, dev = Path(g("--split-file")).stem, g("--seed"), (g("--device") or "cpu").replace(":", "")
    if g("--optimizer") != "sgdm" or g("--sgd-clip") is None or not sp.startswith("r13_"):
        raise SystemExit(f"R13: command does not match the R13 trainer call: {' '.join(cmd)[:120]}")
    return (f"EXP-016_baseline_seed{s}_thr{g('--threads')}_{sp}_sgdm{float(g('--sgd-lr'))!r}_{float(g('--sgd-momentum'))!r}"
            f"_clip{float(g('--sgd-clip'))!r}" + ("" if dev == "cpu" else f"_dev{dev}"))


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r13", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_r13.py")


# ---------------------------------------------------------------- analysis
def expect(man: dict, s: int, split: Path) -> Expect:
    return Expect(seed=s, device=man["device"], max_steps=man["steps"], split_file=split,
                  config={"p": P, "task": "add", "arch": "transformer"}, at=(SECONDARY_STEP, man["steps"]))


def run_info(man: dict, c: str, s: int, arm: str) -> dict | str:
    """Per run: primary/secondary W_E power k = 1..56 plus descriptive fields; a string = technical failure."""
    split = SPL / f"{stem(c, s, arm)}.npy"
    d = run_dir(shlex.split(job(man, c, s, arm)))
    if not d.exists():
        return "fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"defekt: {why}"
    L = load_run(d, expect(man, s, split))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(split):
        return f"defekt after load: {why or 'split bytes differ'}"
    r = L.res
    clip_ev = (r.get("events") or {}).get("sgd_clip") or {}
    if (r.get("optimizer") != "sgdm" or r.get("sgd_lr") != man["sgd_lr"] or r.get("sgd_momentum") != man["sgd_momentum"]
            or clip_ev.get("max_norm") != man["clip"][c]):
        return "defekt: optimizer settings differ from the manifest"
    norms = clip_ev.get("norms") or []
    vals = [n[1] if isinstance(n, (list, tuple)) else n for n in norms]
    gen = ((r.get("transitions") or {}).get("primary") or {}).get("generalization", {}).get("first_crossing_step")
    out = {"train_acc": (r.get("final_acc") or {}).get("train"), "test_acc": (r.get("final_acc") or {}).get("test"), "gen_step": gen,
           "clipped_share": clip_ev.get("clipped_steps", 0) / man["steps"],
           "nonfinite_norm": any(not np.isfinite(float(v)) for v in vals if v is not None),
           "primary": np.asarray(L.spectrum(man["steps"]), dtype=np.float64),
           "secondary": np.asarray(L.spectrum(SECONDARY_STEP), dtype=np.float64)}
    for k in ("primary", "secondary"):
        if out[k].shape != (56,) or not np.all(np.isfinite(out[k])):
            return f"defekt: {k} spectrum shape or values"
    return out


def seed_row(man: dict, c: str, s: int) -> dict:
    T = {a: json.loads((SPL / f"{stem(c, s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
    runs = {a: run_info(man, c, s, a) for a in "FG"}
    bad = [f"{a}: {v}" for a, v in runs.items() if isinstance(v, str)]
    if bad:
        return {"seed": s, "technical": True, "reason": "; ".join(bad)}
    d = c1.delta_pow_checked(runs["F"]["primary"], runs["G"]["primary"], T["F"], T["G"])
    diag = {f"{k}_{a}": runs[a][k] for a in "FG" for k in ("train_acc", "test_acc", "gen_step", "clipped_share", "nonfinite_norm")}
    diag["Delta_pow_250"] = c1.delta_pow_checked(runs["F"]["secondary"], runs["G"]["secondary"], T["F"], T["G"])
    if d is None:
        return {"seed": s, "technical": True, "reason": "Delta_pow undefined", **diag}
    return {"seed": s, "technical": False, "Delta_pow": d, **diag}


def verdict(rows: dict[str, list[dict]], n_planned: dict[str, int], rng: np.random.Generator) -> dict:
    out, ps = {}, {}
    for c, rs in rows.items():
        n_tech = sum(1 for r in rs if r.get("technical"))
        if n_tech or len(rs) != n_planned[c] or n_planned[c] != N_PER_COND:
            out[c], ps[c] = {"n": len(rs), "n_technical": n_tech, "verdict": "nicht auswertbar"}, 1.0
            continue
        D = np.array([r["Delta_pow"] for r in rs])
        p = c1.sign_flip_p(D, rng)
        sec = [r["Delta_pow_250"] for r in rs if r.get("Delta_pow_250") is not None]
        fit = [r[f"train_acc_{a}"] for r in rs for a in "FG" if r.get(f"train_acc_{a}") is not None]
        out[c] = {"n": len(D), "mean": float(D.mean()), "sd": float(D.std(ddof=1)), "p": p, "ci95": c1.boot_ci(D, rng),
                  "n_positive": int((D > 0).sum()), "n_technical": 0,
                  "Delta_pow_250_mean": float(np.mean(sec)) if sec else None,
                  "n_arms_train_ge_0.99": int(sum(x >= 0.99 for x in fit)), "median_train_acc": float(np.median(fit)) if fit else None,
                  "n_arms_generalised": int(sum(r.get(f"gen_step_{a}") is not None for r in rs for a in "FG")),
                  "median_clipped_share": float(np.median([r[f"clipped_share_{a}"] for r in rs for a in "FG"])),
                  "n_arms_nonfinite_norm": int(sum(bool(r.get(f"nonfinite_norm_{a}")) for r in rs for a in "FG"))}
        ps[c] = p
    ph = c1.holm(ps)
    for c in out:
        if "p" in out[c]:
            out[c]["p_holm"] = ph[c]
            out[c]["verdict"] = "bestätigt" if ph[c] < ALPHA and out[c]["ci95"][0] >= MIN_EFFECT else "nicht bestätigt"
    return out


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "R13_summary.json"
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    check_design(man)
    bad = [m for c in CONDS for m in (split_mismatch(c, s) for s in man["seeds"][c]) if m]
    if bad:
        raise SystemExit(f"R13 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = {c: [seed_row(man, c, s) for s in man["seeds"][c]] for c in CONDS}
    out = {"manifest_commit": man["commit"], "min_effect": MIN_EFFECT,
           "conditions": verdict(rows, {c: len(man["seeds"][c]) for c in CONDS}, np.random.default_rng(13)), "rows": rows}
    stale.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    seeds = {"c01": list(range(4400, 4415)), "c0017": list(range(4415, 4430))}
    for bad in ({"c01": seeds["c0017"], "c0017": seeds["c01"]}, {**seeds, "c01": seeds["c01"][:14]}, {**seeds, "c0017": seeds["c01"]}, {**seeds, "c01": [4400] * 15},
                {**seeds, "c0017": list(range(9000, 9015))}, {**seeds, "c01": [float(x) for x in seeds["c01"]]}, {"c01": seeds["c01"]}):
        try:
            check_design({"seeds": bad})
            raise AssertionError("bad seed design accepted")
        except SystemExit:
            pass
    check_design({"seeds": seeds})
    man = {**REGISTERED, "python": "PY", "seeds": seeds}
    BLOCK.check_registered(man)
    tj = trainer_jobs(man)
    assert len(tj) == 2 * 15 * 2 and len(set(tj)) == len(tj) and all("r13_raw" in j and "\\" not in j for j in tj)
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert len(set(ids)) == len(ids)
    assert ids[0] == "EXP-016_baseline_seed4400_thr1_r13_c01_seed4400_F_sgdm0.1_0.9_clip0.1_devcuda", ids[0]
    assert ids[30] == "EXP-016_baseline_seed4415_thr1_r13_c0017_seed4415_F_sgdm0.1_0.9_clip0.017_devcuda", ids[30]
    assert "--sgd-clip 0.1 " in tj[0] and "--sgd-clip 0.017 " in tj[30] and "--steps 2000" in tj[0]
    assert "--stop-after-gen 100000" in tj[0] and "--spectra-at 250,2000" in tj[0] and "--sgd-lr 0.1 --sgd-momentum 0.9" in tj[0]
    for bad_cmd in (tj[0].replace("--optimizer sgdm ", ""), tj[0].replace("r13_c01", "p4_c01")):
        try:
            expected_run_id(shlex.split(bad_cmd))
            raise AssertionError("non-R13 command accepted")
        except SystemExit:
            pass
    # splits: the P1 construction with experiment 13 (fresh streams), F/G disjoint, mask carries the own targets
    for s in (4400, 4429):
        T = cs.target_sets(EXPERIMENT, "add", P, s)
        assert not set(T["F"]) & set(T["G"]) and T != cs.target_sets(7, "add", P, s) and T != cs.target_sets(1, "add", P, s)
        for a in "FG":
            idx, TT = build(s, a)
            assert len(idx) == 3831 and len(np.unique(idx)) == 3831 and TT == T
    # verdict logic; exact sign-flip p for n = 15: all positive -> 1 / 2^15
    rng = np.random.default_rng(0)
    assert c1.sign_flip_p(np.arange(1.0, 16.0), rng) == 1 / 2 ** 15
    ok = [{"seed": i, "technical": False, "Delta_pow": 5.0 + 0.1 * i, "train_acc_F": 1.0, "train_acc_G": 0.3, "gen_step_F": 900,
           "gen_step_G": None, "clipped_share_F": 0.05, "clipped_share_G": 0.95, "nonfinite_norm_F": False,
           "nonfinite_norm_G": False, "Delta_pow_250": 0.3} for i in range(15)]
    v = verdict({c: ok for c in CONDS}, {c: 15 for c in CONDS}, rng)
    assert all(x["verdict"] == "bestätigt" for x in v.values()), v
    assert v["c01"]["n_arms_train_ge_0.99"] == 15 and v["c01"]["n_arms_generalised"] == 15 and v["c01"]["median_clipped_share"] == 0.5
    v = verdict({**{c: ok for c in CONDS}, "c0017": ok[:14]}, {c: 15 for c in CONDS}, rng)
    assert v["c0017"]["verdict"] == "nicht auswertbar" and v["c01"]["verdict"] == "bestätigt"
    v = verdict({**{c: ok for c in CONDS}, "c01": ok[:14] + [{"seed": 99, "technical": True, "reason": "x"}]}, {c: 15 for c in CONDS}, rng)
    assert v["c01"]["verdict"] == "nicht auswertbar"
    weak = [{**ok[i], "Delta_pow": 0.5 + 0.03 * i} for i in range(15)]
    assert verdict({**{c: ok for c in CONDS}, "c01": weak}, {c: 15 for c in CONDS}, rng)["c01"]["verdict"] == "nicht bestätigt"
    mixed = [{**ok[i], "Delta_pow": (3.0 if i % 2 else -2.5)} for i in range(15)]
    assert verdict({**{c: ok for c in CONDS}, "c0017": mixed}, {c: 15 for c in CONDS}, rng)["c0017"]["verdict"] == "nicht bestätigt"
    selftest_binding(BLOCK, tj[0], tj[1], tj[30])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    print("[confirm_r13] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
