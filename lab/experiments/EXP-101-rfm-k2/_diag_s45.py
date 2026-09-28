"""Session 45 diagnostic (not part of the experiment): is the fast-vs-dense AGOP mismatch in the selftest only from psd_sqrt
amplifying roundoff-level eigenvalues? Compare both paths with the square root replaced by the identity."""
import sys, numpy as np, torch
sys.path.insert(0, "lab/experiments/EXP-101-rfm-k2")
import rfm_k2 as R
torch.manual_seed(0); p, L = 11, 2.5
rng = np.random.default_rng(0); idx = rng.choice(p * p, size=60, replace=False)
(ab, Xtr, Ytr, _), _ = R.data(idx, p)
A = torch.randn(2 * p, 2 * p, dtype=R.DTYPE); M = torch.eye(2 * p, dtype=R.DTYPE) + 0.05 * (A @ A.T)
K = R.gauss_kernel(Xtr, Xtr, M, L); alpha = torch.linalg.solve(K, Ytr)
sq = R.psd_sqrt
R.psd_sqrt = lambda X: X
f, dn = R.agop_update(Xtr, ab, alpha, K, M, L, p), R.dense_update(Xtr, alpha, K, M, L)
print(f"pre-sqrt rel err {float((f-dn).abs().max()/dn.abs().max()):.2e}")
ev = torch.linalg.eigvalsh((dn + dn.T) / 2)
print("smallest eigenvalues", [f"{float(x):.1e}" for x in ev[:4]], "largest", f"{float(ev[-1]):.1e}")
R.psd_sqrt = sq
fs, ds = sq(f), sq(dn)
print(f"post-sqrt rel err {float((fs-ds).abs().max()/ds.abs().max()):.2e}")
