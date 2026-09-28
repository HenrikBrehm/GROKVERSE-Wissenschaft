"""R9 confirmation (FINDINGS 'largest open question'; pilots EXP-089/090/091): does the early lock-in follow the summed learning rate
once Adam's EMA windows are also measured in summed learning rate? Session 40, UNTESTED BEYOND --selftest.

Registration: lab/confirm/R9_REGISTRATION_DRAFT.md. Protocol as EXP-090 (omega = 0 EXP-053 splits built from the seed, both switch
directions A->B and B->A at t, then BUDGET = 2000 steps at the default lr and betas; pi = persistence of the old choice in the log energy
ratio of the final W_E group power, against the pure A/B runs of the seed, EXP-056 definition). Pre-switch history per cell:
  n25   : default,                       t = 25                  (Lambda = 25)
  n30   : default,                       t = 30                  (Lambda = 30)
  l100  : --lr-scale 0.25,               t = 100                 (Lambda = 25, windows 4x shorter in Lambda)
  l100b : --lr-scale 0.25, --pre-switch-betas 0.975,0.995, t = 100 (windows equal in Lambda to n25)
  c2    : --lr-scale 2,                  t = 15                  (Lambda = 30, windows 2x longer in Lambda)
  c2b   : --lr-scale 2, --pre-switch-betas 0.8,0.96, t = 15     (windows equal in Lambda to n30)
Primary family (Holm over 3, alpha 0.05):
  H1  e1 = pi(l100) - pi(l100b); one-sided t-test of e1 > 0; 'bestätigt' = Holm p < 0.05 and bootstrap CI lower bound of e1 > 0
      (Fassung 2 after the pre-freeze review: the 0.05 margin had power ~0.12 at half the pilot effect; 0.05 is reported descriptively)
  H2  d1 = pi(l100b) - pi(n25) inside +-0.1; TOST p = max of the two one-sided t-test p; 'bestätigt' = Holm p < 0.05
  H3  e2 = pi(c2b) - pi(c2); one-sided t-test of e2 > 0; 'bestätigt' = Holm p < 0.05 and bootstrap CI lower bound of e2 > 0
Descriptive: d2 = pi(c2b) - pi(n30); separation at the switch (counter-free reading, EXP-090 Nachtrag a).
Validity: any technical failure -> 'nicht auswertbar'. Seeds with L(A) - L(B) < 2 are excluded and counted; more than 6 -> 'nicht auswertbar'.

  python lab/tools/confirm_r9.py --hash-code | --splits M | --jobs M | --run M -- <cmd> | --analyze M | --selftest
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

RAW = LAB / "confirm" / "r9_raw"
BIND = LAB / "confirm" / "r9_bindings"
SPL = LAB / "confirm" / "r9_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"
BUDGET, ALPHA, OMEGA, P = 2000, 0.05, 0.0, 113
MIN_E1, EQ, MIN_LALB, MAX_EXCLUDED = 0.0, 0.1, 2.0, 6
LR_SCALE_UNTIL = 250
CELLS = {"n25": {"c": 1.0, "t": 25, "psb": None}, "n30": {"c": 1.0, "t": 30, "psb": None},
         "l100": {"c": 0.25, "t": 100, "psb": None}, "l100b": {"c": 0.25, "t": 100, "psb": [0.975, 0.995]},
         "c2": {"c": 2.0, "t": 15, "psb": None}, "c2b": {"c": 2.0, "t": 15, "psb": [0.8, 0.96]}}
HYP = ("H1", "H2", "H3")
REGISTERED = {"seeds": list(range(3300, 3336)), "budget": 2000, "device": "cuda", "threads": 1,
              "cells": {k: dict(v) for k, v in CELLS.items()}}
CODE_FILES = ("lab/tools/confirm_r9.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_p2.py",
              "lab/tools/confirm_splits.py", "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py",
              "lab/experiments/EXP-001-freq-ban/freq_ban.py",
              "lab/experiments/EXP-053-p3-overlap-design/overlap_split.py", "lab/experiments/EXP-053-p3-overlap-design/calibration.json",
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py",
              "lab/experiments/EXP-056-overlap-persistence/analyze.py", "lab/experiments/EXP-056-overlap-persistence/make_splits.py")


# ---------------------------------------------------------------- splits and jobs
def stem(s: int, arm: str) -> str:
    return f"r9_seed{s}_w0_{arm}"


def build(s: int) -> tuple[list[int], list[int], dict]:
    eps = json.loads(CAL.read_text(encoding="utf-8"))["levels"][str(OMEGA)]["eps"]
    F, G = ov.targets(s)
    return F, G, ov.build(s, OMEGA, eps)


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, a)}.npy" for s in man["seeds"] for a in "AB"] + [f"r9_seed{s}_test.npy" for s in man["seeds"]]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("R9 splits exist already: never overwrite")
    for s in man["seeds"]:
        F, G, d = build(s)
        assert len(d["A"]) == len(d["B"]) == ov.N_TRAIN and not np.intersect1d(d["A"], d["B"]).size
        assert not np.intersect1d(d["test"], np.union1d(d["A"], d["B"])).size
        for a in "AB":
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, d[a].astype(np.int64))
        with open(SPL / f"r9_seed{s}_test.npy", "xb") as f:
            np.save(f, d["test"].astype(np.int64))
        with open(SPL / f"r9_seed{s}_w0.json", "x", encoding="utf-8") as f:
            json.dump({"seed": s, "omega": OMEGA, "targets": {"A": F, "B": G}, "share_A_F": ov.share(d["A"], F),
                       "share_B_G": ov.share(d["B"], G), "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(man: dict, s: int) -> str | None:
    F, G, d = build(s)
    meta_f = SPL / f"r9_seed{s}_w0.json"
    files = {"A": SPL / f"{stem(s, 'A')}.npy", "B": SPL / f"{stem(s, 'B')}.npy", "test": SPL / f"r9_seed{s}_test.npy"}
    if not meta_f.exists() or not all(f.exists() for f in files.values()):
        return f"seed {s}: split file missing"
    meta = json.loads(meta_f.read_text(encoding="utf-8"))
    if not all(np.array_equal(np.load(f), d[k].astype(np.int64)) for k, f in files.items()) or meta.get("targets") != {"A": F, "B": G}:
        return f"seed {s}: splits differ from the deterministic rebuild"
    return None


def cell_flags(cell: dict) -> str:
    return ((f" --lr-scale {cell['c']:g}" if cell["c"] != 1.0 else "")
            + (f" --pre-switch-betas {cell['psb'][0]},{cell['psb'][1]}" if cell["psb"] else ""))


def trainer_jobs(man: dict) -> list[str]:
    pure, switch, bud = [], [], man["budget"]
    for s in man["seeds"]:
        base = (f"{c1.interp(man)} {FB} --seed {s} --condition baseline --threads {man['threads']} --device {man['device']} "
                f"--test-file lab/confirm/r9_splits/r9_seed{s}_test.npy --out-root lab/confirm/r9_raw")
        a, b = (f"lab/confirm/r9_splits/{stem(s, x)}.npy" for x in "AB")
        for first in (a, b):
            pure.append(f"{base} --steps {bud} --split-file {first} --spectra-at 50,250,{bud}")
        for cell in man["cells"].values():
            t = cell["t"]
            for first, second in ((a, b), (b, a)):
                switch.append(f"{base} --steps {t + bud} --split-file {first} --switch-split-file {second} --switch-step {t} "
                              f"--spectra-at {t},{t + 250},{t + bud}{cell_flags(cell)}")
    return pure + switch


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban ids: EXP-018 (split file) or EXP-020 (switch), then _lrs (':g'), then _psb (repr), then _dev."""
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
    dev = g("--device") or "cpu"
    return rid + ("" if dev == "cpu" else f"_dev{dev.replace(':', '')}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r9", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_r9.py")


# ---------------------------------------------------------------- analysis
_e56 = None


def e56():
    global _e56
    if _e56 is None:
        spec = importlib.util.spec_from_file_location("exp056", LAB / "experiments/EXP-056-overlap-persistence/analyze.py")
        _e56 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_e56)
    return _e56


def one_run(man: dict, s: int, first: str, second: str | None, cell: str | None) -> tuple[np.ndarray, np.ndarray | None] | str:
    """Group power of W_E at the end (and at the switch) of one run through the shared loader + R9 binding (unbound before/after)."""
    spec = man["cells"][cell] if cell else {"c": 1.0, "t": 0, "psb": None}
    t = spec["t"]
    sp, te = SPL / f"{stem(s, first)}.npy", SPL / f"r9_seed{s}_test.npy"
    sw = SPL / f"{stem(s, second)}.npy" if second else None
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--split-file", str(sp)]
    if second:
        cmd += ["--switch-split-file", str(sw), "--switch-step", str(t)]
        cmd += ["--lr-scale", f"{spec['c']:g}"] if spec["c"] != 1.0 else []
        cmd += ["--pre-switch-betas", f"{spec['psb'][0]},{spec['psb'][1]}"] if spec["psb"] else []
    d, steps, tag = run_dir(cmd), man["budget"] + (t if second else 0), f"{cell or 'pure'}:{first}{second or ''}"
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=steps, split_file=sp, test_file=te, switch_file=sw,
                           config={"p": P, "task": "add", "arch": "transformer", "lr": 1e-3, "weight_decay": 1.0, "train_frac": 0.3,
                                   "beta1": 0.9, "beta2": 0.98, "lr_scale": spec["c"], "pre_switch_betas": spec["psb"]},
                           snapshots_at=(steps,) + ((t,) if second else ())))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(sp):
        return f"{tag}: defekt after load: {why or 'split bytes differ'}"
    if second and (L.res.get("switch_step") != t or int(L.res.get("lr_scale_until", -1)) < t):
        return f"{tag}: defekt: switch_step/lr_scale_until do not match the cell"
    if spec["psb"] and L.res.get("events", {}).get("pre_switch_betas", {}).get("check") is not True:
        return f"{tag}: defekt: beta switch not recorded"
    try:
        gp = lambda st: e56()._a43.group_power(L.snapshot(st), "add", P)[0]   # noqa: E731
        end, at = gp(steps), (gp(t) if second else None)
    except Exception as ex:   # any load/transform failure is technical, never an abort
        return f"{tag}: defekt: {type(ex).__name__}: {ex}"
    if not np.isfinite(end).all() or (at is not None and not np.isfinite(at).all()):
        return f"{tag}: defekt: non-finite group power"
    return end, at


def seed_row(man: dict, s: int) -> dict:
    meta = json.loads((SPL / f"r9_seed{s}_w0.json").read_text(encoding="utf-8"))
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
        r[f"sep_{c}"] = (lr(sw[(c, "AB")][1]) - lr(sw[(c, "BA")][1])) / (LA - LB)
    return r


def stats(rows: list[dict]) -> dict[str, np.ndarray]:
    col = lambda k: np.array([r[k] for r in rows])   # noqa: E731
    return {"e1": col("pi_l100") - col("pi_l100b"), "d1": col("pi_l100b") - col("pi_n25"),
            "e2": col("pi_c2b") - col("pi_c2"), "d2": col("pi_c2b") - col("pi_n30")}


def test_family(rows: list[dict], rng: np.random.Generator) -> dict:
    X = stats(rows)
    p = {"H1": c1.t_test_secondary(X["e1"] - MIN_E1)["p_one_sided"],
         "H2": max(c1.t_test_secondary(X["d1"] + EQ)["p_one_sided"], c1.t_test_secondary(EQ - X["d1"])["p_one_sided"]),
         "H3": c1.t_test_secondary(X["e2"])["p_one_sided"]}
    ph = c1.holm(p)
    ci = {k: c1.boot_ci(X[k], rng) for k in ("e1", "d1", "e2", "d2")}
    ok = {"H1": ph["H1"] < ALPHA and ci["e1"][0] > MIN_E1, "H2": ph["H2"] < ALPHA, "H3": ph["H3"] < ALPHA and ci["e2"][0] > 0}
    out = {h: {"statistic": s, "mean": float(X[s].mean()), "sd": float(X[s].std(ddof=1)), "ci95": ci[s],
               "n_positive": int((X[s] > 0).sum()), "p": p[h], "p_holm": ph[h], "verdict": "bestätigt" if ok[h] else "nicht bestätigt"}
           for h, s in (("H1", "e1"), ("H2", "d1"), ("H3", "e2"))}
    out["d2_descriptive"] = {"mean": float(X["d2"].mean()), "ci95": ci["d2"]}
    out["e1_above_0p05_descriptive"] = bool(ci["e1"][0] > 0.05)
    return out


def verdict(rows: list[dict], n_planned: int, rng: np.random.Generator) -> dict:
    n_tech = sum(1 for r in rows if r.get("technical"))
    ok = [r for r in rows if r.get("valid")]
    n_excl = len(rows) - n_tech - len(ok)
    if n_tech > 0 or len(rows) != n_planned or n_excl > MAX_EXCLUDED or len(ok) < 3:
        return {"n": len(rows), "n_technical": n_tech, "n_excluded": n_excl, "verdict": "nicht auswertbar"}
    out = {"n": len(ok), "n_technical": 0, "n_excluded": n_excl, **test_family(ok, rng)}
    conf = [h for h in HYP if out[h]["verdict"] == "bestätigt"]
    out["reading"] = ("Fenster-Regel bestätigt (H1, H2, H3)" if len(conf) == len(HYP)
                      else ("teilweise: " + ", ".join(conf)) if conf else "nicht bestätigt")
    sm = {c: float(np.mean([r[f"sep_{c}"] for r in ok])) for c in CELLS}
    den = sm["l100"] - sm["n25"]
    out["sep_means"], out["r_sep_c025"] = sm, (float((sm["l100b"] - sm["n25"]) / den) if den != 0 else None)
    return out


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "R9_summary.json"
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(man, s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"R9 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [seed_row(man, s) for s in man["seeds"]]
    out = {"manifest_commit": man["commit"], "n_planned": len(man["seeds"]),
           "hypotheses": verdict(rows, len(man["seeds"]), np.random.default_rng(9)), "rows": rows}
    (LAB / "confirm" / "R9_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    assert all(v["t"] < LR_SCALE_UNTIL for v in CELLS.values())
    for k, v in CELLS.items():                      # beta' = 1 - c (1 - beta) where given (first-order window matching)
        if v["psb"]:
            assert abs(v["psb"][0] - (1 - v["c"] * 0.1)) < 1e-12 and abs(v["psb"][1] - (1 - v["c"] * 0.02)) < 1e-12, k
    for bad in ({"seeds": list(range(3300, 3335))}, {"budget": 2000.0}, {"threads": True},
                {"cells": {k: v for k, v in CELLS.items() if k != "c2b"}},
                {"cells": {**CELLS, "l100b": {"c": 0.25, "t": 100, "psb": [0.97, 0.995]}}}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    assert len(tj) == 36 * 14 and len(set(tj)) == len(tj) and all("r9_raw" in j and "\\" not in j for j in tj)
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert len(set(ids)) == len(ids)
    assert ids[0] == "EXP-018_baseline_seed3300_thr1_r9_seed3300_w0_A_devcuda", ids[0]
    l100b = [i for i in ids if "_at100_" in i and "psb" in i]
    assert l100b[0] == "EXP-020_baseline_seed3300_thr1_r9_seed3300_w0_A_to_r9_seed3300_w0_B_at100_lrs0.25_psb0.975_0.995_devcuda", l100b[0]
    c2b = [i for i in ids if "_at15_" in i and "psb" in i]
    assert c2b[0].endswith("_at15_lrs2_psb0.8_0.96_devcuda"), c2b[0]
    assert all(j.startswith("python lab/tools/confirm_r9.py --run M -- ") for j in BLOCK.jobs(man, "M"))
    BLOCK.check_job(man, shlex.split(tj[0]))
    for foreign in (shlex.split(tj[0]) + ["--force"], [x if x != "3300" else "3301" for x in shlex.split(tj[0])]):
        try:
            BLOCK.check_job(man, foreign)
            raise AssertionError("foreign command accepted")
        except SystemExit:
            pass

    def mk(e1=0.16, d1=0.0, e2=0.05, n=0.0, valid=True):
        base = 0.33 + n
        return {"valid": valid, "technical": False, "pi_n25": base, "pi_n30": base + 0.1, "pi_l100b": base + d1, "pi_l100": base + d1 + e1,
                "pi_c2": base + 0.05, "pi_c2b": base + 0.05 + e2, **{f"sep_{c}": 0.04 for c in CELLS}}
    rng = np.random.default_rng(0)
    jit = lambda i: 0.01 * ((i * 7) % 5 - 2)   # noqa: E731
    yes = [mk(e1=0.16 + jit(i), d1=jit(i + 1), e2=0.05 + jit(i + 2), n=jit(i + 3)) for i in range(36)]
    v = verdict(yes, 36, rng)
    assert all(v[h]["verdict"] == "bestätigt" for h in HYP) and v["reading"].startswith("Fenster-Regel bestätigt"), v
    no = [mk(e1=jit(i), d1=0.16 + jit(i + 1), e2=jit(i + 2)) for i in range(36)]
    v = verdict(no, 36, rng)
    assert all(v[h]["verdict"] == "nicht bestätigt" for h in HYP) and v["reading"] == "nicht bestätigt", v
    part = [mk(e1=0.16 + jit(i), d1=0.16 + jit(i + 1), e2=jit(i + 2)) for i in range(36)]
    assert verdict(part, 36, rng)["reading"] == "teilweise: H1"
    assert verdict(yes[:35], 36, rng)["verdict"] == "nicht auswertbar"
    assert verdict(yes[:35] + [{"seed": 1, "valid": False, "technical": True}], 36, rng)["verdict"] == "nicht auswertbar"
    assert verdict(yes[:29] + [{**yes[0], "valid": False}] * 7, 36, rng)["verdict"] == "nicht auswertbar"
    assert verdict(yes[:30] + [{**yes[0], "valid": False}] * 6, 36, rng)["n_excluded"] == 6
    F, G = ov.targets(3300)
    assert not set(F) & set(G) and len(F) == len(G) == 5
    selftest_binding(BLOCK, tj[0], tj[2], tj[3])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    src = (ROOT / FB).read_text(encoding="utf-8")
    assert f"LR_SCALE_UNTIL = {LR_SCALE_UNTIL}" in src and "on_first = switch_idx is None or step <= a.switch_step" in src
    assert 'run_id += f"_psb{psb[0]!r}_{psb[1]!r}"' in src
    e56()
    loaded = {Path(m.__file__).resolve().relative_to(ROOT.resolve()).as_posix() for m in list(sys.modules.values())
              if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to((ROOT / "lab").resolve())}
    assert loaded <= set(CODE_FILES), sorted(loaded - set(CODE_FILES))
    print("[confirm_r9] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
