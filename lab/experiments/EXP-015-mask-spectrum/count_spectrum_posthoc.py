import sys, json, numpy as np
sys.path.insert(0,'lab/experiments/EXP-015-mask-spectrum'); sys.path.insert(0,'lab/experiments/EXP-014-split-vs-init')
import mask_spectrum as ms, grad_preview as gp
import predict as p12
k009={}
for r in json.loads(p12.EXP009.read_text(encoding='utf-8'))['runs']:
    if r['run'].startswith('txf_add_p113_wd1.0_frac0.3_seed'): k009[int(r['run'].split('seed')[1].split('_')[0])]=r['k_final']
p=113; K=56
rb=[]; rho=[]
for s in range(10):
    M=ms.mask_matrix(s); n=M.sum(0)+M.sum(1)
    P=np.abs(np.fft.fft(n))**2; C=P[1:K+1]+P[p-K:][::-1]
    m=ms.m0(M); rho.append(gp.spearman(C,m)); rb.append(p12.rbar(C,k009[s]))
print('rho(count spectrum, M0):',np.round(rho,2),np.mean(rho)); print('rbar count spectrum:',np.round(rb,3),np.mean(rb))
