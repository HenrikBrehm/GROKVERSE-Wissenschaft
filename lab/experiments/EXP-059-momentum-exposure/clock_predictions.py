"""Session 27 (numpy only, no training): predictions of two clock models for a beta1/beta2 variation of the N28/N29
switch protocol, from the scalar Adam model of inflight_adam.py.

Displacement clock (H40-like): lock-in depends on the displacement along the old direction, in update-equivalents,
including the momentum tail after the switch. Pre-switch, bias-corrected Adam moves ~1 update per step for a consistent
gradient, almost independent of beta1/beta2, so only the tail changes -> effective exposure t_eff = t + tail(beta1, beta2).
beta2-horizon clock (N37): the window scales with 1/(1 - beta2) (50 steps at 0.98).
Printed: tail, the pre-switch displacement after t steps (update-equivalents), and the switch step t* that gives the same
effective exposure as the reference t = 25 at (0.9, 0.98) under each model.

    python lab/experiments/EXP-059-momentum-exposure/clock_predictions.py
"""
import numpy as np

EPS = 1e-8


def pre_and_tail(t: int, b1: float, b2: float, r: float = 1.0, K: int = 600) -> tuple[float, float]:
    m = v = 0.0
    pre = last = 0.0
    for s in range(1, t + 1):
        m = b1 * m + (1 - b1)
        v = b2 * v + (1 - b2)
        last = (m / (1 - b1 ** s)) / (np.sqrt(v / (1 - b2 ** s)) + EPS)
        pre += last
    tail = 0.0
    for k in range(1, K + 1):
        s = t + k
        m = b1 * m
        v = b2 * v + (1 - b2) * r * r
        tail += (m / (1 - b1 ** s)) / (np.sqrt(v / (1 - b2 ** s)) + EPS)
    return pre, tail / last


if __name__ == "__main__":
    ref_pre, ref_tail = pre_and_tail(25, 0.9, 0.98)
    target = ref_pre + ref_tail
    print(f"reference (0.9, 0.98), t = 25: pre {ref_pre:.2f}, tail {ref_tail:.2f}, exposure {target:.2f}")
    print("beta1  beta2  tail(t=25)  t* displacement clock  t* beta2 clock")
    for b1, b2 in ((0.8, 0.98), (0.9, 0.98), (0.95, 0.98), (0.9, 0.95), (0.9, 0.995)):
        ts = next(t for t in range(1, 400) if sum(pre_and_tail(t, b1, b2)) >= target)
        print(f"{b1:5}  {b2:5}  {pre_and_tail(25, b1, b2)[1]:10.2f}  {ts:21d}  {25 * (1 - 0.98) / (1 - b2):14.1f}")
