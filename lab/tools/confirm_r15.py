"""R15 confirmation (session 69): does a spectrally constructed training set generalize at the data edge where an equally large
random set does not? Registration: lab/confirm/R15_REGISTRATION.md. Pilot: EXP-140 (add 401, 14 000 pairs, 3 seeds: all three random
arms R without generalization in 30 000 steps, constructed arms of the same seeds at gen_E 5013-6150).

Cells (family of two, Holm): H1 add 401 with N = 14 000 pairs (pilot cell), H2 add 307 with N = 9425 pairs (no R pilot; E pilot
EXP-137 / R14: all arms generalize, gen 5850-23 000). Unit = seed with arms F, G (constructed, eps 2, disjoint targets) and R (same
construction with eps 0 = uniform random subset of exactly N pairs); same init for all three arms of a seed. Splits: P1 construction
(confirm_splits) with experiment id 15 and train fraction N / p^2 (confirm_splits.TRAIN_FRAC overridden only inside build()).
Trainer: freq_ban.py (unchanged), full batch, at most 30 000 steps, stop 2000 steps after generalization.
Per arm: g = transitions.primary.generalization.first_crossing_step, censored at 30 000 if None (a lower bound for that arm).
Per seed: g_E = mean of the censored g_F and g_G; L = ln(g_R / g_E) (censored values -> L is a lower bound when only R fails,
0 when all fail). Test per cell: exact one-sided sign-flip test of mean L > 0 (n = 10, 2^10 patterns), Holm over the two cells,
95 % bootstrap CI of mean L. Cell "bestaetigt" if Holm-p < 0.05 AND CI lower bound > 0 AND L > 0 in >= 9 of 10 seeds
(one-sided binomial p 0.011). Pre-stated description of a confirmed cell: "ermoeglicht" if R generalizes in <= 2 of 10 seeds and
both E arms in >= 8 of 10, else "beschleunigt". Any technical failure (missing, unbound, config, stop rule) -> "nicht auswertbar".

  python lab/tools/confirm_r15.py --selftest
  python lab/tools/confirm_r15.py --splits|--jobs|--analyze lab/confirm/R15_manifest.json
"""
from __future__ import annotations

import json
import math
import shlex
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
import confirm_p1 as c1  # noqa: E402  (read-only reuse: sign_flip_p, boot_ci, holm, interp)
import confirm_splits as cs  # noqa: E402
from bound_block import Block, selftest_binding, sha  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

RAW = LAB / "confirm" / "r15_raw"
BIND = LAB / "confirm" / "r15_bindings"
SPL = LAB / "confirm" / "r15_splits"
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"
CELLS = {401: 14000, 307: 9425}            # H1 (pilot cell), H2 (generality, no R pilot)
ALPHA, EPS, EXPERIMENT, ARMS = 0.05, 2.0, 15, "FGR"
N_SEEDS, SEEDS = 10, list(range(4500, 4510))
MIN_POSITIVE = 9                           # >= 9/10 seeds with L > 0 (one-sided binomial p = 0.011)
STEPS, STOP_AFTER_GEN = 30_000, 2000
SNAPS = [50, 250, 500, *range(1000, STEPS + 1, 1000)]
REGISTERED = {"experiment": EXPERIMENT, "cells": {str(p): n for p, n in CELLS.items()}, "eps": EPS, "device": "cuda", "threads": 1,
              "steps": STEPS, "stop_after_gen": STOP_AFTER_GEN}
CODE_FILES = ("lab/tools/confirm_r15.py", "lab/tools/bound_block.py", "lab/tools/confirm_p1.py", "lab/tools/confirm_splits.py",
              "lab/tools/result_loader.py", "lab/tools/trainer_guard.py", "lab/tools/paket_a_device.py", FB,
              "lab/experiments/EXP-043-generalize-steering/make_split.py", "lab/experiments/EXP-043-generalize-steering/analyze.py",
              "lab/experiments/EXP-046-dihedral-steering/make_split.py", "lab/experiments/EXP-046-dihedral-steering/dihedral.py")


def frac(p: int) -> float:
    return CELLS[p] / (p * p)


# ---------------------------------------------------------------- splits
def build(p: int, s: int, arm: str) -> tuple[np.ndarray, dict[str, list[int]]]:
    old = cs.TRAIN_FRAC
    cs.TRAIN_FRAC = frac(p)
    try:
        idx, _ = cs.build(EXPERIMENT, "add", p, s, arm, EPS)
    finally:
        cs.TRAIN_FRAC = old
    return idx, cs.target_sets(EXPERIMENT, "add", p, s)


def check_design(man: dict) -> None:
    s = man.get("seeds")
    if not isinstance(s, list) or s != SEEDS or not all(type(x) is int for x in s):
        raise SystemExit(f"R15 manifest: seeds must be exactly {SEEDS[0]}-{SEEDS[-1]}")


def stem(p: int, s: int, arm: str) -> str:
    return f"r15_add{p}_seed{s}_{arm}"


def mask_top5(idx: np.ndarray, p: int) -> list[int]:
    pw = cs.m0(idx, "add", p)
    return sorted(int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:5])


def write_splits(man: dict) -> None:
    check_design(man)
    SPL.mkdir(parents=True, exist_ok=True)
    if any((SPL / f"{stem(p, s, a)}{e}").exists() for p in CELLS for s in SEEDS for a in ARMS for e in (".npy", ".json")):
        raise SystemExit("R15 splits exist already: never overwrite")
    for p in CELLS:
        for s in SEEDS:
            for a in ARMS:
                idx, T = build(p, s, a)
                if len(idx) != CELLS[p] or len(np.unique(idx)) != len(idx):
                    raise SystemExit(f"R15 split {stem(p, s, a)}: bad size")
                with open(SPL / f"{stem(p, s, a)}.npy", "xb") as f:
                    np.save(f, idx.astype(np.int64))
                with open(SPL / f"{stem(p, s, a)}.json", "x", encoding="utf-8") as f:
                    json.dump({"p": p, "seed": s, "arm": a, "targets": T["G" if a == "G" else "F"], "eps": 0.0 if a == "R" else EPS,
                               "n": int(len(idx)), "mask_top5": mask_top5(idx, p), "manifest_commit": man["commit"]}, f, indent=1)


def split_mismatch(p: int, s: int) -> str | None:
    for a in ARMS:
        idx, _ = build(p, s, a)
        f = SPL / f"{stem(p, s, a)}.npy"
        if not f.exists() or not np.array_equal(np.load(f), idx.astype(np.int64)):
            return f"{stem(p, s, a)}: split missing or differs from the deterministic rebuild"
    return None


# ---------------------------------------------------------------- jobs and binding
def job(man: dict, p: int, s: int, a: str) -> str:
    return (f"{c1.interp(man)} {FB} --seed {s} --condition baseline --steps {man['steps']} --stop-after-gen {man['stop_after_gen']} "
            f"--threads {man['threads']} --device {man['device']} --p {p} --task add --train-frac {frac(p)!r} "
            f"--split-file lab/confirm/r15_splits/{stem(p, s, a)}.npy --spectra-at {','.join(str(x) for x in SNAPS)} "
            f"--out-root lab/confirm/r15_raw")


def trainer_jobs(man: dict) -> list[str]:
    return [job(man, p, s, a) for p in CELLS for s in man["seeds"] for a in ARMS]


def expected_run_id(cmd: list[str]) -> str:
    """freq_ban.py rule as observed in EXP-139/140/141: EXP-043_baseline_seed<s>_thr<t>_<stem>_add<p>_tf<frac!r>_dev<dev>."""
    g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None   # noqa: E731
    sp, s, dev = Path(g("--split-file")).stem, g("--seed"), (g("--device") or "cpu").replace(":", "")
    if not sp.startswith("r15_") or g("--p") not in {str(p) for p in CELLS} or g("--train-frac") is None:
        raise SystemExit(f"R15: command does not match the R15 trainer call: {' '.join(cmd)[:120]}")
    return f"EXP-043_baseline_seed{s}_thr{g('--threads')}_{sp}_add{g('--p')}_tf{float(g('--train-frac'))!r}" + ("" if dev == "cpu" else f"_dev{dev}")


def run_dir(cmd: list[str]) -> Path:
    return RAW / expected_run_id(cmd)


BLOCK = Block(name="confirm_r15", raw=RAW, bind=BIND, code_files=CODE_FILES, registered=REGISTERED, trainer_jobs=trainer_jobs,
              run_dir=run_dir, script="lab/tools/confirm_r15.py")


# ---------------------------------------------------------------- analysis
def stop_mismatch(done: object, gen: object, man: dict) -> str | None:
    want = man["steps"] if gen is None else min(man["steps"], int(gen) + man["stop_after_gen"])
    return None if done == want else f"steps_completed {done!r} inconsistent with the stop rule (expected {want})"


def run_info(man: dict, p: int, s: int, arm: str) -> dict | str:
    split = SPL / f"{stem(p, s, arm)}.npy"
    d = run_dir(shlex.split(job(man, p, s, arm)))
    if not d.exists():
        return "fehlt"
    if (why := BLOCK.unbound(man, d)):
        return f"defekt: {why}"
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=man["steps"], min_steps_completed=1, split_file=split,
                           config={"p": p, "task": "add", "arch": "transformer", "train_frac": frac(p)}))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    if L.res.get("fingerprint_fields", {}).get("split_file_sha256") != sha(split):
        return "defekt: split bytes differ"
    gen = ((L.res.get("transitions") or {}).get("primary") or {}).get("generalization", {}).get("first_crossing_step")
    if (why := stop_mismatch(L.res.get("steps_completed"), gen, man)):
        return f"defekt: {why}"
    return {"gen": gen, "test_acc": (L.res.get("final_acc") or {}).get("test")}


def seed_row(man: dict, p: int, s: int) -> dict:
    R = {a: run_info(man, p, s, a) for a in ARMS}
    bad = [f"{a}: {v}" for a, v in R.items() if isinstance(v, str)]
    if bad:
        return {"seed": s, "technical": True, "reason": "; ".join(bad)}
    c = {a: man["steps"] if R[a]["gen"] is None else R[a]["gen"] for a in ARMS}
    g_e = (c["F"] + c["G"]) / 2
    return {"seed": s, "technical": False, "gen": {a: R[a]["gen"] for a in ARMS}, "test_acc": {a: R[a]["test_acc"] for a in ARMS},
            "g_E": g_e, "L": math.log(c["R"] / g_e), "R_generalised": R["R"]["gen"] is not None,
            "E_both_generalised": R["F"]["gen"] is not None and R["G"]["gen"] is not None}


def cell_stats(rows: list[dict], rng: np.random.Generator) -> dict:
    if len(rows) != N_SEEDS or any(r.get("technical") for r in rows):
        return {"technical": True, "n": len(rows), "n_technical": sum(bool(r.get("technical")) for r in rows)}
    L = np.array([r["L"] for r in rows])
    return {"technical": False, "n": len(L), "mean_L": float(L.mean()), "ci95_L": c1.boot_ci(L, rng), "p": c1.sign_flip_p(L, rng),
            "n_positive": int((L > 0).sum()), "n_R_generalised": sum(r["R_generalised"] for r in rows),
            "n_E_both": sum(r["E_both_generalised"] for r in rows), "median_g_E": float(np.median([r["g_E"] for r in rows]))}


def verdict(stats: dict[int, dict]) -> dict:
    if any(st["technical"] for st in stats.values()):
        return {"verdict": "nicht auswertbar", "cells": {str(p): st for p, st in stats.items()}}
    adj = c1.holm({str(p): st["p"] for p, st in stats.items()})
    out = {}
    for p, st in stats.items():
        ok = adj[str(p)] < ALPHA and st["ci95_L"][0] > 0 and st["n_positive"] >= MIN_POSITIVE
        desc = ("ermöglicht" if st["n_R_generalised"] <= 2 and st["n_E_both"] >= 8 else "beschleunigt") if ok else None
        out[str(p)] = {**st, "p_holm": adj[str(p)], "verdict": "bestätigt" if ok else "nicht bestätigt", "description": desc}
    return {"verdict": {"H1_401": out["401"]["verdict"], "H2_307": out["307"]["verdict"]}, "cells": out}


def analyze(manifest: Path) -> None:
    out_f = LAB / "confirm" / "R15_summary.json"
    if out_f.exists():
        out_f.unlink()
    man = json.loads(manifest.read_text(encoding="utf-8"))
    BLOCK.check_manifest(manifest, man)
    check_design(man)
    bad = [m for m in (split_mismatch(p, s) for p in CELLS for s in man["seeds"]) if m]
    if bad:
        raise SystemExit(f"R15 splits differ from the registered construction, confirmation void: {bad[:3]}")
    rows = {p: [seed_row(man, p, s) for s in man["seeds"]] for p in CELLS}
    rng = np.random.default_rng(15)
    out = {"manifest_commit": man["commit"], "result": verdict({p: cell_stats(rows[p], rng) for p in CELLS}),
           "rows": {str(p): r for p, r in rows.items()}}
    out_f.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out["result"], indent=1, ensure_ascii=False))


def selftest() -> None:
    for bad in ({"seeds": SEEDS[:9]}, {"seeds": list(range(4430, 4440))}, {"seeds": [float(x) for x in SEEDS]}):
        try:
            check_design(bad)
            raise AssertionError("bad seeds accepted")
        except SystemExit:
            pass
    man = {**REGISTERED, "python": "PY", "seeds": SEEDS}
    BLOCK.check_registered(man)
    tj = trainer_jobs(man)
    assert len(tj) == 60 and len(set(tj)) == 60 and all("r15_raw" in j and "\\" not in j for j in tj)
    ids = [expected_run_id(shlex.split(j)) for j in tj]
    assert len(set(ids)) == 60
    assert ids[0] == f"EXP-043_baseline_seed4500_thr1_r15_add401_seed4500_F_add401_tf{14000 / 401 ** 2!r}_devcuda", ids[0]
    assert "--p 401 --task add" in tj[0] and "--stop-after-gen 2000" in tj[0] and ",29000,30000 " in tj[0]
    assert sum("--p 307 " in j for j in tj) == 30 and f"--train-frac {9425 / 307 ** 2!r} " in tj[30]
    # splits: sizes exact, fraction restored, fresh streams; constructed arms carry their targets in the mask, R does not favour F
    for p in CELLS:
        T = cs.target_sets(EXPERIMENT, "add", p, 4500)
        assert not set(T["F"]) & set(T["G"]) and T != cs.target_sets(14, "add", p, 4500)
        idx = {a: build(p, 4500, a)[0] for a in ARMS}
        assert cs.TRAIN_FRAC == 0.3 and all(len(v) == CELLS[p] == len(np.unique(v)) for v in idx.values())
        assert len({v.tobytes() for v in idx.values()}) == 3
        assert mask_top5(idx["F"], p) == T["F"] and mask_top5(idx["G"], p) == T["G"], (p, mask_top5(idx["F"], p), T)
        assert len(set(mask_top5(idx["R"], p)) & set(T["F"])) <= 1
    # verdict on synthetic rows
    rng = np.random.default_rng(0)
    row = lambda s, gr, gf=5000, gg=6000: {"seed": s, "technical": False, "g_E": (gf + gg) / 2, "L": math.log((gr or 30000) / ((gf + gg) / 2)),  # noqa: E731
                                           "R_generalised": gr is not None, "E_both_generalised": True}
    enable = [row(s, None) for s in SEEDS]
    late = [row(s, 20000) for s in SEEDS]
    same = [row(s, 5500 + 100 * ((-1) ** i)) for i, s in enumerate(SEEDS)]
    v = verdict({401: cell_stats(enable, rng), 307: cell_stats(late, rng)})
    assert v["verdict"] == {"H1_401": "bestätigt", "H2_307": "bestätigt"}, v
    assert v["cells"]["401"]["description"] == "ermöglicht" and v["cells"]["307"]["description"] == "beschleunigt"
    assert v["cells"]["401"]["p"] == 1 / 2 ** 10 and v["cells"]["401"]["p_holm"] == 2 / 2 ** 10
    v = verdict({401: cell_stats(enable, rng), 307: cell_stats(same, rng)})
    assert v["verdict"] == {"H1_401": "bestätigt", "H2_307": "nicht bestätigt"}, v
    eight = enable[:8] + [row(s, 4000) for s in SEEDS[8:]]
    assert verdict({401: cell_stats(eight, rng), 307: cell_stats(enable, rng)})["verdict"]["H1_401"] == "nicht bestätigt"
    nine = enable[:9] + [row(s, 4000) for s in SEEDS[9:]]
    assert verdict({401: cell_stats(nine, rng), 307: cell_stats(enable, rng)})["verdict"]["H1_401"] == "bestätigt"
    allfail = [{**row(s, None, 30000, 30000), "E_both_generalised": False} for s in SEEDS]
    assert cell_stats(allfail, rng)["n_positive"] == 0
    assert verdict({401: cell_stats(enable[:9], rng), 307: cell_stats(enable, rng)})["verdict"] == "nicht auswertbar"
    m = {"steps": 30000, "stop_after_gen": 2000}
    assert stop_mismatch(30000, None, m) is None and stop_mismatch(8125, 6125, m) is None and stop_mismatch(30000, 29000, m) is None
    assert stop_mismatch(8000, None, m) and stop_mismatch(30000, 6125, m)
    selftest_binding(BLOCK, tj[0], tj[1], tj[2])
    assert set(CODE_FILES) <= set(BLOCK.code_hashes())
    print("[confirm_r15] selftest ok", flush=True)


if __name__ == "__main__":
    BLOCK.cli(sys.argv[1:], analyze, write_splits, selftest)
