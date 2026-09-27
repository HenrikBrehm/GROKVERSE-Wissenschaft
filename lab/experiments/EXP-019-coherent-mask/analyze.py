"""EXP-019: coherent mask spectrum M0c vs M0 on fresh seeds (EXP-018 arm R 20-29, EXP-003d baselines 18, 19).
Definition: README.md. No training; reads finished runs only. Run through guarded_run.py (make_dataset is used).
Nachtrag c (session 35, before any EXP-019 statistic was computed): --device cuda reads the EXP-018 GPU runs
(raw/EXP-018_baseline_seed{s}_thr1_seed{s}_train_{arm}_devcuda, EXP-018 Nachtrag c) and requires device = cuda in each
result.json; the registered CPU runs (thr4) were never produced. Statistics unchanged. Output summary_cuda.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-015-mask-spectrum"))
sys.path.insert(0, str(LAB / "experiments/EXP-015-mask-spectrum/posthoc"))
sys.path.insert(0, str(LAB / "experiments/EXP-016-engineered-split"))
import mask_spectrum as ms  # noqa: E402
from coherent_m0 import m0c  # noqa: E402
from make_split import mask_from_idx  # noqa: E402

p12 = ms.p12
E18 = LAB / "experiments/EXP-018-split-speed"
MIN_VALID = 10
DEVICE = "cuda" if sys.argv[1:] == ["--device", "cuda"] else "cpu"
if sys.argv[1:] not in ([], ["--device", "cuda"]):
    raise SystemExit("usage: analyze.py [--device cuda]")


def run_k(d: Path) -> list[int] | None:
    f = d / "result.json"
    if not f.exists():
        return None
    res = json.loads(f.read_text(encoding="utf-8"))
    if res["status"] != "completed":
        return None
    if d.parent.parent == E18 and res.get("device", "cpu") != DEVICE:      # Nachtrag c: EXP-018 runs must match the device
        raise SystemExit(f"{d.name}: device {res.get('device')!r}, expected {DEVICE}")
    return res.get("final_top_m_freqs")


def combined(s: int, M: np.ndarray, K: list[int]) -> dict:
    """Secondary (Nachtrag b): log E0 (init power of seed s) + log M0c."""
    E0 = p12.init_predictors(s)[0]["E0"]
    return {"rbar_E0": p12.rbar(E0, K), "rbar_sum": p12.rbar(np.log(E0) + np.log(m0c(M)), K)}


def rows_for(arm: str) -> list[dict]:
    rows = []
    for s in range(20, 30):
        K = run_k(E18 / (f"raw/EXP-018_baseline_seed{s}_thr4_seed{s}_train_{arm}" if DEVICE == "cpu"
                         else f"raw/EXP-018_baseline_seed{s}_thr1_seed{s}_train_{arm}_devcuda"))
        if K is not None:
            M = mask_from_idx(np.load(E18 / f"splits/seed{s}_train_{arm}.npy"))
            rows.append({"seed": s, "src": f"EXP-018/{arm}", "K": K})
            rows[-1].update(rbar_M0=p12.rbar(ms.m0(M), K), rbar_M0c=p12.rbar(m0c(M), K), **combined(s, M, K))
    if arm == "R":
        for s in (18, 19):
            K = run_k(Path(str(p12.BASE_D).format(s=s)))
            if K is not None:
                M = ms.mask_matrix(s)
                rows.append({"seed": s, "src": "EXP-003d", "K": K,
                             "rbar_M0": p12.rbar(ms.m0(M), K), "rbar_M0c": p12.rbar(m0c(M), K), **combined(s, M, K)})
    return rows


def summary(rows: list[dict]) -> dict:
    if len(rows) < MIN_VALID:
        return {"n": len(rows), "verdict": "nicht auswertbar"}
    d = np.array([r["rbar_M0"] - r["rbar_M0c"] for r in rows])
    p = p12.sign_flip_p(d)
    rc = float(np.mean([r["rbar_M0c"] for r in rows]))
    return {"n": len(rows), "rbar_M0": float(np.mean([r["rbar_M0"] for r in rows])), "rbar_M0c": rc,
            "d_mean": float(d.mean()), "p_one_sided": p, "p_M0c_vs_null": p12.mc_null_p(rc, len(rows)),
            "verdict": "widerspricht" if d.mean() <= 0 else ("M0c besser" if p < p12.ALPHA
                                                             else "richtungsgleich, nicht signifikant"),
            "secondary_sum_vs_M0c": {"rbar_sum": float(np.mean([r["rbar_sum"] for r in rows])),
                                     "rbar_E0": float(np.mean([r["rbar_E0"] for r in rows])),
                                     "p_sum_better": p12.sign_flip_p(np.array([r["rbar_M0c"] - r["rbar_sum"]
                                                                                for r in rows]))}}


def main() -> None:
    prim, sec = rows_for("R"), rows_for("D")
    out = {"primary_R_plus_baselines": summary(prim), "secondary_arm_D": summary(sec), "rows": prim + sec}
    out["device_exp018"] = DEVICE
    (HERE / ("summary.json" if DEVICE == "cpu" else "summary_cuda.json")).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
