"""P4 confirmation (rule 19b): does split steering (K2, measure Delta_pow of the W_E power) hold in the shared-embedding MLP, at 4x width
(d_model 512) and for NON-modular integer addition, on fresh seeds? Session 25, UNTESTED (selftest and Codex before freezing).

Registration draft: lab/confirm/P4_REGISTRATION_DRAFT.md. Three conditions (Holm over 3); unit = seed with an F/G pair (same init for F and
G, as P1); experiment id 7; fresh seeds per condition (disjoint across conditions).
  mlp     freq_ban.py --arch mlp, add 113, P1 splits (confirm_splits.build, experiment 7), 10 000 steps, primary Delta_pow at 10 000
          (secondary: at 2000)
  d512    EXP-049 width_train.py --d-model 512, add 113, P1 splits (experiment 7), 2000 steps, Delta_pow at 2000
  intadd  EXP-048 intadd_train.py, a + b in 0..224, EXP-048 construction with streams SeedSequence([48001, 7, seed, arm, purpose]) (the
          pilot used [48001, seed, arm, purpose]), 2000 steps, primary Delta_pow on the DETRENDED final W_E (EXP-048 analyze.detrend,
          Nachtrag a); secondary: raw spectrum Delta_pow, linear R^2
Verdict per condition: all planned pairs valid, Holm-p (over 3) of the exact one-sided sign-flip test < 0.05 AND bootstrap CI lower bound
>= MIN_EFFECT (1.0, as P1); any technical failure -> "nicht auswertbar" (p = 1 in the family).

  python lab/tools/confirm_p4.py --selftest
  python lab/tools/confirm_p4.py --splits|--jobs|--analyze lab/confirm/P4_manifest.json
"""
from __future__ import annotations

import functools
import importlib.util
import io
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

RAW = LAB / "confirm" / "p4_raw"
BIND = LAB / "confirm" / "p4_bindings"
SPL = LAB / "confirm" / "p4_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
WT = "lab/experiments/EXP-049-width-steering/width_train.py"
IT = "lab/experiments/EXP-048-intadd-steering/intadd_train.py"
A48 = "lab/experiments/EXP-048-intadd-steering/analyze.py"
MS48 = "lab/experiments/EXP-048-intadd-steering/make_split.py"
P, ALPHA, MIN_EFFECT, EPS, EXPERIMENT = 113, 0.05, 1.0, 2.0, 7
N_PER_COND, SEED_MIN, SEED_MAX = 15, 2360, 2419
CONDS = ("mlp", "d512", "intadd")
STEPS = {"mlp": 10_000, "d512": 2000, "intadd": 2000}
SECONDARY_STEP = 2000                                    # mlp: Delta_pow also at 2000 (reported, no verdict)
STOP_AFTER_GEN = 100_000                                 # freq_ban stops 2000 steps after generalisation by default
D_MODEL = 512
REGISTERED = {"experiment": EXPERIMENT, "p": P, "eps": EPS, "device": "cuda", "threads": 1, "steps": dict(STEPS),
              "d_model": D_MODEL, "stop_after_gen": STOP_AFTER_GEN}     # "seeds" (per condition) is added at registration
CODE_FILES = ("lab/tools/confirm_p4.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py",
              "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py", FB, WT, IT, A48, MS48,
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py")


@functools.lru_cache(maxsize=None)
def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ms48 = _load("p4_exp048_make_split", MS48)        # pilot construction (targets pool, mask power); the file itself is not changed


# ---------------------------------------------------------------- splits
def int_rng(seed: int, arm: str, purpose: str) -> np.random.Generator:
    """EXP-048 streams extended by the experiment id (never equal to a pilot stream: other entropy length)."""
    return np.random.default_rng(np.random.SeedSequence([ms48.SALT, EXPERIMENT, seed, ms48.ARM_ID[arm], ms48.PURPOSE[purpose]]))


def int_targets(seed: int, rng_for=int_rng) -> dict[str, list[int]]:
    ks = np.arange(ms48.KMIN, ms48.KMAX + 1)
    F = sorted(int(k) for k in rng_for(seed, "F", "targets").choice(ks, size=ms48.M, replace=False))
    G = sorted(int(k) for k in rng_for(seed, "G", "targets").choice(np.setdiff1d(ks, F), size=ms48.M, replace=False))
    return {"F": F, "G": G}


def int_engineered(seed: int, arm: str, targets: list[int], eps: float, rng_for=int_rng) -> np.ndarray:
    """ms48.engineered with the stream as a parameter (selftest: identical to the pilot file with the pilot stream)."""
    rng = rng_for(seed, arm, "pairs")
    a, b = np.arange(P).repeat(P), np.tile(np.arange(P), P)
    phi = rng.uniform(0, 2 * np.pi, size=(len(targets), ms48.NC))
    wave = np.mean([np.cos(2 * np.pi * k * a / P + phi[i, a + b]) for i, k in enumerate(targets)], axis=0)
    q = np.clip(1.0 + eps * wave, 0.05, None)
    keys = rng.random(P * P) ** (1.0 / q)
    return np.sort(np.argsort(-keys)[:int(round(ms48.TRAIN_FRAC * P * P))])


def build(cond: str, s: int, arm: str) -> tuple[np.ndarray, dict[str, list[int]]]:
    """Train indices (flat a*113+b) and both target sets of the unit."""
    if cond == "intadd":
        T = int_targets(s)
        return int_engineered(s, arm, T[arm], EPS), T
    idx, _ = cs.build(EXPERIMENT, "add", P, s, arm, EPS)
    return idx, cs.target_sets(EXPERIMENT, "add", P, s)


def check_design(man: dict) -> None:
    """Exactly N_PER_COND integer seeds per condition, globally distinct, inside the reserved block."""
    seeds = man.get("seeds") or {}
    if set(seeds) != set(CONDS) or any(not isinstance(v, list) or len(v) != N_PER_COND or len(set(v)) != N_PER_COND
                                       or not all(type(x) is int for x in v) for v in seeds.values()):
        raise SystemExit(f"P4 manifest: need exactly {N_PER_COND} distinct integer seeds per condition")
    flat = [x for v in seeds.values() for x in v]
    if len(set(flat)) != len(flat) or min(flat) < SEED_MIN or max(flat) > SEED_MAX:
        raise SystemExit(f"P4 manifest: seeds must be globally distinct and from the reserved block {SEED_MIN}-{SEED_MAX}")


def stem(cond: str, s: int, arm: str) -> str:
    return f"p4_{cond}_seed{s}_{arm}"


def write_splits(man: dict) -> None:
    check_design(man)
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(c, s, a)}{ext}" for c in CONDS for s in man["seeds"][c] for a in "FG" for ext in (".npy", ".json")]   # Codex s25
    if any((SPL / n).exists() for n in names):
        raise SystemExit("P4 splits exist already: never overwrite")
    for c in CONDS:
        for s in man["seeds"][c]:
            for a in "FG":
                idx, T = build(c, s, a)
                if len(idx) != int(round(0.3 * P * P)) or len(np.unique(idx)) != len(idx):
                    raise SystemExit(f"P4 split {stem(c, s, a)}: bad size")
                with open(SPL / f"{stem(c, s, a)}.npy", "xb") as f:
                    np.save(f, idx.astype(np.int64))
                with open(SPL / f"{stem(c, s, a)}.json", "x", encoding="utf-8") as f:
                    json.dump({"cond": c, "seed": s, "arm": a, "targets": T[a], "other_targets": T["G" if a == "F" else "F"],
                               "eps": EPS, "n": int(len(idx)), "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(c: str, s: int) -> str | None:
    for a in "FG":
        idx, T = build(c, s, a)
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
    return f"lab/confirm/p4_splits/{stem(c, s, a)}.npy"


def job(man: dict, c: str, s: int, a: str) -> str:
    py, st, th, dev = c1.interp(man), man["steps"][c], man["threads"], man["device"]
    if c == "mlp":
        return (f"{py} {FB} --seed {s} --condition baseline --steps {st} --stop-after-gen {man['stop_after_gen']} --threads {th} "
                f"--device {dev} --arch mlp --split-file {split_arg(c, s, a)} --spectra-at {SECONDARY_STEP},{st} --out-root lab/confirm/p4_raw")
    if c == "d512":
        return (f"{py} {WT} --seed {s} --d-model {man['d_model']} --split-file {split_arg(c, s, a)} --steps {st} --threads {th} "
                f"--device {dev} --out-root lab/confirm/p4_raw")
    return f"{py} {IT} --seed {s} --split-file {split_arg(c, s, a)} --steps {st} --threads {th} --device {dev} --out-root lab/confirm/p4_raw"


def trainer_jobs(man: dict) -> list[str]:
    return [job(man, c, s, a) for c in CONDS for s in man["seeds"][c] for a in "FG"]


def expected_run_id(cmd: list[str]) -> str:
    """Run-id rules of the three trainers (freq_ban: EXP-045_<cond>_seed<s>_thr<t>_<stem>_mlp[_dev]; width_train: EXP-049_d<d>_seed<s>_
    <stem>_dev<dev>; intadd_train: EXP-048_seed<s>_<stem>_dev<dev>)."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    sp, s, dev = Path(g("--split-file")).stem, g("--seed"), (g("--device") or "cpu").replace(":", "")
    cond = Path(g("--split-file")).name.split("_")[1]         # the split stem names the condition (selftest fakes drop the script)
    if cond == "mlp" and g("--arch") == "mlp":
        return f"EXP-045_baseline_seed{s}_thr{g('--threads')}_{sp}_mlp" + ("" if dev == "cpu" else f"_dev{dev}")
    if cond == "d512" and g("--d-model"):
        return f"EXP-049_d{g('--d-model')}_seed{s}_{sp}_dev{dev}"
    if cond == "intadd" and g("--arch") is None and g("--d-model") is None:
        return f"EXP-048_seed{s}_{sp}_dev{dev}"
    raise SystemExit(f"P4: command does not match a P4 trainer: {' '.join(cmd)[:120]}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_p4", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_p4.py")


# ---------------------------------------------------------------- analysis
def expect(man: dict, c: str, s: int, split: Path) -> Expect:
    st = man["steps"][c]
    if c == "mlp":
        return Expect(seed=s, device=man["device"], max_steps=st, split_file=split,
                      config={"p": P, "task": "add", "arch": "mlp"}, at=(SECONDARY_STEP, st))
    if c == "d512":
        return Expect(seed=s, device=man["device"], max_steps=st, split_file=split,
                      config={"p": P, "arch": "transformer", "d_model": man["d_model"]}, at=(st,))
    return Expect(seed=s, device=man["device"], max_steps=st, split_file=split, config={"p": 2 * P - 1}, at=(st,), files=("we_final.npy",))


def spectra(man: dict, c: str, s: int, arm: str) -> dict | str:
    """Per run: 'primary' (and for mlp/intadd 'secondary') W_E power k = 1..56, plus descriptive fields; a string = technical failure."""
    split = SPL / f"{stem(c, s, arm)}.npy"
    d = run_dir(shlex.split(job(man, c, s, arm)))
    if not d.exists():
        return "fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"defekt: {why}"
    L = load_run(d, expect(man, c, s, split))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(split):
        return f"defekt after load: {why or 'split bytes differ'}"
    st = man["steps"][c]
    out = {"test_acc": (L.res.get("final_acc") or {}).get("test"),
           "gen_step": L.res.get("generalization_step", (L.res.get("events") or {}).get("generalization_step"))}
    if c == "intadd":
        a48, it = _load("p4_exp048_analyze", A48), _load("p4_intadd_train", IT)
        W = np.load(io.BytesIO(BLOCK.bound_bytes(man, d / "we_final.npy"))).astype(np.float64)
        if W.shape[0] != P or not np.all(np.isfinite(W)):
            return "defekt: we_final shape or values"
        out.update(primary=it.dft_power(a48.detrend(W)), secondary=np.asarray(L.spectrum(st), dtype=np.float64),
                   linear_r2=(L.res.get("linear_r2") or [None])[-1])
    elif c == "mlp":
        out.update(primary=np.asarray(L.spectrum(st), dtype=np.float64), secondary=np.asarray(L.spectrum(SECONDARY_STEP), dtype=np.float64))
    else:
        out.update(primary=np.asarray(L.spectrum(st), dtype=np.float64))
    for k in ("primary", "secondary"):
        if k in out and (out[k].shape != (56,) or not np.all(np.isfinite(out[k]))):
            return f"defekt: {k} spectrum shape or values"
    return out


def seed_row(man: dict, c: str, s: int) -> dict:
    T = {a: json.loads((SPL / f"{stem(c, s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
    runs = {a: spectra(man, c, s, a) for a in "FG"}
    bad = [f"{a}: {v}" for a, v in runs.items() if isinstance(v, str)]
    if bad:
        return {"seed": s, "technical": True, "reason": "; ".join(bad)}
    d = c1.delta_pow_checked(runs["F"]["primary"], runs["G"]["primary"], T["F"], T["G"])
    diag = {f"{k}_{a}": runs[a][k] for a in "FG" for k in ("test_acc", "gen_step", "linear_r2") if k in runs[a]}
    if "secondary" in runs["F"]:
        diag["Delta_pow_secondary"] = c1.delta_pow_checked(runs["F"]["secondary"], runs["G"]["secondary"], T["F"], T["G"])
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
        sec = [r["Delta_pow_secondary"] for r in rs if r.get("Delta_pow_secondary") is not None]
        accs = [r[f"test_acc_{a}"] for r in rs for a in "FG" if r.get(f"test_acc_{a}") is not None]
        out[c] = {"n": len(D), "mean": float(D.mean()), "sd": float(D.std(ddof=1)), "p": p, "ci95": c1.boot_ci(D, rng),
                  "n_positive": int((D > 0).sum()), "n_technical": 0,
                  "secondary_mean": float(np.mean(sec)) if sec else None, "secondary_n": len(sec),
                  "median_test_acc": float(np.median(accs)) if accs else None,
                  "n_arms_generalised": int(sum(r.get(f"gen_step_{a}") is not None for r in rs for a in "FG"))}
        ps[c] = p
    ph = c1.holm(ps)
    for c in out:
        if "p" in out[c]:
            out[c]["p_holm"] = ph[c]
            out[c]["verdict"] = "bestätigt" if ph[c] < ALPHA and out[c]["ci95"][0] >= MIN_EFFECT else "nicht bestätigt"
    return out


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "P4_summary.json"
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    check_design(man)
    bad = [m for c in CONDS for m in (split_mismatch(c, s) for s in man["seeds"][c]) if m]
    if bad:
        raise SystemExit(f"P4 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = {c: [seed_row(man, c, s) for s in man["seeds"][c]] for c in CONDS}
    out = {"manifest_commit": man["commit"], "min_effect": MIN_EFFECT,
           "conditions": verdict(rows, {c: len(man["seeds"][c]) for c in CONDS}, np.random.default_rng(7)), "rows": rows}
    stale.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    seeds = {c: list(range(SEED_MIN + 15 * i, SEED_MIN + 15 * i + 15)) for i, c in enumerate(CONDS)}
    for bad in ({**seeds, "d512": seeds["d512"][:14]}, {**seeds, "d512": seeds["mlp"]}, {**seeds, "d512": [SEED_MIN] * 15},
                {**seeds, "intadd": list(range(9000, 9015))}, {**seeds, "intadd": [float(x) for x in seeds["intadd"]]}):
        try:
            check_design({"seeds": bad})
            raise AssertionError("bad seed design accepted")
        except SystemExit:
            pass
    check_design({"seeds": seeds})
    man = {**REGISTERED, "python": "PY", "seeds": seeds}
    BLOCK.check_registered(man)
    tj = trainer_jobs(man)
    assert len(tj) == 3 * 15 * 2 and len(set(tj)) == len(tj) and all("p4_raw" in j and "\\" not in j for j in tj)
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert len(set(ids)) == len(ids)
    assert ids[0] == f"EXP-045_baseline_seed{SEED_MIN}_thr1_p4_mlp_seed{SEED_MIN}_F_mlp_devcuda", ids[0]
    assert ids[30] == f"EXP-049_d512_seed{SEED_MIN + 15}_p4_d512_seed{SEED_MIN + 15}_F_devcuda", ids[30]
    assert ids[60] == f"EXP-048_seed{SEED_MIN + 30}_p4_intadd_seed{SEED_MIN + 30}_F_devcuda", ids[60]
    assert "--stop-after-gen 100000" in tj[0] and "--spectra-at 2000,10000" in tj[0] and "--steps 10000" in tj[0]
    assert "--d-model 512" in tj[30] and "--steps 2000" in tj[30] and "--steps 2000" in tj[60]
    # splits: add 113 = the P1 construction with experiment 7; intadd = the pilot construction with extended streams
    for c, s in (("mlp", SEED_MIN), ("d512", SEED_MIN + 15)):
        for a in "FG":
            idx, T = build(c, s, a)
            ref, Tr = cs.build(EXPERIMENT, "add", P, s, a, EPS)
            assert np.array_equal(idx, ref) and T[a] == Tr and len(idx) == 3831
    pilot_T = ms48.target_sets(160)
    assert int_targets(160, rng_for=ms48.rng_for) == pilot_T
    for a in "FG":
        assert np.array_equal(int_engineered(160, a, pilot_T[a], EPS, rng_for=ms48.rng_for), ms48.engineered(160, a, pilot_T[a], EPS))
    for s in (160, SEED_MIN + 30):                      # Codex s25: same seed, pilot stream vs P4 stream -> other targets and pairs
        Tp, Tn = int_targets(s, rng_for=ms48.rng_for), int_targets(s)
        assert Tp != Tn and not np.array_equal(int_engineered(s, "F", Tn["F"], EPS), int_engineered(s, "F", Tn["F"], EPS, rng_for=ms48.rng_for))
    T = int_targets(SEED_MIN + 30)
    assert T != pilot_T and not set(T["F"]) & set(T["G"]) and all(ms48.KMIN <= k <= ms48.KMAX for k in T["F"] + T["G"])
    idx = int_engineered(SEED_MIN + 30, "F", T["F"], EPS)
    assert len(idx) == 3831 and len(np.unique(idx)) == 3831
    pw = ms48.mask_power(idx)
    assert pw[[k - 1 for k in T["F"]]].sum() / pw.sum() > pw[[k - 1 for k in T["G"]]].sum() / pw.sum()   # mask carries F, not G
    # measure: detrended intadd Delta_pow (EXP-048 analyze) is positive on a synthetic F/G pair despite a shared number line
    a48, it = _load("p4_exp048_analyze", A48), _load("p4_intadd_train", IT)
    rng = np.random.default_rng(0)
    x = np.arange(P)
    ramp = np.outer(x, rng.normal(size=8))
    wF = np.outer(np.cos(2 * np.pi * 9 * x / P), rng.normal(size=8))
    wG = np.outer(np.cos(2 * np.pi * 40 * x / P + 1.0), rng.normal(size=8))
    base = 0.05 * rng.normal(size=(P, 8))
    d = c1.delta_pow_checked(it.dft_power(a48.detrend(3 * ramp + wF + base)), it.dft_power(a48.detrend(ramp + wG + base)), [9], [40])
    assert d is not None and d > 1, d
    # verdict logic; exact sign-flip p for n = 15 (Codex s25): all positive -> 1 / 2^15
    assert c1.sign_flip_p(np.arange(1.0, 16.0), rng) == 1 / 2 ** 15
    ok = [{"seed": i, "technical": False, "Delta_pow": 5.0 + 0.1 * i, "test_acc_F": 1.0, "test_acc_G": 0.5, "gen_step_F": 900,
           "gen_step_G": None, "Delta_pow_secondary": 2.0} for i in range(15)]
    v = verdict({c: ok for c in CONDS}, {c: 15 for c in CONDS}, rng)
    assert all(x["verdict"] == "bestätigt" for x in v.values()), v
    assert v["mlp"]["n_arms_generalised"] == 15 and v["mlp"]["median_test_acc"] == 0.75 and v["mlp"]["secondary_mean"] == 2.0
    v = verdict({**{c: ok for c in CONDS}, "d512": ok[:14]}, {c: 15 for c in CONDS}, rng)
    assert v["d512"]["verdict"] == "nicht auswertbar" and v["mlp"]["verdict"] == "bestätigt"
    v = verdict({**{c: ok for c in CONDS}, "intadd": ok[:14] + [{"seed": 99, "technical": True, "reason": "x"}]}, {c: 15 for c in CONDS}, rng)
    assert v["intadd"]["verdict"] == "nicht auswertbar"
    weak = [{"seed": i, "technical": False, "Delta_pow": 0.5 + 0.05 * i} for i in range(15)]
    assert verdict({**{c: ok for c in CONDS}, "intadd": weak}, {c: 15 for c in CONDS}, rng)["intadd"]["verdict"] == "nicht bestätigt"
    mixed = [{"seed": i, "technical": False, "Delta_pow": (3.0 if i % 2 else -2.5)} for i in range(15)]
    assert verdict({**{c: ok for c in CONDS}, "mlp": mixed}, {c: 15 for c in CONDS}, rng)["mlp"]["verdict"] == "nicht bestätigt"
    selftest_binding(BLOCK, tj[0], tj[30], tj[60])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    print("[confirm_p4] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
