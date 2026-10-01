import numpy as np
# (p, N, generalised, source, budget) -- engineered splits, full batch, 1-layer transformer
pts = [(113, 3831, True, "P1 add113 30%", None), (97, 2823, True, "P1 add97 30%", None),
       (211, 13356, True, "EXP-136 211 30%", 20000), (307, 28275, True, "EXP-136 307 30%", 20000),
       (211, 3831, False, "EXP-136 211 3831", 20000), (307, 3831, False, "EXP-136 307 3831", 20000),
       (211, 4452, False, "EXP-137 211 10%", 30000), (211, 6678, True, "EXP-137 211 15%", 30000),
       (211, 8905, True, "EXP-137 211 20%", 30000), (307, 9425, True, "EXP-137 307 10% (+R14)", 30000),
       (401, 9425, False, "EXP-139 401 9425", 30000), (401, 14000, True, "EXP-139 401 14000", 30000)]
ok = []
for a in np.arange(0.0, 2.51, 0.01):
    y = [N / p ** a for p, N, g, *_ in pts if g]; n = [N / p ** a for p, N, g, *_ in pts if not g]
    if max(n) < min(y): ok.append(round(a, 2))
print("alpha separating:", (min(ok), max(ok)) if ok else None)
for a in (1.0, 5/3, 2.0):
    y = [N / p ** a for p, N, g, *_ in pts if g]; n = [N / p ** a for p, N, g, *_ in pts if not g]
    print(f"alpha={a:.2f}: max no {max(n):.4g} < min yes {min(y):.4g}? {max(n) < min(y)}")
