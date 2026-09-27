#!/usr/bin/env python3
"""EXP-078 analysis (pilot, session 26, UNTESTED): does split steering (K2) carry over to a two-layer transformer?

Per seed 1000-1009 (P1 add-113 splits, experiment 1, eps 2; W_E and layer-1 init identical to the one-layer P1 run of the seed):
Delta_pow = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)] of the W_E power at step 2000 (primary) and at 10000 (secondary), and the paired
difference to the frozen one-layer P1 value of the same seed (lab/confirm/P1_summary.json). Reading fixed in README before any run.

  python lab/tools/guarded_run.py -- python lab/experiments/EXP-078-two-layer-steering/analyze.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "paper" / "repro"))
from k2 import delta_pow, sign_flip_p  # noqa: E402

SEEDS, STEPS, PRIMARY, SPL = list(range(1000, 1010)), 10000, 2000, LAB / "confirm" / "splits"
MODEL_TAG = "EXP-078 TwoLayerTransformer"


def spectrum(run: Path, s: int, arm: str, step: int) -> np.ndarray | str:
    f = run / "result.json"
    if not f.exists():
        return "fehlt"
    r = json.loads(f.read_text(encoding="utf-8"))
    if r.get("seed") != s or r.get("steps") != STEPS or r.get("device") != "cuda" or not str(r.get("model", "")).startswith(MODEL_TAG):
        return f"defekt: result.json (seed/steps/device/model) {r.get('seed')}/{r.get('steps')}/{r.get('device')}/{r.get('model')}"
    argv = r.get("argv", [])                     # review s26: arm provenance (a swapped F/G directory would flip the sign)
    if "--split-file" not in argv or Path(argv[argv.index("--split-file") + 1]).name != f"confirm_exp1_eps2.0_add113_seed{s}_{arm}.npy":
        return "defekt: split file in result.json does not match seed/arm"
    if f.stat().st_mtime < (run / "spectra.npy").stat().st_mtime:   # review s26: result.json is written last; older = stale
        return "defekt: result.json older than spectra.npy (stale rerun)"
    st = np.load(run / "spectra_steps.npy").tolist()
    if step not in st:
        return f"defekt: no spectrum at {step}"
    pw = np.load(run / "spectra.npy")[st.index(step)].astype(np.float64)
    return pw if pw.shape == (56,) and np.all(np.isfinite(pw)) and np.all(pw > 0) else "defekt: spectrum shape/values"


def summarize(D: np.ndarray, rng: np.random.Generator) -> dict:
    boot = np.array([rng.choice(D, len(D)).mean() for _ in range(10_000)])
    return {"n": len(D), "mean": float(D.mean()), "sd": float(D.std(ddof=1)) if len(D) > 1 else None,
            "ci95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))], "p_one_sided": sign_flip_p(D, rng),
            "n_positive": int((D > 0).sum())}


def reading(s: dict) -> str:
    if s["n"] < 8:
        return "nicht auswertbar"
    if s["mean"] >= 1.0 and s["p_one_sided"] < 0.05:
        return "Steuerung überträgt sich auf zwei Schichten (Pilot)"
    if s["mean"] < 0.5:                          # review s26 (before any run): p >= 0.2 alone is 'unklar', not 'keine'
        return "keine Steuerung in zwei Schichten (Pilot)"
    return "unklar"


def main() -> None:
    p1 = {r["seed"]: r["Delta_pow"] for r in json.loads((LAB / "confirm" / "P1_summary.json").read_text(encoding="utf-8"))["tasks"]["add113"]["rows"]
          if r.get("valid")}
    rows, bad = [], []
    for s in SEEDS:
        T = {a: json.loads((SPL / f"confirm_exp1_eps2.0_add113_seed{s}_{a}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
        row: dict = {"seed": s}
        for step in (PRIMARY, STEPS):
            pw = {a: spectrum(HERE / "raw" / f"seed{s}_{a}", s, a, step) for a in "FG"}
            if any(isinstance(v, str) for v in pw.values()):
                bad.append(f"seed {s} @ {step}: " + "; ".join(f"{a} {v}" for a, v in pw.items() if isinstance(v, str)))
                row = {}
                break
            row[f"D{step}"] = delta_pow(pw["F"], pw["G"], T["F"], T["G"])
        if not row:
            continue
        res = {a: json.loads((HERE / "raw" / f"seed{s}_{a}" / "result.json").read_text(encoding="utf-8")) for a in "FG"}
        row.update({"D1L_2000": p1.get(s), "test_acc": {a: res[a]["final_acc"]["test"] for a in "FG"},
                    "gen_step": {a: res[a]["generalization_step"] for a in "FG"}})
        rows.append(row)
    rng = np.random.default_rng(78)
    out: dict = {"n_valid": len(rows), "problems": bad, "rows": rows}
    if rows:
        out["primary_D2000"] = summarize(np.array([r["D2000"] for r in rows]), rng)
        out["reading"] = reading(out["primary_D2000"])
        out["secondary_D10000"] = summarize(np.array([r["D10000"] for r in rows]), rng)
        paired = np.array([r["D2000"] - r["D1L_2000"] for r in rows if r["D1L_2000"] is not None])
        out["secondary_paired_2L_minus_1L_at2000"] = summarize(paired, rng) if len(paired) > 1 else None
        out["n_generalised_both_arms"] = sum(all(g is not None for g in r["gen_step"].values()) for r in rows)
    else:
        out["reading"] = "nicht auswertbar"
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    mk = lambda m, sd=0.3: summarize(np.random.default_rng(1).normal(m, sd, 10), np.random.default_rng(2))   # noqa: E731
    assert reading(mk(3.0)).startswith("Steuerung"), reading(mk(3.0))
    assert reading(mk(0.1)).startswith("keine"), reading(mk(0.1))
    assert reading(mk(0.8, 0.3)) == "unklar", (mk(0.8, 0.3), reading(mk(0.8, 0.3)))
    assert reading({**mk(3.0), "n": 7}) == "nicht auswertbar"
    assert reading({"n": 10, "mean": 3.0, "p_one_sided": 0.3}) == "unklar"
    pF, pG = np.ones(56), np.ones(56)
    pF[[k - 1 for k in (1, 2, 3, 4, 5)]] = np.e
    assert abs(delta_pow(pF, pG, [1, 2, 3, 4, 5], [6, 7, 8, 9, 10]) - 1.0) < 1e-12
    import torch
    sys.path.insert(0, str(LAB.parent / "training"))
    from grokverse.config import get_config
    from grokverse.models import build_model
    from grokverse.seed import set_seed
    from two_layer import TwoLayerTransformer
    cfg = get_config("arch25k", seed=1000, steps=10, threads=1)
    from grokverse.data import make_dataset
    set_seed(1000); make_dataset(cfg); m1 = build_model(cfg)          # same order as the trainer (dataset between seed and init)
    set_seed(1000); make_dataset(cfg); m2 = TwoLayerTransformer(cfg)
    for nm in ("W_E", "W_pos", "W_Q", "W_K", "W_V", "W_O", "W_in", "W_out", "W_U"):   # same init as the one-layer model
        assert torch.equal(getattr(m1, nm), getattr(m2, nm)), nm
    assert not torch.equal(m2.W_Q, m2.W_Q2) and m2.logits_last(torch.tensor([[1, 2, 113]])).shape == (1, 114)
    print("[EXP-078] selftest ok", flush=True)


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    selftest() if "--selftest" in sys.argv else main()
