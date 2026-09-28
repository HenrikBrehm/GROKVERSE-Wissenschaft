"""EXP-100, secondary L0 part (rule 20b): does the early lock-in (K4: a data switch after 50 steps keeps the old choice, after
25 steps the new one wins) hold under i.i.d. minibatch training? Session 44, written before any run; exploration (pilot seeds
3700-3707, 8 seeds; a confirmation would be its own registration).

Runs: design.py --switch (raw_switch): arms fb (full batch, 2000 steps after the switch) and iid256 (30 000 steps after the
switch), switch F -> G and G -> F at t = 25 and 50. Pure F / G runs of the same seed and arm: the pilot block (raw).
Persistence as N28/EXP-056: L = log[P(T_F) / P(T_G)] of the final W_E group power; per seed and arm
pi(t) = ((L_FG(t) - L_G) / (L_F - L_G) + (L_GF(t) - L_F) / (L_G - L_F)) / 2   (1 = the old choice persists, 0 = the new wins).
Valid seed/arm: all four switch runs and both pure runs load (shared loader) and L_F - L_G >= 0.5.
Readings (fixed here; bootstrap 95 % CI over valid seeds, 10 000 resamples, seed 100; < 6 valid -> "nicht auswertbar"):
  reference   d_fb = pi_fb(50) - pi_fb(25): CI > 0 -> the full-batch reversal replicates on these seeds; else "Referenz nicht
              repliziert" and the minibatch reading below is only descriptive.
  minibatch   d_mb = pi_iid256(50) - pi_iid256(25):
              "Fenster wie Full-Batch"      d_mb CI > 0
              "Fenster verschoben/fehlt"    d_mb CI contains 0 (then report pi_iid256(25) and (50): both >= 0.5 -> locks
                                            earlier than 25 steps; both < 0.5 -> later than 50 or not at all;
                                            otherwise "(gemischt)")
              "umgekehrt"                   d_mb CI < 0
Descriptive: pi per cell, paired d_mb - d_fb, epochs at the switch (t / 15 at B = 256), generalisation step per run.
Note (N52): at B = 256 an epoch is 15 steps, so both switch times lie after at least one full epoch.

  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-100-set-vs-order/switch_analyze.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))    # review s44: do not rely on analyze.py's side effect
sys.path.insert(0, str(HERE))
import analyze as A  # noqa: E402  (shared loader, EXP-043 group power, bootstrap)
import design as D  # noqa: E402
from result_loader import Expect, find_run, load_run  # noqa: E402

MIN_SEP = 0.5


def logratio(pw: np.ndarray, F: list[int], G: list[int]) -> float:
    return float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))


def pi_pair(LF: float, LG: float, LFG: float, LGF: float) -> float:
    return ((LFG - LG) / (LF - LG) + (LGF - LF) / (LG - LF)) / 2


def load_switch(s: int, arm: str, first: str, second: str, t: int) -> dict | str:
    total = D.ARMS[arm][3] + t
    pat = f"EXP-020_baseline_seed{s}_thr*_seed{s}_{first}_to_seed{s}_{second}_at{t}{A.suffix(arm)}{A.SUF}"
    L = load_run(find_run(HERE / "raw_switch", pat),
                 Expect(seed=s, device="cuda", max_steps=total, split_file=A.SPL / f"seed{s}_{first}.npy",
                        test_file=A.SPL / f"seed{s}_test.npy", switch_file=A.SPL / f"seed{s}_{second}.npy",
                        config={"p": 113, "task": "add"}, snapshots_at=(total,)))
    if L.status != "ok":
        return f"seed {s} {arm} {first}->{second}@{t}: {L.status}: {L.reason}"
    pw = A._a43.group_power(L.snapshot(total), "add", 113)[0]
    if not np.isfinite(pw).all():
        return f"seed {s} {arm} {first}->{second}@{t}: non-finite"
    r = L.res
    gen = (r.get("transitions") or {}).get("primary", {}).get("generalization", {}).get("first_crossing_step")
    spe = r.get("events", {}).get("minibatch", {}).get("steps_per_epoch", 1) if D.ARMS[arm][0] else 1
    return {"end": pw, "t_gen": gen, "epochs_at_switch": t / spe}


def seed_pis(s: int) -> dict:
    T = json.loads((A.SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
    F, G = T["F"], T["G"]
    out: dict = {"seed": s, "errors": []}
    for arm in D.SWITCH_ARMS:
        pure = {x: A.load(s, x, arm) for x in "FG"}
        sw = {(a, b, t): load_switch(s, arm, a, b, t) for t in D.SWITCH_T for a, b in (("F", "G"), ("G", "F"))}
        bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
        if bad:
            out["errors"] += bad
            continue
        LF, LG = logratio(pure["F"]["end"], F, G), logratio(pure["G"]["end"], F, G)
        if LF - LG < MIN_SEP:
            out["errors"].append(f"seed {s} {arm}: pure runs not separated (L_F - L_G = {LF - LG:.2f})")
            continue
        for t in D.SWITCH_T:
            out[f"pi_{arm}_{t}"] = pi_pair(LF, LG, logratio(sw[("F", "G", t)]["end"], F, G), logratio(sw[("G", "F", t)]["end"], F, G))
            out[f"tgen_{arm}_{t}"] = [sw[(a, b, t)]["t_gen"] for a, b in (("F", "G"), ("G", "F"))]
            out[f"epochs_at_switch_{arm}_{t}"] = sw[("F", "G", t)]["epochs_at_switch"]
    return out


def reading(rows: list[dict]) -> dict:
    need = [f"pi_{a}_{t}" for a in D.SWITCH_ARMS for t in D.SWITCH_T]
    ok = [r for r in rows if all(k in r for k in need)]
    if len(ok) < A.MIN_VALID:
        return {"n": len(ok), "reading": "nicht auswertbar"}
    col = lambda k: np.array([r[k] for r in ok], dtype=float)   # noqa: E731
    d_fb, d_mb = col("pi_fb_50") - col("pi_fb_25"), col("pi_iid256_50") - col("pi_iid256_25")
    c_fb, c_mb = A.boot_ci(d_fb), A.boot_ci(d_mb)
    ref = "Referenz repliziert" if c_fb[0] > 0 else "Referenz nicht repliziert"
    mb = ("Fenster wie Full-Batch" if c_mb[0] > 0 else "umgekehrt" if c_mb[1] < 0 else "Fenster verschoben/fehlt")
    if mb == "Fenster verschoben/fehlt":
        p25, p50 = float(col("pi_iid256_25").mean()), float(col("pi_iid256_50").mean())
        mb += (" (legt vor 25 Schritten fest)" if min(p25, p50) >= 0.5 else
               " (legt nach 50 Schritten oder nicht fest)" if max(p25, p50) < 0.5 else " (gemischt)")
    return {"n": len(ok), "reference": ref, "minibatch": mb if ref == "Referenz repliziert" else f"{mb} (nur beschreibend)",
            "d_fb": {"mean": float(d_fb.mean()), "ci95": c_fb}, "d_mb": {"mean": float(d_mb.mean()), "ci95": c_mb},
            "d_mb_minus_d_fb": {"mean": float((d_mb - d_fb).mean()), "ci95": A.boot_ci(d_mb - d_fb)},
            "pi_means": {k: float(col(k).mean()) for k in need},
            "tgen_median": {f"{a}_{t}": (float(np.median(g)) if (g := [x for r in ok for x in r.get(f"tgen_{a}_{t}", [])
                                                                         if x is not None]) else None)
                            for a in D.SWITCH_ARMS for t in D.SWITCH_T},
            "n_generalised": {f"{a}_{t}": sum(x is not None for r in ok for x in r.get(f"tgen_{a}_{t}", []))
                              for a in D.SWITCH_ARMS for t in D.SWITCH_T},
            "epochs_at_switch": {f"{a}_{t}": ok[0].get(f"epochs_at_switch_{a}_{t}") for a in D.SWITCH_ARMS for t in D.SWITCH_T}}


def main() -> None:
    rows = [seed_pis(s) for s in D.SEEDS]
    out = {"primary": reading(rows), "rows": rows}
    (HERE / "switch_summary.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps(out["primary"], indent=1, ensure_ascii=False))


def selftest() -> None:
    assert abs(pi_pair(2.0, -2.0, 2.0, -2.0) - 1.0) < 1e-12 and abs(pi_pair(2.0, -2.0, -2.0, 2.0)) < 1e-12
    rng = np.random.default_rng(0)
    mk = lambda fb25, fb50, mb25, mb50: [{"seed": s, "pi_fb_25": fb25 + rng.normal(0, .05), "pi_fb_50": fb50 + rng.normal(0, .05),  # noqa: E731
                                          "pi_iid256_25": mb25 + rng.normal(0, .05), "pi_iid256_50": mb50 + rng.normal(0, .05)}
                                         for s in range(8)]
    v = reading(mk(0.2, 0.9, 0.2, 0.9))
    assert (v["reference"], v["minibatch"]) == ("Referenz repliziert", "Fenster wie Full-Batch"), v
    v = reading(mk(0.2, 0.9, 0.8, 0.8))
    assert v["minibatch"] == "Fenster verschoben/fehlt (legt vor 25 Schritten fest)", v
    v = reading(mk(0.2, 0.9, 0.1, 0.1))
    assert v["minibatch"] == "Fenster verschoben/fehlt (legt nach 50 Schritten oder nicht fest)", v
    v = reading(mk(0.5, 0.5, 0.2, 0.9))
    assert v["reference"] == "Referenz nicht repliziert" and v["minibatch"].endswith("(nur beschreibend)"), v
    assert reading(mk(0.2, 0.9, 0.2, 0.9)[:5])["reading"] == "nicht auswertbar"
    assert len(D.switch_jobs()) == len(D.SEEDS) * 2 * 2 * 2
    print("[exp100-switch] selftest ok")


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
