"""Session 34 (numpy only): per-output pair counts of the engineered split E vs the control D (weights permuted within anti-diagonals).
Traces the paper's "realized per-output counts differ by ~3 of ~34 pairs". Output (session 34): mean |count_E(c) - count_D(c)| 2.80
(per seed 2.57-2.92), mean count 33.9, max 12 over 10 seeds.   python lab/experiments/EXP-018-split-speed/posthoc/count_diff_s34.py"""
import glob
import numpy as np
P = 113
md, mc, mx = [], [], []
for f in sorted(glob.glob("lab/experiments/EXP-018-split-speed/splits/seed*_train_E.npy")):
    E, D = np.load(f), np.load(f.replace("_E", "_D"))
    cE, cD = (np.bincount((X // P + X % P) % P, minlength=P) for X in (E, D))
    md.append(np.abs(cE - cD).mean()); mc.append(cE.mean()); mx.append(np.abs(cE - cD).max())
print(len(md), "mean |dcount| %.2f (range %.2f-%.2f), mean count %.1f, max %d" % (np.mean(md), min(md), max(md), np.mean(mc), max(mx)))
