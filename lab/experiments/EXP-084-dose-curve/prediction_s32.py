"""EXP-084: prediction written BEFORE any EXP-084 run (session 32, 2026-09-27, window closed). No training, only stored JSON.

Two competing phenomenological models for the generalisation time b (first test >= 0.95) of an engineered split, calibrated on
SEEN runs only (EXP-020/042 only-G runs, seeds 30/31/32/34, same init and test set per seed; posthoc_speed_dose.json):
  M_share  b = T_inf + A / (s - s0)   s = realised M0 power share on the 5 targets (the split's pair spectrum).
           Concentration acts only through s; since s saturates for eps >= 16, b saturates too.
  M_eps    log2 b linear in log2 eps (through the eps 2 and eps 8 medians). The extremity of the draw weights acts, not s.
Calibration points (medians over the 4 seen seeds): eps 2 -> s 0.18, b 775; eps 8 -> s 0.357, b 437.5.
M_share has a third parameter s0; it is fixed by the random-split level: EXP-003d random splits (CPU, complement test sets,
different init seeds) median 5975 at s ~ 0.09 (R arms of EXP-084: 0.081-0.096). This is a coarse anchor, labelled as such.
Check against the censored seen point: eps 1 (s ~ 0.115) did not generalise by 2000 in 4/4 seeds.
Output: predicted median b per EXP-084 arm (using the arms' realised shares per unit, cap 4000) and the predicted reading
of analyze.py, plus the discriminating quantity median log2(b(e32) / b(e8)).
  python lab/experiments/EXP-084-dose-curve/prediction_s32.py
"""
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ARMS = ("R", "e0.5", "e1", "e2", "e4", "e8", "e16", "e32")
CAP = 4000
S2, B2, S8, B8 = 0.18, 775.0, 0.357, 437.5
S_R, B_R = 0.09, 5975.0


def fit_share() -> tuple[float, float, float]:
    """Solve T_inf + A/(s - s0) through the three anchors (bisection in s0 on the ratio condition)."""
    def resid(s0: float) -> float:
        a = (B2 - B8) / (1 / (S2 - s0) - 1 / (S8 - s0))
        t = B2 - a / (S2 - s0)
        return t + a / (S_R - s0) - B_R
    lo, hi = 0.0, S_R - 1e-6
    for _ in range(200):
        mid = (lo + hi) / 2
        (lo, hi) = (mid, hi) if resid(mid) < 0 else (lo, mid)
    s0 = (lo + hi) / 2
    a = (B2 - B8) / (1 / (S2 - s0) - 1 / (S8 - s0))
    return B2 - a / (S2 - s0), a, s0


def m_share(s: float, p: tuple[float, float, float]) -> float:
    t, a, s0 = p
    return CAP if s <= s0 else min(CAP, t + a / (s - s0))


def m_eps(arm: str) -> float:
    if arm == "R":
        return CAP
    e = float(arm[1:])
    slope = math.log2(B8 / B2) / 2.0                     # per doubling of eps
    return min(CAP, B2 * 2 ** (slope * math.log2(e / 2.0)))


def main() -> None:
    p = fit_share()
    shares = {a: [] for a in ARMS}
    for u in range(10):
        meta = json.loads((HERE / "splits" / f"u{u}.json").read_text(encoding="utf-8"))
        for a in ARMS:
            shares[a].append(meta["arms"][a]["m0_target_share"])
    out = {"note": "prediction before any EXP-084 run; calibrated on seen seeds only", "m_share_params": {"T_inf": p[0], "A": p[1], "s0": p[2]},
           "check_eps1_seen_s0.115_pred": m_share(0.115, p), "per_arm": {}}
    for a in ARMS:
        bs = [m_share(s, p) for s in shares[a]]
        out["per_arm"][a] = {"share_median": float(np.median(shares[a])), "M_share_median_b": round(float(np.median(bs))),
                             "M_eps_b": round(m_eps(a))}
    r32 = [math.log2(m_share(s32, p) / m_share(s8, p)) for s32, s8 in zip(shares["e32"], shares["e8"])]
    out["median_log2_e32_over_e8"] = {"M_share": float(np.median(r32)), "M_eps": math.log2(m_eps("e32") / m_eps("e8"))}
    (HERE / "prediction_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
