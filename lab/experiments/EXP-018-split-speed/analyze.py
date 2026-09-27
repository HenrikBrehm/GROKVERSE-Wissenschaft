"""EXP-018: does a spectrally concentrated train split speed up grokking? (UNTESTED on real runs)

Per init seed i in 20..29: arms E (concentrated mask spectrum), D (equal-strength spread modulation), R (uniform),
all evaluated on the same held-out test set T*_i. gen = first eval step with test acc >= threshold (primary 0.95).
Nachtrag a (Codex review 2026-09-26): a run without a crossing is censored at its LAST evaluated step (not at CAP);
for the primary threshold such a run is only valid if it ran to CAP. Primary endpoint is the restricted (capped)
time: L_i = log2(min(gen_D, CAP) / min(gen_E, CAP)), one-sided sign-flip test; co-condition: censoring-robust
paired sign test over the seeds whose order is determined. Definition: README.md.
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
RUN_CUDA = HERE / "raw/EXP-018_baseline_seed{s}_thr1_seed{s}_train_{arm}_devcuda"   # Nachtrag c (session 30): GPU variant
DEVICE = "cpu"                                                                      # set by --device in main(); never mixed
SEEDS = range(20, 30)
ARMS = ("E", "D", "R")
THRESHOLDS = {"primary": 0.95, "sens_loose": 0.90, "sens_strict": 0.99}
M, CAP, ALPHA, MIN_VALID = 5, 8000, 0.05, 8
STOP_AFTER, EVAL_EVERY = 25, 25


def gen_step(res: dict, thr: float) -> tuple[int, bool]:
    """(step, observed). Without a crossing: (last evaluated test step, False) = right-censored there."""
    steps, accs = res["dense"]["test_steps"], res["dense"]["test_acc"]
    for step, acc in zip(steps, accs):
        if acc >= thr:
            return int(step), True
    return int(steps[-1]), False


def order_sign(e: tuple[int, bool], d: tuple[int, bool]) -> int | None:
    """+1 if E crossed strictly before D, -1 if after, None if tied or undetermined under censoring."""
    (ge, oe), (gd, od) = e, d
    if oe and od:
        return None if ge == gd else (1 if ge < gd else -1)
    if oe and ge < gd:        # D censored at gd, E already crossed before
        return 1
    if od and gd < ge:
        return -1
    return None


def protocol_error(res: dict, s: int) -> str | None:
    want = {"exp_id": "EXP-018", "condition": "baseline", "seed": s, "max_steps": CAP,
            "stop_after_generalization": STOP_AFTER, "device": DEVICE}
    for k, v in want.items():
        got = res.get(k, "cpu") if k == "device" else res.get(k)     # pre-rule-16 records have no device field (CPU)
        if got != v:
            return f"{k}={got!r}, expected {v!r}"
    if res["config"].get("eval_every_test") != EVAL_EVERY:
        return "eval cadence differs"
    return None


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
        err = "status" if res["status"] != "completed" else protocol_error(res, s)
        if err:
            r["reason"] = f"arm {arm}: {err}"
            return r
        if res["split_hash"] != split_hash(np.load(HERE / f"splits/seed{s}_train_{arm}.npy")):
            r["reason"] = f"arm {arm}: split content hash mismatch"
            return r
        if res.get("test_hash") != test_hash:
            r["reason"] = f"arm {arm}: test set differs"
            return r
        for name, thr in THRESHOLDS.items():
            r[f"gen_{arm}_{name}"] = gen_step(res, thr)
        g, seen = r[f"gen_{arm}_primary"]
        if not seen and res["steps_completed"] != CAP:
            r["reason"] = f"arm {arm}: no primary crossing but stopped at {res['steps_completed']} < {CAP}"
            return r
        r[f"ov_F_{arm}_gen"] = len(set(top_at(d, g)) & F)
        r[f"ov_F_{arm}_2000"] = len(set(top_at(d, 2000)) & F) if g >= 2000 else None
    g = {arm: min(r[f"gen_{arm}_primary"][0], CAP) for arm in ARMS}
    r["L_DE"] = float(np.log2(g["D"] / g["E"]))           # restricted (capped) endpoint
    r["L_RE"] = float(np.log2(g["R"] / g["E"]))
    r["L_RD"] = float(np.log2(g["R"] / g["D"]))
    for name in THRESHOLDS:
        for x, y in (("E", "D"), ("E", "R"), ("D", "R")):
            r[f"sign_{x}{y}_{name}"] = order_sign(r[f"gen_{x}_{name}"], r[f"gen_{y}_{name}"])
    r["valid"] = True
    return r


def one_sided_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def sign_test(valid: list[dict], key: str) -> dict:
    """One-sided exact binomial test that the first arm crosses first, over determined seeds."""
    from math import comb
    sg = [r[key] for r in valid if r[key] is not None]
    n, k = len(sg), sum(x > 0 for x in sg)
    p = sum(comb(n, j) for j in range(k, n + 1)) / 2 ** n if n else 1.0
    return {"n_determined": n, "n_first_arm_earlier": k, "p_one_sided": p}


def contrast(valid: list[dict], key: str) -> dict:
    x = np.array([r[key] for r in valid])
    return {"mean": float(x.mean()), "sd": float(x.std(ddof=1)) if len(x) > 1 else None,
            "p_one_sided": one_sided_p(x), "n": len(x)}


def main() -> None:
    global RUN, DEVICE
    if sys.argv[1:] == ["--device", "cuda"]:                     # Nachtrag c: all arms and seeds on the GPU, one summary per device
        RUN, DEVICE = RUN_CUDA, "cuda"
    elif sys.argv[1:] not in ([], ["--device", "cpu"]):
        raise SystemExit("usage: analyze.py [--device cpu|cuda]")
    rows = [row(s) for s in SEEDS]
    valid = [r for r in rows if r["valid"]]
    out: dict = {"rows": rows, "n_valid": len(valid)}
    if len(valid) < MIN_VALID:
        out["verdict"] = "nicht auswertbar"
    else:
        prim = contrast(valid, "L_DE")
        robust = sign_test(valid, "sign_ED_primary")
        out["primary_L_DE_capped"] = prim
        out["co_condition_sign_ED"] = robust
        out["verdict"] = ("widerspricht" if prim["mean"] <= 0 else
                          "beschleunigt" if prim["p_one_sided"] < ALPHA and robust["p_one_sided"] < ALPHA
                          else "richtungsgleich, nicht signifikant")
        out["secondary"] = {"L_RE_capped": contrast(valid, "L_RE"), "L_RD_capped": contrast(valid, "L_RD"),
                            **{f"sign_{c}_{t}": sign_test(valid, f"sign_{c}_{t}")
                               for c in ("ED", "ER", "DR") for t in THRESHOLDS if (c, t) != ("ED", "primary")}}
        out["censored_primary"] = {arm: sum(not r[f"gen_{arm}_primary"][1] for r in valid) for arm in ARMS}
    out["device"] = DEVICE
    (HERE / ("summary.json" if DEVICE == "cpu" else "summary_cuda.json")).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print({k: v for k, v in r.items() if not k.startswith("sign_") or k.endswith("primary")})


if __name__ == "__main__":
    main()
