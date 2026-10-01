"""EXP-137 analysis (readings fixed in README and here before any block result, session 67).
Per cell (p, fraction) and seed, both arms F and G must have generalized (first_crossing_step of the primary
generalization transition) for the seed to count. Primary measure: Delta_pow (as P1/EXP-043/EXP-136) of the W_E group
power at the post-generalization snapshots: per arm the first stored snapshot >= its own gen + 1000 (snapshots every 1000
steps, a run stops at gen + 2000, so it exists if the arm generalized before step 29 000). Delta_pow is a sum of two
within-run log ratios, so the two arms may be read at different steps. (Changed before any block result, session 67,
~05:46 Berlin (between measurements 05:45 and 05:47): the first version required one common step >= max(gen_F, gen_G)
+ 1000, which does not exist when one arm generalizes > 1000 steps earlier and therefore stops earlier.)

Cell reading (threshold 1, as EXP-136): fewer than 2 seeds with both arms generalized -> 'kein Lernen im Budget';
>= 2 such seeds but fewer than 2 evaluable (no snapshot >= gen + 1000, load problem) -> 'nicht auswertbar';
otherwise among the evaluable seeds: all Delta_pow > 1 -> 'steuert'; at least half |Delta_pow| <= 1 -> 'bricht';
else 'unklar'.
Calibrated cell reading (amendment, session 67, 05:54 Berlin measured, after the independent code review and before any
block result): in EXP-136 the placebo SD of Delta_pow was 0.11-0.15 in memorizing networks but 1.21-1.91 in generalized
ones, so the threshold 1 is not calibrated after generalization. Per evaluable seed: placebo Delta_pow for 2000 random
disjoint 5-sets outside F u G at the same two post-generalization spectra; q99 / q90 = 99 % / 90 % quantile of
|placebo|. 'steuert' if every evaluable seed has Delta_pow > q99; 'nicht unterscheidbar' if at least half have
Delta_pow <= q90; else 'unklar'; same 'kein Lernen im Budget' / 'nicht auswertbar' rules.
THE OVERALL READING USES THE CALIBRATED CELL READING (amendment, same time); the threshold-1 reading is reported beside it.
Overall reading per p (descriptive across fractions, pilot): every evaluable cell 'steuert' and the lowest evaluable
fraction <= 0.15 -> 'K2 haelt bei p mit weniger Daten'; the lowest evaluable cell 'nicht unterscheidbar' while f20
'steuert' -> 'Steuerung schwindet mit der Dichte'; no evaluable cell -> 'kein Lernen im Budget'; else 'beschreibend'.
Descriptive: Delta_pow at step 2000 (as EXP-136); Delta_pow at the last snapshot before each arm's generalization
('dpow_pre', memorization imprint, to compare with dpow_post); generalization steps; final test accuracy; top-5 overlap;
Spearman(mask Delta, Delta_pow post) pooled and within each p (first-order prediction fixed before the runs,
mask_prediction_s67.json); mean Delta_pow per cell.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-137-modulus-density/analyze.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_jobs as mj  # noqa: E402

RAW = HERE / "raw"
STEP = 2000
POST = 1000
N_PLACEBO = 2000


def group_power(W: np.ndarray, p: int) -> np.ndarray:
    """As EXP-136 / EXP-043 analyze.group_power for add p (odd p): power per k = 1..(p-1)//2 of the number rows."""
    sq = (np.abs(np.fft.fft(W[:p], axis=0)) ** 2).sum(axis=1)
    return 2.0 * sq[1:(p - 1) // 2 + 1] / p


def delta_pow(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float | None:
    s = lambda pw, S: float(pw[[k - 1 for k in S]].sum())   # noqa: E731
    sums = [s(pF, F), s(pF, G), s(pG, G), s(pG, F)]
    if not all(np.isfinite(x) and x > 0 for x in sums):
        return None
    d = float(np.log(sums[0] / sums[1]) + np.log(sums[2] / sums[3]))
    return d if np.isfinite(d) else None


def placebo_q(a: np.ndarray, b: np.ndarray, F: list[int], G: list[int], seed: int) -> tuple[float, float, float]:
    """|placebo Delta_pow| quantiles (90 %, 99 %) and SD for random disjoint 5-sets outside F u G (as EXP-136.placebo_sd)."""
    rng = np.random.default_rng(137_000 + seed)
    pool = np.array([k for k in range(1, len(a) + 1) if k not in set(F) | set(G)])
    v = [delta_pow(a, b, list(c[:5]), list(c[5:])) for c in (rng.choice(pool, 10, replace=False) for _ in range(N_PLACEBO))]
    v = np.array([x for x in v if x is not None])
    return float(np.quantile(np.abs(v), 0.90)), float(np.quantile(np.abs(v), 0.99)), float(np.std(v))


def find_run(split_npy: str) -> Path | None:
    hits = [r.parent for r in RAW.glob("*/result.json")
            if Path(json.loads(r.read_text(encoding="utf-8")).get("split_file") or "").name == split_npy]
    return hits[0] if len(hits) == 1 else None


def load(p: int, fr: str, s: int, arm: str) -> dict | str:
    st = mj.stem(p, fr, s, arm)
    d = find_run(f"{st}.npy")
    if d is None:
        return f"{st}: fehlt oder doppelt"
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    if r.get("status") != "completed":
        return f"{st}: status {r.get('status')}"
    if r["config"].get("p") != p or r.get("device") != "cuda" or abs(r["config"].get("train_frac") - mj.FRACS[fr]) > 1e-12:
        return f"{st}: config differs"
    steps = [int(x) for x in np.load(d / "we_snapshot_steps.npy").tolist()]
    snaps = np.load(d / "we_snapshots.npy").astype(np.float64)
    if not np.isfinite(snaps).all():
        return f"{st}: non-finite snapshot"
    meta = json.loads((HERE / "splits" / f"{st}.json").read_text(encoding="utf-8"))
    gen = (r.get("transitions") or {}).get("primary", {}).get("generalization", {}).get("first_crossing_step")
    return {"snaps": {t: group_power(snaps[i], p) for i, t in enumerate(steps)}, "T": meta["targets"], "gen": gen,
            "final_acc": r.get("final_acc"), "last_step": steps[-1]}


def top5(pw: np.ndarray) -> set[int]:
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:5]}   # tie-break as EXP-043


def reading(x: list[float], n_gen: int) -> str:
    if n_gen < 2:
        return "kein Lernen im Budget"
    if len(x) < 2:
        return "nicht auswertbar"
    a = np.array(x)
    if (a > 1).all():
        return "steuert"
    if 2 * (np.abs(a) <= 1).sum() >= len(a):
        return "bricht"
    return "unklar"


def reading_cal(rows: list[dict], n_gen: int) -> str:
    ev = [r for r in rows if r["dpow_post"] is not None]
    if n_gen < 2:
        return "kein Lernen im Budget"
    if len(ev) < 2:
        return "nicht auswertbar"
    if all(r["dpow_post"] > r["placebo_q99"] for r in ev):
        return "steuert"
    if 2 * sum(r["dpow_post"] <= r["placebo_q90"] for r in ev) >= len(ev):
        return "nicht unterscheidbar"
    return "unklar"


def cell(p: int, fr: str, loader=load) -> dict:
    rows, bad = [], []
    for s in mj.SEEDS:
        F, G = loader(p, fr, s, "F"), loader(p, fr, s, "G")
        if isinstance(F, str) or isinstance(G, str):
            bad.append(F if isinstance(F, str) else G)
            continue
        both2000 = STEP in F["snaps"] and STEP in G["snaps"]
        row = {"seed": s, "gen": [F["gen"], G["gen"]], "final_acc": [F["final_acc"], G["final_acc"]],
               "dpow_2000": delta_pow(F["snaps"][STEP], G["snaps"][STEP], F["T"], G["T"]) if both2000 else None,
               "dpow_post": None, "post_step": None, "dpow_pre": None, "pre_step": None}
        if F["gen"] is not None and G["gen"] is not None:
            preF = [t for t in sorted(F["snaps"]) if t < F["gen"]]
            preG = [t for t in sorted(G["snaps"]) if t < G["gen"]]
            if preF and preG:
                row.update(pre_step=[preF[-1], preG[-1]],
                           dpow_pre=delta_pow(F["snaps"][preF[-1]], G["snaps"][preG[-1]], F["T"], G["T"]))
            tF = [t for t in sorted(F["snaps"]) if t >= F["gen"] + POST]
            tG = [t for t in sorted(G["snaps"]) if t >= G["gen"] + POST]
            if tF and tG:
                a, b = F["snaps"][tF[0]], G["snaps"][tG[0]]
                q90, q99, sd = placebo_q(a, b, F["T"], G["T"], s)
                row.update(post_step=[tF[0], tG[0]], dpow_post=delta_pow(a, b, F["T"], G["T"]),
                           placebo_q90=q90, placebo_q99=q99, placebo_sd=sd,
                           top5_own_post=[len(top5(a) & set(F["T"])), len(top5(b) & set(G["T"]))])
            else:
                bad.append(f"seed {s}: no snapshot >= gen + {POST}")
        rows.append(row)
    n_gen = sum(r["gen"][0] is not None and r["gen"][1] is not None for r in rows)
    x = [r["dpow_post"] for r in rows if r["dpow_post"] is not None]
    return {"p": p, "fraction": fr, "train_frac": mj.FRACS[fr], "verdict_cal": reading_cal(rows, n_gen),
            "verdict_thr1": reading(x, n_gen), "n_both_generalised": n_gen, "n_evaluable": len(x),
            "n_not_generalised": sum(g is None for r in rows for g in r["gen"]), "rows": rows, "problems": bad}


def overall(cells: list[dict], p: int) -> str:
    cs = [c for c in cells if c["p"] == p]
    ev = [c for c in cs if c["verdict_cal"] not in ("kein Lernen im Budget", "nicht auswertbar")]
    if not ev:
        return "kein Lernen im Budget"
    lowest = min(ev, key=lambda c: c["train_frac"])
    if all(c["verdict_cal"] == "steuert" for c in ev) and lowest["train_frac"] <= 0.15 + 1e-12:
        return "K2 haelt bei p mit weniger Daten"
    f20 = [c for c in cs if c["fraction"] == "f20"]
    if lowest["verdict_cal"] == "nicht unterscheidbar" and f20 and f20[0]["verdict_cal"] == "steuert":
        return "Steuerung schwindet mit der Dichte"
    return "beschreibend"


def spearman(pairs: list[tuple[float, float]]) -> float | None:
    if len(pairs) < 3:
        return None
    rk = lambda w: np.argsort(np.argsort(w)).astype(float)   # noqa: E731
    return float(np.corrcoef(rk(np.array([a for a, _ in pairs])), rk(np.array([b for _, b in pairs])))[0, 1])


def mask_check(cells: list[dict]) -> dict | None:
    f = HERE / "mask_prediction_s67.json"
    if not f.exists():
        return None
    m = {(r["p"], r["fraction"], r["seed"]): r["delta_mask"] for r in json.loads(f.read_text(encoding="utf-8"))}
    pairs = {p: [(m[(c["p"], c["fraction"], r["seed"])], r["dpow_post"]) for c in cells if c["p"] == p
                 for r in c["rows"] if r["dpow_post"] is not None] for p in mj.PS}
    means = {f"{c['p']}_{c['fraction']}": (float(np.mean([r["dpow_post"] for r in c["rows"] if r["dpow_post"] is not None]))
                                            if c["n_evaluable"] else None) for c in cells}
    return {"spearman_pooled": spearman([x for v in pairs.values() for x in v]),
            "spearman_within_p": {str(p): spearman(v) for p, v in pairs.items()},
            "n": sum(len(v) for v in pairs.values()), "mean_dpow_post": means}


def main(loader=load) -> dict:
    cells = [cell(p, fr, loader) for p in mj.PS for fr in mj.FRACS]
    return {"cells": cells, "overall": {str(p): overall(cells, p) for p in mj.PS}, "mask_prediction_check": mask_check(cells)}


def selftest() -> None:
    rng = np.random.default_rng(0)

    def fake(strength, gen=500, noise=0.1):
        def ld(p, fr, s, arm):
            T = [1, 2, 3, 4, 5] if arm == "F" else [6, 7, 8, 9, 10]
            g = gen(fr, arm) if callable(gen) else gen
            end = 30_000 if g is None else min(30_000, g + 2000)      # the real run stops at gen + 2000

            def pw():
                v = np.ones((p - 1) // 2) + rng.random((p - 1) // 2) * (noise(fr) if callable(noise) else noise)
                v[[k - 1 for k in T]] += strength(fr)
                return v
            steps = [t for t in [50, 250, 500, *range(1000, 30_001, 1000)] if t <= end]
            return {"snaps": {t: pw() for t in steps}, "T": T, "gen": g, "final_acc": None, "last_step": steps[-1]}
        return ld
    r = main(fake(lambda fr: 5.0))
    assert all(c["verdict_cal"] == c["verdict_thr1"] == "steuert" and c["rows"][0]["post_step"] == [2000, 2000]
               for c in r["cells"]), r["cells"][0]
    assert set(r["overall"].values()) == {"K2 haelt bei p mit weniger Daten"}
    r = main(fake(lambda fr: 5.0 if fr == "f20" else 0.0))
    assert set(r["overall"].values()) == {"Steuerung schwindet mit der Dichte"}, r["overall"]
    r = main(fake(lambda fr: 5.0, gen=None))
    assert all(c["verdict_cal"] == "kein Lernen im Budget" for c in r["cells"])
    assert set(r["overall"].values()) == {"kein Lernen im Budget"}
    r = main(fake(lambda fr: 5.0, gen=lambda fr, arm: None if fr == "f10" else 500))
    assert set(r["overall"].values()) == {"K2 haelt bei p mit weniger Daten"}   # lowest evaluable is f15
    r = main(fake(lambda fr: 5.0, gen=lambda fr, arm: None if fr != "f20" else 500))
    assert set(r["overall"].values()) == {"beschreibend"}                       # only f20 evaluable
    r = main(fake(lambda fr: 5.0, gen=29_500))                                  # no snapshot >= gen + 1000
    assert all(c["verdict_cal"] == "nicht auswertbar" and c["problems"] for c in r["cells"])
    r = main(fake(lambda fr: 5.0, gen=lambda fr, arm: 500 if arm == "F" else 1900))   # F stops at 2500
    assert all(c["verdict_cal"] == "steuert" and c["rows"][0]["post_step"] == [2000, 3000] for c in r["cells"])
    assert all(c["rows"][0]["pre_step"] == [250, 1000] for c in r["cells"])
    # large placebo noise: Delta_pow > 1 but inside the placebo band -> threshold-1 'steuert', calibrated not
    r = main(fake(lambda fr: 0.5, noise=20.0))
    assert any(c["verdict_cal"] != "steuert" for c in r["cells"]), [c["verdict_cal"] for c in r["cells"]]
    r = main(fake(lambda fr: 0.0, gen=lambda fr, arm: 500 if arm == "F" else None))   # one arm never generalizes
    assert all(c["verdict_cal"] == "kein Lernen im Budget" and c["n_not_generalised"] == 3 for c in r["cells"])
    assert reading([2.0, 0.5], 2) == "bricht" and reading([2.0, 1.5, 0.5], 3) == "unklar"
    assert all(c["verdict_cal"] == "kein Lernen im Budget" for c in main(lambda *a: "x: fehlt")["cells"])
    print("[exp137] selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        res = main()
        (HERE / "summary.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        rd = lambda v: None if v is None else round(v, 2)   # noqa: E731
        for c in res["cells"]:
            print(c["p"], c["fraction"], c["verdict_cal"], "| thr1:", c["verdict_thr1"],
                  "| post:", [rd(r["dpow_post"]) for r in c["rows"]],
                  "| q99:", [rd(r.get("placebo_q99")) for r in c["rows"]],
                  "| pre:", [rd(r["dpow_pre"]) for r in c["rows"]],
                  "| 2000:", [rd(r["dpow_2000"]) for r in c["rows"]],
                  "| gen:", [r["gen"] for r in c["rows"]], c["problems"])
        print("overall:", res["overall"])
        print("first-order prediction check:", res["mask_prediction_check"])
