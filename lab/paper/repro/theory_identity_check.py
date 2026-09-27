"""Paper section 5 numerical check (session 25, numpy only, run from the repo root). See lab/JOURNAL.md, session 25."""
import numpy as np
p = 113; rng = np.random.default_rng(0)
def parts(m):
    t = np.arange(p)[:, None]; c = np.arange(p)[None, :]
    L = m[t, (c - t) % p]; R = m[(c - t) % p, t]          # l_t(c), r_t(c)
    Lh, Rh = np.fft.fft(L, axis=0), np.fft.fft(R, axis=0)  # over t -> [k, c]
    return Lh, Rh
def P(v):  # remove c-mean
    return v - v.mean(axis=1, keepdims=True)
for name, m in (("random", (rng.random((p, p)) < 0.3).astype(float)),
                ("marginal-only", np.repeat((rng.random(p) < 0.3).astype(float)[:, None], p, 1)),
                ("marginal-only right", np.repeat((rng.random(p) < 0.3).astype(float)[None, :], p, 0))):
    Lh, Rh = parts(m)
    lhs = (np.abs(P(Lh + Rh)) ** 2).sum(1)
    nL, nR = Lh.sum(1), Rh.sum(1)
    M0c = (np.abs(Lh + Rh) ** 2).sum(1)
    rhs = M0c - np.abs(nL + nR) ** 2 / p
    sep = (np.abs(P(Lh)) ** 2).sum(1) + (np.abs(P(Rh)) ** 2).sum(1)
    print(name, "identity max err", float(np.max(np.abs(lhs - rhs))), "| shared max (k>=1)", float(lhs[1:].max()), "| separate max (k>=1)", float(sep[1:].max()))
rho = (rng.random(p) < 0.3).astype(float)
m = np.repeat(rho[:, None], p, 1)
Lh, Rh = parts(m)
lhs = (np.abs(P(Lh + Rh)) ** 2).sum(1)
print("m=rho(a): shared power vs p|rho_hat|^2 max rel err", float(np.max(np.abs(lhs[1:] - p * np.abs(np.fft.fft(rho)[1:]) ** 2) / (p * np.abs(np.fft.fft(rho)[1:]) ** 2))))
print("left part after P:", float((np.abs(P(Lh)) ** 2).sum()))
