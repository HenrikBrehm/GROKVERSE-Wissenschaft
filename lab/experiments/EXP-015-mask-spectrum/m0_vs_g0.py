"""EXP-015 check: M0 (mask only) vs actual first-gradient spectrum G0 averaged over 3 inits, per split.
Run from the project root through guarded_run.py. Result 2026-09-26: mean Spearman 0.57, foreign-split control -0.07."""
import sys, numpy as np
sys.path.insert(0,'lab/experiments/EXP-014-split-vs-init'); sys.path.insert(0,'lab/experiments/EXP-015-mask-spectrum')
import grad_preview as gp, mask_spectrum as ms
rho=[]; rho_other=[]
for j in range(10):
    m=ms.m0(ms.mask_matrix(j))
    G=np.mean([gp.g0(i,j)/gp.g0(i,j).sum() for i in range(3)],axis=0)
    rho.append(gp.spearman(m,G)); rho_other.append(gp.spearman(ms.m0(ms.mask_matrix((j+1)%10)),G))
print('spearman M0(split j) vs mean G0(.,j):',np.round(rho,2),np.mean(rho))
print('control M0(split j+1) vs G0(.,j):',np.mean(rho_other))
