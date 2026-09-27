"""Session 32 (2026-09-27, window closed), POST HOC exploration on stored runs, no training.

Question: engineered splits grok earlier the more their pair-mask spectrum M0 concentrates on the targets (M_share, session 32).
Does the same hold for ORDINARY random splits, i.e. does the mask spectrum of a random 30 % split explain part of the large
seed-to-seed spread of the grokking time (3500-11200 steps)?
Data: transformer, add 113, frac 0.3, wd 1, CPU; seeds 0-9 = study runs (training/runs/..._arch25k, 25 000 steps), seeds 10-19 =
EXP-003d baselines (freq_ban, full run to generalisation). Split = make_dataset(get_config("arch25k", seed)); init seed = split
seed, so split and init are NOT separable here (R4 separates them).
Stated before computing (nothing of the gen-vs-spectrum relation has been looked at):
  primary    Spearman(s_K, gen) < 0, s_K = M0 power share on the run's own final top-5 frequencies K (the M_share analogue:
             the frequencies the network actually uses), one-sided permutation p (20 000 draws, seed 0).
  secondary  Spearman(s_top5, gen) < 0, s_top5 = share of the 5 largest M0 entries (independent of the network).
  descriptive M_share(s_K) from prediction_s32.json vs the observed gen (absolute level; expected to fail, since the model was
             calibrated on engineered splits with their target sets).
gen = first test >= 0.95 (study: transitions.primary.generalization.first_crossing_step; EXP-003d: events.generalization_step).
  python lab/confirm/speed_random_splits_s32.py
"""
import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "experiments/EXP-015-mask-spectrum"))
import mask_spectrum as ms  # noqa: E402

P1 = json.loads((LAB / "experiments/EXP-015-mask-spectrum/summary_phase1.json").read_text(encoding="utf-8"))
PAR = json.loads((LAB / "experiments/EXP-084-dose-curve/prediction_s32.json").read_text(encoding="utf-8"))["m_share_params"]


def spear(x, y) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def perm_p(x, y, n=20000) -> float:
    rho, rng = spear(x, y), np.random.default_rng(0)
    return float((np.array([spear(x, rng.permutation(y)) for _ in range(n)]) <= rho).mean())


def k_of(seed: int) -> list[int]:
    if seed < 10:
        return next(r["K"] for r in P1["rows"] if r["seed"] == seed)
    return json.loads((LAB / f"experiments/EXP-003-early-prediction/raw_d/EXP-001_baseline_t2000_m5_seed{seed}_thr4/result.json")
                      .read_text(encoding="utf-8"))["final_top_m_freqs"]


def gen_of(seed: int) -> int:
    if seed < 10:
        r = json.loads((ROOT / f"training/runs/txf_add_p113_wd1.0_frac0.3_seed{seed}_arch25k/run.json").read_text(encoding="utf-8"))
        return r["transitions"]["primary"]["generalization"]["first_crossing_step"]
    r = json.loads((LAB / f"experiments/EXP-003-early-prediction/raw_d/EXP-001_baseline_t2000_m5_seed{seed}_thr4/result.json")
                   .read_text(encoding="utf-8"))
    return r["events"]["generalization_step"]


def main() -> None:
    rows = []
    for s in range(20):
        pw = ms.m0(ms.mask_matrix(s))
        K = k_of(s)
        rows.append({"seed": s, "gen": gen_of(s), "K": K, "s_K": float(pw[[k - 1 for k in K]].sum() / pw.sum()),
                     "s_top5": float(np.sort(pw)[-5:].sum() / pw.sum())})
    g = np.array([r["gen"] for r in rows], dtype=float)
    sK, s5 = np.array([r["s_K"] for r in rows]), np.array([r["s_top5"] for r in rows])
    t, a, s0 = PAR["T_inf"], PAR["A"], PAR["s0"]
    out = {"note": "post hoc exploration; split and init confounded (same seed)", "n": len(rows),
           "gen_median": float(np.median(g)), "gen_range": [float(g.min()), float(g.max())],
           "s_K_median": float(np.median(sK)), "s_K_range": [float(sK.min()), float(sK.max())],
           "s_top5_median": float(np.median(s5)),
           "primary_spearman_sK_gen": spear(sK, g), "primary_p_one_sided": perm_p(sK, g),
           "secondary_spearman_stop5_gen": spear(s5, g), "secondary_p_one_sided": perm_p(s5, g),
           "M_share_pred_at_median_sK": (t + a / (np.median(sK) - s0)) if np.median(sK) > s0 else None,
           "rows": rows}
    (LAB / "confirm/speed_random_splits_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r["seed"], r["gen"], round(r["s_K"], 4), round(r["s_top5"], 4))


if __name__ == "__main__":
    main()
