"""N29 confirmation (FINDINGS programme B, functional persistence): splits, job list, run binding and frozen analysis. Session 23, UNTESTED.

Registration: lab/confirm/N29_REGISTRATION.md. Successor of the EXP-064 pilot (not evaluable, 3 seeds not generalised at 2000 steps).
Per fresh seed s (omega = 0, EXP-053 splits as in N28): switch runs A->B and B->A at t in {25, 50}, then BUDGET = 4000 steps with
--stop-after-gen >= steps (lesson from P2b) and --save-model. On each final model W_E[:113] is projected onto the complement of the old
(resp. new) target frequencies (all 5 removed, EXP-064 intervention); accuracy on the held-out test set of the seed (20 % of all pairs, disjoint from A and B).
Per seed and t: acc_old / acc_new = mean over both directions of the accuracy after removing the old / new targets.
  H1 (holding on at 50):   X1 = (acc_new(50) - acc_old(50)) - MIN_DIFF > 0
  H2 (switching at 25):    X2 = (acc_old(25) - acc_new(25)) - MIN_DIFF > 0
One family {H1, H2}, Holm, one-sided t-test, 95 % bootstrap CI; "bestätigt" = Holm p < 0.05 and CI lower bound >= 0.
Eligibility: base accuracy >= 0.9 in all four runs of a seed; technical failure -> "nicht auswertbar"; < 80 % eligible -> "nicht auswertbar".

  python lab/tools/confirm_n29.py --hash-code | --splits M | --jobs M | --run M -- <cmd> | --analyze M | --selftest
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

RAW = LAB / "confirm" / "n29_raw"
BIND = LAB / "confirm" / "n29_bindings"
SPL = LAB / "confirm" / "n29_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"
BUDGET, ALPHA, OMEGA, ACC_MIN, MIN_VALID_FRAC, MIN_DIFF, P = 4000, 0.05, 0.0, 0.9, 0.8, 0.3, 113
REGISTERED = {"seeds": list(range(2250, 2270)), "ts": [25, 50], "budget": 4000, "device": "cuda", "threads": 1}
CODE_FILES = ("lab/tools/confirm_n29.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_p2.py",
              "lab/tools/confirm_splits.py", "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py",
              "lab/experiments/EXP-001-freq-ban/freq_ban.py",
              "lab/experiments/EXP-053-p3-overlap-design/overlap_split.py", "lab/experiments/EXP-053-p3-overlap-design/calibration.json",
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py",
              "lab/experiments/EXP-051-functional-ablation/analyze.py", "lab/experiments/EXP-055-ablation-dose/analyze.py",
              "lab/experiments/EXP-061-grad-alignment/analyze.py", "lab/experiments/EXP-059-momentum-exposure/analyze.py",
              "lab/experiments/EXP-056-overlap-persistence/analyze.py")


# ---------------------------------------------------------------- splits and jobs
def stem(s: int, arm: str) -> str:
    return f"n29_seed{s}_w0_{arm}"


def build(s: int) -> tuple[list[int], list[int], dict]:
    eps = json.loads(CAL.read_text(encoding="utf-8"))["levels"][str(OMEGA)]["eps"]
    F, G = ov.targets(s)
    return F, G, ov.build(s, OMEGA, eps)


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, a)}.npy" for s in man["seeds"] for a in "AB"] + [f"n29_seed{s}_test.npy" for s in man["seeds"]]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("N29 splits exist already: never overwrite")
    for s in man["seeds"]:
        F, G, d = build(s)
        assert len(d["A"]) == len(d["B"]) == ov.N_TRAIN and not np.intersect1d(d["A"], d["B"]).size
        assert not np.intersect1d(d["test"], np.union1d(d["A"], d["B"])).size
        for a in "AB":
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, d[a].astype(np.int64))
        with open(SPL / f"n29_seed{s}_test.npy", "xb") as f:
            np.save(f, d["test"].astype(np.int64))
        with open(SPL / f"n29_seed{s}_w0.json", "x", encoding="utf-8") as f:
            json.dump({"seed": s, "omega": OMEGA, "targets": {"A": F, "B": G}, "share_A_F": ov.share(d["A"], F),
                       "share_B_G": ov.share(d["B"], G), "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(man: dict, s: int) -> str | None:
    """Rebuild splits and targets deterministically and compare with the files the analysis reads (P2b lesson)."""
    F, G, d = build(s)
    meta_f = SPL / f"n29_seed{s}_w0.json"
    files = {"A": SPL / f"{stem(s, 'A')}.npy", "B": SPL / f"{stem(s, 'B')}.npy", "test": SPL / f"n29_seed{s}_test.npy"}
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
                f"--test-file lab/confirm/n29_splits/n29_seed{s}_test.npy --out-root lab/confirm/n29_raw")
        a, b = (f"lab/confirm/n29_splits/{stem(s, x)}.npy" for x in "AB")
        for t in man["ts"]:
            for first, second in ((a, b), (b, a)):
                out.append(f"{base} --steps {t + bud} --split-file {first} --switch-split-file {second} --switch-step {t} "
                           f"--spectra-at {t},{t + 250},{t + 2000},{t + bud} --stop-after-gen {t + bud} --save-model")
    return out


def expected_run_id(cmd: list[str]) -> str:
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    dev = g("--device") or "cpu"
    rid = (f"EXP-020_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}_to_"
           f"{Path(g('--switch-split-file')).stem}_at{g('--switch-step')}")
    return rid + ("" if dev == "cpu" else f"_dev{dev}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_n29", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_n29.py")


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


def one_run(man: dict, s: int, t: int, first: str, second: str, old: list[int], new: list[int], test: np.ndarray) -> dict | str:
    """Accuracies of one final model through the shared loader + N29 binding (hash -> load -> hash)."""
    sp, sw, te = SPL / f"{stem(s, first)}.npy", SPL / f"{stem(s, second)}.npy", SPL / f"n29_seed{s}_test.npy"
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--split-file", str(sp),
           "--switch-split-file", str(sw), "--switch-step", str(t)]
    d, steps, tag = run_dir(cmd), t + man["budget"], f"{first}{second}@{t}"
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=steps, split_file=sp, test_file=te, switch_file=sw,
                           config={"p": P, "task": "add"}, snapshots_at=(steps,), files=("model_final.pt",)))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(sp):
        return f"{tag}: defekt after load: {why or 'split bytes differ'}"
    try:
        m = p2.load_model_bytes(BLOCK.bound_bytes(man, L.path / "model_final.pt"))
    except ValueError as ex:
        return f"{tag}: defekt: {ex}"
    W = m.W_E.detach().numpy().astype(np.float64)[:P]
    acc = lambda Wr: p2.e55.evaluate(m, Wr, test)["acc"]   # noqa: E731
    vals = {"base": acc(None), "acc_old": acc(W - g61().project(W, old)), "acc_new": acc(W - g61().project(W, new))}
    if not all(np.isfinite(v) for v in vals.values()):
        return f"{tag}: defekt: non-finite accuracy"
    return vals


def seed_row(man: dict, s: int) -> dict:
    meta = json.loads((SPL / f"n29_seed{s}_w0.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    test = np.load(SPL / f"n29_seed{s}_test.npy")    # held-out test set of the seed (as in EXP-064), disjoint from A and B
    runs = {}
    for t in man["ts"]:
        runs[(t, "AB")] = one_run(man, s, t, "A", "B", F, G, test)
        runs[(t, "BA")] = one_run(man, s, t, "B", "A", G, F, test)
    bad = [v for v in runs.values() if isinstance(v, str)]
    if bad:
        return {"seed": s, "valid": False, "technical": True, "reason": "; ".join(bad[:4])}
    r = {"seed": s, "technical": False, "base_min": float(min(v["base"] for v in runs.values())),
         "runs": {f"{t}{k}": v for (t, k), v in runs.items()}}
    for t in man["ts"]:
        r[f"old{t}"] = float(np.mean([runs[(t, k)]["acc_old"] for k in ("AB", "BA")]))
        r[f"new{t}"] = float(np.mean([runs[(t, k)]["acc_new"] for k in ("AB", "BA")]))
    r["valid"] = r["base_min"] >= ACC_MIN
    if not r["valid"]:
        r["reason"] = f"base accuracy < {ACC_MIN}"
    return r


def contrasts(r: dict) -> dict[str, float]:
    return {"H1": (r["new50"] - r["old50"]) - MIN_DIFF, "H2": (r["old25"] - r["new25"]) - MIN_DIFF}


def verdict(rows: list[dict], n_planned: int, rng: np.random.Generator) -> dict:
    n_tech = sum(1 for r in rows if r.get("technical"))
    ok = [r for r in rows if r["valid"]]
    if n_tech > 0 or len(ok) < MIN_VALID_FRAC * n_planned or len(ok) < 3:
        return {"n_valid": len(ok), "n_technical": n_tech, "verdict": "nicht auswertbar"}
    X = {k: np.array([contrasts(r)[k] for r in ok]) for k in ("H1", "H2")}
    tt = {k: c1.t_test_secondary(v) for k, v in X.items()}
    ph = c1.holm({k: t["p_one_sided"] for k, t in tt.items()})
    out: dict = {"n_valid": len(ok), "n_technical": 0}
    for k, v in X.items():
        ci = c1.boot_ci(v, rng)
        out[k] = {"mean_minus_min": float(v.mean()), "mean_diff": float(v.mean() + MIN_DIFF), "sd": float(v.std(ddof=1)), "t": tt[k]["t"],
                  "p": tt[k]["p_one_sided"], "p_holm": ph[k], "ci95_minus_min": ci, "n_positive": int((v > 0).sum()),
                  "verdict": "bestätigt" if ph[k] < ALPHA and ci[0] >= 0.0 else "nicht bestätigt"}
    return out


def analyze(manifest: Path) -> None:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(man, s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"N29 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [seed_row(man, s) for s in man["seeds"]]
    ok = [r for r in rows if r["valid"]]
    out = {"manifest_commit": man["commit"], "min_diff": MIN_DIFF, "n_planned": len(man["seeds"]),
           "hypotheses": verdict(rows, len(man["seeds"]), np.random.default_rng(29)),
           "mean_valid": {k: float(np.mean([r[k] for r in ok])) for k in ("old25", "new25", "old50", "new50")} if ok else {},
           "mean_all_nontechnical": {k: float(np.mean([r[k] for r in rows if not r.get("technical")]))
                                     for k in ("old25", "new25", "old50", "new50")} if any(not r.get("technical") for r in rows) else {},
           "rows": rows}
    (LAB / "confirm" / "N29_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    for bad in ({"seeds": list(range(2250, 2269))}, {"budget": 4000.0}, {"ts": [25, 35]}, {"threads": True}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    assert len(tj) == 80 and len(set(tj)) == 80 and all("n29_raw" in j and "--save-model" in j and "\\" not in j for j in tj)
    for j in tj:
        c = shlex.split(j)
        assert int(c[c.index("--stop-after-gen") + 1]) >= int(c[c.index("--steps") + 1]), j
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert ids[0] == "EXP-020_baseline_seed2250_thr1_n29_seed2250_w0_A_to_n29_seed2250_w0_B_at25_devcuda", ids[0]
    assert ids[3] == "EXP-020_baseline_seed2250_thr1_n29_seed2250_w0_B_to_n29_seed2250_w0_A_at50_devcuda", ids[3]
    assert len(set(ids)) == 80 and "--steps 4050" in tj[3] and "--spectra-at 50,300,2050,4050" in tj[3]
    assert all(j.startswith("python lab/tools/confirm_n29.py --run M -- ") for j in BLOCK.jobs(man, "M"))
    BLOCK.check_job(man, shlex.split(tj[0]))
    try:
        BLOCK.check_job(man, shlex.split(tj[0]) + ["--force"])
        raise AssertionError("foreign command accepted")
    except SystemExit:
        pass
    F, G = ov.targets(2250)
    assert not set(F) & set(G) and len(F) == len(G) == 5
    mk = lambda o25, n25, o50, n50, base=1.0: {"valid": base >= ACC_MIN, "technical": False, "base_min": base,   # noqa: E731
                                               "old25": o25, "new25": n25, "old50": o50, "new50": n50}
    c = contrasts(mk(0.8, 0.1, 0.02, 0.95))
    assert abs(c["H1"] - 0.63) < 1e-12 and abs(c["H2"] - 0.4) < 1e-12
    rng = np.random.default_rng(0)
    good = [mk(0.8 + 0.01 * i, 0.1, 0.02, 0.95) for i in range(20)]
    v = verdict(good, 20, rng)
    assert v["H1"]["verdict"] == "bestätigt" and v["H2"]["verdict"] == "bestätigt", v
    v = verdict([mk(0.25 + 0.01 * i, 0.1, 0.02, 0.95) for i in range(20)], 20, rng)
    assert v["H1"]["verdict"] == "bestätigt" and v["H2"]["verdict"] == "nicht bestätigt", v
    assert verdict(good[:15] + [mk(0.8, 0.1, 0.02, 0.95, base=0.5)] * 5, 20, rng)["verdict"] == "nicht auswertbar"
    assert verdict(good[:16] + [mk(0.8, 0.1, 0.02, 0.95, base=0.5)] * 4, 20, rng)["H1"]["verdict"] == "bestätigt"
    assert verdict(good[:19] + [{"seed": 1, "valid": False, "technical": True}], 20, rng)["verdict"] == "nicht auswertbar"
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    print("[confirm_n29] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
