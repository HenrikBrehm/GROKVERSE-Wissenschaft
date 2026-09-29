"""Session 51, post hoc EXPLORATION on seen data (EXP-103 part B + part A, P1 preset add 113, seeds 1000-1009, paired F/G
splits and init). Follow-up to toy_order_s50.py, which found that in the toy model steering (Delta_pow > 1) starts together with
fitting the training pairs (train accuracy >= 0.1), as in the small LM (EXP-113/114), only much earlier.
Question: is this coupling a coincidence of one setting, or does the steering onset move WITH the fitting onset when the
learning rate changes the pace? Three arms with the same lr*wd: lr 1e-3/wd 1 (P1, part A), lr 2e-3/wd 0.5 and lr 5e-4/wd 2
(part B). Already seen: the early Delta_pow curves of part B (paired difference +1.83 at t = 100, i.e. lr 2e-3 steers earlier)
and one P1 seed's dense train curve; the train-accuracy onsets of the part-B arms were NOT looked at before writing this.

Definitions (continuous, fixed before the run):
  t_learn = first step where min(train_F, train_G) >= 0.1, linear interpolation on the dense 10-step train grid;
  t_steer = first crossing of Delta_pow = 1, linear interpolation in log t between spectra snapshots (t > 0);
  r = ln(t_steer / t_learn) per seed and arm.
Readings (fixed before the run; paired over the 10 seeds, lr 2e-3 vs lr 5e-4; bootstrap 95 % CI, 10 000 resamples, seed 0):
  'not separable'  if |mean paired diff of ln t_learn| < 0.2 (the learning rate does not move the fitting onset enough);
  'coupled'        else if |mean paired diff of r| < 0.2 and its CI lies inside (-0.4, 0.4);
  'decoupled'      else if |mean paired diff of r| > 0.4 and its CI excludes 0 (steering keeps its own clock);
  'unclear'        otherwise. P1 is reported descriptively as the middle arm.
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-114-lm-dilution-pilot/toy_order_lr_s51.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
E103 = LAB / "experiments/EXP-103-early-steering-curve"
ARMS = {"lr2e-3_wd0.5": ("raw_x_lr2e-3_wd0.5", "_lr0.002_wd0.5"), "P1_lr1e-3_wd1": ("raw", ""),
        "lr5e-4_wd2": ("raw_x_lr5e-4_wd2", "_lr0.0005_wd2.0")}
SEEDS = range(1000, 1010)


def delta(pF, pG, F, G):
    s = lambda pw, S: pw[..., [k - 1 for k in S]].sum(-1)   # noqa: E731  (as EXP-103 analyze.delta)
    return float(np.log(s(pF, F) / s(pF, G)) + np.log(s(pG, G) / s(pG, F)))


def t_learn(dense: dict) -> float | None:
    st = np.asarray(dense["F"]["train_steps"], float)
    assert st.tolist() == dense["G"]["train_steps"]
    acc = np.minimum(dense["F"]["train_acc"], dense["G"]["train_acc"])
    i = next((k for k, a in enumerate(acc) if a >= 0.1), None)
    if i is None:
        return None
    if i == 0:
        return float(st[0])
    return float(st[i - 1] + (0.1 - acc[i - 1]) / (acc[i] - acc[i - 1]) * (st[i] - st[i - 1]))


def t_steer(steps: list[int], dp: list[float]) -> float | None:
    for k in range(1, len(steps)):
        if dp[k] > 1:
            if k == 1 or steps[k - 1] == 0:
                return float(steps[k])
            a, b = np.log(steps[k - 1]), np.log(steps[k])
            return float(np.exp(a + (1 - dp[k - 1]) / (dp[k] - dp[k - 1]) * (b - a)))
    return None


def boot(x: np.ndarray) -> list[float]:
    rng = np.random.default_rng(0)
    m = rng.choice(x, size=(10_000, len(x)), replace=True).mean(1)
    return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]


def run_arm(arm: str, s: int) -> dict:
    sub, suffix = ARMS[arm]
    T = {a: json.loads((LAB / f"confirm/splits/confirm_exp1_eps2.0_add113_seed{s}_{a}.json").read_text(encoding="utf-8"))["targets"] for a in "FG"}
    d = {a: E103 / sub / f"EXP-016_baseline_seed{s}_thr1_confirm_exp1_eps2.0_add113_seed{s}_{a}{suffix}_devcuda" for a in "FG"}
    st = [int(x) for x in np.load(d["F"] / "spectra_steps.npy")]
    assert st == [int(x) for x in np.load(d["G"] / "spectra_steps.npy")]
    sp = {a: np.load(d[a] / "spectra.npy") for a in "FG"}
    dense = {a: json.loads((d[a] / "result.json").read_text(encoding="utf-8"))["dense"] for a in "FG"}
    keep = [i for i, t in enumerate(st) if t <= 250]
    steps = [st[i] for i in keep]
    dp = [delta(sp["F"][i], sp["G"][i], T["F"], T["G"]) for i in keep]
    tl, ts = t_learn(dense), t_steer(steps, dp)
    return {"t_learn": tl, "t_steer": ts, "r": (float(np.log(ts / tl)) if tl and ts else None)}


def main() -> None:
    rows = {arm: {s: run_arm(arm, s) for s in SEEDS} for arm in ARMS}
    hi, lo = "lr2e-3_wd0.5", "lr5e-4_wd2"
    ok = [s for s in SEEDS if all(rows[a][s]["r"] is not None for a in (hi, lo))]
    dl = np.array([np.log(rows[hi][s]["t_learn"] / rows[lo][s]["t_learn"]) for s in ok])
    dr = np.array([rows[hi][s]["r"] - rows[lo][s]["r"] for s in ok])
    ci_r = boot(dr)
    if abs(dl.mean()) < 0.2:
        reading = "not separable"
    elif abs(dr.mean()) < 0.2 and -0.4 < ci_r[0] and ci_r[1] < 0.4:
        reading = "coupled"
    elif abs(dr.mean()) > 0.4 and (ci_r[0] > 0 or ci_r[1] < 0):
        reading = "decoupled"
    else:
        reading = "unclear"
    per_arm = {a: {k: float(np.median([rows[a][s][k] for s in SEEDS if rows[a][s][k] is not None]))
                   for k in ("t_learn", "t_steer", "r")} for a in ARMS}
    out = {"reading": reading, "n_paired": len(ok), "diff_ln_t_learn_hi_minus_lo": float(dl.mean()), "ci_ln_t_learn": boot(dl),
           "diff_r_hi_minus_lo": float(dr.mean()), "ci_r": ci_r,
           "median_per_arm": per_arm, "rows": {a: {str(s): v for s, v in r.items()} for a, r in rows.items()}}
    (HERE / "toy_order_lr_s51.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
