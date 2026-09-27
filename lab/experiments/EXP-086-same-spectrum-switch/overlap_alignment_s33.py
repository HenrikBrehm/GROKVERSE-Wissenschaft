"""EXP-086 pre-run check (session 33, pure numpy on stored EXP-056 split files): signed first-order gradient alignment of A and B at the
F and G targets for the overlap levels omega 0 / 0.2 / 0.4 (see gradient_overlap_s33.py for the measure).
  python lab/experiments/EXP-086-same-spectrum-switch/overlap_alignment_s33.py
"""
import sys, numpy as np
sys.path.insert(0, "lab/experiments/EXP-086-same-spectrum-switch"); sys.path.insert(0, "lab/experiments/EXP-053-p3-overlap-design")
import gradient_overlap_s33 as g, overlap_split as ov
S = g.S56
for w in ("w0", "w200", "w400"):
    rows = []
    for s in range(400, 410):
        F, G = ov.targets(s)
        A, B = np.load(S / f"seed{s}_{w}_A.npy"), np.load(S / f"seed{s}_{w}_B.npy")
        XA, XB = g.coeffs(A), g.coeffs(B)
        rows.append((g.rho(XA, XB, F, True), g.rho(XA, XB, G, True), ov.share(B, F), ov.share(A, G), len(np.intersect1d(A, B)) / len(A)))
    r = np.array(rows).mean(0)
    print(w, "cosF %.3f cosG %.3f shareF(B) %.3f shareG(A) %.3f overlap %.2f" % tuple(r))
