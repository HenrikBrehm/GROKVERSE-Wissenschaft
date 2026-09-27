"""Session 32 (2026-09-27), POST HOC descriptive on stored N29b/N29c runs, no training.
Question: is the extra delay after a value-path (VO) reset vs a query/key (QK) reset (N29c, 19/20) explained by more immediate damage?
Measure: train loss on the new split at step 50 (right after switch + reset) and 60, minus the same in the plain switch run (same seed and
direction); and log2 time difference (cap 2000) VO - QK. Descriptive only; stated before looking: if immediate damage explained the delay,
the VO - QK loss difference would be clearly positive in most seeds.   python lab/confirm/speed_reset_damage_s32.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]


def main() -> None:
    out = {}
    for block, kinds in (("n29c", ("vo", "qk")), ("n29b", ("attn", "mlp"))):
        pat = re.compile(rf"seed(\d+)_thr1_{block}_seed\d+_w0_(A|B)_to_{block}_seed\d+_w0_(A|B)_at50(?:_rs(\w+))?_devcuda$")
        R: dict = {}
        for d in (LAB / f"confirm/{block}_raw").iterdir():
            m = pat.search(d.name)
            r = json.loads((d / "result.json").read_text(encoding="utf-8"))
            dn = r["dense"]
            L = dict(zip(dn["train_steps"], dn["train_loss"]))
            g = (r.get("events") or {}).get("generalization_step")
            R[(int(m.group(1)), m.group(2) + m.group(3), m.group(4) or "none")] = (L[50], L[60], math.log2(min(g, 2000) if g else 2000))
        seeds = sorted({k[0] for k in R})
        res = {}
        for k in kinds:
            dl50 = [np.mean([R[(s, dr, k)][0] - R[(s, dr, "none")][0] for dr in ("AB", "BA")]) for s in seeds]
            dl60 = [np.mean([R[(s, dr, k)][1] - R[(s, dr, "none")][1] for dr in ("AB", "BA")]) for s in seeds]
            res[k] = {"dloss50_mean": float(np.mean(dl50)), "dloss60_mean": float(np.mean(dl60))}
        a, b = kinds
        dd = np.array([np.mean([R[(s, dr, a)][0] - R[(s, dr, b)][0] for dr in ("AB", "BA")]) for s in seeds])
        dt = np.array([np.mean([R[(s, dr, a)][2] - R[(s, dr, b)][2] for dr in ("AB", "BA")]) for s in seeds])
        rx, ry = np.argsort(np.argsort(dd)), np.argsort(np.argsort(dt))
        res[f"{a}_minus_{b}"] = {"dloss50_mean": float(dd.mean()), "dloss50_pos": int((dd > 0).sum()), "dlog2time_mean": float(dt.mean()),
                                 "spearman_dloss_dtime": float(np.corrcoef(rx, ry)[0, 1]), "n": len(seeds)}
        out[block] = res
    (LAB / "confirm/speed_reset_damage_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
