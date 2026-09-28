"""EXP-100 feasibility reader (session 44, written before any run). Applies the rule fixed in session 43 (README, design.feas)
per batch size: "no order effect at B" if o(R-stride_B) - o(R-iid_B) <= 0.02 in all 3 seeds and no stride run has its peak
frequency in O. o = share of the W_E group power (k = 1..56, number rows) at O at the end of the run.
Also prints the first-order window prediction (firstorder_window_s44.json) next to it: B = 256 washed out, B = 64 can act.
Consequence (README): no effect at 256 but an effect at 64 -> the conflict arm also runs with B = 64 (stride64) in the
pilot; no effect at either -> "conflict not testable at 30 % data" (reported as a finding, abgrenzung to LeDoux).

  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-100-set-vs-order/feas_read.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P, O = 113, (11, 12, 22, 23, 34, 45)
SEEDS = (3700, 3701, 3702)


def power(W: np.ndarray) -> np.ndarray:
    sq = (np.abs(np.fft.fft(W[:P].astype(np.float64), axis=0)) ** 2).sum(1)
    return 2.0 * sq[1:(P - 1) // 2 + 1] / P


def end_power(seed: int, B: int, stride: bool) -> np.ndarray | str:
    cands = [d for d in (HERE / "raw_feas").glob(f"*seed{seed}_*seed{seed}_R*") if f"_bs{B}_" in d.name + "_"
             and ("_ordstride" in d.name) == stride]
    if len(cands) != 1:
        return f"fehlt/mehrdeutig ({len(cands)})"
    r = json.loads((cands[0] / "result.json").read_text(encoding="utf-8"))
    if r.get("status") != "completed" or r.get("steps_completed") != r.get("max_steps"):
        return "defekt"
    steps = list(np.load(cands[0] / "we_snapshot_steps.npy"))
    W = np.load(cands[0] / "we_snapshots.npy")[steps.index(r["steps_completed"])]
    return power(W)


def main() -> None:
    out = {}
    for B in (256, 64):
        rows, bad = [], []
        for s in SEEDS:
            st, ii = end_power(s, B, True), end_power(s, B, False)
            if isinstance(st, str) or isinstance(ii, str):
                bad.append([s, st if isinstance(st, str) else ii])
                continue
            o = lambda pw: float(pw[[k - 1 for k in O]].sum() / pw.sum())   # noqa: E731
            rows.append({"seed": s, "o_stride": o(st), "o_iid": o(ii), "diff": o(st) - o(ii),
                         "peak_stride": int(np.argmax(st)) + 1, "peak_in_O": int(np.argmax(st)) + 1 in O})
        effect = None if bad else not (all(r["diff"] <= 0.02 for r in rows) and not any(r["peak_in_O"] for r in rows))
        out[f"B{B}"] = {"rows": rows, "bad": bad, "order_effect": effect}
    pred = json.loads((HERE / "firstorder_window_s44.json").read_text(encoding="utf-8"))["summary"]
    out["first_order_prediction"] = {k: v["prediction"] for k, v in pred.items() if v["prediction"]}
    (HERE / "feas_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
