"""EXP-024 exploratory (not pre-registered): overlap of top-5 with F, H and fold(2F) at each recorded step."""
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
        T = set(r["targets"]); H = {fold(57 * t) for t in T}; T2 = {fold(2 * t) for t in T}
        for step, sp in r["spectra"].items():
            top = set(int(k) for k in np.argsort(-np.array(sp["weighted"]))[:5] + 1)
            acc.setdefault(int(step), []).append((len(top & T), len(top & H), len(top & T2)))
    for step in sorted(acc):
        a = np.array(acc[step])
        print(act, step, "n", len(a), "ov_F %.2f ov_H %.2f ov_2F %.2f" % tuple(a.mean(0)))
