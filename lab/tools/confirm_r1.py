"""R1 confirmation (rule 19a robustness of K2): does split steering (P1 measure Delta_pow at step 2000, add 113) hold when exactly one
hyperparameter differs from the preset (lr, weight decay, train fraction)? Session 24, UNTESTED (selftest and Codex before freezing).

Registration draft: lab/confirm/R1_REGISTRATION_DRAFT.md. Six cells, one deviation each; unit = seed with an F/G pair (same init for F and G,
as P1); experiment id 8 (own SeedSequence streams via confirm_splits.rng_for); fresh seeds per cell (disjoint across cells).
Splits: the P1 construction (confirm_splits.weights_cyclic + key draw) with the train size round(f * 113^2) as a PARAMETER (confirm_splits.py
itself is not changed: its hash is frozen in older manifests). For train_frac cells eps is calibrated beforehand on calibration seeds so
that the mean M0 target share equals the share at the standard (f = 0.3, eps = 2.0); calibrated eps values go into the manifest.
Verdict per cell: all planned pairs valid, Holm-p (over the 6 cells) of the exact one-sided sign-flip test < 0.05 AND bootstrap CI lower
bound >= MIN_EFFECT (1.0, as P1); any technical failure -> "nicht auswertbar" (p = 1 in the family).

  python lab/tools/confirm_r1.py --selftest
  python lab/tools/confirm_r1.py --calibrate                    # prints eps per train_frac cell (calibration seeds only, numpy)
  python lab/tools/confirm_r1.py --splits|--jobs|--analyze lab/confirm/R1_manifest.json
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

RAW = LAB / "confirm" / "r1_raw"
BIND = LAB / "confirm" / "r1_bindings"
SPL = LAB / "confirm" / "r1_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
P, STEP, ALPHA, MIN_EFFECT, EPS0, FRAC0 = 113, 2000, 0.05, 1.0, 2.0, 0.3
CAL_SEEDS = tuple(range(900, 910))
CAL_EXPERIMENT = 98                                      # calibration streams never used for the block itself
CELLS = {"lr5e-4": {"lr": 5e-4}, "lr2e-3": {"lr": 2e-3}, "wd0.3": {"weight_decay": 0.3}, "wd3": {"weight_decay": 3.0},
         "tf0.2": {"train_frac": 0.2}, "tf0.5": {"train_frac": 0.5}}
FLAG = {"lr": "--lr", "weight_decay": "--weight-decay", "train_frac": "--train-frac"}
TAG = {"lr": "lr", "weight_decay": "wd", "train_frac": "tf"}
REGISTERED = {"experiment": 8, "task": "add", "p": P, "steps": STEP, "device": "cuda", "threads": 1,
              "cells": {k: {**v} for k, v in CELLS.items()}}      # "seeds" (per cell) and "eps" (per cell) are added at registration
CODE_FILES = ("lab/tools/confirm_r1.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py",
              "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py", FB,
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py")


# ---------------------------------------------------------------- splits
def frac_of(cell: str) -> float:
    return float(CELLS[cell].get("train_frac", FRAC0))


def build(experiment: int, s: int, arm: str, eps: float, frac: float) -> tuple[np.ndarray, list[int]]:
    """P1 construction (confirm_splits.draw) with the train size as a parameter."""
    T = cs.target_sets(experiment, "add", P, s)[arm]
    q = cs.weights_cyclic("add", P, T, eps, cs.rng_for(experiment, "add", P, s, arm, "phases"))
    keys = cs.rng_for(experiment, "add", P, s, arm, "keys").random(len(q)) ** (1.0 / q)
    return np.sort(np.argsort(-keys)[:int(round(frac * len(q)))]), T


def target_share(idx: np.ndarray, T: list[int]) -> float:
    pw = cs.m0(idx, "add", P)
    return float(pw[[k - 1 for k in T]].sum() / pw.sum())


def mean_share(eps: float, frac: float) -> float:
    return float(np.mean([target_share(*build(CAL_EXPERIMENT, s, a, eps, frac)) for s in CAL_SEEDS for a in "FG"]))


def calibrate() -> dict[str, float]:
    """eps per train_frac cell so that the mean M0 target share on calibration seeds equals the standard (bisection, monotone in eps)."""
    goal = mean_share(EPS0, FRAC0)
    out = {}
    for cell in CELLS:
        f = frac_of(cell)
        if f == FRAC0:
            out[cell] = EPS0
            continue
        lo, hi = 0.25, 16.0
        for _ in range(30):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if mean_share(mid, f) < goal else (lo, mid)
        out[cell] = round((lo + hi) / 2, 4)
    return {"goal_share": goal, "eps": out}


def stem(cell: str, s: int, arm: str) -> str:
    return f"r1_{cell}_seed{s}_{arm}"


def write_splits(man: dict) -> None:
    SPL.mkdir(parents=True, exist_ok=True)
    names = [f"{stem(c, s, a)}.npy" for c in CELLS for s in man["seeds"][c] for a in "FG"]
    if any((SPL / n).exists() for n in names):
        raise SystemExit("R1 splits exist already: never overwrite")
    for c in CELLS:
        for s in man["seeds"][c]:
            T = cs.target_sets(man["experiment"], "add", P, s)
            for a in "FG":
                idx, targ = build(man["experiment"], s, a, man["eps"][c], frac_of(c))
                assert targ == T[a]
                with open(SPL / f"{stem(c, s, a)}.npy", "xb") as f:
                    np.save(f, idx.astype(np.int64))
                with open(SPL / f"{stem(c, s, a)}.json", "x", encoding="utf-8") as f:
                    json.dump({"cell": c, "seed": s, "arm": a, "targets": T[a], "other_targets": T["G" if a == "F" else "F"],
                               "eps": man["eps"][c], "train_frac": frac_of(c), "n": int(len(idx)), "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(man: dict, c: str, s: int) -> str | None:
    T = cs.target_sets(man["experiment"], "add", P, s)
    for a in "FG":
        idx, targ = build(man["experiment"], s, a, man["eps"][c], frac_of(c))
        f, j = SPL / f"{stem(c, s, a)}.npy", SPL / f"{stem(c, s, a)}.json"
        if not f.exists() or not j.exists():
            return f"{stem(c, s, a)}: split file missing"
        meta = json.loads(j.read_text(encoding="utf-8"))
        if not (np.array_equal(np.load(f), idx.astype(np.int64)) and meta.get("targets") == targ == T[a] and meta.get("seed") == s):
            return f"{stem(c, s, a)}: differs from the deterministic rebuild"
    return None


# ---------------------------------------------------------------- jobs and binding
def hp_flags(c: str) -> str:
    return " ".join(f"{FLAG[k]} {v!r}" for k, v in CELLS[c].items())


def trainer_jobs(man: dict) -> list[str]:
    return [f"{c1.interp(man)} {FB} --seed {s} --condition baseline --steps {man['steps']} --threads {man['threads']} --device {man['device']} "
            f"--split-file lab/confirm/r1_splits/{stem(c, s, a)}.npy --spectra-at {man['steps']} {hp_flags(c)} --out-root lab/confirm/r1_raw"
            for c in CELLS for s in man["seeds"][c] for a in "FG"]


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban: --split-file without --test-file (add 113) -> EXP-016_<cond>_seed<s>_thr<t>_<stem>, then hp suffixes (repr), then _dev."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    rid = f"EXP-016_baseline_seed{g('--seed')}_thr{g('--threads')}_{Path(g('--split-file')).stem}"
    for k in ("lr", "weight_decay", "train_frac"):
        if FLAG[k] in cmd:
            rid += f"_{TAG[k]}{float(g(FLAG[k]))!r}"
    dev = g("--device") or "cpu"
    return rid + ("" if dev == "cpu" else f"_dev{dev.replace(':', '')}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r1", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_r1.py")


# ---------------------------------------------------------------- analysis
def power(man: dict, c: str, s: int, arm: str) -> np.ndarray | str:
    split = SPL / f"{stem(c, s, arm)}.npy"
    cmd = ["x", FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--split-file", str(split)]
    for k, v in CELLS[c].items():
        cmd += [FLAG[k], repr(v)]
    d = run_dir(cmd)
    if not d.exists():
        return "fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"defekt: {why}"
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=man["steps"], split_file=split,
                           config={"p": P, "task": "add", **CELLS[c]}, at=(man["steps"],)))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    if (why := BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(split):
        return f"defekt after load: {why or 'split bytes differ'}"
    pw = np.asarray(L.spectrum(man["steps"]), dtype=np.float64)
    return pw if pw.shape == (56,) and np.all(np.isfinite(pw)) else "defekt: spectrum shape or values"


def seed_row(man: dict, c: str, s: int) -> dict:
    T = {a: json.loads((SPL / f"{stem(c, s, a)}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
    pw = {a: power(man, c, s, a) for a in "FG"}
    bad = [f"{a}: {v}" for a, v in pw.items() if isinstance(v, str)]
    if bad:
        return {"seed": s, "technical": True, "reason": "; ".join(bad)}
    d = c1.delta_pow_checked(pw["F"], pw["G"], T["F"], T["G"])
    return {"seed": s, "technical": d is None, "Delta_pow": d} if d is not None else {"seed": s, "technical": True, "reason": "Delta_pow undefined"}


def verdict(rows: dict[str, list[dict]], n_planned: dict[str, int], rng: np.random.Generator) -> dict:
    out, ps = {}, {}
    for c, rs in rows.items():
        n_tech = sum(1 for r in rs if r.get("technical"))
        if n_tech or len(rs) != n_planned[c] or n_planned[c] < 5:
            out[c], ps[c] = {"n": len(rs), "n_technical": n_tech, "verdict": "nicht auswertbar"}, 1.0
            continue
        D = np.array([r["Delta_pow"] for r in rs])
        p = c1.sign_flip_p(D, rng)
        out[c] = {"n": len(D), "mean": float(D.mean()), "sd": float(D.std(ddof=1)), "p": p, "ci95": c1.boot_ci(D, rng),
                  "n_positive": int((D > 0).sum()), "n_technical": 0}
        ps[c] = p
    ph = c1.holm(ps)
    for c in out:
        if "p" in out[c]:
            out[c]["p_holm"] = ph[c]
            out[c]["verdict"] = "bestätigt" if ph[c] < ALPHA and out[c]["ci95"][0] >= MIN_EFFECT else "nicht bestätigt"
    return out


def analyze(manifest: Path) -> None:
    stale = LAB / "confirm" / "R1_summary.json"
    if stale.exists():
        stale.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    bad = [m for c in CELLS for m in (split_mismatch(man, c, s) for s in man["seeds"][c]) if m]
    if bad:
        raise SystemExit(f"R1 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = {c: [seed_row(man, c, s) for s in man["seeds"][c]] for c in CELLS}
    out = {"manifest_commit": man["commit"], "min_effect": MIN_EFFECT, "eps": man["eps"],
           "cells": verdict(rows, {c: len(man["seeds"][c]) for c in CELLS}, np.random.default_rng(8)), "rows": rows}
    stale.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    seeds = {c: list(range(9000 + 20 * i, 9015 + 20 * i)) for i, c in enumerate(CELLS)}   # placeholder, never a registered block
    man = {**REGISTERED, "python": "PY", "seeds": seeds, "eps": {c: EPS0 for c in CELLS}}
    BLOCK.check_registered(man)
    tj = trainer_jobs(man)
    assert len(tj) == 6 * 15 * 2 and len(set(tj)) == len(tj) and all("r1_raw" in j and "\\" not in j for j in tj)
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert len(set(ids)) == len(ids)
    assert ids[0] == "EXP-016_baseline_seed9000_thr1_r1_lr5e-4_seed9000_F_lr0.0005_devcuda", ids[0]
    assert any(i.endswith("_tf0.2_devcuda") for i in ids) and any(i.endswith("_wd3.0_devcuda") for i in ids)
    # split construction: standard fraction reproduces the P1 draw exactly; other fractions change only the size
    for s, a in ((1, "F"), (2, "G")):
        idx, T = build(9, s, a, EPS0, FRAC0)
        ref, Tr = cs.build(9, "add", P, s, a, EPS0)
        assert np.array_equal(idx, ref) and T == Tr
        assert len(build(9, s, a, EPS0, 0.2)[0]) == round(0.2 * P * P) and len(build(9, s, a, EPS0, 0.5)[0]) == round(0.5 * P * P)
    assert mean_share(4.0, 0.5) > mean_share(1.0, 0.5)                                    # monotone in eps (bisection premise)
    # verdict logic
    rng = np.random.default_rng(0)
    ok = [{"seed": i, "technical": False, "Delta_pow": 5.0 + 0.1 * i} for i in range(15)]
    v = verdict({c: ok for c in CELLS}, {c: 15 for c in CELLS}, rng)
    assert all(x["verdict"] == "bestätigt" for x in v.values()), v
    v = verdict({**{c: ok for c in CELLS}, "wd3": ok[:14]}, {c: 15 for c in CELLS}, rng)
    assert v["wd3"]["verdict"] == "nicht auswertbar" and v["lr2e-3"]["verdict"] == "bestätigt"
    weak = [{"seed": i, "technical": False, "Delta_pow": 0.5 + 0.05 * i} for i in range(15)]
    assert verdict({**{c: ok for c in CELLS}, "tf0.5": weak}, {c: 15 for c in CELLS}, rng)["tf0.5"]["verdict"] == "nicht bestätigt"
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    print("[confirm_r1] selftest ok", flush=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["--calibrate"]:
        print(json.dumps(calibrate(), indent=1))
    else:
        BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
