"""EXP-016: does an engineered split steer the learned frequencies toward its target set? (UNTESTED)

Read-only. Definition and decision rule: README.md.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "EXP-014-split-vs-init"))
import analyze as a14  # noqa: E402  (load, chance_p)

BASE = LAB / "experiments/EXP-003-early-prediction/raw_d/EXP-001_baseline_t2000_m5_seed{s}_thr4"
ENG = HERE / "raw/EXP-016_baseline_seed{s}_thr4_split_seed{s}_eps2.0"
SEEDS = range(10, 20)
ALPHA, MIN_VALID = 0.05, 8


def row(s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    meta = json.loads((HERE / f"splits/split_seed{s}_eps2.0.json").read_text(encoding="utf-8"))
    F = set(meta["targets"])
    try:
        e, es, est = a14.load(Path(str(ENG).format(s=s)))
        b, bs, bst = a14.load(Path(str(BASE).format(s=s)))
    except FileNotFoundError as ex:
        r["reason"] = f"missing {ex.filename}"
        return r
    if any(x["status"] != "completed" or x["events"].get("generalization_step") is None for x in (e, b)):
        r["reason"] = "not completed or not crossed"
        return r
    if not str(e.get("split_file", "")).replace("\\", "/").endswith(f"split_seed{s}_eps2.0.npy"):
        r["reason"] = "wrong split file"
        return r
    if not np.allclose(es[est.index(0)], bs[bst.index(0)], rtol=1e-6):
        r["reason"] = "init mismatch"
        return r
    ke, kb = set(e["final_top_m_freqs"]), set(b["final_top_m_freqs"])
    r.update({"valid": True, "F": sorted(F), "K_eng": sorted(ke), "K_base": sorted(kb),
              "ov_eng": len(ke & F), "ov_base": len(kb & F),
              "gen_eng": e["events"]["generalization_step"], "gen_base": b["events"]["generalization_step"]})
    r["D"] = r["ov_eng"] - r["ov_base"]
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
        D = np.array([r["D"] for r in valid], dtype=float)
        p = one_sided_p(D)
        oe = float(np.mean([r["ov_eng"] for r in valid]))
        out.update({"D_mean": float(D.mean()), "p": p, "ov_eng_mean": oe,
                    "ov_base_mean": float(np.mean([r["ov_base"] for r in valid])),
                    "p_ov_eng_vs_chance": a14.chance_p(oe, len(valid)),
                    "delta_gen_mean": float(np.mean([r["gen_eng"] - r["gen_base"] for r in valid])),
                    "verdict": "widerspricht" if D.mean() <= 0 else
                    ("steuerbar" if p < ALPHA else "richtungsgleich, nicht signifikant")})
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
