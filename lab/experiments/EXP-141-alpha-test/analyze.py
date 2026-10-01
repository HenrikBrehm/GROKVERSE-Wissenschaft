"""EXP-141 analysis (cloned from EXP-139 analyze.py, session 68 ~10:20 Berlin, before any EXP-141 run; only q1, EQ,
paths, placebo salt and the self-test changed). EXP-141 reading (alpha test): both cells generalize -> 'passt zu alpha ~ 1 (Daten je Zahlzeile),
nicht zu p^(5/3)'; neither -> 'passt zu p^(5/3), nicht zu alpha = 1 mit Schwelle <= 30.7'; only n18100 -> 'Schwelle in N/p bei p 503 zwischen 32 und 36
(gegen 30.7 bei p 307): unentschieden'; only n16100 -> 'nicht monoton: unklar'. Q2 (steering) as EXP-139.
Original EXP-139 text: EXP-139 analysis (readings fixed in README and here before any block result, session 68, 2026-10-01 ~08:40 Berlin).
Cells (p, N) with p in {401, 503, 613}, N in {9425, 14000} pairs. Per seed both arms F and G must have generalized
(first_crossing_step of the primary generalization transition). Measure as EXP-137: per arm the first stored snapshot
>= its own gen + 1000; Delta_pow (P1 formula, W_E group power) from these two spectra; placebo q90/q99 of |Delta_pow| for
2000 random disjoint 5+5 sets outside F u G at the same spectra.
Cell reading (calibrated, as EXP-137): < 2 seeds with both arms generalized -> 'kein Lernen im Budget'; >= 2 but < 2
evaluable -> 'nicht auswertbar'; every evaluable Delta_pow > q99 -> 'steuert'; at least half <= q90 -> 'nicht
unterscheidbar'; else 'unklar'. A cell 'generalizes' if >= 2 seeds have both arms generalized.
Question 1 (generalization): all three N = 9425 cells generalize -> 'Paarzahl traegt (bis 2.5 %)'; no N = 9425 cell
generalizes -> 'Paarzahl 9425 reicht oberhalb p 307 nicht'; otherwise 'Grenze bei N = 9425 zwischen den Anteilen'.
Always reported: the equal-fraction contrast (both 3.73 %): 613/14000 generalizes and 503/9425 not -> 'bei gleichem
Anteil helfen mehr Paare'; the reverse -> 'bei gleichem Anteil helfen mehr Paare nicht (umgekehrt)'; equal ->
'Gleich-Anteil-Kontrast unentschieden'.
Question 2 (steering): no evaluable cell -> 'kein Lernen im Budget'; any evaluable cell 'nicht unterscheidbar' ->
'Steuerung schwindet bei kleinem Anteil'; every evaluable cell 'steuert' -> 'K2 haelt bis zum kleinsten generalisierenden
Anteil' (the fraction is reported); else 'beschreibend'.
Descriptive: gen steps, Delta_pow at 2000 and at the last snapshot before gen, top-5 overlap, Spearman(mask Delta,
Delta_pow post) (mask_prediction_s68_141.json, fixed before the runs).
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-141-alpha-test/analyze.py [--selftest]
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
STEP, POST, N_PLACEBO = 2000, 1000, 2000


def group_power(W: np.ndarray, p: int) -> np.ndarray:
    """As EXP-137 / EXP-043 analyze.group_power for add p (odd p): power per k = 1..(p-1)//2 of the number rows."""
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
    rng = np.random.default_rng(141_000 + seed)
    pool = np.array([k for k in range(1, len(a) + 1) if k not in set(F) | set(G)])
    v = [delta_pow(a, b, list(c[:5]), list(c[5:])) for c in (rng.choice(pool, 10, replace=False) for _ in range(N_PLACEBO))]
    v = np.array([x for x in v if x is not None])
    return float(np.quantile(np.abs(v), 0.90)), float(np.quantile(np.abs(v), 0.99)), float(np.std(v))


def find_run(split_npy: str) -> Path | None:
    hits = [r.parent for r in RAW.glob("*/result.json")
            if Path(json.loads(r.read_text(encoding="utf-8")).get("split_file") or "").name == split_npy]
    return hits[0] if len(hits) == 1 else None


def load(p: int, cell: str, s: int, arm: str) -> dict | str:
    st = mj.stem(p, cell, s, arm)
    d = find_run(f"{st}.npy")
    if d is None:
        return f"{st}: fehlt oder doppelt"
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    if r.get("status") != "completed":
        return f"{st}: status {r.get('status')}"
    if r["config"].get("p") != p or r.get("device") != "cuda" or abs(r["config"].get("train_frac") - mj.frac(p, cell)) > 1e-12:
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
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:5]}


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


def cell_eval(p: int, cell: str, loader=load) -> dict:
    rows, bad = [], []
    for s in mj.SEEDS:
        F, G = loader(p, cell, s, "F"), loader(p, cell, s, "G")
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
    return {"p": p, "cell": cell, "train_frac": mj.frac(p, cell), "verdict_cal": reading_cal(rows, n_gen),
            "generalises": n_gen >= 2, "n_both_generalised": n_gen,
            "n_evaluable": sum(r["dpow_post"] is not None for r in rows),
            "n_not_generalised": sum(g is None for r in rows for g in r["gen"]), "rows": rows, "problems": bad}


def q1(cells: list[dict]) -> dict:
    g = {c["cell"]: c["generalises"] for c in cells}
    a_, b_ = g["n16100"], g["n18100"]
    reading = ("passt zu alpha ~ 1 (Daten je Zahlzeile), nicht zu p^(5/3)" if a_ and b_ else
               "passt zu p^(5/3), nicht zu alpha = 1 mit Schwelle <= 30.7" if not a_ and not b_ else
               "Schwelle in N/p bei p 503 zwischen 32 und 36: unentschieden" if b_ else "nicht monoton: unklar")
    return {"reading": reading, "generalises": g}


def q2(cells: list[dict]) -> dict:
    ev = [c for c in cells if c["verdict_cal"] not in ("kein Lernen im Budget", "nicht auswertbar")]
    if not ev:
        return {"reading": "kein Lernen im Budget", "smallest_fraction": None}
    smallest = min(ev, key=lambda c: c["train_frac"])["train_frac"]
    weak = [f"{c['p']}_{c['cell']}" for c in ev if c["verdict_cal"] == "nicht unterscheidbar"]
    if weak:
        return {"reading": "Steuerung schwindet bei kleinem Anteil", "cells": weak, "smallest_fraction": smallest}
    if all(c["verdict_cal"] == "steuert" for c in ev):
        return {"reading": "K2 haelt bis zum kleinsten generalisierenden Anteil", "smallest_fraction": smallest}
    return {"reading": "beschreibend", "smallest_fraction": smallest}


def spearman(pairs: list[tuple[float, float]]) -> float | None:
    if len(pairs) < 3:
        return None
    rk = lambda w: np.argsort(np.argsort(w)).astype(float)   # noqa: E731
    return float(np.corrcoef(rk(np.array([a for a, _ in pairs])), rk(np.array([b for _, b in pairs])))[0, 1])


def mask_check(cells: list[dict]) -> dict | None:
    f = HERE / "mask_prediction_s68_141.json"
    if not f.exists():
        return None
    m = {(r["p"], r["cell"], r["seed"]): r["delta_mask"] for r in json.loads(f.read_text(encoding="utf-8"))}
    pairs = [(m[(c["p"], c["cell"], r["seed"])], r["dpow_post"]) for c in cells for r in c["rows"] if r["dpow_post"] is not None]
    return {"spearman_pooled": spearman(pairs), "n": len(pairs)}


def threshold_fit(points: list[dict]) -> dict:
    """Amendment a (session 68, before any result): which single-variable threshold separates generalizing from
    non-generalizing cells? points: {p, n_pairs, generalises}. A variable fits if max over non-generalizing cells <
    min over generalizing cells (or one group is empty). Descriptive only."""
    var = {"pairs_per_p": lambda c: c["n_pairs"] / c["p"], "fraction": lambda c: c["n_pairs"] / c["p"] ** 2,
           "n_pairs": lambda c: c["n_pairs"]}
    fits = {}
    for k, f in var.items():
        yes = [f(c) for c in points if c["generalises"]]
        no = [f(c) for c in points if not c["generalises"]]
        fits[k] = (not yes or not no) or max(no) < min(yes)
    ok = [k for k, v in fits.items() if v]
    reading = ("Muster passt zu Paaren je Token" if ok == ["pairs_per_p"] else
               "nicht getrennt" if len(ok) > 1 else "passt zu keiner Einzelschwelle" if not ok else f"passt nur zu {ok[0]}")
    return {"fits": fits, "reading": reading}


def exp137_points() -> list[dict]:
    f = HERE.parent / "EXP-137-modulus-density" / "summary.json"
    if not f.exists():
        return []
    return [{"p": c["p"], "n_pairs": int(round(c["train_frac"] * c["p"] ** 2)), "generalises": c["n_both_generalised"] >= 2,
             "source": "EXP-137"} for c in json.loads(f.read_text(encoding="utf-8"))["cells"]]


def main(loader=load, extra=None) -> dict:
    cells = [cell_eval(p, c, loader) for p in mj.PS for c in mj.NS]
    pts = [{"p": c["p"], "n_pairs": mj.NS[c["cell"]], "generalises": c["generalises"], "source": "EXP-139"} for c in cells]
    pts += exp137_points() if extra is None else extra
    return {"cells": cells, "q1": q1(cells), "q2": q2(cells), "mask_prediction_check": mask_check(cells),
            "threshold_fit": threshold_fit(pts), "threshold_points": pts}


def selftest() -> None:
    rng = np.random.default_rng(0)

    def fake(strength, gen=500, noise=0.1):
        def ld(p, cell, s, arm):
            T = [1, 2, 3, 4, 5] if arm == "F" else [6, 7, 8, 9, 10]
            g = gen(p, cell, arm) if callable(gen) else gen
            end = 30_000 if g is None else min(30_000, g + 2000)

            def pw():
                v = np.ones((p - 1) // 2) + rng.random((p - 1) // 2) * noise
                v[[k - 1 for k in T]] += strength(p, cell)
                return v
            steps = [t for t in [50, 250, 500, *range(1000, 30_001, 1000)] if t <= end]
            return {"snaps": {t: pw() for t in steps}, "T": T, "gen": g, "final_acc": None, "last_step": steps[-1]}
        return ld
    r = main(fake(lambda p, c: 5.0), extra=[])
    assert r["q1"]["reading"].startswith("passt zu alpha ~ 1") and r["q2"]["reading"].startswith("K2 haelt")
    r = main(fake(lambda p, c: 5.0, gen=None), extra=[])
    assert r["q1"]["reading"].startswith("passt zu p^(5/3)") and r["q2"]["reading"] == "kein Lernen im Budget"
    r = main(fake(lambda p, c: 5.0, gen=lambda p, c, arm: 500 if c == "n18100" else None), extra=[])
    assert r["q1"]["reading"].endswith("unentschieden")
    r = main(fake(lambda p, c: 5.0, gen=lambda p, c, arm: 500 if c == "n16100" else None), extra=[])
    assert r["q1"]["reading"] == "nicht monoton: unklar"
    r = main(fake(lambda p, c: 0.0), extra=[])
    assert r["q2"]["reading"] == "Steuerung schwindet bei kleinem Anteil"
    r = main(fake(lambda p, c: 5.0, gen=lambda p, c, arm: 500 if arm == "F" else None), extra=[])
    assert all(not c["generalises"] for c in r["cells"])
    print("[exp141] selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        res = main()
        (HERE / "summary.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        rd = lambda v: None if v is None else round(v, 2)   # noqa: E731
        for c in res["cells"]:
            print(c["p"], c["cell"], round(100 * c["train_frac"], 2), "%", c["verdict_cal"],
                  "| post:", [rd(r["dpow_post"]) for r in c["rows"]], "| q99:", [rd(r.get("placebo_q99")) for r in c["rows"]],
                  "| pre:", [rd(r["dpow_pre"]) for r in c["rows"]], "| 2000:", [rd(r["dpow_2000"]) for r in c["rows"]],
                  "| gen:", [r["gen"] for r in c["rows"]], c["problems"])
        print("Q1:", res["q1"])
        print("Q2:", res["q2"])
        print("first-order prediction check:", res["mask_prediction_check"])
