"""R3 confirmation (FINDINGS 'largest open question'; K4c timing): does the lock-in follow the summed learning rate (Lambda clock) or the
step count? Session 26, UNTESTED.

Registration: lab/confirm/R3_REGISTRATION_DRAFT.md. Protocol exactly as N29 (confirm_n29.py: omega = 0 EXP-053 splits, both directions,
BUDGET = 4000 steps after the switch, --stop-after-gen >= steps, --save-model, W_E[:113] projected off the old / new targets, accuracy on the
held-out test set of the seed), but the learning rate on the FIRST split only is scaled by c (freq_ban --lr-scale c: c * lr for the steps
1..t on the first train set, full lr after the switch; EXP-039 option), so that only the pre-switch history differs:
  cell lrs2  : --lr-scale 2    t = 25   (Lambda = 50 lr-steps, as the standard switch at 50)
  cell lrs05 : --lr-scale 0.5  t = 50   (Lambda = 25 lr-steps, as the standard switch at 25)
Primary family (Holm over 2, one-sided t-test, 95 % bootstrap CI; "bestätigt" = Holm p < 0.05 and CI lower bound >= 0), Lambda-clock predictions:
  HL_hold   (lrs2 @ 25):  (acc_new - acc_old) - MIN_DIFF > 0      holds like the standard switch at 50
  HL_switch (lrs05 @ 50): (acc_old - acc_new) - MIN_DIFF > 0      switches like the standard switch at 25
Secondary, no verdict: the mirrored step-clock contrasts (switch at lrs2@25, hold at lrs05@50) with CIs; reading fixed in the registration.
Primary sample: ALL seeds (as N29, Codex s23); any technical failure -> "nicht auswertbar".

  python lab/tools/confirm_r3.py --hash-code | --splits M | --jobs M | --run M -- <cmd> | --analyze M | --selftest
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

RAW = LAB / "confirm" / "r3_raw"
BIND = LAB / "confirm" / "r3_bindings"
SPL = LAB / "confirm" / "r3_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"
BUDGET, ALPHA, OMEGA, ACC_MIN, MIN_DIFF, P = 4000, 0.05, 0.0, 0.9, 0.3, 113
LR_SCALE_UNTIL = 250                                     # freq_ban constant; must exceed every t so the scaling covers all pre-switch steps
CELLS = {"lrs2": {"c": 2.0, "t": 25}, "lrs05": {"c": 0.5, "t": 50}}
PRIMARY = {"HL_hold": ("lrs2", "hold"), "HL_switch": ("lrs05", "switch")}
REGISTERED = {"seeds": list(range(2540, 2560)), "budget": 4000, "device": "cuda", "threads": 1,
              "cells": {k: dict(v) for k, v in CELLS.items()}}
CODE_FILES = ("lab/tools/confirm_r3.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_p2.py",
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
    return f"r3_seed{s}_w0_{arm}"


def build(s: int) -> tuple[list[int], list[int], dict]:
    eps = json.loads(CAL.read_text(encoding="utf-8"))["levels"][str(OMEGA)]["eps"]
    F, G = ov.targets(s)
    return F, G, ov.build(s, OMEGA, eps)


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, a)}.npy" for s in man["seeds"] for a in "AB"] + [f"r3_seed{s}_test.npy" for s in man["seeds"]]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("R3 splits exist already: never overwrite")
    for s in man["seeds"]:
        F, G, d = build(s)
        assert len(d["A"]) == len(d["B"]) == ov.N_TRAIN and not np.intersect1d(d["A"], d["B"]).size
        assert not np.intersect1d(d["test"], np.union1d(d["A"], d["B"])).size
        for a in "AB":
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, d[a].astype(np.int64))
        with open(SPL / f"r3_seed{s}_test.npy", "xb") as f:
            np.save(f, d["test"].astype(np.int64))
        with open(SPL / f"r3_seed{s}_w0.json", "x", encoding="utf-8") as f:
            json.dump({"seed": s, "omega": OMEGA, "targets": {"A": F, "B": G}, "share_A_F": ov.share(d["A"], F),
                       "share_B_G": ov.share(d["B"], G), "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(man: dict, s: int) -> str | None:
    """Rebuild splits and targets deterministically and compare with the files the analysis reads (P2b lesson)."""
    F, G, d = build(s)
    meta_f = SPL / f"r3_seed{s}_w0.json"
    files = {"A": SPL / f"{stem(s, 'A')}.npy", "B": SPL / f"{stem(s, 'B')}.npy", "test": SPL / f"r3_seed{s}_test.npy"}
    if not meta_f.exists() or not all(f.exists() for f in files.values()):
        return f"seed {s}: split file missing"
    meta = json.loads(meta_f.read_text(encoding="utf-8"))
    if not all(np.array_equal(np.load(f), d[k].astype(np.int64)) for k, f in files.items()) or meta.get("targets") != {"A": F, "B": G}:
        return f"seed {s}: splits differ from the deterministic rebuild"
    return None


def trainer_jobs(man: dict) -> list[str]:
    out, bud = [], man["budget"]
    for s in man["seeds"]:
        base = (f"{c1.interp(man)} {FB} --seed {s} --condition baseline --threads {man['threads']} --device {man['device']} "
                f"--test-file lab/confirm/r3_splits/r3_seed{s}_test.npy --out-root lab/confirm/r3_raw")
        a, b = (f"lab/confirm/r3_splits/{stem(s, x)}.npy" for x in "AB")
        for cell in man["cells"].values():
            t = cell["t"]
            for first, second in ((a, b), (b, a)):
                out.append(f"{base} --steps {t + bud} --split-file {first} --switch-split-file {second} --switch-step {t} "
                           f"--spectra-at {t},{t + 250},{t + 2000},{t + bud} --stop-after-gen {t + bud} --save-model --lr-scale {cell['c']:g}")
    return out


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban EXP-020 id, then the lr-scale suffix (':g' as in freq_ban), then _dev."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    rid = (f"EXP-020_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}_to_"
           f"{Path(g('--switch-split-file')).stem}_at{g('--switch-step')}")
    if g("--lr-scale") is not None and float(g("--lr-scale")) != 1.0:
        rid += f"_lrs{float(g('--lr-scale')):g}"
    dev = g("--device") or "cpu"
    return rid + ("" if dev == "cpu" else f"_dev{dev.replace(':', '')}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r3", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_r3.py")


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


def one_run(man: dict, c: str, s: int, first: str, second: str, old: list[int], new: list[int], test: np.ndarray) -> dict | str:
    """Accuracies of one final model through the shared loader + R3 binding (hash -> load -> hash)."""
    cell = man["cells"][c]
    t = cell["t"]
    sp, sw, te = SPL / f"{stem(s, first)}.npy", SPL / f"{stem(s, second)}.npy", SPL / f"r3_seed{s}_test.npy"
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--split-file", str(sp),
           "--switch-split-file", str(sw), "--switch-step", str(t), "--lr-scale", f"{cell['c']:g}"]
    d, steps, tag = run_dir(cmd), t + man["budget"], f"{c}:{first}{second}@{t}"
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=steps, split_file=sp, test_file=te, switch_file=sw,
                           config={"p": P, "task": "add", "arch": "transformer", "lr": 1e-3, "weight_decay": 1.0, "train_frac": 0.3},
                           snapshots_at=(steps,), files=("model_final.pt",)))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(sp):
        return f"{tag}: defekt after load: {why or 'split bytes differ'}"
    if float(L.res.get("lr_scale", 1.0)) != cell["c"] or int(L.res.get("lr_scale_until", -1)) < t or L.res.get("switch_step") != t:
        return f"{tag}: defekt: lr_scale/lr_scale_until/switch_step in result.json do not match the cell"
    try:
        m = p2.load_model_bytes(BLOCK.bound_bytes(man, L.path / "model_final.pt"))
    except ValueError as ex:
        return f"{tag}: defekt: {ex}"
    W = m.W_E.detach().numpy().astype(np.float64)[:P]
    ev = {"base": p2.e55.evaluate(m, None, test), "old": p2.e55.evaluate(m, W - g61().project(W, old), test),
          "new": p2.e55.evaluate(m, W - g61().project(W, new), test)}
    if not all(np.isfinite(x) for e in ev.values() for x in e.values()) or not all(bool(q.isfinite().all()) for q in m.parameters()):
        return f"{tag}: defekt: non-finite loss/margin/weights"
    return {"base": ev["base"]["acc"], "acc_old": ev["old"]["acc"], "acc_new": ev["new"]["acc"],
            "margin": {k: e["margin"] for k, e in ev.items()}}


def seed_row(man: dict, s: int) -> dict:
    meta = json.loads((SPL / f"r3_seed{s}_w0.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    test = np.load(SPL / f"r3_seed{s}_test.npy")
    runs = {}
    for c in man["cells"]:
        runs[(c, "AB")] = one_run(man, c, s, "A", "B", F, G, test)
        runs[(c, "BA")] = one_run(man, c, s, "B", "A", G, F, test)
    bad = [v for v in runs.values() if isinstance(v, str)]
    if bad:
        return {"seed": s, "valid": False, "technical": True, "reason": "; ".join(bad[:4])}
    r: dict = {"seed": s, "technical": False, "runs": {f"{c}{k}": v for (c, k), v in runs.items()},
               "base_min": float(min(v["base"] for v in runs.values()))}
    for c in man["cells"]:
        r[f"old_{c}"] = float(np.mean([runs[(c, k)]["acc_old"] for k in ("AB", "BA")]))
        r[f"new_{c}"] = float(np.mean([runs[(c, k)]["acc_new"] for k in ("AB", "BA")]))
    r["valid"] = r["base_min"] >= ACC_MIN
    return r


def contrasts(r: dict) -> dict[str, float]:
    out = {}
    for h, (c, kind) in PRIMARY.items():
        d = r[f"new_{c}"] - r[f"old_{c}"]
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
        if label:                                   # outcome-selected subset: no inferential fields (as R2, Codex s26)
            out[k].update({"t": tt[k]["t"], "p": tt[k]["p_one_sided"], "p_holm": ph[k],
                           "verdict": "bestätigt" if ph[k] < ALPHA and ci[0] >= 0.0 else "nicht bestätigt"})
    return out


def step_clock_secondary(rows: list[dict], rng: np.random.Generator) -> dict:
    """Mirrored contrasts (step-clock predictions): lrs2@25 switches, lrs05@50 holds. Descriptive, reading fixed in the registration."""
    out = {}
    for name, c, sign in (("S_switch_lrs2", "lrs2", -1.0), ("S_hold_lrs05", "lrs05", 1.0)):
        v = np.array([sign * (r[f"new_{c}"] - r[f"old_{c}"]) - MIN_DIFF for r in rows])
        ci = c1.boot_ci(v, rng)
        out[name] = {"mean_diff": float(v.mean() + MIN_DIFF), "ci95_minus_min": ci, "n_positive": int((v > 0).sum())}
    out["reading"] = ("passt zur Schrittuhr" if all(out[k]["ci95_minus_min"][0] > 0 for k in ("S_switch_lrs2", "S_hold_lrs05"))
                      else "passt nicht zur Schrittuhr")
    return out


def verdict(rows: list[dict], n_planned: int, rng: np.random.Generator) -> dict:
    n_tech = sum(1 for r in rows if r.get("technical"))
    if n_tech > 0 or len(rows) != n_planned or n_planned < 3:
        return {"n": len(rows), "n_technical": n_tech, "verdict": "nicht auswertbar"}
    out: dict = {"n": len(rows), "n_technical": 0, "n_generalised": sum(1 for r in rows if r["valid"]), **test_family(rows, rng)}
    both = all(out[h]["verdict"] == "bestätigt" for h in PRIMARY)
    out["lambda_clock"] = ("Λ-Uhr bestätigt (Skalierung wie Λ in zwei Zellen, kein Mechanismus)" if both
                           else "Λ-Uhr nicht bestätigt (keine Bestätigung der Schrittuhr; siehe step_clock_secondary)")   # Codex s26
    out["step_clock_secondary"] = step_clock_secondary(rows, rng)
    ok = [r for r in rows if r["valid"]]
    out["descriptive_generalised_only"] = test_family(ok, rng, label=False) if len(ok) >= 3 else None
    return out


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "R3_summary.json"            # s27 audit (as P2f): an aborted analysis must not leave an older summary behind
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(man, s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"R3 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [seed_row(man, s) for s in man["seeds"]]
    out = {"manifest_commit": man["commit"], "min_diff": MIN_DIFF, "n_planned": len(man["seeds"]),
           "hypotheses": verdict(rows, len(man["seeds"]), np.random.default_rng(3)), "rows": rows}
    (LAB / "confirm" / "R3_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    assert all(v["t"] < LR_SCALE_UNTIL for v in CELLS.values())
    for bad in ({"seeds": list(range(2540, 2559))}, {"budget": 4000.0}, {"threads": True},
                {"cells": {"lrs2": {"c": 2.0, "t": 25}}}, {"cells": {"lrs2": {"c": 2, "t": 25}, "lrs05": {"c": 0.5, "t": 50}}},
                {"cells": {"lrs2": {"c": 2.0, "t": 50}, "lrs05": {"c": 0.5, "t": 50}}}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    assert len(tj) == 80 and len(set(tj)) == 80 and all("r3_raw" in j and "--save-model" in j and "\\" not in j for j in tj)
    for j in tj:
        cmd = shlex.split(j)
        assert int(cmd[cmd.index("--stop-after-gen") + 1]) >= int(cmd[cmd.index("--steps") + 1]), j
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert ids[0] == "EXP-020_baseline_seed2540_thr1_r3_seed2540_w0_A_to_r3_seed2540_w0_B_at25_lrs2_devcuda", ids[0]
    assert ids[3] == "EXP-020_baseline_seed2540_thr1_r3_seed2540_w0_B_to_r3_seed2540_w0_A_at50_lrs0.5_devcuda", ids[3]
    assert len(set(ids)) == 80 and "--steps 4025" in tj[0] and "--lr-scale 2 " not in tj[0] and tj[0].endswith("--lr-scale 2")
    assert "--steps 4050" in tj[2] and "--spectra-at 50,300,2050,4050" in tj[2] and tj[2].endswith("--lr-scale 0.5")
    assert all(j.startswith("python lab/tools/confirm_r3.py --run M -- ") for j in BLOCK.jobs(man, "M"))
    BLOCK.check_job(man, shlex.split(tj[0]))
    for foreign in (shlex.split(tj[0]) + ["--force"], [x if x != "2" else "3" for x in shlex.split(tj[0])]):
        try:
            BLOCK.check_job(man, foreign)
            raise AssertionError("foreign command accepted")
        except SystemExit:
            pass
    F, G = ov.targets(2540)
    assert not set(F) & set(G) and len(F) == len(G) == 5

    def mk(o2=0.02, n2=0.95, o05=0.8, n05=0.1, base=1.0):
        return {"valid": base >= ACC_MIN, "technical": False, "old_lrs2": o2, "new_lrs2": n2, "old_lrs05": o05, "new_lrs05": n05}
    c = contrasts(mk())
    assert abs(c["HL_hold"] - 0.63) < 1e-12 and abs(c["HL_switch"] - 0.4) < 1e-12
    rng = np.random.default_rng(0)
    lam = [mk(n2=0.95 - 0.005 * i, o05=0.8 + 0.005 * i) for i in range(20)]          # Lambda clock
    v = verdict(lam, 20, rng)
    assert v["lambda_clock"].startswith("Λ-Uhr bestätigt") and v["step_clock_secondary"]["reading"] == "passt nicht zur Schrittuhr", v
    stp = [mk(o2=0.8 + 0.005 * i, n2=0.1, o05=0.02, n05=0.95) for i in range(20)]   # step clock
    v = verdict(stp, 20, rng)
    assert v["lambda_clock"].startswith("Λ-Uhr nicht bestätigt") and v["step_clock_secondary"]["reading"] == "passt zur Schrittuhr", v
    assert all(v[h]["verdict"] == "nicht bestätigt" for h in PRIMARY)
    w = verdict(lam[:15] + [mk(base=0.5)] * 5, 20, rng)
    assert w["n_generalised"] == 15 and all(not {"verdict", "p", "p_holm", "t"} & set(x) for x in w["descriptive_generalised_only"].values())
    assert verdict(lam[:19], 20, rng)["verdict"] == "nicht auswertbar"
    assert verdict(lam[:19] + [{"seed": 1, "valid": False, "technical": True}], 20, rng)["verdict"] == "nicht auswertbar"
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    src = (ROOT / FB).read_text(encoding="utf-8")                  # the freq_ban constant this design relies on
    assert f"LR_SCALE_UNTIL = {LR_SCALE_UNTIL}" in src and "on_first = switch_idx is None or step <= a.switch_step" in src
    g61()
    loaded = {Path(m.__file__).resolve().relative_to(ROOT.resolve()).as_posix() for m in list(sys.modules.values())
              if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to((ROOT / "lab").resolve())}
    assert loaded <= set(CODE_FILES), sorted(loaded - set(CODE_FILES))
    print("[confirm_r3] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
