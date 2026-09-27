"""N29b confirmation (FINDINGS programme B, locus of the exclusion at t = 50): splits, jobs, binding, frozen analysis. Session 23 (selftest ok).

Registration: lab/confirm/N29b_REGISTRATION.md. Successor of the EXP-067 pilot (attention reset at the switch lifted the exclusion, 10/10).
Per fresh seed s (omega = 0, EXP-053 splits as N28/N29): switch runs A->B and B->A at t = 50, then BUDGET = 4000 steps with
--stop-after-gen >= steps and --save-model, in three arms: normal, rsattn (--reset-at-switch attn: W_Q, W_K, W_V, W_O to init + AdamW
state cleared), rsmlp (--reset-at-switch mlp: W_in, W_out). On each final model W_E[:113] is projected onto the complement of the old
(resp. new) targets (N29 intervention); accuracy on the held-out test set of the seed. Per seed and arm, mean over both directions:
  R(arm) = acc_new - acc_old   (acc_new = accuracy after removing the NEW targets; R > 0 = the model relies on the OLD targets)
  H1 (attention reset moves reliance to the new targets):        X1 = R(normal) - R(rsattn) - 0.5 > 0
  H2 (more than an MLP reset of twice the parameter count does): X2 = R(rsmlp)  - R(rsattn) - 0.3 > 0
One family {H1, H2}, Holm, one-sided t-test, 95 % bootstrap CI; "bestätigt" = Holm p < 0.05 and CI lower bound >= 0. Primary sample = ALL
seeds (N29 lesson); any technical failure (missing, unbound, loader error, non-finite, reset not recorded) -> "nicht auswertbar".

  python lab/tools/confirm_n29b.py --hash-code | --splits M | --jobs M | --run M -- <cmd> | --analyze M | --selftest
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

RAW = LAB / "confirm" / "n29b_raw"
BIND = LAB / "confirm" / "n29b_bindings"
SPL = LAB / "confirm" / "n29b_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"
ALPHA, OMEGA, ACC_MIN, P = 0.05, 0.0, 0.9, 113
MIN_DIFF = {"H1": 0.5, "H2": 0.3}
REGISTERED = {"seeds": list(range(2300, 2320)), "t": 50, "arms": ["normal", "rsattn", "rsmlp"], "budget": 4000, "device": "cuda", "threads": 1}
CODE_FILES = ("lab/tools/confirm_n29b.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_p2.py",
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
    return f"n29b_seed{s}_w0_{arm}"


def build(s: int) -> tuple[list[int], list[int], dict]:
    eps = json.loads(CAL.read_text(encoding="utf-8"))["levels"][str(OMEGA)]["eps"]
    F, G = ov.targets(s)
    return F, G, ov.build(s, OMEGA, eps)


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, a)}.npy" for s in man["seeds"] for a in "AB"] + [f"n29b_seed{s}_test.npy" for s in man["seeds"]]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("N29b splits exist already: never overwrite")
    for s in man["seeds"]:
        F, G, d = build(s)
        assert len(d["A"]) == len(d["B"]) == ov.N_TRAIN and not np.intersect1d(d["A"], d["B"]).size
        assert not np.intersect1d(d["test"], np.union1d(d["A"], d["B"])).size
        for a in "AB":
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, d[a].astype(np.int64))
        with open(SPL / f"n29b_seed{s}_test.npy", "xb") as f:
            np.save(f, d["test"].astype(np.int64))
        with open(SPL / f"n29b_seed{s}_w0.json", "x", encoding="utf-8") as f:
            json.dump({"seed": s, "omega": OMEGA, "targets": {"A": F, "B": G}, "share_A_F": ov.share(d["A"], F),
                       "share_B_G": ov.share(d["B"], G), "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(man: dict, s: int) -> str | None:
    F, G, d = build(s)
    meta_f = SPL / f"n29b_seed{s}_w0.json"
    files = {"A": SPL / f"{stem(s, 'A')}.npy", "B": SPL / f"{stem(s, 'B')}.npy", "test": SPL / f"n29b_seed{s}_test.npy"}
    if not meta_f.exists() or not all(f.exists() for f in files.values()):
        return f"seed {s}: split file missing"
    meta = json.loads(meta_f.read_text(encoding="utf-8"))
    if not all(np.array_equal(np.load(f), d[k].astype(np.int64)) for k, f in files.items()) or meta.get("targets") != {"A": F, "B": G}:
        return f"seed {s}: splits differ from the deterministic rebuild"
    return None


def trainer_jobs(man: dict) -> list[str]:
    out, t, bud = [], man["t"], man["budget"]
    for s in man["seeds"]:
        base = (f"{c1.interp(man)} {FB} --seed {s} --condition baseline --threads {man['threads']} --device {man['device']} "
                f"--test-file lab/confirm/n29b_splits/n29b_seed{s}_test.npy --out-root lab/confirm/n29b_raw")
        a, b = (f"lab/confirm/n29b_splits/{stem(s, x)}.npy" for x in "AB")
        for arm in man["arms"]:
            for first, second in ((a, b), (b, a)):
                out.append(f"{base} --steps {t + bud} --split-file {first} --switch-split-file {second} --switch-step {t} "
                           f"--spectra-at {t},{t + 250},{t + 2000},{t + bud} --stop-after-gen {t + bud} --save-model"
                           + ("" if arm == "normal" else f" --reset-at-switch {arm[2:]}"))
    return out


def expected_run_id(cmd: list[str]) -> str:
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    dev = g("--device") or "cpu"
    rid = (f"EXP-020_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}_to_"
           f"{Path(g('--switch-split-file')).stem}_at{g('--switch-step')}")
    if g("--reset-at-switch"):
        rid += f"_rs{g('--reset-at-switch')}"
    return rid + ("" if dev == "cpu" else f"_dev{dev}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_n29b", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_n29b.py")


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


def one_run(man: dict, s: int, arm: str, first: str, second: str, old: list[int], new: list[int], test: np.ndarray) -> dict | str:
    """Accuracies of one final model through the shared loader + N29b binding (hash -> load -> hash)."""
    t = man["t"]
    sp, sw, te = SPL / f"{stem(s, first)}.npy", SPL / f"{stem(s, second)}.npy", SPL / f"n29b_seed{s}_test.npy"
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--split-file", str(sp),
           "--switch-split-file", str(sw), "--switch-step", str(t)] + ([] if arm == "normal" else ["--reset-at-switch", arm[2:]])
    d, steps, tag = run_dir(cmd), t + man["budget"], f"{arm} {first}{second}"
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
    ev = L.res.get("events", {}).get("reset_at_switch")
    if arm == "normal" and ev is not None:
        return f"{tag}: defekt: unexpected reset event"
    if arm != "normal" and not (ev and ev.get("which") == arm[2:] and ev.get("check") is True):
        return f"{tag}: defekt: reset not recorded"
    try:
        m = p2.load_model_bytes(BLOCK.bound_bytes(man, L.path / "model_final.pt"))
        W = m.W_E.detach().numpy().astype(np.float64)[:P]
        ev_ = {"base": p2.e55.evaluate(m, None, test), "old": p2.e55.evaluate(m, W - g61().project(W, old), test),
               "new": p2.e55.evaluate(m, W - g61().project(W, new), test)}
        finite = all(np.isfinite(x) for e in ev_.values() for x in e.values()) and all(bool(q.isfinite().all()) for q in m.parameters())
    except Exception as ex:                   # any load/forward failure is technical, never an abort
        return f"{tag}: defekt: {type(ex).__name__}: {ex}"
    if not finite:
        return f"{tag}: defekt: non-finite loss/margin/weights"
    return {"base": ev_["base"]["acc"], "acc_old": ev_["old"]["acc"], "acc_new": ev_["new"]["acc"]}


def seed_row(man: dict, s: int) -> dict:
    meta = json.loads((SPL / f"n29b_seed{s}_w0.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    test = np.load(SPL / f"n29b_seed{s}_test.npy")
    runs = {}
    for arm in man["arms"]:
        runs[(arm, "AB")] = one_run(man, s, arm, "A", "B", F, G, test)
        runs[(arm, "BA")] = one_run(man, s, arm, "B", "A", G, F, test)
    bad = [v for v in runs.values() if isinstance(v, str)]
    if bad:
        return {"seed": s, "technical": True, "reason": "; ".join(bad[:4])}
    r = {"seed": s, "technical": False, "runs": {f"{a} {k}": v for (a, k), v in runs.items()},
         "generalised": all(v["base"] >= ACC_MIN for v in runs.values())}
    for arm in man["arms"]:
        r[f"R_{arm}"] = float(np.mean([runs[(arm, k)]["acc_new"] - runs[(arm, k)]["acc_old"] for k in ("AB", "BA")]))
    return r


def contrasts(r: dict) -> dict[str, float]:
    return {"H1": r["R_normal"] - r["R_rsattn"] - MIN_DIFF["H1"], "H2": r["R_rsmlp"] - r["R_rsattn"] - MIN_DIFF["H2"]}


def test_family(rows: list[dict], rng: np.random.Generator, label: bool) -> dict:
    X = {k: np.array([contrasts(r)[k] for r in rows]) for k in MIN_DIFF}
    tt = {k: c1.t_test_secondary(v) for k, v in X.items()}
    ph = c1.holm({k: t["p_one_sided"] for k, t in tt.items()})
    out: dict = {}
    for k, v in X.items():
        ci = c1.boot_ci(v, rng)
        out[k] = {"mean_minus_min": float(v.mean()), "mean_diff": float(v.mean() + MIN_DIFF[k]), "sd": float(v.std(ddof=1)), "t": tt[k]["t"],
                  "p": tt[k]["p_one_sided"], "p_holm": ph[k], "ci95_minus_min": ci, "n_positive": int((v > 0).sum())}
        if label:
            out[k]["verdict"] = "bestätigt" if ph[k] < ALPHA and ci[0] >= 0.0 else "nicht bestätigt"
    return out


def verdict(rows: list[dict], n_planned: int, rng: np.random.Generator) -> dict:
    n_tech = sum(1 for r in rows if r.get("technical"))
    if n_tech > 0 or len(rows) != n_planned or n_planned < 3:
        return {"n": len(rows), "n_technical": n_tech, "verdict": "nicht auswertbar"}
    ok = [r for r in rows if r["generalised"]]
    return {"n": len(rows), "n_technical": 0, "n_generalised": len(ok), **test_family(rows, rng, True),
            "descriptive_generalised_only": test_family(ok, rng, False) if len(ok) >= 3 else None}


def analyze(manifest: Path) -> None:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(man, s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"N29b splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [seed_row(man, s) for s in man["seeds"]]
    ok = [r for r in rows if not r.get("technical")]
    out = {"manifest_commit": man["commit"], "min_diff": MIN_DIFF, "n_planned": len(man["seeds"]),
           "hypotheses": verdict(rows, len(man["seeds"]), np.random.default_rng(292)),
           "mean_R": {a: float(np.mean([r[f"R_{a}"] for r in ok])) for a in man["arms"]} if ok else {}, "rows": rows}
    (LAB / "confirm" / "N29b_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    man = {**REGISTERED, "python": "PY"}
    BLOCK.check_registered(man)
    for bad in ({"seeds": list(range(2300, 2319))}, {"budget": 4000.0}, {"t": 25}, {"arms": ["normal", "rsattn"]}):
        try:
            BLOCK.check_registered({**man, **bad})
            raise AssertionError(f"unregistered manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    assert len(tj) == 120 and len(set(tj)) == 120 and all("n29b_raw" in j and "--save-model" in j and "\\" not in j for j in tj)
    for j in tj:
        c = shlex.split(j)
        assert int(c[c.index("--stop-after-gen") + 1]) >= int(c[c.index("--steps") + 1]) == 4050, j
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert ids[0] == "EXP-020_baseline_seed2300_thr1_n29b_seed2300_w0_A_to_n29b_seed2300_w0_B_at50_devcuda", ids[0]
    assert ids[2] == "EXP-020_baseline_seed2300_thr1_n29b_seed2300_w0_A_to_n29b_seed2300_w0_B_at50_rsattn_devcuda", ids[2]
    assert ids[5] == "EXP-020_baseline_seed2300_thr1_n29b_seed2300_w0_B_to_n29b_seed2300_w0_A_at50_rsmlp_devcuda", ids[5]
    assert len(set(ids)) == 120 and "--reset-at-switch" not in tj[0] and tj[2].endswith("--reset-at-switch attn")
    BLOCK.check_job(man, shlex.split(tj[0]))
    try:
        BLOCK.check_job(man, shlex.split(tj[0]) + ["--force"])
        raise AssertionError("foreign command accepted")
    except SystemExit:
        pass
    mk = lambda rn, ra, rm, g=True: {"technical": False, "generalised": g, "R_normal": rn, "R_rsattn": ra, "R_rsmlp": rm}   # noqa: E731
    c = contrasts(mk(0.9, -0.6, 0.8))
    assert abs(c["H1"] - 1.0) < 1e-12 and abs(c["H2"] - 1.1) < 1e-12
    rng = np.random.default_rng(0)
    good = [mk(0.9, -0.6 + 0.01 * i, 0.8) for i in range(20)]
    v = verdict(good, 20, rng)
    assert v["H1"]["verdict"] == "bestätigt" and v["H2"]["verdict"] == "bestätigt", v
    v = verdict([mk(0.9, 0.5 + 0.005 * i, 0.8) for i in range(20)], 20, rng)          # attn reset barely moves reliance
    assert v["H1"]["verdict"] == "nicht bestätigt" and v["H2"]["verdict"] == "nicht bestätigt", v
    v = verdict(good[:15] + [mk(0.9, -0.6, 0.8, g=False)] * 5, 20, rng)
    assert v["n_generalised"] == 15 and all("verdict" not in x for x in v["descriptive_generalised_only"].values())
    assert verdict(good[:19], 20, rng)["verdict"] == "nicht auswertbar"
    assert verdict(good[:19] + [{"seed": 1, "technical": True}], 20, rng)["verdict"] == "nicht auswertbar"
    F, G = ov.targets(2300)
    assert not set(F) & set(G) and len(F) == len(G) == 5
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    g61()
    loaded = {Path(m.__file__).resolve().relative_to(ROOT.resolve()).as_posix() for m in list(sys.modules.values())
              if getattr(m, "__file__", None) and Path(m.__file__).resolve().is_relative_to((ROOT / "lab").resolve())}
    assert loaded <= set(CODE_FILES), sorted(loaded - set(CODE_FILES))
    print("[confirm_n29b] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
