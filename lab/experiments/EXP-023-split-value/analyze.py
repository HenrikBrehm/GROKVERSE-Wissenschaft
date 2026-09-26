"""EXP-023: with position-specific value matrices, does M0c lose its advantage over M0? (UNTESTED on real runs)
Definition: README.md. Read-only; uses make_dataset through mask_matrix, so run it through guarded_run.py."""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-015-mask-spectrum"))
sys.path.insert(0, str(LAB / "experiments/EXP-015-mask-spectrum/posthoc"))
import mask_spectrum as ms  # noqa: E402
from coherent_m0 import m0c  # noqa: E402

p12 = ms.p12
BASE = LAB / "experiments/EXP-003-early-prediction/raw_d/EXP-001_baseline_t2000_m5_seed{s}_thr4"
SV = HERE / "raw/EXP-023_baseline_t2000_m5_seed{s}_thr4_sv"
SEEDS, MIN_VALID, ALPHA = range(10, 20), 8, 0.05


def load(d: Path):
    if not (d / "result.json").exists():
        return None
    return (json.loads((d / "result.json").read_text(encoding="utf-8")), np.load(d / "spectra.npy"),
            np.load(d / "spectra_steps.npy").tolist())


def row(s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    b, v = load(Path(str(BASE).format(s=s))), load(Path(str(SV).format(s=s)))
    if b is None or v is None:
        r["reason"] = "missing"
        return r
    (rb, sb, tb), (rv, sv, tv) = b, v
    if any(x["status"] != "completed" or x["events"].get("generalization_step") is None for x in (rb, rv)):
        r["reason"] = "not completed or not crossed"
        return r
    if rv.get("split_value") is not True or rv["split_hash"] != rb["split_hash"]:
        r["reason"] = "protocol (split_value flag or split)"
        return r
    if not np.allclose(sb[tb.index(0)], sv[tv.index(0)], rtol=1e-6):
        r["reason"] = "init mismatch"
        return r
    M = ms.mask_matrix(s)
    a, c = ms.m0(M), m0c(M)
    Kb, Kv = rb["final_top_m_freqs"], rv["final_top_m_freqs"]
    d_b = p12.rbar(c, Kb) - p12.rbar(a, Kb)
    d_v = p12.rbar(c, Kv) - p12.rbar(a, Kv)
    r.update({"valid": True, "K_base": Kb, "K_sv": Kv, "ov": len(set(Kb) & set(Kv)),
              "rbar_sv_M0": p12.rbar(a, Kv), "rbar_sv_M0c": p12.rbar(c, Kv), "d_base": d_b, "d_sv": d_v,
              "Delta_d": d_v - d_b, "gen_base": rb["events"]["generalization_step"],
              "gen_sv": rv["events"]["generalization_step"]})
    return r


def one_sided_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def main() -> None:
    rows = [row(s) for s in SEEDS]
    valid = [r for r in rows if r["valid"]]
    out: dict = {"rows": rows, "n_valid": len(valid)}
    if len(valid) < MIN_VALID:
        out["verdict"] = "nicht auswertbar"
    else:
        D = np.array([r["Delta_d"] for r in valid])
        p = one_sided_p(D)
        out.update({"Delta_d_mean": float(D.mean()), "p_one_sided": p,
                    "rbar_sv_M0": float(np.mean([r["rbar_sv_M0"] for r in valid])),
                    "rbar_sv_M0c": float(np.mean([r["rbar_sv_M0c"] for r in valid])),
                    "ov_mean": float(np.mean([r["ov"] for r in valid])),
                    "verdict": "widerspricht" if D.mean() <= 0 else
                    ("bestätigt" if p < ALPHA else "richtungsgleich, nicht signifikant")})
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
