"""EXP-128 post hoc (session 67, after the pre-set analysis and the text check; seen seeds 3704-3707, NOT a test):
Delta_pow (P1 formula, additive DFT spectra.npy, k = 1..56) between the F and the G run of each seed at steps 50, 250, 2000,
5000 and 20 000, per clip value. Motivated the R13 confirmation (lab/confirm/R13_REGISTRATION.md).
  python lab/experiments/EXP-128-sgd-clip/posthoc_dpow_s67.py   -> posthoc_dpow_s67.json
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SPL = HERE.parents[0] / "EXP-100-set-vs-order" / "splits"
STEPS = (50, 250, 2000, 5000, 20000)


def main() -> dict:
    runs = {}
    for f in (HERE / "raw").glob("*/result.json"):
        r = json.loads(f.read_text(encoding="utf-8"))
        clip = (r["events"].get("sgd_clip") or {}).get("max_norm")
        arm = Path(r["split_file"]).stem[-1]
        runs[(clip, r["seed"], arm)] = (np.load(f.parent / "spectra.npy"), [int(x) for x in np.load(f.parent / "spectra_steps.npy")])
    out = {}
    for clip in sorted({k[0] for k in runs}):
        out[str(clip)] = {}
        for t in STEPS:
            row = {}
            for s in sorted({k[1] for k in runs}):
                T = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
                (a, sa), (b, sb) = runs[(clip, s, "F")], runs[(clip, s, "G")]
                pa, pb = a[sa.index(t)], b[sb.index(t)]
                S = lambda pw, K: float(pw[[k - 1 for k in K]].sum())   # noqa: E731
                row[str(s)] = float(np.log(S(pa, T["F"]) / S(pa, T["G"])) + np.log(S(pb, T["G"]) / S(pb, T["F"])))
            out[str(clip)][str(t)] = row
    return out


if __name__ == "__main__":
    res = main()
    (HERE / "posthoc_dpow_s67.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    for c, v in res.items():
        for t, row in v.items():
            print(c, t, [round(x, 2) for x in row.values()])
