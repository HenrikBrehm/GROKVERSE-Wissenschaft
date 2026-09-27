"""Session 27 (post hoc, numpy only, no training): how many update-equivalents of displacement along the OLD
direction are still "in flight" in Adam's first moment at a data switch?

Scalar model of one coordinate: constant gradient g for t steps (bias-corrected AdamW with the study's betas
0.9/0.98; weight decay ignored, lr*wd = 1e-3 per step), then no gradient along the old direction. The second moment
after the switch is fed with gradients of magnitude r*g (r = proxy for how strongly the new data hit the same
coordinate). Output: sum of all post-switch updates divided by the last pre-switch update, i.e. the number of
"extra old steps" that zeroing exp_avg at the switch removes (the new-direction ramp of m is identical with and
without zeroing, so this tail is the only difference). Compare with EXP-059 summary.json "delta_shift".

    python lab/experiments/EXP-059-momentum-exposure/inflight_adam.py
"""
import numpy as np

B1, B2, EPS = 0.9, 0.98, 1e-8


def tail(t: int, r: float, K: int = 400, g: float = 1.0) -> float:
    m = v = 0.0
    last = 0.0
    for s in range(1, t + 1):
        m = B1 * m + (1 - B1) * g
        v = B2 * v + (1 - B2) * g * g
        last = (m / (1 - B1 ** s)) / (np.sqrt(v / (1 - B2 ** s)) + EPS)
    out = 0.0
    for k in range(1, K + 1):
        s = t + k
        m = B1 * m
        v = B2 * v + (1 - B2) * (r * g) ** 2
        out += (m / (1 - B1 ** s)) / (np.sqrt(v / (1 - B2 ** s)) + EPS)
    return out / last


if __name__ == "__main__":
    print("t   r=0    r=0.5  r=1    r=2   (update-equivalents in flight)")
    for t in (10, 25, 30, 35, 50):
        print(t, *(f"{tail(t, r):6.2f}" for r in (0.0, 0.5, 1.0, 2.0)))
