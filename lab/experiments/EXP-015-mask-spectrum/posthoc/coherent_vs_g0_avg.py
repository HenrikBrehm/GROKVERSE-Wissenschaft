"""Post hoc (session 5): same comparison as m0_vs_g0.py (G0 averaged over 3 inits per split j, seeds 0-9),
now M0 vs coherent M0c. Run from the project root through guarded_run.py."""
import sys
import numpy as np
sys.path.insert(0, 'lab/experiments/EXP-014-split-vs-init')
sys.path.insert(0, 'lab/experiments/EXP-015-mask-spectrum')
sys.path.insert(0, 'lab/experiments/EXP-015-mask-spectrum/posthoc')
import grad_preview as gp
import mask_spectrum as ms
from coherent_m0 import m0c
r0, rc, rcf = [], [], []
for j in range(10):
    M = ms.mask_matrix(j)
    G = np.mean([gp.g0(i, j) / gp.g0(i, j).sum() for i in range(3)], axis=0)
    r0.append(gp.spearman(ms.m0(M), G))
    rc.append(gp.spearman(m0c(M), G))
    rcf.append(gp.spearman(m0c(ms.mask_matrix((j + 1) % 10)), G))
print('M0 :', np.round(r0, 2), round(float(np.mean(r0)), 3))
print('M0c:', np.round(rc, 2), round(float(np.mean(rc)), 3))
print('M0c foreign:', round(float(np.mean(rcf)), 3), '| M0c higher in', int(np.sum(np.array(rc) > np.array(r0))), 'of 10')
