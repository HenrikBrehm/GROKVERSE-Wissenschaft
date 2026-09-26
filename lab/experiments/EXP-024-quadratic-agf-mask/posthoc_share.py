"""EXP-024 post hoc (session 7, not pre-registered): share of weighted input power on F, H and 2F vs the chance share 5/56."""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P = 113


def fold(k):
    k %= P
    return min(k, P - k)


for act in ("quad", "relu"):
    acc = {}
    for f in sorted((HERE / "raw").glob(f"EXP-024_{act}_seed*/result.json")):
        r = json.loads(f.read_text())
        if (r["args"]["seed"], r["args"]["arm"]) == (12, "G") or not r.get("complete"):
            continue
        T = r["targets"]; H = sorted({fold(57 * t) for t in T}); T2 = sorted({fold(2 * t) for t in T})
        for step, sp in r["spectra"].items():
            w = np.array(sp["weighted"]); w = w / w.sum()
            acc.setdefault(int(step), []).append([w[[k - 1 for k in S]].sum() for S in (T, H, T2)])
    for step in sorted(acc):
        a = np.array(acc[step])
        hi = (a[:, 1] > a[:, 0]).sum()
        print(act, step, "n", len(a), "share F %.3f H %.3f 2F %.3f (chance %.3f); units H>F %d" % (*a.mean(0), 5 / 56, hi))
