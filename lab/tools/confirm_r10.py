"""R10 confirmation (FINDINGS, open question after EXP-093/094; pilot EXP-095): does early lock-in need the gradient to be re-evaluated
along the path? Session 42, UNTESTED BEYOND --selftest.

Registration: lab/confirm/R10_REGISTRATION_DRAFT.md. Protocol as EXP-095 (omega = 0 EXP-053 splits built from the seed, both switch
directions A->B and B->A at t, then BUDGET = 2000 steps at the default lr and betas; pi = persistence of the old choice in the log energy
ratio of the final W_E group power, against the pure A/B runs of the seed, EXP-056 definition). Pre-switch history per cell (Lambda = 24):
  n24  : default, t = 24                                                  (24 gradient evaluations, 24 Adam steps)
  g8   : default, t = 24, --pre-switch-grad-every 8                       (3 evaluations, 24 Adam steps)
  g24  : default, t = 24, --pre-switch-grad-every 24                      (initial gradient only, 24 Adam steps)
  c8b  : --lr-scale 8, --pre-switch-betas 0.2,0.84, t = 3                 (3 evaluations, 3 Adam steps, windows matched in Lambda)
Primary family (Holm over 3, alpha 0.05):
  H1  e8 = pi(n24) - pi(g8); one-sided t-test of e8 > 0; 'bestätigt' = Holm p < 0.05 and bootstrap CI lower bound of e8 > 0
  H2  r8 = pi(g8) - pi(c8b) inside +-0.05; TOST p = max of the two one-sided t-test p; 'bestätigt' = Holm p < 0.05
  H3  e24 = pi(n24) - pi(g24); one-sided t-test of e24 > 0; 'bestätigt' = Holm p < 0.05 and bootstrap CI lower bound of e24 > 0
Descriptive: e24 - e8; target share and norm of the W_E displacement at the switch per cell (EXP-092 selectivity; taken before
any post-switch step, so free of the Adam step-counter difference after the switch: c8b switches at counter 3, the others at 24).
Validity: any technical failure -> 'nicht auswertbar'. Seeds with L(A) - L(B) < 2 are excluded and counted; more than 8 -> 'nicht auswertbar'.

  python lab/tools/confirm_r10.py --hash-code | --splits M | --jobs M | --run M -- <cmd> | --analyze M | --selftest
"""
from __future__ import annotations

import importlib.util
import json
import shlex
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "experiments/EXP-053-p3-overlap-design"))
import confirm_p1 as c1  # noqa: E402  (read-only reuse: interp, t-test, bootstrap, holm)
from bound_block import Block, selftest_binding, sha  # noqa: E402
import overlap_split as ov  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "r10_raw"
BIND = LAB / "confirm" / "r10_bindings"
SPL = LAB / "confirm" / "r10_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"
BUDGET, ALPHA, OMEGA, P = 2000, 0.05, 0.0, 113
EQ, MIN_LALB, MAX_EXCLUDED = 0.05, 2.0, 8
LR_SCALE_UNTIL = 250
CELLS = {"n24": {"c": 1.0, "t": 24, "psb": None, "k": 1}, "g8": {"c": 1.0, "t": 24, "psb": None, "k": 8},
         "g24": {"c": 1.0, "t": 24, "psb": None, "k": 24}, "c8b": {"c": 8.0, "t": 3, "psb": [0.2, 0.84], "k": 1}}
HYP = ("H1", "H2", "H3")
REGISTERED = {"seeds": list(range(3500, 3548)), "budget": 2000, "device": "cuda", "threads": 1,
              "cells": {k: dict(v) for k, v in CELLS.items()}}
CODE_FILES = ("lab/tools/confirm_r10.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_p2.py",
              "lab/tools/confirm_splits.py", "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py",
              "lab/experiments/EXP-001-freq-ban/freq_ban.py",
              "lab/experiments/EXP-053-p3-overlap-design/overlap_split.py", "lab/experiments/EXP-053-p3-overlap-design/calibration.json",
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py",
              "lab/experiments/EXP-056-overlap-persistence/analyze.py", "lab/experiments/EXP-056-overlap-persistence/make_splits.py")


# ---------------------------------------------------------------- splits and jobs
def stem(s: int, arm: str) -> str:
    return f"r10_seed{s}_w0_{arm}"


def build(s: int) -> tuple[list[int], list[int], dict]:
    eps = json.loads(CAL.read_text(encoding="utf-8"))["levels"][str(OMEGA)]["eps"]
    F, G = ov.targets(s)
    return F, G, ov.build(s, OMEGA, eps)


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, a)}.npy" for s in man["seeds"] for a in "AB"] + [f"r10_seed{s}_test.npy" for s in man["seeds"]]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("R10 splits exist already: never overwrite")
    for s in man["seeds"]:
        F, G, d = build(s)
        assert len(d["A"]) == len(d["B"]) == ov.N_TRAIN and not np.intersect1d(d["A"], d["B"]).size
        assert not np.intersect1d(d["test"], np.union1d(d["A"], d["B"])).size
        for a in "AB":
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, d[a].astype(np.int64))
        with open(SPL / f"r10_seed{s}_test.npy", "xb") as f:
            np.save(f, d["test"].astype(np.int64))
        with open(SPL / f"r10_seed{s}_w0.json", "x", encoding="utf-8") as f:
            json.dump({"seed": s, "omega": OMEGA, "targets": {"A": F, "B": G}, "share_A_F": ov.share(d["A"], F),
                       "share_B_G": ov.share(d["B"], G), "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(man: dict, s: int) -> str | None:
    F, G, d = build(s)
    meta_f = SPL / f"r10_seed{s}_w0.json"
    files = {"A": SPL / f"{stem(s, 'A')}.npy", "B": SPL / f"{stem(s, 'B')}.npy", "test": SPL / f"r10_seed{s}_test.npy"}
    if not meta_f.exists() or not all(f.exists() for f in files.values()):
        return f"seed {s}: split file missing"
    meta = json.loads(meta_f.read_text(encoding="utf-8"))
    if not all(np.array_equal(np.load(f), d[k].astype(np.int64)) for k, f in files.items()) or meta.get("targets") != {"A": F, "B": G}:
        return f"seed {s}: splits differ from the deterministic rebuild"
    return None


def cell_flags(cell: dict) -> str:
    return ((f" --lr-scale {cell['c']:g}" if cell["c"] != 1.0 else "")
            + (f" --pre-switch-betas {cell['psb'][0]},{cell['psb'][1]}" if cell["psb"] else "")
            + (f" --pre-switch-grad-every {cell['k']}" if cell["k"] != 1 else ""))


def trainer_jobs(man: dict) -> list[str]:
    pure, switch, bud = [], [], man["budget"]
    for s in man["seeds"]:
        base = (f"{c1.interp(man)} {FB} --seed {s} --condition baseline --threads {man['threads']} --device {man['device']} "
                f"--test-file lab/confirm/r10_splits/r10_seed{s}_test.npy --out-root lab/confirm/r10_raw")
        a, b = (f"lab/confirm/r10_splits/{stem(s, x)}.npy" for x in "AB")
        for first in (a, b):
            pure.append(f"{base} --steps {bud} --split-file {first} --spectra-at 50,250,{bud}")
        for cell in man["cells"].values():
            t = cell["t"]
            for first, second in ((a, b), (b, a)):
                switch.append(f"{base} --steps {t + bud} --split-file {first} --switch-split-file {second} --switch-step {t} "
                              f"--spectra-at {t},{t + 250},{t + bud}{cell_flags(cell)}")
    return pure + switch


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban ids: EXP-018 (split file) or EXP-020 (switch), then _lrs (':g'), _psb (repr), _ge (int), then _dev."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    if g("--switch-split-file") is None:
        rid = f"EXP-018_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}"
    else:
        rid = (f"EXP-020_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}_to_"
               f"{Path(g('--switch-split-file')).stem}_at{g('--switch-step')}")
    if g("--lr-scale") is not None and float(g("--lr-scale")) != 1.0:
        rid += f"_lrs{float(g('--lr-scale')):g}"
    if g("--pre-switch-betas") is not None:
        b1, b2 = (float(x) for x in g("--pre-switch-betas").split(","))
        rid += f"_psb{b1!r}_{b2!r}"
    if g("--pre-switch-grad-every") is not None and int(g("--pre-switch-grad-every")) != 1:
        rid += f"_ge{int(g('--pre-switch-grad-every'))}"
    dev = g("--device") or "cpu"
    return rid + ("" if dev == "cpu" else f"_dev{dev.replace(':', '')}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r10", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_r10.py")


# ---------------------------------------------------------------- analysis
_e56 = None


def e56():
    global _e56
    if _e56 is None:
        spec = importlib.util.spec_from_file_location("exp056", LAB / "experiments/EXP-056-overlap-persistence/analyze.py")
        _e56 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_e56)
    return _e56


def one_run(man: dict, s: int, first: str, second: str | None, cell: str | None) -> tuple | str:
    """Group power of W_E at the end, and W_E at the switch and at step 0, of one run through the shared loader + R10 binding."""
    spec = man["cells"][cell] if cell else {"c": 1.0, "t": 0, "psb": None, "k": 1}
    t = spec["t"]
    sp, te = SPL / f"{stem(s, first)}.npy", SPL / f"r10_seed{s}_test.npy"
    sw = SPL / f"{stem(s, second)}.npy" if second else None
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--split-file", str(sp)]
    if second:
        cmd += ["--switch-split-file", str(sw), "--switch-step", str(t)]
        cmd += ["--lr-scale", f"{spec['c']:g}"] if spec["c"] != 1.0 else []
        cmd += ["--pre-switch-betas", f"{spec['psb'][0]},{spec['psb'][1]}"] if spec["psb"] else []
        cmd += ["--pre-switch-grad-every", str(spec["k"])] if spec["k"] != 1 else []
    d, steps, tag = run_dir(cmd), man["budget"] + (t if second else 0), f"{cell or 'pure'}:{first}{second or ''}"
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=steps, split_file=sp, test_file=te, switch_file=sw,
                           config={"p": P, "task": "add", "arch": "transformer", "lr": 1e-3, "weight_decay": 1.0, "train_frac": 0.3,
                                   "beta1": 0.9, "beta2": 0.98, "lr_scale": spec["c"], "pre_switch_betas": spec["psb"]},
                           snapshots_at=(steps,) + ((t, 0) if second else ())))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(sp):
        return f"{tag}: defekt after load: {why or 'split bytes differ'}"
    if second and (L.res.get("switch_step") != t or int(L.res.get("lr_scale_until", -1)) < t):
        return f"{tag}: defekt: switch_step/lr_scale_until do not match the cell"
    if spec["psb"] and L.res.get("events", {}).get("pre_switch_betas", {}).get("check") is not True:
        return f"{tag}: defekt: beta switch not recorded"
    if second:
        ev = L.res.get("events", {}).get("pre_switch_grad_every")
        if spec["k"] != 1 and (L.res.get("pre_switch_grad_every") != spec["k"] or not ev or ev.get("k") != spec["k"]
                               or ev.get("eval_steps_pre_switch") != list(range(1, t + 1, spec["k"]))):
            return f"{tag}: defekt: gradient schedule not recorded as k = {spec['k']}"
        if spec["k"] == 1 and (L.res.get("pre_switch_grad_every", 1) != 1 or ev is not None):
            return f"{tag}: defekt: unexpected gradient schedule"
    try:
        gp = lambda st: e56()._a43.group_power(L.snapshot(st), "add", P)[0]   # noqa: E731
        end = gp(steps)
        at = (L.snapshot(t), L.snapshot(0)) if second else None
    except Exception as ex:   # any load/transform failure is technical, never an abort
        return f"{tag}: defekt: {type(ex).__name__}: {ex}"
    if not np.isfinite(end).all() or (at is not None and not all(np.isfinite(x).all() for x in at)):
        return f"{tag}: defekt: non-finite values"
    return end, at


def selectivity(W_t: np.ndarray, W_0: np.ndarray, F: list[int]) -> tuple[float, float]:
    """Share of the displacement's group power on the targets F, and the displacement norm (rows 0..p-1); as EXP-092."""
    pw = e56()._a43.group_power(W_t - W_0, "add", P)[0]
    return float(pw[[k - 1 for k in F]].sum() / pw.sum()), float(np.linalg.norm((W_t - W_0)[:P]))


def seed_row(man: dict, s: int) -> dict:
    meta = json.loads((SPL / f"r10_seed{s}_w0.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    pure = {k: one_run(man, s, k, None, None) for k in "AB"}
    sw = {(c, k): one_run(man, s, k[0], k[1], c) for c in man["cells"] for k in ("AB", "BA")}
    bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
    if bad:
        return {"seed": s, "valid": False, "technical": True, "reason": "; ".join(bad[:4])}
    lr = lambda pw: e56().logratio(pw, F, G)   # noqa: E731
    LA, LB = lr(pure["A"][0]), lr(pure["B"][0])
    r: dict = {"seed": s, "technical": False, "LA_minus_LB": LA - LB, "valid": bool(LA - LB >= MIN_LALB)}
    if not r["valid"]:
        return r
    for c in man["cells"]:
        L = {"A": LA, "B": LB, "AB": lr(sw[(c, "AB")][0]), "BA": lr(sw[(c, "BA")][0])}
        r[f"pi_{c}"] = e56().pi_of(L)["pi"]
        fa, na = selectivity(*sw[(c, "AB")][1], F)
        fb, nb = selectivity(*sw[(c, "BA")][1], G)
        r[f"fsel_{c}"], r[f"dnorm_{c}"] = (fa + fb) / 2, (na + nb) / 2
    return r


def stats(rows: list[dict]) -> dict[str, np.ndarray]:
    col = lambda k: np.array([r[k] for r in rows])   # noqa: E731
    return {"e8": col("pi_n24") - col("pi_g8"), "r8": col("pi_g8") - col("pi_c8b"), "e24": col("pi_n24") - col("pi_g24"),
            "e24_minus_e8": col("pi_g8") - col("pi_g24")}


def test_family(rows: list[dict], rng: np.random.Generator) -> dict:
    X = stats(rows)
    p = {"H1": c1.t_test_secondary(X["e8"])["p_one_sided"],
         "H2": max(c1.t_test_secondary(X["r8"] + EQ)["p_one_sided"], c1.t_test_secondary(EQ - X["r8"])["p_one_sided"]),
         "H3": c1.t_test_secondary(X["e24"])["p_one_sided"]}
    ph = c1.holm(p)
    ci = {k: c1.boot_ci(X[k], rng) for k in X}
    ok = {"H1": ph["H1"] < ALPHA and ci["e8"][0] > 0, "H2": ph["H2"] < ALPHA, "H3": ph["H3"] < ALPHA and ci["e24"][0] > 0}
    out = {h: {"statistic": s, "mean": float(X[s].mean()), "sd": float(X[s].std(ddof=1)), "ci95": ci[s],
               "n_positive": int((X[s] > 0).sum()), "p": p[h], "p_holm": ph[h], "verdict": "bestätigt" if ok[h] else "nicht bestätigt"}
           for h, s in (("H1", "e8"), ("H2", "r8"), ("H3", "e24"))}
    out["e24_minus_e8_descriptive"] = {"mean": float(X["e24_minus_e8"].mean()), "ci95": ci["e24_minus_e8"]}
    return out


def verdict(rows: list[dict], n_planned: int, rng: np.random.Generator) -> dict:
    n_tech = sum(1 for r in rows if r.get("technical"))
    ok = [r for r in rows if r.get("valid")]
    n_excl = len(rows) - n_tech - len(ok)
    if n_tech > 0 or len(rows) != n_planned or n_excl > MAX_EXCLUDED or len(ok) < 3:
        return {"n": len(rows), "n_technical": n_tech, "n_excluded": n_excl, "verdict": "nicht auswertbar"}
    out = {"n": len(ok), "n_technical": 0, "n_excluded": n_excl, **test_family(ok, rng)}
    conf = [h for h in HYP if out[h]["verdict"] == "bestätigt"]
    out["reading"] = ("Auswertungen-Befund bestätigt (H1, H2, H3)" if len(conf) == len(HYP)
                      else ("teilweise: " + ", ".join(conf)) if conf else "nicht bestätigt")
    out["cell_means"] = {k: {c: float(np.mean([r[f"{k}_{c}"] for r in ok])) for c in CELLS} for k in ("pi", "fsel", "dnorm")}
    return out


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "R10_summary.json"
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(man, s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"R10 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [seed_row(man, s) for s in man["seeds"]]
    out = {"manifest_commit": man["commit"], "n_planned": len(man["seeds"]),
           "hypotheses": verdict(rows, len(man["seeds"]), np.random.default_rng(10)), "rows": rows}
    (LAB / "confirm" / "R10_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    assert all(v["t"] < LR_SCALE_UNTIL and v["c"] * v["t"] == 24 and v["t"] % v["k"] == 0 for v in CELLS.values())
    for k, v in CELLS.items():                      # beta' = 1 - c (1 - beta) where given (first-order window matching)
        if v["psb"]:
            assert abs(v["psb"][0] - (1 - v["c"] * 0.1)) < 1e-12 and abs(v["psb"][1] - (1 - v["c"] * 0.02)) < 1e-12, k
    for bad in ({"seeds": list(range(3500, 3547))}, {"budget": 2000.0}, {"threads": True},
                {"cells": {k: v for k, v in CELLS.items() if k != "g24"}},
                {"cells": {**CELLS, "g8": {"c": 1.0, "t": 24, "psb": None, "k": 4}}}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    assert len(tj) == 48 * 10 and len(set(tj)) == len(tj) and all("r10_raw" in j and "\\" not in j for j in tj)
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert len(set(ids)) == len(ids)
    assert ids[0] == "EXP-018_baseline_seed3500_thr1_r10_seed3500_w0_A_devcuda", ids[0]
    g8 = [i for i in ids if i.endswith("_ge8_devcuda")]
    assert len(g8) == 96 and g8[0] == "EXP-020_baseline_seed3500_thr1_r10_seed3500_w0_A_to_r10_seed3500_w0_B_at24_ge8_devcuda", g8[0]
    assert sum(i.endswith("_at24_ge24_devcuda") for i in ids) == 96
    c8b = [i for i in ids if "_at3_" in i]
    assert len(c8b) == 96 and c8b[0].endswith("_at3_lrs8_psb0.2_0.84_devcuda"), c8b[0]
    assert all(j.startswith("python lab/tools/confirm_r10.py --run M -- ") for j in BLOCK.jobs(man, "M"))
    BLOCK.check_job(man, shlex.split(tj[0]))
    for foreign in (shlex.split(tj[0]) + ["--force"], [x if x != "3500" else "3501" for x in shlex.split(tj[0])]):
        try:
            BLOCK.check_job(man, foreign)
            raise AssertionError("foreign command accepted")
        except SystemExit:
            pass

    def mk(e8=0.14, r8=0.0, e24=0.19, n=0.0, valid=True):
        base = 0.28 + n
        return {"valid": valid, "technical": False, "pi_n24": base, "pi_g8": base - e8, "pi_c8b": base - e8 - r8, "pi_g24": base - e24,
                **{f"{k}_{c}": 0.1 for k in ("fsel", "dnorm") for c in CELLS}}
    rng = np.random.default_rng(0)
    jit = lambda i: 0.01 * ((i * 7) % 5 - 2)   # noqa: E731
    yes = [mk(e8=0.14 + jit(i), r8=jit(i + 1), e24=0.19 + jit(i + 2), n=jit(i + 3)) for i in range(48)]
    v = verdict(yes, 48, rng)
    assert all(v[h]["verdict"] == "bestätigt" for h in HYP) and v["reading"].startswith("Auswertungen-Befund bestätigt"), v
    no = [mk(e8=jit(i), r8=0.14 + jit(i + 1), e24=jit(i + 2)) for i in range(48)]
    v = verdict(no, 48, rng)
    assert all(v[h]["verdict"] == "nicht bestätigt" for h in HYP) and v["reading"] == "nicht bestätigt", v
    part = [mk(e8=0.14 + jit(i), r8=0.14 + jit(i + 1), e24=jit(i + 2)) for i in range(48)]
    assert verdict(part, 48, rng)["reading"] == "teilweise: H1"
    neg = [mk(e8=0.14 + jit(i), r8=-0.14 + jit(i + 1), e24=0.19 + jit(i + 2)) for i in range(48)]      # TOST fails below
    assert verdict(neg, 48, rng)["H2"]["verdict"] == "nicht bestätigt"
    wide = [mk(e8=0.14 + jit(i), r8=25 * jit(i + 1), e24=0.19 + jit(i + 2)) for i in range(48)]     # mean ~0, SD ~0.35
    assert abs(np.mean([r["pi_g8"] - r["pi_c8b"] for r in wide])) < 0.05 and verdict(wide, 48, rng)["H2"]["verdict"] == "nicht bestätigt"
    assert verdict(yes[:47], 48, rng)["verdict"] == "nicht auswertbar"
    assert verdict(yes[:47] + [{"seed": 1, "valid": False, "technical": True}], 48, rng)["verdict"] == "nicht auswertbar"
    assert verdict(yes[:39] + [{**yes[0], "valid": False}] * 9, 48, rng)["verdict"] == "nicht auswertbar"
    assert verdict(yes[:40] + [{**yes[0], "valid": False}] * 8, 48, rng)["n_excluded"] == 8
    F, G = ov.targets(3500)
    assert not set(F) & set(G) and len(F) == len(G) == 5
    selftest_binding(BLOCK, tj[0], tj[2], tj[3])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    src = (ROOT / FB).read_text(encoding="utf-8")
    assert f"LR_SCALE_UNTIL = {LR_SCALE_UNTIL}" in src and "on_first = switch_idx is None or step <= a.switch_step" in src
    assert 'run_id += f"_psb{psb[0]!r}_{psb[1]!r}"' in src and 'run_id += f"_ge{gek}"' in src
    e56()
    loaded = {Path(m.__file__).resolve().relative_to(ROOT.resolve()).as_posix() for m in list(sys.modules.values())
              if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to((ROOT / "lab").resolve())}
    assert loaded <= set(CODE_FILES), sorted(loaded - set(CODE_FILES))
    print("[confirm_r10] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
