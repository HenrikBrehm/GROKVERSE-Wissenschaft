"""EXP-016 (design after Nachtrag a): do engineered splits steer the learned frequencies? (UNTESTED)

Per init seed i: two engineered runs with disjoint target sets F_i (arm F) and G_i (arm G), same
construction strength, both trained for a FIXED 2000 steps; K = top-5 of W_E at step 2000
(independent of the test set and of any stopping rule; failures to generalize are irrelevant).
Primary per i: Delta_i = ov(K_F, F) + ov(K_G, G) - ov(K_F, G) - ov(K_G, F).
One-sided sign-flip test over independent init seeds (each seed has its own two runs).
Secondary: EXP-003d baseline top-5 at step 2000 against F and G (random-split reference).
Definition: README.md (Nachtrag a).
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB.parent / "training"))
from grokverse.data import split_hash  # noqa: E402

BASE = LAB / "experiments/EXP-003-early-prediction/raw_d/EXP-001_baseline_t2000_m5_seed{s}_thr4"
RUN = HERE / "raw/EXP-016_baseline_seed{s}_thr4_split_seed{s}_eps2.0{suffix}"
SEEDS = range(10, 20)
ARMS = {"F": "", "G": "_G"}
M, STEP, ALPHA, MIN_VALID = 5, 2000, 0.05, 8


def top_at(d: Path, step: int) -> set[int] | None:
    spec, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
    if step not in steps:
        return None
    pw = spec[steps.index(step)]
    order = np.lexsort((np.arange(len(pw)), -pw))
    return {int(k) + 1 for k in order[:M]}


def row(s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    targets, K = {}, {}
    for arm, suf in ARMS.items():
        stem = f"split_seed{s}_eps2.0{suf}"
        targets[arm] = set(json.loads((HERE / f"splits/{stem}.json").read_text(encoding="utf-8"))["targets"])
        d = Path(str(RUN).format(s=s, suffix=suf))
        if not (d / "result.json").exists():
            r["reason"] = f"missing arm {arm}"
            return r
        res = json.loads((d / "result.json").read_text(encoding="utf-8"))
        if res["status"] != "completed" or res["seed"] != s or res["steps_completed"] < STEP:
            r["reason"] = f"arm {arm}: status/seed/steps"
            return r
        if res["split_hash"] != split_hash(np.load(HERE / f"splits/{stem}.npy")):
            r["reason"] = f"arm {arm}: split content hash mismatch"
            return r
        K[arm] = top_at(d, STEP)
        if K[arm] is None:
            r["reason"] = f"arm {arm}: no spectrum at step {STEP}"
            return r
    F, G = targets["F"], targets["G"]
    ov = {f"{x}{y}": len(K[x] & targets[y]) for x in "FG" for y in "FG"}
    r.update({"valid": True, "F": sorted(F), "G": sorted(G), "K_F": sorted(K["F"]), "K_G": sorted(K["G"]),
              **{f"ov_{k}": v for k, v in ov.items()},
              "Delta": ov["FF"] + ov["GG"] - ov["FG"] - ov["GF"]})
    kb = top_at(Path(str(BASE).format(s=s)), STEP) if (Path(str(BASE).format(s=s)) / "spectra.npy").exists() else None
    if kb is not None:
        r["ov_base_F"], r["ov_base_G"] = len(kb & F), len(kb & G)
    return r


def one_sided_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def main() -> None:
    rows = [row(s) for s in SEEDS]
    valid = [r for r in rows if r["valid"]]
    out: dict = {"rows": rows, "n_valid": len(valid)}
    if len(valid) < MIN_VALID:
        out["verdict"] = "nicht auswertbar"
    else:
        D = np.array([r["Delta"] for r in valid], dtype=float)
        p = one_sided_p(D)
        out.update({"Delta_mean": float(D.mean()), "p": p,
                    "ov_matched_mean": float(np.mean([(r["ov_FF"] + r["ov_GG"]) / 2 for r in valid])),
                    "ov_crossed_mean": float(np.mean([(r["ov_FG"] + r["ov_GF"]) / 2 for r in valid])),
                    "verdict": "widerspricht" if D.mean() <= 0 else
                    ("steuerbar" if p < ALPHA else "richtungsgleich, nicht signifikant")})
        base = [r for r in valid if "ov_base_F" in r]
        if base:
            out["baseline_ov_mean"] = float(np.mean([(r["ov_base_F"] + r["ov_base_G"]) / 2 for r in base]))
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
