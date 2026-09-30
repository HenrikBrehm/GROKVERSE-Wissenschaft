"""EXP-128 analysis (session 59, written before any clipped pilot run; readings in README "Pilot (Sitzung 59)"). Same definitions as
EXP-126/analyze.py, per clipping value instead of per lr: a run is 'divergiert' if its spectrum at 20 000 is not finite, its final train
accuracy is not finite, or the trainer logged a non-finite gradient norm; 'nicht gelernt' if final train accuracy < 0.99; a seed is evaluable
if F and G are ok. Delta_pow at 20 000 (confirm_p1.delta_pow_checked, P1 definition). Reading per clipping value: 'K2 ohne Adam' if >= 3
evaluable seeds and Delta_pow > 1 in all; 'bricht' if >= 3 evaluable and |Delta_pow| <= 1 in all; 'nicht auswertbar' if < 3 evaluable;
else 'unklar'. Descriptive: Delta_pow at 2000, clipped-step share, generalization step, test accuracy.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-128-sgd-clip/analyze.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
import confirm_p1 as c1  # noqa: E402

SPL = LAB / "experiments/EXP-100-set-vs-order/splits"
SEEDS, CLIPS, END = (3704, 3705, 3706, 3707), (0.017, 0.1), 20_000


def _finite(v) -> bool:
    return v is not None and isinstance(v, (int, float)) and math.isfinite(v)


def run(s: int, x: str, c: float) -> dict:
    ds = list((HERE / "raw").glob(f"*_seed{s}_thr1_seed{s}_{x}_sgdm0.1_0.9_clip{c!r}_devcuda"))
    if len(ds) != 1 or not (ds[0] / "result.json").exists():
        return {"state": "fehlt"}
    r = json.loads((ds[0] / "result.json").read_text(encoding="utf-8"))
    if r.get("status") not in ("completed", "finalizing") or r.get("steps_completed") != END:
        return {"state": "fehlt"}
    ev = (r.get("events") or {}).get("sgd_clip") or {}
    if not ev or ev.get("max_norm") != c:                                # s59 review: guard against a run without the clip event
        return {"state": "fehlt"}
    bad_norm = next((int(t) for t, v in ev.get("norms", []) if not _finite(v)), None)
    S, st = np.load(ds[0] / "spectra.npy"), [int(v) for v in np.load(ds[0] / "spectra_steps.npy")]
    sp = {t: S[i] for i, t in enumerate(st)}
    fa = r.get("final_acc") or {}
    if END not in sp or not np.isfinite(sp[END]).all() or not _finite(fa.get("train")) or bad_norm is not None:
        first = next((t for t in st if not np.isfinite(sp[t]).all()), None)
        return {"state": "divergiert", "first_nonfinite": first, "first_bad_norm": bad_norm}
    if r.get("status") != "completed":
        return {"state": "fehlt"}
    return {"state": "ok" if fa["train"] >= 0.99 else "nicht gelernt", "end": sp[END], "at2k": sp.get(2000), "train": fa["train"],
            "test": fa.get("test"), "gen": (r.get("events") or {}).get("generalization_step"),
            "clipped_share": ev.get("clipped_steps", 0) / END}


def main() -> None:
    out: dict = {}
    for c in CLIPS:
        rows = []
        for s in SEEDS:
            T = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
            a, b = run(s, "F", c), run(s, "G", c)
            row = {"seed": s, "F": a["state"], "G": b["state"], "first_nonfinite": [a.get("first_nonfinite"), b.get("first_nonfinite")],
                   "first_bad_norm": [a.get("first_bad_norm"), b.get("first_bad_norm")]}
            for k, v in (("F", a), ("G", b)):
                row[f"train_{k}"], row[f"test_{k}"], row[f"gen_{k}"] = v.get("train"), v.get("test"), v.get("gen")
                row[f"clipped_share_{k}"] = v.get("clipped_share")
            if a["state"] == b["state"] == "ok":
                row["dpow_end"] = c1.delta_pow_checked(a["end"], b["end"], T["F"], T["G"])
                if a["at2k"] is not None and b["at2k"] is not None and np.isfinite(a["at2k"]).all() and np.isfinite(b["at2k"]).all():
                    row["dpow_2000"] = c1.delta_pow_checked(a["at2k"], b["at2k"], T["F"], T["G"])
            rows.append(row)
        ev = [r["dpow_end"] for r in rows if r.get("dpow_end") is not None and np.isfinite(r["dpow_end"])]
        reading = ("nicht auswertbar" if len(ev) < 3 else "K2 ohne Adam" if all(d > 1 for d in ev)
                   else "bricht" if all(abs(d) <= 1 for d in ev) else "unklar")
        out[repr(c)] = {"reading": reading, "n_evaluable": len(ev), "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
