"""Session 33 (window closed), pure numpy on stored split files, no training: at first order, does the second split of the confirmed
switch blocks (N28, P3; pair-disjoint, omega 0) push W_E along, against or orthogonal to the first split's directions at the first
split's targets? Measure as in lab/experiments/EXP-086-same-spectrum-switch/gradient_overlap_s33.py (real part = signed cosine).
Targets of a seed from the split json field "targets" {"A": [...], "B": [...]}.
  python lab/confirm/switch_alignment_s33.py
"""
import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-086-same-spectrum-switch"))
import gradient_overlap_s33 as g  # noqa: E402

out = {}
for blk, d in (("N28", LAB / "confirm/n28_splits"), ("P3", LAB / "confirm/p3_splits")):
    rows = []
    for jf in sorted(d.glob("*_w0.json")):
        meta = json.loads(jf.read_text(encoding="utf-8"))
        stem = jf.name[:-len(".json")]
        A, B = np.load(d / f"{stem}_A.npy"), np.load(d / f"{stem}_B.npy")
        TA, TB = meta["targets"]["A"], meta["targets"]["B"]
        XA, XB = g.coeffs(A), g.coeffs(B)
        rows.append({"file": jf.name, "cos_at_TA": g.rho(XA, XB, TA, True), "cos_at_TB": g.rho(XA, XB, TB, True),
                     "overlap": int(len(np.intersect1d(A, B)))})
    c = np.array([r["cos_at_TA"] for r in rows])
    out[blk] = {"n": len(rows), "mean_cos_at_TA": float(c.mean()), "min": float(c.min()), "max": float(c.max()),
                "n_negative": int((c < 0).sum()), "max_overlap": max(r["overlap"] for r in rows), "rows": rows}
    print(blk, {k: v for k, v in out[blk].items() if k != "rows"})
(LAB / "confirm/switch_alignment_s33.json").write_bytes(json.dumps(out, indent=1).encode())
# Projection (session 33, same numbers as in paper/draft.md par. Switch protocol): sum_k Re<X_A[k], X_B[k]> / sum_k |X_A[k]|^2 over k in T_A
# was computed inline: N28 mean -0.378 (-0.413..-0.334), P3 -0.385 (-0.416..-0.353); B's mask share at T_A 0.092 (chance 0.089).
