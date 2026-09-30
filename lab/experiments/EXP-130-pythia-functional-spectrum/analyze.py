"""EXP-130 analysis (session 61, written before any EXP-130 run): readings exactly as in README.md ("Vorab").

Reads result.json of the four runs (seeds 4002/4003 x F/G) under raw/, writes summary.json and prints the reading.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-130-pythia-functional-spectrum/analyze.py [--root DIR]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PRETRAINED_TOP8_IN = {1, 2, 3, 11, 4, 5, 23, 45}
EXPECTED = [(4002, "F"), (4002, "G"), (4003, "F"), (4003, "G")]
STEPS = 4000
MIN_DROP = 0.01      # a frequency enters the top 5 only if removing it costs >= 1 point of held-out accuracy (review S61:
                     # otherwise ties at ~0 would fill the top 5 with k = 1, 2, 3, ... and favour "Wiederverwendung")


def ranks(x: np.ndarray) -> np.ndarray:
    """Average ranks (ties share their mean rank; review S61)."""
    order = np.argsort(x, kind="stable")
    r = np.empty(len(x))
    r[order] = np.arange(len(x), dtype=float)
    for v in np.unique(x):
        idx = np.flatnonzero(x == v)
        r[idx] = r[idx].mean()
    return r


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.corrcoef(ranks(a), ranks(b))[0, 1])


def load(root: Path, steps: int = STEPS) -> dict:
    runs: dict = {}
    for p in sorted(root.glob("*/result.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        c = r.get("config", {})
        key = (c.get("seed"), c.get("arm"))
        if (r.get("status") != "completed" or "sweep" not in r.get("ablation", {}) or key not in EXPECTED
                or c.get("steps") != steps):
            continue
        if key in runs:
            raise SystemExit(f"duplicate run for {key}: {p}")
        runs[key] = r
    return runs


def per_model(r: dict) -> dict:
    sw, cfg = r["ablation"]["sweep"], r["config"]
    own = set(cfg["targets"][cfg["arm"]])
    f = {s: sw["base"] - np.asarray(sw[s], float) for s in ("in", "out", "both")}
    top5 = [int(k) + 1 for k in np.argsort(-f["in"], kind="stable")[:5] if f["in"][k] >= MIN_DROP]
    return {"base": sw["base"], "top5_in": top5,
            "top5_out": [int(k) + 1 for k in np.argsort(-f["out"], kind="stable")[:5] if f["out"][k] >= MIN_DROP],
            "n_pretrained": sum(k in PRETRAINED_TOP8_IN for k in top5), "n_own": sum(k in own for k in top5),
            "own_in_pretrained_top8": sorted(own & PRETRAINED_TOP8_IN), "n_above_min_drop": int((f["in"] >= MIN_DROP).sum()),
            "ties_at_top5_edge": int(np.sum(np.isclose(f["in"], np.sort(f["in"])[-5]))) if len(f["in"]) >= 5 else 0,
            "f_in_top5": [float(f["in"][k - 1]) for k in top5],
            "drop_pretrained_top8": {s: sw["base"] - sw[f"{s}_pretrained_top8"] for s in ("in", "out", "both")},
            "drop_decimal": {s: sw["base"] - sw[f"{s}_decimal"] for s in ("in", "out", "both")},
            "drop_own_in": r["ablation"]["base"] - r["ablation"]["in_own"],
            "drop_other_in": r["ablation"]["base"] - r["ablation"]["in_other"], "f_in": f["in"].tolist()}


def reading(models: list[dict]) -> str:
    if len(models) < 4:
        return "nicht auswertbar (fehlende Läufe)"
    if sum(m["base"] >= 0.5 for m in models) < 3:
        return "nicht auswertbar (lernt nicht)"
    ok = [m for m in models if m["base"] >= 0.5]
    if sum(m["n_pretrained"] >= 3 and m["n_own"] <= 1 for m in ok) >= 3:
        return "Wiederverwendung"
    if sum(m["n_own"] >= 3 for m in ok) >= 3:
        return "Datenwahl"
    if sum(m["n_own"] >= 2 and m["n_pretrained"] >= 2 for m in ok) >= 3:
        return "gemischt"
    return "unklar"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(HERE / "raw"))
    ap.add_argument("--steps", type=int, default=STEPS, help="only for the smoke test")
    a = ap.parse_args()
    runs = load(Path(a.root), a.steps)
    models = {f"{s}_{arm}": per_model(runs[(s, arm)]) for s, arm in EXPECTED if (s, arm) in runs}
    rho = {str(s): spearman(np.asarray(models[f"{s}_F"]["f_in"]), np.asarray(models[f"{s}_G"]["f_in"]))
           for s in (4002, 4003) if f"{s}_F" in models and f"{s}_G" in models}
    out = {"reading": reading(list(models.values())), "models": models, "spearman_f_in_F_vs_G": rho,
           "missing": [f"{s}_{arm}" for s, arm in EXPECTED if (s, arm) not in runs]}
    (HERE / ("summary.json" if a.steps == STEPS else "smoke/summary_smoke.json")).write_text(json.dumps(out, indent=1), encoding="utf-8")
    for k, m in models.items():
        print(f"{k}: base {m['base']:.3f} top5_in {m['top5_in']} (pretrained {m['n_pretrained']}, own {m['n_own']}) "
              f"top5_out {m['top5_out']} drop top8/decimal in {m['drop_pretrained_top8']['in']:.3f}/{m['drop_decimal']['in']:.3f} "
              f"own/other in {m['drop_own_in']:.3f}/{m['drop_other_in']:.3f}")
    print("spearman f_in F vs G:", rho)
    print("reading:", out["reading"], "| missing:", out["missing"])


if __name__ == "__main__":
    main()
