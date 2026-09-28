"""P1 post hoc (session 44, exploration on seen data; numpy on stored spectra only). Written AFTER a first look at the numbers
(computed once in a scratch script with identical code), so this is a description, not a test.

Question: what drives the near-linear growth of Delta_pow with t * lr * wd (R1 post hoc, draft 3.7, Fig. 12)? If after the
early choice the frequencies of the other split only shrink by decoupled weight decay, their power falls like
exp(-2 lr wd t) = -0.002 per step (log) at the preset, and Delta_pow (two log ratios) grows by at most 4 lr wd = 0.004 per step.
Per P1 add-113 run (seeds 1000-1049, arms F and G, stored spectra at 250..2000): least-squares slope over steps of the log
power on the own targets, on the other split's targets, on the remaining 46 frequencies, and of the total power.

  python lab/confirm/P1_posthoc_decomp_s44.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]


def main() -> None:
    parts = {"own": [], "other": [], "rest": [], "total": []}
    for s in range(1000, 1050):
        for arm, oarm in (("F", "G"), ("G", "F")):
            T = json.loads((LAB / f"confirm/splits/confirm_exp1_eps2.0_add113_seed{s}_{arm}.json").read_text(encoding="utf-8"))["targets"]
            To = json.loads((LAB / f"confirm/splits/confirm_exp1_eps2.0_add113_seed{s}_{oarm}.json").read_text(encoding="utf-8"))["targets"]
            d = LAB / f"confirm/raw/EXP-016_baseline_seed{s}_thr1_confirm_exp1_eps2.0_add113_seed{s}_{arm}_devcuda"
            r = json.loads((d / "result.json").read_text(encoding="utf-8"))
            assert r["status"] == "completed" and r["steps_completed"] == 2000, d
            st, sp = np.load(d / "spectra_steps.npy"), np.load(d / "spectra.npy")
            k = st >= 250
            rest = [x for x in range(1, 57) if x not in T and x not in To]
            for key, S in (("own", T), ("other", To), ("rest", rest)):
                parts[key].append(float(np.polyfit(st[k], np.log(sp[k][:, [x - 1 for x in S]].sum(1)), 1)[0]))
            parts["total"].append(float(np.polyfit(st[k], np.log(sp[k].sum(1)), 1)[0]))
    out = {key: {"mean": float(np.mean(v)), "median": float(np.median(v)), "n": len(v)} for key, v in parts.items()}
    out["implied_dpow_slope"] = 2 * (out["own"]["mean"] - out["other"]["mean"])
    out["pure_decay_power_slope"] = -2 * 1e-3 * 1.0
    (LAB / "confirm/P1_posthoc_decomp_s44.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
