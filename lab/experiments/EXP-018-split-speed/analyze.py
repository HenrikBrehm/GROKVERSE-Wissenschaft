"""EXP-018: does a spectrally concentrated train split speed up grokking? (UNTESTED on real runs)

Per init seed i in 20..29: arms E (concentrated mask spectrum), D (equal-strength spread modulation), R (uniform),
all evaluated on the same held-out test set T*_i. gen = first eval step with test acc >= threshold (primary 0.95),
censored at CAP. Primary: L_i = log2(gen_D / gen_E), one-sided sign-flip test over seeds. Definition: README.md.
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

RUN = HERE / "raw/EXP-018_baseline_seed{s}_thr4_seed{s}_train_{arm}"
SEEDS = range(20, 30)
ARMS = ("E", "D", "R")
THRESHOLDS = {"primary": 0.95, "sens_loose": 0.90, "sens_strict": 0.99}
M, CAP, ALPHA, MIN_VALID = 5, 8000, 0.05, 8


def gen_step(res: dict, thr: float) -> int:
    for step, acc in zip(res["dense"]["test_steps"], res["dense"]["test_acc"]):
        if acc >= thr:
            return int(step)
    return CAP                                        # censored (conservative, see README)


def top_at(d: Path, step: int) -> list[int]:
    spec, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy")
    j = int(np.searchsorted(steps, step, side="right")) - 1      # last spectrum at or before step
    pw = spec[max(j, 0)]
    return sorted(int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:M])


def row(s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    F = set(json.loads((HERE / f"splits/seed{s}.json").read_text(encoding="utf-8"))["targets"])
    test_hash = split_hash(np.load(HERE / f"splits/seed{s}_test.npy"))
    for arm in ARMS:
        d = Path(str(RUN).format(s=s, arm=arm))
        if not (d / "result.json").exists():
            r["reason"] = f"missing arm {arm}"
            return r
        res = json.loads((d / "result.json").read_text(encoding="utf-8"))
        if res["status"] != "completed" or res["seed"] != s:
            r["reason"] = f"arm {arm}: status/seed"
            return r
        if res["split_hash"] != split_hash(np.load(HERE / f"splits/seed{s}_train_{arm}.npy")):
            r["reason"] = f"arm {arm}: split content hash mismatch"
            return r
        if res.get("test_hash") != test_hash:
            r["reason"] = f"arm {arm}: test set differs"
            return r
        for name, thr in THRESHOLDS.items():
            r[f"gen_{arm}_{name}"] = gen_step(res, thr)
        g = r[f"gen_{arm}_primary"]
        r[f"ov_F_{arm}_gen"] = len(set(top_at(d, g)) & F)
        r[f"ov_F_{arm}_2000"] = len(set(top_at(d, 2000)) & F) if g >= 2000 else None
    for name in THRESHOLDS:
        g = {arm: r[f"gen_{arm}_{name}"] for arm in ARMS}
        r[f"L_DE_{name}"] = float(np.log2(g["D"] / g["E"]))
        r[f"L_RE_{name}"] = float(np.log2(g["R"] / g["E"]))
        r[f"L_RD_{name}"] = float(np.log2(g["R"] / g["D"]))
    r["valid"] = True
    return r


def one_sided_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def contrast(valid: list[dict], key: str) -> dict:
    x = np.array([r[key] for r in valid])
    return {"mean": float(x.mean()), "sd": float(x.std(ddof=1)) if len(x) > 1 else None,
            "p_one_sided": one_sided_p(x), "n": len(x)}


def main() -> None:
    rows = [row(s) for s in SEEDS]
    valid = [r for r in rows if r["valid"]]
    out: dict = {"rows": rows, "n_valid": len(valid)}
    if len(valid) < MIN_VALID:
        out["verdict"] = "nicht auswertbar"
    else:
        prim = contrast(valid, "L_DE_primary")
        out["primary_L_DE"] = prim
        out["verdict"] = ("widerspricht" if prim["mean"] <= 0 else
                          "beschleunigt" if prim["p_one_sided"] < ALPHA else "richtungsgleich, nicht signifikant")
        out["secondary"] = {f"{c}_{t}": contrast(valid, f"{c}_{t}")
                            for c in ("L_DE", "L_RE", "L_RD") for t in THRESHOLDS
                            if not (c == "L_DE" and t == "primary")}
        out["censored"] = {arm: sum(r[f"gen_{arm}_primary"] >= CAP for r in valid) for arm in ARMS}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print({k: v for k, v in r.items() if not k.startswith("L_") or k.endswith("primary")})


if __name__ == "__main__":
    main()
