"""EXP-137 analysis (readings fixed in README and here before any block run, session 67).
Per cell (p, fraction) and seed, both arms F and G must have generalized (first_crossing_step of the primary
generalization transition) for the seed to count. Primary measure: Delta_pow (as P1/EXP-043/EXP-136) of the W_E group
power at the post-generalization snapshots: per arm the first stored snapshot >= its own gen + 1000 (snapshots every 1000
steps, a run stops at gen + 2000, so it exists if the arm generalized). Delta_pow is a sum of two within-run log ratios,
so the two arms may be read at different steps. (Changed before any block result, session 67, ~05:46 Berlin (between measurements 05:45 and 05:47): the first version
required one common step >= max(gen_F, gen_G) + 1000, which does not exist when one arm generalizes > 1000 steps earlier
and therefore stops earlier.)
Cell reading: fewer than 2 seeds with both arms generalized -> 'kein Lernen im Budget';
otherwise among those seeds: all Delta_pow > 1 -> 'steuert'; at least half |Delta_pow| <= 1 -> 'bricht'; else 'unklar'.
Overall reading per p (descriptive across fractions, pilot): every evaluable cell 'steuert' and the lowest evaluable
fraction <= 0.15 -> 'K2 haelt bei p mit weniger Daten'; the lowest evaluable cell 'bricht' while f20 'steuert' ->
'Steuerung schwindet mit der Dichte'; no evaluable cell -> 'kein Lernen im Budget'; else 'beschreibend'.
Descriptive: Delta_pow at step 2000 (as EXP-136), generalization steps, final test accuracy, top-5 overlap,
Spearman(mask Delta, Delta_pow post-gen) over seed cells (first-order prediction fixed before the runs,
mask_prediction_s67.json) and the mean Delta_pow per cell (does it rise with the fraction at each p?).
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


def reading(x: list[float]) -> str:
    if len(x) < 2:
        return "kein Lernen im Budget"
    a = np.array(x)
    if (a > 1).all():
        return "steuert"
    if 2 * (np.abs(a) <= 1).sum() >= len(a):
        return "bricht"
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
               "dpow_post": None, "post_step": None}
        if F["gen"] is not None and G["gen"] is not None:
            tF = [t for t in sorted(F["snaps"]) if t >= F["gen"] + POST]
            tG = [t for t in sorted(G["snaps"]) if t >= G["gen"] + POST]
            if tF and tG:
                a, b = F["snaps"][tF[0]], G["snaps"][tG[0]]
                row.update(post_step=[tF[0], tG[0]], dpow_post=delta_pow(a, b, F["T"], G["T"]),
                           top5_own_post=[len(top5(a) & set(F["T"])), len(top5(b) & set(G["T"]))])
            else:
                bad.append(f"seed {s}: no snapshot >= gen + {POST}")
        rows.append(row)
    x = [r["dpow_post"] for r in rows if r["dpow_post"] is not None]
    return {"p": p, "fraction": fr, "train_frac": mj.FRACS[fr], "verdict": reading(x), "n_evaluable": len(x),
            "n_not_generalised": sum(g is None for r in rows for g in r["gen"]), "rows": rows, "problems": bad}


def overall(cells: list[dict], p: int) -> str:
    cs = [c for c in cells if c["p"] == p]
    ev = [c for c in cs if c["verdict"] != "kein Lernen im Budget"]
    if not ev:
        return "kein Lernen im Budget"
    lowest = min(ev, key=lambda c: c["train_frac"])
    if all(c["verdict"] == "steuert" for c in ev) and lowest["train_frac"] <= 0.15 + 1e-12:
        return "K2 haelt bei p mit weniger Daten"
    f20 = [c for c in cs if c["fraction"] == "f20"]
    if lowest["verdict"] == "bricht" and f20 and f20[0]["verdict"] == "steuert":
        return "Steuerung schwindet mit der Dichte"
    return "beschreibend"


def mask_check(cells: list[dict]) -> dict | None:
    f = HERE / "mask_prediction_s67.json"
    if not f.exists():
        return None
    m = {(r["p"], r["fraction"], r["seed"]): r["delta_mask"] for r in json.loads(f.read_text(encoding="utf-8"))}
    pairs = [(m[(c["p"], c["fraction"], r["seed"])], r["dpow_post"]) for c in cells for r in c["rows"] if r["dpow_post"] is not None]
    rk = lambda w: np.argsort(np.argsort(w)).astype(float)   # noqa: E731
    rho = (float(np.corrcoef(rk(np.array([a for a, _ in pairs])), rk(np.array([b for _, b in pairs])))[0, 1])
           if len(pairs) >= 3 else None)
    means = {f"{c['p']}_{c['fraction']}": (float(np.mean([r["dpow_post"] for r in c["rows"] if r["dpow_post"] is not None]))
                                            if c["n_evaluable"] else None) for c in cells}
    return {"spearman_mask_vs_dpow_post": rho, "n": len(pairs), "mean_dpow_post": means}


def main(loader=load) -> dict:
    cells = [cell(p, fr, loader) for p in mj.PS for fr in mj.FRACS]
    return {"cells": cells, "overall": {str(p): overall(cells, p) for p in mj.PS}, "mask_prediction_check": mask_check(cells)}


def selftest() -> None:
    rng = np.random.default_rng(0)

    def fake(strength, gen=500):
        def ld(p, fr, s, arm):
            T = [1, 2, 3, 4, 5] if arm == "F" else [6, 7, 8, 9, 10]

            def pw():
                v = np.ones((p - 1) // 2) + rng.random((p - 1) // 2) * 0.1
                v[[k - 1 for k in T]] += strength(fr)
                return v
            g = gen(fr) if callable(gen) else gen
            return {"snaps": {t: pw() for t in [50, 250, 500, 1000, 2000, 3000]}, "T": T, "gen": g, "final_acc": None,
                    "last_step": 3000}
        return ld
    r = main(fake(lambda fr: 5.0))
    assert all(c["verdict"] == "steuert" and c["rows"][0]["post_step"] == [2000, 2000] for c in r["cells"]), r["cells"][0]
    assert set(r["overall"].values()) == {"K2 haelt bei p mit weniger Daten"}
    r = main(fake(lambda fr: 5.0 if fr == "f20" else 0.0))
    assert set(r["overall"].values()) == {"Steuerung schwindet mit der Dichte"}, r["overall"]
    r = main(fake(lambda fr: 5.0, gen=None))
    assert all(c["verdict"] == "kein Lernen im Budget" for c in r["cells"])
    assert set(r["overall"].values()) == {"kein Lernen im Budget"}
    r = main(fake(lambda fr: 5.0, gen=lambda fr: None if fr == "f10" else 500))
    assert set(r["overall"].values()) == {"K2 haelt bei p mit weniger Daten"}   # lowest evaluable is f15
    r = main(fake(lambda fr: 5.0, gen=lambda fr: None if fr != "f20" else 500))
    assert set(r["overall"].values()) == {"beschreibend"}                       # only f20 evaluable
    r = main(fake(lambda fr: 5.0, gen=2500))
    assert all(c["verdict"] == "kein Lernen im Budget" and c["problems"] for c in r["cells"])   # no snapshot >= gen + 1000
    r = main(fake(lambda fr: 5.0, gen=lambda fr: None))
    gens = iter([500, 1900] * 100)                         # arms generalize 1400 steps apart: read at 2000 and 3000
    r = main(lambda p, fr, s, arm: dict(fake(lambda f: 5.0)(p, fr, s, arm), gen=next(gens)))
    assert all(c["verdict"] == "steuert" and c["rows"][0]["post_step"] == [2000, 3000] for c in r["cells"]), r["cells"][0]
    assert all(c["verdict"] == "kein Lernen im Budget" for c in main(lambda *a: "x: fehlt")["cells"])
    print("[exp137] selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        res = main()
        (HERE / "summary.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        for c in res["cells"]:
            print(c["p"], c["fraction"], c["verdict"],
                  "post:", [None if r["dpow_post"] is None else round(r["dpow_post"], 2) for r in c["rows"]],
                  "| 2000:", [None if r["dpow_2000"] is None else round(r["dpow_2000"], 2) for r in c["rows"]],
                  "| gen:", [r["gen"] for r in c["rows"]], c["problems"])
        print("overall:", res["overall"])
        print("first-order prediction check:", res["mask_prediction_check"])
