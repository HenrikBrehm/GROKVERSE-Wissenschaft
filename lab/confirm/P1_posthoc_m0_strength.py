"""P1 post hoc (session 25, exploratory; frozen P1 splits and summary only, no runs): does the M0 / centred-M0c target contrast of a seed's F/G splits
predict the size of its Delta_pow? Spearman over the 50 add-113 seeds, permutation p. Run from the repo root."""
import json, sys, numpy as np
sys.path.insert(0, "lab/tools"); import confirm_splits as cs
p, K = 113, 56
def shared(idx):
    m = np.zeros((p, p)); m[idx//p, idx%p] = 1
    t = np.arange(p)[:, None]; c = np.arange(p)[None, :]
    X = np.fft.fft(m[t, (c-t)%p] + m[(c-t)%p, t], axis=0); X = X - X.mean(1, keepdims=True)
    s = (np.abs(X)**2).sum(1); return s[1:K+1] + s[p-K:][::-1]
S = lambda pw, T: pw[[k-1 for k in T]].sum()
rows = json.load(open("lab/confirm/P1_summary.json"))["tasks"]["add113"]["rows"]
C1, C0, D = [], [], []
for r in rows:
    if not r["valid"]: continue
    s = r["seed"]; T = cs.target_sets(1, "add", p, s)
    pw = {a: np.load(f"lab/confirm/splits/confirm_exp1_eps2.0_add113_seed{s}_{a}.npy") for a in "FG"}
    mc = {a: shared(pw[a]) for a in "FG"}; m0 = {a: cs.m0(pw[a], "add", p) for a in "FG"}
    f = lambda q: np.log(S(q["F"], T["F"])/S(q["F"], T["G"])) + np.log(S(q["G"], T["G"])/S(q["G"], T["F"]))
    C1.append(f(mc)); C0.append(f(m0)); D.append(r["Delta_pow"])
C1, C0, D = map(np.array, (C1, C0, D))
def spear(x, y):
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y)); return np.corrcoef(rx, ry)[0, 1]
rng = np.random.default_rng(0)
for name, C in (("centred M0c", C1), ("M0", C0)):
    rho = spear(C, D); null = np.array([spear(C, rng.permutation(D)) for _ in range(20000)])
    print(name, "n", len(D), "rho %.3f" % rho, "p_two %.4f" % ((np.abs(null) >= abs(rho)).mean()), "C mean %.2f sd %.2f" % (C.mean(), C.std()))
print("D mean %.2f sd %.2f" % (D.mean(), D.std(ddof=1)))
