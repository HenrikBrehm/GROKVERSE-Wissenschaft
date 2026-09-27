import json, glob, numpy as np, os
p = 113; K = 56
def sh(idx):
    m = np.zeros((p, p)); m[idx//p, idx%p] = 1
    t = np.arange(p)[:, None]; c = np.arange(p)[None, :]
    X = np.fft.fft(m[t, (c-t)%p] + m[(c-t)%p, t], axis=0); X = X - X.mean(1, keepdims=True)
    s = (np.abs(X)**2).sum(1); return s[1:K+1] + s[p-K:][::-1]
for kind in ("eng", "shuf"):
    R, S = [], []
    for f in sorted(glob.glob(f"lab/experiments/EXP-047-marginal-control/splits/*{kind}*.npy")):
        meta = json.load(open(f[:-4] + ".json")); T = meta["targets"]
        pw = sh(np.load(f)); r = np.argsort(np.argsort(-pw))
        R.append(np.mean([r[k-1] for k in T])); S.append(pw[[k-1 for k in T]].sum()/pw.sum())
    print(kind, len(R), round(np.mean(R), 1), round(np.mean(S), 3))
