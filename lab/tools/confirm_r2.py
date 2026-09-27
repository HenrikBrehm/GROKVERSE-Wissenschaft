"""R2 confirmation (rule 19a robustness of K4c): does the N29 transition (switch early, hold at 50) survive lr 2e-3 and wd 0.3? Session 26, UNTESTED.

Registration: lab/confirm/R2_REGISTRATION_DRAFT.md. Protocol exactly as N29 (confirm_n29.py: omega = 0 EXP-053 splits, both directions,
BUDGET = 4000 steps after the switch, --stop-after-gen >= steps, --save-model, W_E[:113] projected off the old / new targets, accuracy on
the held-out test set of the seed), with ONE hyperparameter changed per cell:
  cell lr2  : --lr 0.002             switch times t in {12, 25, 50}
  cell wd03 : --weight-decay 0.3     switch times t in {25, 50}
Primary family (Holm over 4, one-sided t-test, 95 % bootstrap CI, "bestätigt" = Holm p < 0.05 and CI lower bound >= 0):
  H1_lr2  : (acc_new(50) - acc_old(50)) - MIN_DIFF > 0      hold at 50
  H2_lr2  : (acc_old(12) - acc_new(12)) - MIN_DIFF > 0      switch at 12
  H1_wd03 : (acc_new(50) - acc_old(50)) - MIN_DIFF > 0
  H2_wd03 : (acc_old(25) - acc_new(25)) - MIN_DIFF > 0
Secondary, no verdict (timing, EXP-039 'unklar'): lr2 at t = 25, D25 = acc_new(25) - acc_old(25), mean + CI with a pre-stated reading.
Primary sample: ALL seeds (as N29, Codex s23); any technical failure -> "nicht auswertbar".

  python lab/tools/confirm_r2.py --hash-code | --splits M | --jobs M | --run M -- <cmd> | --analyze M | --selftest
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
sys.path.insert(0, str(LAB / "experiments/EXP-053-p3-overlap-design"))
import confirm_p1 as c1  # noqa: E402  (read-only reuse: interp, t-test, bootstrap, holm)
import confirm_p2 as p2  # noqa: E402  (read-only reuse: EXP-055 evaluate, load_model_bytes)
from bound_block import Block, selftest_binding, sha  # noqa: E402
import overlap_split as ov  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "r2_raw"
BIND = LAB / "confirm" / "r2_bindings"
SPL = LAB / "confirm" / "r2_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"
BUDGET, ALPHA, OMEGA, ACC_MIN, MIN_DIFF, P = 4000, 0.05, 0.0, 0.9, 0.3, 113
LR0, WD0, FRAC0 = 1e-3, 1.0, 0.3                                     # preset values (arch25k), checked in every result.json
CELLS = {"lr2": {"hp": {"lr": 0.002}, "ts": [12, 25, 50]},
         "wd03": {"hp": {"weight_decay": 0.3}, "ts": [25, 50]}}
FLAG = {"lr": "--lr", "weight_decay": "--weight-decay"}
TAG = {"lr": "lr", "weight_decay": "wd"}
PRIMARY = {"H1_lr2": ("lr2", 50, "hold"), "H2_lr2": ("lr2", 12, "switch"),
           "H1_wd03": ("wd03", 50, "hold"), "H2_wd03": ("wd03", 25, "switch")}
REGISTERED = {"seeds": list(range(2510, 2540)), "budget": 4000, "device": "cuda", "threads": 1,
              "cells": {c: {"hp": v["hp"], "ts": v["ts"]} for c, v in CELLS.items()}}
CODE_FILES = ("lab/tools/confirm_r2.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_p2.py",
              "lab/tools/confirm_splits.py", "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py",
              "lab/experiments/EXP-001-freq-ban/freq_ban.py",
              "lab/experiments/EXP-053-p3-overlap-design/overlap_split.py", "lab/experiments/EXP-053-p3-overlap-design/calibration.json",
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py",
              "lab/experiments/EXP-051-functional-ablation/analyze.py", "lab/experiments/EXP-055-ablation-dose/analyze.py",
              "lab/experiments/EXP-061-grad-alignment/analyze.py", "lab/experiments/EXP-059-momentum-exposure/analyze.py",
              "lab/experiments/EXP-056-overlap-persistence/analyze.py", "lab/experiments/EXP-056-overlap-persistence/make_splits.py")


# ---------------------------------------------------------------- splits and jobs
def stem(s: int, arm: str) -> str:
    return f"r2_seed{s}_w0_{arm}"


def build(s: int) -> tuple[list[int], list[int], dict]:
    eps = json.loads(CAL.read_text(encoding="utf-8"))["levels"][str(OMEGA)]["eps"]
    F, G = ov.targets(s)
    return F, G, ov.build(s, OMEGA, eps)


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, a)}.npy" for s in man["seeds"] for a in "AB"] + [f"r2_seed{s}_test.npy" for s in man["seeds"]]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("R2 splits exist already: never overwrite")
    for s in man["seeds"]:
        F, G, d = build(s)
        assert len(d["A"]) == len(d["B"]) == ov.N_TRAIN and not np.intersect1d(d["A"], d["B"]).size
        assert not np.intersect1d(d["test"], np.union1d(d["A"], d["B"])).size
        for a in "AB":
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, d[a].astype(np.int64))
        with open(SPL / f"r2_seed{s}_test.npy", "xb") as f:
            np.save(f, d["test"].astype(np.int64))
        with open(SPL / f"r2_seed{s}_w0.json", "x", encoding="utf-8") as f:
            json.dump({"seed": s, "omega": OMEGA, "targets": {"A": F, "B": G}, "share_A_F": ov.share(d["A"], F),
                       "share_B_G": ov.share(d["B"], G), "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(man: dict, s: int) -> str | None:
    """Rebuild splits and targets deterministically and compare with the files the analysis reads (P2b lesson)."""
    F, G, d = build(s)
    meta_f = SPL / f"r2_seed{s}_w0.json"
    files = {"A": SPL / f"{stem(s, 'A')}.npy", "B": SPL / f"{stem(s, 'B')}.npy", "test": SPL / f"r2_seed{s}_test.npy"}
    if not meta_f.exists() or not all(f.exists() for f in files.values()):
        return f"seed {s}: split file missing"
    meta = json.loads(meta_f.read_text(encoding="utf-8"))
    if not all(np.array_equal(np.load(f), d[k].astype(np.int64)) for k, f in files.items()) or meta.get("targets") != {"A": F, "B": G}:
        return f"seed {s}: splits differ from the deterministic rebuild"
    return None


def hp_flags(cell: dict) -> str:
    return " ".join(f"{FLAG[k]} {v!r}" for k, v in cell["hp"].items())


def trainer_jobs(man: dict) -> list[str]:
    out, bud = [], man["budget"]
    for s in man["seeds"]:
        base = (f"{c1.interp(man)} {FB} --seed {s} --condition baseline --threads {man['threads']} --device {man['device']} "
                f"--test-file lab/confirm/r2_splits/r2_seed{s}_test.npy --out-root lab/confirm/r2_raw")
        a, b = (f"lab/confirm/r2_splits/{stem(s, x)}.npy" for x in "AB")
        for cell in man["cells"].values():
            for t in cell["ts"]:
                for first, second in ((a, b), (b, a)):
                    out.append(f"{base} --steps {t + bud} --split-file {first} --switch-split-file {second} --switch-step {t} "
                               f"--spectra-at {t},{t + 250},{t + 2000},{t + bud} --stop-after-gen {t + bud} --save-model {hp_flags(cell)}")
    return out


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban EXP-020 id, then hp suffixes with repr (Codex s24), then _dev."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    rid = (f"EXP-020_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}_to_"
           f"{Path(g('--switch-split-file')).stem}_at{g('--switch-step')}")
    for k in ("lr", "weight_decay"):
        if FLAG[k] in cmd:
            rid += f"_{TAG[k]}{float(g(FLAG[k]))!r}"
    dev = g("--device") or "cpu"
    return rid + ("" if dev == "cpu" else f"_dev{dev.replace(':', '')}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r2", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_r2.py")


# ---------------------------------------------------------------- analysis
_g61 = None


def g61():
    global _g61
    if _g61 is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("exp061", LAB / "experiments/EXP-061-grad-alignment/analyze.py")
        _g61 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_g61)
    return _g61


def one_run(man: dict, c: str, s: int, t: int, first: str, second: str, old: list[int], new: list[int], test: np.ndarray) -> dict | str:
    """Accuracies of one final model through the shared loader + R2 binding (hash -> load -> hash)."""
    cell = man["cells"][c]
    sp, sw, te = SPL / f"{stem(s, first)}.npy", SPL / f"{stem(s, second)}.npy", SPL / f"r2_seed{s}_test.npy"
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--split-file", str(sp),
           "--switch-split-file", str(sw), "--switch-step", str(t)]
    for k, v in cell["hp"].items():
        cmd += [FLAG[k], repr(v)]
    d, steps, tag = run_dir(cmd), t + man["budget"], f"{c}:{first}{second}@{t}"
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    hp = {"lr": LR0, "weight_decay": WD0, "train_frac": FRAC0, **cell["hp"]}   # all three checked, not only the varied one (as R1; Codex s26)
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=steps, split_file=sp, test_file=te, switch_file=sw,
                           config={"p": P, "task": "add", "arch": "transformer", **hp}, snapshots_at=(steps,), files=("model_final.pt",)))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(sp):
        return f"{tag}: defekt after load: {why or 'split bytes differ'}"
    try:                                      # s27 audit (as N29c): any load/forward failure is technical, never an abort
        m = p2.load_model_bytes(BLOCK.bound_bytes(man, L.path / "model_final.pt"))
        W = m.W_E.detach().numpy().astype(np.float64)[:P]
        ev = {"base": p2.e55.evaluate(m, None, test), "old": p2.e55.evaluate(m, W - g61().project(W, old), test),
              "new": p2.e55.evaluate(m, W - g61().project(W, new), test)}
        finite = all(np.isfinite(x) for e in ev.values() for x in e.values()) and all(bool(q.isfinite().all()) for q in m.parameters())
    except Exception as ex:
        return f"{tag}: defekt: {type(ex).__name__}: {ex}"
    if not finite:
        return f"{tag}: defekt: non-finite loss/margin/weights"
    return {"base": ev["base"]["acc"], "acc_old": ev["old"]["acc"], "acc_new": ev["new"]["acc"],
            "margin": {k: e["margin"] for k, e in ev.items()}}


def seed_row(man: dict, s: int) -> dict:
    meta = json.loads((SPL / f"r2_seed{s}_w0.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    test = np.load(SPL / f"r2_seed{s}_test.npy")
    runs = {}
    for c, cell in man["cells"].items():
        for t in cell["ts"]:
            runs[(c, t, "AB")] = one_run(man, c, s, t, "A", "B", F, G, test)
            runs[(c, t, "BA")] = one_run(man, c, s, t, "B", "A", G, F, test)
    bad = [v for v in runs.values() if isinstance(v, str)]
    if bad:
        return {"seed": s, "valid": False, "technical": True, "reason": "; ".join(bad[:4])}
    r: dict = {"seed": s, "technical": False, "runs": {f"{c}@{t}{k}": v for (c, t, k), v in runs.items()}}
    for c, cell in man["cells"].items():
        r[f"base_min_{c}"] = float(min(runs[(c, t, k)]["base"] for t in cell["ts"] for k in ("AB", "BA")))
        for t in cell["ts"]:
            r[f"old_{c}_{t}"] = float(np.mean([runs[(c, t, k)]["acc_old"] for k in ("AB", "BA")]))
            r[f"new_{c}_{t}"] = float(np.mean([runs[(c, t, k)]["acc_new"] for k in ("AB", "BA")]))
    r["valid"] = all(r[f"base_min_{c}"] >= ACC_MIN for c in man["cells"])
    return r


def contrasts(r: dict) -> dict[str, float]:
    out = {}
    for h, (c, t, kind) in PRIMARY.items():
        d = r[f"new_{c}_{t}"] - r[f"old_{c}_{t}"]
        out[h] = (d if kind == "hold" else -d) - MIN_DIFF
    return out


def test_family(rows: list[dict], rng: np.random.Generator, label: bool = True) -> dict:
    X = {k: np.array([contrasts(r)[k] for r in rows]) for k in PRIMARY}
    tt = {k: c1.t_test_secondary(v) for k, v in X.items()}
    ph = c1.holm({k: t["p_one_sided"] for k, t in tt.items()})
    out: dict = {}
    for k, v in X.items():
        ci = c1.boot_ci(v, rng)
        out[k] = {"mean_minus_min": float(v.mean()), "mean_diff": float(v.mean() + MIN_DIFF), "sd": float(v.std(ddof=1)),
                  "ci95_minus_min": ci, "n_positive": int((v > 0).sum())}
        if label:                                   # outcome-selected subset: no inferential fields at all (Codex s26)
            out[k].update({"t": tt[k]["t"], "p": tt[k]["p_one_sided"], "p_holm": ph[k],
                           "verdict": "bestätigt" if ph[k] < ALPHA and ci[0] >= 0.0 else "nicht bestätigt"})
    return out


def timing_secondary(rows: list[dict], rng: np.random.Generator) -> dict:
    """lr2 at t = 25 (Lambda = 0.05 as at the standard t = 50): D25 = acc_new - acc_old; reading fixed in the registration, no verdict.
    Not diagnostic for the clock (Codex s26): lr 2e-3 also holds after the switch, so faster re-adaptation can favour switching."""
    v = np.array([r["new_lr2_25"] - r["old_lr2_25"] for r in rows])
    ci = c1.boot_ci(v, rng)
    reading = ("Festhalten bei t = 25" if ci[0] > 0 else "Umstieg bei t = 25" if ci[1] < 0 else "unklar")
    return {"mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else None, "ci95": ci, "n_positive": int((v > 0).sum()),
            "reading": reading}


def verdict(rows: list[dict], n_planned: int, rng: np.random.Generator) -> dict:
    """Primary: all planned seeds (as N29, Codex s23 blocker 1). Generalised subset: descriptive only, no labels."""
    n_tech = sum(1 for r in rows if r.get("technical"))
    if n_tech > 0 or len(rows) != n_planned or n_planned < 3:
        return {"n": len(rows), "n_technical": n_tech, "verdict": "nicht auswertbar"}
    out: dict = {"n": len(rows), "n_technical": 0, "n_generalised": sum(1 for r in rows if r["valid"]), **test_family(rows, rng)}
    out["robust"] = {c: ("Übergang bestätigt" if all(out[h]["verdict"] == "bestätigt" for h, (cc, _, _) in PRIMARY.items() if cc == c)
                         else "Übergang nicht bestätigt") for c in CELLS}
    out["timing_lr2_t25"] = timing_secondary(rows, rng)
    ok = [r for r in rows if r["valid"]]
    out["descriptive_generalised_only"] = test_family(ok, rng, label=False) if len(ok) >= 3 else None
    return out


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "R2_summary.json"            # s27 audit (as P2f): an aborted analysis must not leave an older summary behind
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(man, s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"R2 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [seed_row(man, s) for s in man["seeds"]]
    out = {"manifest_commit": man["commit"], "min_diff": MIN_DIFF, "n_planned": len(man["seeds"]),
           "hypotheses": verdict(rows, len(man["seeds"]), np.random.default_rng(2)), "rows": rows}
    (LAB / "confirm" / "R2_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    for bad in ({"seeds": list(range(2510, 2539))}, {"budget": 4000.0}, {"threads": True},
                {"cells": {"lr2": {"hp": {"lr": 0.002}, "ts": [12, 25, 50]}}},
                {"cells": {**REGISTERED["cells"], "wd03": {"hp": {"weight_decay": 0.3}, "ts": [12, 50]}}}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    n = len(REGISTERED["seeds"]) * 2 * sum(len(v["ts"]) for v in CELLS.values())
    assert len(tj) == n == 300 and len(set(tj)) == n and all("r2_raw" in j and "--save-model" in j and "\\" not in j for j in tj)
    for j in tj:
        cmd = shlex.split(j)
        assert int(cmd[cmd.index("--stop-after-gen") + 1]) >= int(cmd[cmd.index("--steps") + 1]), j
        assert ("--lr" in cmd) != ("--weight-decay" in cmd), j          # exactly one override per run
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert ids[0] == "EXP-020_baseline_seed2510_thr1_r2_seed2510_w0_A_to_r2_seed2510_w0_B_at12_lr0.002_devcuda", ids[0]
    assert ids[7] == "EXP-020_baseline_seed2510_thr1_r2_seed2510_w0_B_to_r2_seed2510_w0_A_at25_wd0.3_devcuda", ids[7]
    assert len(set(ids)) == n and "--steps 4050" in tj[4] and "--spectra-at 50,300,2050,4050" in tj[4] and "--lr 0.002" in tj[4]
    assert all(j.startswith("python lab/tools/confirm_r2.py --run M -- ") for j in BLOCK.jobs(man, "M"))
    BLOCK.check_job(man, shlex.split(tj[0]))
    for foreign in (shlex.split(tj[0]) + ["--force"], [x if x != "0.002" else "0.003" for x in shlex.split(tj[0])]):
        try:
            BLOCK.check_job(man, foreign)
            raise AssertionError("foreign command accepted")
        except SystemExit:
            pass
    F, G = ov.targets(2510)
    assert not set(F) & set(G) and len(F) == len(G) == 5
    # the old -> new mapping must follow the direction: A->B has old = targets(A) = F
    def mk(o12=0.8, n12=0.1, o25=0.05, n25=0.9, o50=0.02, n50=0.95, wo25=0.8, wn25=0.1, wo50=0.02, wn50=0.95, base=1.0):
        return {"valid": base >= ACC_MIN, "technical": False, "old_lr2_12": o12, "new_lr2_12": n12, "old_lr2_25": o25, "new_lr2_25": n25,
                "old_lr2_50": o50, "new_lr2_50": n50, "old_wd03_25": wo25, "new_wd03_25": wn25, "old_wd03_50": wo50, "new_wd03_50": wn50}
    c = contrasts(mk())
    assert abs(c["H1_lr2"] - 0.63) < 1e-12 and abs(c["H2_lr2"] - 0.4) < 1e-12 and abs(c["H2_wd03"] - 0.4) < 1e-12
    rng = np.random.default_rng(0)
    good = [mk(o12=0.8 + 0.005 * i, wo25=0.8 + 0.005 * i) for i in range(30)]
    v = verdict(good, 30, rng)
    assert all(v[h]["verdict"] == "bestätigt" for h in PRIMARY) and v["robust"] == {"lr2": "Übergang bestätigt", "wd03": "Übergang bestätigt"}, v
    assert v["timing_lr2_t25"]["reading"] == "Festhalten bei t = 25", v["timing_lr2_t25"]
    v = verdict([mk(o12=0.8 + 0.005 * i, wo25=0.3 + 0.005 * i, o25=0.8, n25=0.1) for i in range(30)], 30, rng)
    assert v["H2_wd03"]["verdict"] == "nicht bestätigt" and v["robust"]["wd03"] == "Übergang nicht bestätigt" and v["robust"]["lr2"] == "Übergang bestätigt", v
    assert v["timing_lr2_t25"]["reading"] == "Umstieg bei t = 25", v["timing_lr2_t25"]
    w = verdict(good[:25] + [mk(base=0.5)] * 5, 30, rng)
    assert w["n_generalised"] == 25 and w["n"] == 30 and all(not {"verdict", "p", "p_holm", "t"} & set(x) for x in w["descriptive_generalised_only"].values())
    assert verdict(good[:29], 30, rng)["verdict"] == "nicht auswertbar"
    assert verdict(good[:29] + [{"seed": 1, "valid": False, "technical": True}], 30, rng)["verdict"] == "nicht auswertbar"
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    g61()
    loaded = {Path(m.__file__).resolve().relative_to(ROOT.resolve()).as_posix() for m in list(sys.modules.values())
              if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to((ROOT / "lab").resolve())}
    assert loaded <= set(CODE_FILES), sorted(loaded - set(CODE_FILES))
    print("[confirm_r2] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
