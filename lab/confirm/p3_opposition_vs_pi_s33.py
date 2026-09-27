"""Session 33 (window closed), post hoc on the confirmed P3 block, split files + frozen P3_summary.json only, no training.
Question (stated before computing the omega-0.4 alignment): P3's secondary contrast shows persistence pi unchanged between omega 0 and 0.4
(dpi 0.005, CI [-0.030, 0.042]). If the first-order opposing term of B at A's targets (switch_alignment_s33.py) is much weaker at
omega 0.4, persistence is insensitive to that term. Reported: signed cosine and projection (in units of A's own push) per omega, and the
per-seed Spearman correlation between the change in projection and the change in pi (omega 0.4 minus 0).
  python lab/confirm/p3_opposition_vs_pi_s33.py
"""
import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-086-same-spectrum-switch"))
import gradient_overlap_s33 as g  # noqa: E402

D = LAB / "confirm/p3_splits"


def terms(s: int, w: str) -> tuple[float, float]:
    m = json.loads((D / f"p3_seed{s}_{w}.json").read_text(encoding="utf-8"))
    T = m["targets"]["A"]
    XA, XB = g.coeffs(np.load(D / f"p3_seed{s}_{w}_A.npy")), g.coeffs(np.load(D / f"p3_seed{s}_{w}_B.npy"))
    proj = sum(np.vdot(XA[k], XB[k]).real for k in T) / sum(np.vdot(XA[k], XA[k]).real for k in T)
    return g.rho(XA, XB, T, True), float(proj)


def rank(x: np.ndarray) -> np.ndarray:
    return np.argsort(np.argsort(x)).astype(float)


summ = json.loads((LAB / "confirm/P3_summary.json").read_text(encoding="utf-8"))
rows = []
for r in summ["rows"]:
    s = r["seed"]
    c0, p0 = terms(s, "w0")
    c4, p4 = terms(s, "w400")
    rows.append({"seed": s, "cos_w0": c0, "cos_w400": c4, "proj_w0": p0, "proj_w400": p4, "row": {k: v for k, v in r.items() if k != "seed"}})
out = {k: float(np.mean([r[k] for r in rows])) for k in ("cos_w0", "cos_w400", "proj_w0", "proj_w400")}
out["n"] = len(rows)
ok = [r for r in rows if r["row"]["levels"]["0.0"].get("valid") and r["row"]["levels"]["0.4"].get("valid")]
dpi = np.array([r["row"]["levels"]["0.4"]["pi"] - r["row"]["levels"]["0.0"]["pi"] for r in ok])
dproj = np.array([r["proj_w400"] - r["proj_w0"] for r in ok])
out.update(n_valid_both=len(ok), mean_pi_w0=float(np.mean([r["row"]["levels"]["0.0"]["pi"] for r in ok])),
           mean_pi_w400=float(np.mean([r["row"]["levels"]["0.4"]["pi"] for r in ok])), mean_dpi=float(dpi.mean()),
           spearman_dproj_dpi=float(np.corrcoef(rank(dproj), rank(dpi))[0, 1]))
print(json.dumps(out, indent=1))
(LAB / "confirm/p3_opposition_vs_pi_s33.json").write_bytes(json.dumps({"summary": out, "rows": rows}, indent=1, default=float).encode())
