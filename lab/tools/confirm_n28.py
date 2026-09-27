"""N28 confirmation (FINDINGS programme B, mechanism of persistence): splits, job list, run binding and frozen analysis. Session 22, UNTESTED.

Registration: lab/confirm/N28_REGISTRATION.md. Own manifest (lab/confirm/N28_manifest.json), own code-hash list, own raw directory,
splits and bindings. Binding and gating: lab/tools/bound_block.py (the confirm_p3 logic, parametrised; confirm_p3.py stays unchanged, frozen with P3).
Multiplicity: one family for the session-22 confirmations {N28-H1, N28-H2, P2b}; Holm with P2b as a p = 1 placeholder (worst case).

Per seed s (fresh block, omega = 0, EXP-053 splits with matched steering strength): pure A, pure B (2000 steps) and the switch runs
A->B, B->A at t for every registered arm (t, part): part "normal" (AdamW state kept) or "m" (exp_avg zeroed at the switch, step and
exp_avg_sq kept; freq_ban --reset-optim-part m). pi(arm) = mean of pi_AB, pi_BA of the final W_E power (EXP-056 / P3 definition).
Primary and secondary quantities: see PRIMARY in the registration and verdict() below.

  python lab/tools/confirm_n28.py --hash-code
  python lab/tools/confirm_n28.py --splits lab/confirm/N28_manifest.json       # after freezing; never overwrites
  python lab/tools/confirm_n28.py --jobs lab/confirm/N28_manifest.json > lab/confirm/N28_jobs.txt
  python lab/tools/confirm_n28.py --run lab/confirm/N28_manifest.json -- <trainer command>
  python lab/tools/confirm_n28.py --analyze lab/confirm/N28_manifest.json      # under guarded_run.py
  python lab/tools/confirm_n28.py --selftest
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

RAW = LAB / "confirm" / "n28_raw"
BIND = LAB / "confirm" / "n28_bindings"
SPL = LAB / "confirm" / "n28_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"
BUDGET, ALPHA, MIN_SEP, OMEGA = 2000, 0.05, 2.0, 0.0
MIN_EFFECT, NI_MARGIN = {"H1": 0.05, "H2": 0.0}, 0.05
REGISTERED = {"seeds": list(range(2200, 2230)), "arms": [["normal", 25], ["m", 25], ["m", 35], ["normal", 50]], "device": "cuda", "threads": 1}
CODE_FILES = ("lab/tools/confirm_n28.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py", "lab/tools/result_loader.py",
              "lab/tools/paket_a_device.py", "lab/experiments/EXP-001-freq-ban/freq_ban.py",
              "lab/experiments/EXP-053-p3-overlap-design/overlap_split.py", "lab/experiments/EXP-053-p3-overlap-design/calibration.json",
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py")

_a43 = None


def a43():
    global _a43
    if _a43 is None:
        spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
        _a43 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_a43)
    return _a43


# ---------------------------------------------------------------- splits and jobs
def stem(s: int, arm: str) -> str:
    return f"n28_seed{s}_w0_{arm}"


def write_splits(man: dict) -> None:
    eps = json.loads(CAL.read_text(encoding="utf-8"))["levels"][str(OMEGA)]["eps"]
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(s, a)}.npy" for s in man["seeds"] for a in "AB"] + [f"n28_seed{s}_test.npy" for s in man["seeds"]]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("N28 splits exist already: never overwrite")
    for s in man["seeds"]:
        F, G = ov.targets(s)
        d = ov.build(s, OMEGA, eps)
        assert len(d["A"]) == len(d["B"]) == ov.N_TRAIN and not np.intersect1d(d["A"], d["B"]).size
        assert not np.intersect1d(d["test"], np.union1d(d["A"], d["B"])).size
        for a in "AB":
            with open(SPL / f"{stem(s, a)}.npy", "xb") as f:
                np.save(f, d[a].astype(np.int64))
        with open(SPL / f"n28_seed{s}_test.npy", "xb") as f:
            np.save(f, d["test"].astype(np.int64))
        with open(SPL / f"n28_seed{s}_w0.json", "x", encoding="utf-8") as f:
            json.dump({"seed": s, "omega": OMEGA, "targets": {"A": F, "B": G}, "share_A_F": ov.share(d["A"], F),
                       "share_B_G": ov.share(d["B"], G), "manifest_commit": man["commit"]}, f, indent=1)


def switch_args(first: str, second: str, t: int, part: str) -> str:
    return (f"--steps {t + BUDGET} --split-file {first} --switch-split-file {second} --switch-step {t} "
            f"--spectra-at {t},{t + 250},{t + BUDGET} --log-update-norms 10" + (" --reset-optim-part m" if part == "m" else ""))


def trainer_jobs(man: dict) -> list[str]:
    out = []
    for s in man["seeds"]:
        base = (f"{c1.interp(man)} {FB} --seed {s} --condition baseline --threads {man['threads']} --device {man['device']} "
                f"--test-file lab/confirm/n28_splits/n28_seed{s}_test.npy --out-root lab/confirm/n28_raw")
        a, b = (f"lab/confirm/n28_splits/{stem(s, x)}.npy" for x in "AB")
        for first in (a, b):
            out.append(f"{base} --steps {BUDGET} --split-file {first} --spectra-at 50,250,{BUDGET}")
        for part, t in man["arms"]:
            for first, second in ((a, b), (b, a)):
                out.append(f"{base} {switch_args(first, second, t, part)}")
    return out


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban run-id rules: --split-file + --test-file (EXP-018), --switch-split-file (EXP-020), --reset-optim-part (EXP-058)."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    s, thr, dev, sp, sw, part = g("--seed"), g("--threads"), g("--device") or "cpu", g("--split-file"), g("--switch-split-file"), g("--reset-optim-part")
    rid = f"EXP-018_baseline_seed{s}_thr{thr}_{Path(sp).stem}"
    if sw is not None:
        rid = f"EXP-020_baseline_seed{s}_thr{thr}_{Path(sp).stem}_to_{Path(sw).stem}_at{g('--switch-step')}"
    if part is not None:
        rid += f"_ro{part}"
    return rid + ("" if dev == "cpu" else f"_dev{dev}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_n28", raw=RAW, bind=BIND, code_files=CODE_FILES + ("lab/tools/bound_block.py",), registered=REGISTERED,
              trainer_jobs=trainer_jobs, run_dir=run_dir, script="lab/tools/confirm_n28.py")


# ---------------------------------------------------------------- analysis
def logratio(pw: np.ndarray, F: list[int], G: list[int]) -> float:
    return float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))


def pi_pair(L: dict[str, float], LAB_: float, LBA: float) -> float:
    return ((LAB_ - L["B"]) / (L["A"] - L["B"]) + (LBA - L["A"]) / (L["B"] - L["A"])) / 2


def arm_key(part: str, t: int) -> str:
    return f"{part}{t}"


def load_final(man: dict, s: int, first: str, second: str | None, t: int | None, part: str | None) -> np.ndarray | str:
    """Final W_E of one run through the shared loader + N28 binding (hash -> load -> hash)."""
    dev = man["device"]
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", dev, "--split-file", str(SPL / f"{stem(s, first)}.npy")]
    if second:
        cmd += ["--switch-split-file", str(SPL / f"{stem(s, second)}.npy"), "--switch-step", str(t)]
        if part == "m":
            cmd += ["--reset-optim-part", "m"]
    d = run_dir(cmd)
    steps = BUDGET + (t if second else 0)
    tag = f"{first}{second or ''}{'' if not second else '@' + arm_key(part, t)}"
    if not d.exists():
        return f"{tag}: fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"{tag}: defekt: {why}"
    split = SPL / f"{stem(s, first)}.npy"
    L = load_run(d, Expect(seed=s, device=dev, max_steps=steps, split_file=split, test_file=SPL / f"n28_seed{s}_test.npy",
                           switch_file=SPL / f"{stem(s, second)}.npy" if second else None, config={"p": 113, "task": "add"},
                           snapshots_at=(steps,)))
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(split):
        return f"{tag}: defekt after load: {why or 'split bytes differ'}"
    if part == "m" and L.res.get("events", {}).get("reset_optim_part", {}).get("check") is not True:
        return f"{tag}: defekt: partial reset not recorded"
    return np.asarray(L.snapshot(steps), dtype=np.float64)


def split_mismatch(man: dict, s: int) -> str | None:
    """Codex s22 (P2b blocker 1, same risk here): rebuild the splits and targets deterministically and compare."""
    eps = json.loads(CAL.read_text(encoding="utf-8"))["levels"][str(OMEGA)]["eps"]
    F, G = ov.targets(s)
    d = ov.build(s, OMEGA, eps)
    meta_f = SPL / f"n28_seed{s}_w0.json"
    if not meta_f.exists():
        return f"seed {s}: split metadata missing"
    meta = json.loads(meta_f.read_text(encoding="utf-8"))
    files = {"A": SPL / f"{stem(s, 'A')}.npy", "B": SPL / f"{stem(s, 'B')}.npy", "test": SPL / f"n28_seed{s}_test.npy"}
    if not all(f.exists() for f in files.values()):
        return f"seed {s}: split file missing"
    if not all(np.array_equal(np.load(f), d[k].astype(np.int64)) for k, f in files.items()) or meta.get("targets") != {"A": F, "B": G}:
        return f"seed {s}: splits differ from the deterministic rebuild"
    return None


def seed_row(man: dict, s: int) -> dict:
    meta = json.loads((SPL / f"n28_seed{s}_w0.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    gp = lambda W: a43().group_power(W, "add", 113)[0]   # noqa: E731
    W = {"A": load_final(man, s, "A", None, None, None), "B": load_final(man, s, "B", None, None, None)}
    for part, t in man["arms"]:
        for first, second in (("A", "B"), ("B", "A")):
            W[(arm_key(part, t), first + second)] = load_final(man, s, first, second, t, part)
    bad = [v for v in W.values() if isinstance(v, str)]
    if bad:
        return {"seed": s, "valid": False, "reason": "; ".join(bad[:4]), "n_bad": len(bad)}
    L = {"A": logratio(gp(W["A"]), F, G), "B": logratio(gp(W["B"]), F, G)}
    pis = {}
    for part, t in man["arms"]:
        k = arm_key(part, t)
        lab_, lba = logratio(gp(W[(k, "AB")]), F, G), logratio(gp(W[(k, "BA")]), F, G)
        if not (np.isfinite(lab_) and np.isfinite(lba)):
            return {"seed": s, "valid": False, "reason": f"non-finite L in {k}"}
        pis[k] = pi_pair(L, lab_, lba)
    if not all(np.isfinite(v) for v in L.values()):
        return {"seed": s, "valid": False, "reason": "non-finite L", "L": L}
    if not L["A"] - L["B"] >= MIN_SEP:
        return {"seed": s, "valid": False, "reason": f"L(A) - L(B) < {MIN_SEP}", "L": L}
    return {"seed": s, "valid": True, "L": L, "pi": pis}


def contrasts(pi: dict[str, float]) -> dict[str, float]:
    """H1: pi_normal(25) - pi_m(25) > 0.05 (zeroing m lowers persistence).
    H2 (after EXP-059, non-inferiority): pi_m(35) - pi_normal(25) + NI_MARGIN > 0, i.e. 10 extra plain A steps with m zeroed reach at
    least the persistence of the normal switch at 25 minus 0.05 (the momentum tail acts like prolonged exposure)."""
    return {"H1": pi["normal25"] - pi["m25"], "H2": pi["m35"] - pi["normal25"] + NI_MARGIN}


def verdict(X: dict[str, np.ndarray], n_planned: int, rng: np.random.Generator) -> dict:
    if any(len(v) != n_planned for v in X.values()):
        return {"verdict": "nicht auswertbar"}
    tt = {k: c1.t_test_secondary(v) for k, v in X.items()}
    ph = c1.holm({**{k: t["p_one_sided"] for k, t in tt.items()}, "_P2b": 1.0})
    out = {}
    for k, v in X.items():
        ci = c1.boot_ci(v, rng)
        out[k] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)), "t": tt[k]["t"], "p": tt[k]["p_one_sided"], "p_holm": ph[k],
                  "ci95": ci, "n_positive": int((v > 0).sum()),
                  "verdict": "bestätigt" if ph[k] < ALPHA and ci[0] >= MIN_EFFECT[k] else "nicht bestätigt"}
    return out


def analyze(manifest: Path) -> None:
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for m in (split_mismatch(man, s) for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"N28 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = [seed_row(man, s) for s in man["seeds"]]
    ok = [r for r in rows if r["valid"]]
    X = {k: np.array([contrasts(r["pi"])[k] for r in ok]) for k in MIN_EFFECT}
    out = {"manifest_commit": man["commit"], "min_effect": MIN_EFFECT, "n_valid": len(ok), "n_planned": len(man["seeds"]),
           "hypotheses": verdict(X, len(man["seeds"]), np.random.default_rng(28))}
    out["pi_mean"] = {arm_key(p, t): float(np.mean([r["pi"][arm_key(p, t)] for r in ok])) for p, t in man["arms"]} if ok else {}
    out["rows"] = rows
    (LAB / "confirm" / "N28_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    man = {**REGISTERED, "seeds": [2200], "python": "PY"}
    try:
        BLOCK.check_registered(man)
        raise AssertionError("unregistered seed list accepted")
    except SystemExit:
        pass
    BLOCK.check_registered({**man, "seeds": list(range(2200, 2230))})
    for bad in ({"seeds": [float(x) for x in range(2200, 2230)]}, {"arms": [["normal", 25.0], ["m", 25], ["m", 35], ["normal", 50]]}, {"threads": True}):
        try:
            BLOCK.check_registered({**man, "seeds": list(range(2200, 2230)), **bad})
            raise AssertionError(f"type-sloppy manifest accepted: {bad}")
        except SystemExit:
            pass
    tj = trainer_jobs(man)
    assert len(tj) == 2 + 2 * len(REGISTERED["arms"]) and all("n28_raw" in j and "\\" not in j for j in tj)
    assert all(j.startswith("python lab/tools/confirm_n28.py --run M -- ") for j in BLOCK.jobs(man, "M"))
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert ids[0] == "EXP-018_baseline_seed2200_thr1_n28_seed2200_w0_A_devcuda", ids[0]
    assert ids[2] == "EXP-020_baseline_seed2200_thr1_n28_seed2200_w0_A_to_n28_seed2200_w0_B_at25_devcuda", ids[2]
    assert ids[5] == "EXP-020_baseline_seed2200_thr1_n28_seed2200_w0_B_to_n28_seed2200_w0_A_at25_rom_devcuda", ids[5]
    assert ids[6] == "EXP-020_baseline_seed2200_thr1_n28_seed2200_w0_A_to_n28_seed2200_w0_B_at35_rom_devcuda", ids[6]
    assert len(set(ids)) == len(ids)
    assert "--steps 2035" in tj[6] and "--spectra-at 35,285,2035" in tj[6] and tj[6].endswith("--reset-optim-part m")
    assert "--reset-optim" not in tj[2] and "--reset-optim" not in tj[0]
    BLOCK.check_job(man, shlex.split(tj[0]))
    try:
        BLOCK.check_job(man, shlex.split(tj[0]) + ["--force"])
        raise AssertionError("foreign command accepted")
    except SystemExit:
        pass
    L = {"A": 2.0, "B": -2.0}
    assert pi_pair(L, 0.0, 0.0) == 0.5 and pi_pair(L, 2.0, -2.0) == 1.0 and pi_pair(L, -2.0, 2.0) == 0.0
    c = contrasts({"normal25": 0.3, "m25": 0.1, "m35": 0.2, "normal50": 1.0})
    assert abs(c["H1"] - 0.2) < 1e-12 and abs(c["H2"] - (-0.05)) < 1e-12
    assert "--steps 2050" in tj[8] and "--reset-optim" not in tj[8] and "at50" in expected_run_id(shlex.split(tj[9]))
    rng = np.random.default_rng(0)
    assert verdict({"H1": np.full(29, 0.3), "H2": np.full(30, 0.3)}, 30, rng)["verdict"] == "nicht auswertbar"
    v = verdict({"H1": np.linspace(0.1, 0.4, 30), "H2": np.linspace(-0.03, 0.03, 30)}, 30, rng)
    assert v["H1"]["verdict"] == "bestätigt" and v["H2"]["verdict"] == "nicht bestätigt", v
    assert v["H1"]["p"] < v["H2"]["p"] and abs(v["H1"]["p_holm"] - 3 * v["H1"]["p"]) < 1e-12, v     # worst case with the P2b placeholder
    selftest_binding(BLOCK, tj[4], tj[1], tj[5])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    print("[confirm_n28] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
