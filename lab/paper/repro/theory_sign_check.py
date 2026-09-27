"""Paper section 5 numerical check (session 25, numpy only, run from the repo root). See lab/JOURNAL.md, session 25."""
import sys, numpy as np
sys.path.insert(0, "lab/tools"); import confirm_splits as cs
p, d = 113, 128; K = (p-1)//2
a = np.arange(p)
B = [np.ones(p)/np.sqrt(p)]
for k in range(1, K+1): B += [np.cos(2*np.pi*k*a/p)*np.sqrt(2/p), np.sin(2*np.pi*k*a/p)*np.sqrt(2/p)]
B = np.stack(B, 1)
def fp(W): sq = ((B.T @ W)**2).sum(1); return sq[1::2] + sq[2::2]
res = {"g": [], "sign": [], "g_share": [], "sign_share": []}
for s in range(900, 910):
    rng = np.random.default_rng(s)
    for arm in "FG":
        idx, T = cs.build(99, "add", p, s, arm, 2.0)
        m = np.zeros((p, p)); m[idx//p, idx%p] = 1
        t = np.arange(p)[:, None]; c = np.arange(p)[None, :]
        Lr = m[t, (c-t)%p] + m[(c-t)%p, t]           # [t, c], shared path
        Lr = Lr - Lr.mean(1, keepdims=True)           # P-perp over c
        J = rng.normal(size=(p, d)) / np.sqrt(p)      # isotropic random Jacobian (logits c -> embedding dim)
        g = Lr @ J                                    # [t, d] first gradient (up to sign/scale)
        for name, W in (("g", g), ("sign", np.sign(g))):
            pw = fp(W); top = set(np.argsort(-pw)[:5] + 1)
            res[name].append(len(top & set(T))); res[name + "_share"].append(pw[[k-1 for k in T]].sum()/pw.sum())
for k, v in res.items(): print(k, np.mean(v).round(3))
