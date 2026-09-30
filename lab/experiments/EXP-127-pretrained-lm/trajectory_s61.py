import sys, json, glob
import numpy as np
sys.path.insert(0, 'lab/experiments/EXP-127-pretrained-lm')
from analyze import power, residual, delta_pow
out = {}
for s in (4000, 4001):
    tj = json.load(open(f'lab/confirm/lm1_splits/seed{s}.json'))['targets']
    S = {}
    for arm in 'FG':
        d = glob.glob(f'lab/experiments/EXP-127-pretrained-lm/raw/pt_seed{s}_seed{s}_{arm}_steps4000_*')[0]
        S[arm] = np.load(d + '/in_snapshots.npy'); steps = np.load(d + '/snapshot_steps.npy')
    row = []
    for i, st in enumerate(steps):
        if st == 0: continue
        pF = power(residual(S['F'][i], S['F'][0])); pG = power(residual(S['G'][i], S['G'][0]))
        top = lambda p: [int(k)+1 for k in np.argsort(-p)[:5]]
        row.append((int(st), round(delta_pow(pF, pG, tj['F'], tj['G']), 3), top(pF), top(pG)))
    out[s] = row
    print(s, tj)
    for r in row: print('  ', r)
json.dump({str(k): v for k, v in out.items()}, open('lab/experiments/EXP-127-pretrained-lm/trajectory_s61.json', 'w'), indent=1)
