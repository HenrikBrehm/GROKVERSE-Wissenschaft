"""Post hoc (session 31), EXPLORATION, stored P1 runs and frozen P1 splits only (no training).

Question: within one concentration level (eps 2), does the realised target share of the split's M0 predict how early the run
generalises? Stated before looking: Spearman(share, gen_step) < 0 (more concentrated -> earlier). One predictor, one test.
Motivation: across eps 1/2/8 (EXP-020/042 only-G runs) generalisation is strictly ordered by concentration (posthoc_speed_dose.py).
Data: P1 add 113, 50 seeds x arms F/G (GPU, 2000 steps; test set = complement of the split, so it differs between runs).
share = M0 power on the arm's own 5 targets / total M0 power (confirm_splits.m0). Censored runs (no gen in 2000) get rank last.
Added after the first look (same session, labelled): F and G of one init share the init, so also (a) a paired sign test within
init (does the higher-share arm generalise earlier?) and (b) the between-seed Spearman of the per-seed mean share vs mean gen
(main block only, init seed == split seed; censored = 2000).
  python lab/confirm/speed_posthoc_share_within.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
import confirm_splits as cs  # noqa: E402

P = 113


def spear(x, y):
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def main() -> None:
    share, gen, rows = [], [], []
    for d in sorted((LAB / "confirm/raw").glob("EXP-016_*add113_seed*_[FG]_devcuda")):
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        seed, arm = int(d.name.split("_seed")[-1].split("_")[0]), d.name.split("_")[-2]
        init = int(d.name.split("_seed")[1].split("_")[0])
        assert r["status"] == "completed" and r["steps_completed"] == 2000, d.name
        T = cs.target_sets(1, "add", P, seed)[arm]
        m0 = cs.m0(np.load(LAB / f"confirm/splits/confirm_exp1_eps2.0_add113_seed{seed}_{arm}.npy"), "add", P)
        s = float(m0[[k - 1 for k in T]].sum() / m0.sum())
        g = (r.get("events") or {}).get("generalization_step")
        share.append(s); gen.append(np.inf if g is None else g)
        rows.append({"seed": seed, "init": init, "arm": arm, "share": round(s, 4), "gen": g})
    share, gen = np.array(share), np.array(gen)
    rho = spear(share, gen)
    rng = np.random.default_rng(0)
    null = np.array([spear(share, rng.permutation(gen)) for _ in range(20000)])
    p_one = float((null <= rho).mean())
    fin = np.isfinite(gen)
    out = {"n": len(gen), "n_censored": int((~fin).sum()), "share_mean": float(share.mean()), "share_sd": float(share.std(ddof=1)),
           "gen_median": float(np.median(gen[fin])), "gen_iqr": [float(np.percentile(gen[fin], 25)), float(np.percentile(gen[fin], 75))],
           "spearman_share_gen": rho, "p_one_sided_perm": p_one, "rows": rows,
           "note": "post hoc exploration on seen P1 runs; not a confirmation"}
    pairs = {}
    for r in rows:
        pairs.setdefault((r["init"], r["seed"]), {})[r["arm"]] = r
    win = lose = tie = 0
    for v in pairs.values():
        hi, lo = (v["F"], v["G"]) if v["F"]["share"] > v["G"]["share"] else (v["G"], v["F"])
        gh, gl = (np.inf if x["gen"] is None else x["gen"] for x in (hi, lo))
        win, lose, tie = win + (gh < gl), lose + (gh > gl), tie + (gh == gl)
    n = win + lose
    out["paired_within_init"] = {"pairs": len(pairs), "higher_share_earlier": int(win), "later": int(lose), "ties": int(tie),
                                 "p_one_sided_sign": sum(math.comb(n, k) for k in range(win, n + 1)) / 2 ** n}
    main_ = [(v["F"], v["G"]) for (i, s), v in pairs.items() if i == s]
    ms = np.array([(f["share"] + g["share"]) / 2 for f, g in main_])
    mg = np.array([((f["gen"] or 2000) + (g["gen"] or 2000)) / 2 for f, g in main_])
    rb = spear(ms, mg)
    nb = np.array([spear(ms, rng.permutation(mg)) for _ in range(20000)])
    out["between_seed"] = {"n": len(main_), "spearman": rb, "p_one_sided_perm": float((nb <= rb).mean())}
    (LAB / "confirm/speed_posthoc_share_within.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print({k: v for k, v in out.items() if k != "rows"})


if __name__ == "__main__":
    main()
