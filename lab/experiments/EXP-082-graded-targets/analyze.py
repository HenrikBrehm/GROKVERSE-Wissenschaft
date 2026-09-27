"""EXP-082 analysis (session 28, UNTESTED; written before any run). Pilot, known seeds 600-609, exploration with fixed hypotheses.

Per arm (add 113, step 2000, freq_ban run through the shared loader): rho_amp = Spearman over the 5 targets between the DESIGNED
amplitude a_i and the W_E power (spectra.npy = group basis for addition). Unit = seed (mean F/G). Per grade:
  H-strong: mean rho_amp >= 0.6 (the designed order is reproduced when the lever is large);
  H-weak (main question): mean rho_amp > 0, one-sided exact sign-flip p < 0.05 over 10 seeds (a natural-size difference in the
  pair spectrum causally orders the targets).
Descriptive: rho between the realized M0c and the power, rho with step-0 power, target share of the power, generalized arms.
Technical failures are reported; a grade with < 8 seeds with two valid arms is 'nicht auswertbar'.

  python lab/tools/guarded_run.py -- python lab/experiments/EXP-082-graded-targets/analyze.py [--selftest]
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "confirm"))
import importlib.util  # noqa: E402
import rank_tools as rt  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp043_analyze", LAB / "experiments/EXP-043-generalize-steering/analyze.py")
_e43 = importlib.util.module_from_spec(_spec)          # this file is itself called analyze.py: load EXP-043's by path
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
_spec.loader.exec_module(_e43)
group_power = _e43.group_power
from P1_posthoc_within import m0c_add  # noqa: E402
from result_loader import Expect, find_run, load_run  # noqa: E402

P, STEP, SEEDS, GRADES, MIN_SEEDS, DEV = 113, 2000, range(600, 610), ("strong", "weak"), 8, "cuda"


def arm(s: int, g: str, a: str) -> dict | str:
    stem = f"split_add113_seed{s}_{g}_{a}"
    split = HERE / "splits" / f"{stem}.npy"
    meta = json.loads(split.with_suffix(".json").read_text(encoding="utf-8"))
    L = load_run(find_run(HERE / "raw", f"EXP-016_baseline_seed{s}_thr1_{stem}_dev{DEV}"),
                 Expect(seed=s, device=DEV, max_steps=STEP, split_file=split, config={"p": P, "task": "add"}, at=(STEP,), snapshots_at=(0,)))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    sel = [k - 1 for k in meta["targets"]]
    pw = np.asarray(L.spectrum(STEP), dtype=np.float64)
    pw0 = group_power(L.snapshot(0).astype(np.float64), "add", P)[0]
    mc = m0c_add(np.load(split), P)
    try:
        return {"rho_amp": rt.spearman(np.array(meta["amplitudes"]), pw[sel]), "rho_M0c": rt.spearman(mc[sel], pw[sel]),
                "rho_init": rt.spearman(pw0[sel], pw[sel]), "share": float(pw[sel].sum() / pw.sum()),
                "generalized": (L.res.get("events") or {}).get("generalization_step") is not None}
    except rt.TieError as ex:
        return f"ties: {ex}"


def exact_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1.0, -1.0), repeat=len(d))))
    return float(((flips * d).mean(1) >= d.mean() - 1e-12).mean())


def summarize(units: list[dict], bad: list[str]) -> dict:
    if len(units) < MIN_SEEDS:
        return {"n": len(units), "bad": bad, "verdict": "nicht auswertbar"}
    d = np.array([u["rho_amp"] for u in units])
    rng = np.random.default_rng(82)
    boot = rng.choice(d, size=(10_000, len(d))).mean(1)
    return {"n": len(d), "mean_rho_amp": float(d.mean()), "sd": float(d.std(ddof=1)), "n_pos": int((d > 0).sum()), "p_one_sided": exact_p(d),
            "ci95": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))],
            **{f"mean_{k}": float(np.mean([u[k] for u in units])) for k in ("rho_M0c", "rho_init", "share")},
            "arms_generalized": int(sum(u["gen"] for u in units)), "bad": bad}


def main() -> None:
    out = {}
    for g in GRADES:
        units, bad = [], []
        for s in SEEDS:
            r = {a: arm(s, g, a) for a in "FG"}
            if any(isinstance(v, str) for v in r.values()):
                bad.append(f"{s}: " + "; ".join(f"{a}: {v}" for a, v in r.items() if isinstance(v, str)))
                continue
            units.append({k: (r["F"][k] + r["G"][k]) / 2 for k in ("rho_amp", "rho_M0c", "rho_init", "share")}
                         | {"seed": s, "gen": int(r["F"]["generalized"]) + int(r["G"]["generalized"])})
        out[g] = summarize(units, bad)
    out["verdict"] = {"H-strong": (out["strong"].get("mean_rho_amp", -1) >= 0.6) if "mean_rho_amp" in out["strong"] else "nicht auswertbar",
                      "H-weak": (out["weak"]["mean_rho_amp"] > 0 and out["weak"]["p_one_sided"] < 0.05) if "mean_rho_amp" in out["weak"] else "nicht auswertbar"}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


def selftest() -> None:
    rt.selftest()
    assert abs(exact_p(np.ones(10)) - 1 / 1024) < 1e-12 and exact_p(-np.ones(10)) == 1.0
    s = summarize([{"rho_amp": 0.5, "rho_M0c": 0.4, "rho_init": 0.0, "share": 0.8, "gen": 2, "seed": i} for i in range(10)], [])
    assert s["mean_rho_amp"] == 0.5 and s["p_one_sided"] < 0.01
    assert summarize([{"rho_amp": 0.5, "rho_M0c": 0, "rho_init": 0, "share": 0, "gen": 0, "seed": i} for i in range(7)], [])["verdict"] == "nicht auswertbar"
    for g in GRADES:                                       # split files match the deterministic construction
        spec = importlib.util.spec_from_file_location("ms82", HERE / "make_split.py")
        ms = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ms)
        idx, T, amps = ms.build(600, "F", g)
        meta = json.loads((HERE / f"splits/split_add113_seed600_{g}_F.json").read_text(encoding="utf-8"))
        assert np.array_equal(np.load(HERE / f"splits/split_add113_seed600_{g}_F.npy"), idx) and meta["targets"] == T
        assert np.allclose(meta["amplitudes"], amps)
    print("EXP-082 selftest ok")


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
