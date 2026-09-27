"""Session 31 (2026-09-27), POST HOC exploration, saved spectra only (no training).

Question: is the faster generalisation of more concentrated splits (posthoc_speed_dose.py) accompanied by a faster rise of the
target frequencies in W_E, as the first-order theory (draft section 5: early W_E drive ~ M0) suggests? Stated before looking:
the W_E power share on the 5 G targets at step 250 (after memorisation at ~120, before any generalisation at >= 425) is ordered
eps 8 > eps 2 > eps 1 in every seed. Descriptive also: share at 0 / 250 / 500, and the ratio of the target-share gain
(share(250) - share(0)) between eps 8 and eps 2 against the M0 target-share ratio (0.36 / 0.18 ~ 2).
Spectra: spectra.npy = additive DFT power of W_E, k = 1..56, every 250 steps. Targets: eps{1,8}/splits/seed{s}.json (G targets are
the same for all eps). Usage: python posthoc_speed_amplitude.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOTS = {"1": HERE / "eps1" / "raw", "2": HERE.parents[0] / "EXP-020-data-switch" / "raw", "8": HERE / "eps8" / "raw"}
SEEDS = (30, 31, 32, 34)


def share_at(eps: str, seed: int, targets: list[int], step: int) -> float:
    d = ROOTS[eps] / f"EXP-018_baseline_seed{seed}_thr4_seed{seed}_train_G"
    st = [int(x) for x in np.load(d / "spectra_steps.npy")]
    pw = np.load(d / "spectra.npy")[st.index(step)]
    return float(pw[[k - 1 for k in targets]].sum() / pw.sum())


def main() -> None:
    rows = []
    for sd in SEEDS:
        tg = json.loads((HERE / "eps8" / "splits" / f"seed{sd}.json").read_text(encoding="utf-8"))["targets"]["G"]
        assert tg == json.loads((HERE / "eps1" / "splits" / f"seed{sd}.json").read_text(encoding="utf-8"))["targets"]["G"]
        row = {"seed": sd, "targets": tg}
        for e in ROOTS:
            row[f"eps{e}"] = [round(share_at(e, sd, tg, t), 4) for t in (0, 250, 500)]
        row["ordered_8_2_1_at250"] = row["eps8"][1] > row["eps2"][1] > row["eps1"][1]
        g8, g2 = row["eps8"][1] - row["eps8"][0], row["eps2"][1] - row["eps2"][0]
        row["gain_ratio_8_over_2"] = round(g8 / g2, 2) if g2 > 0 else None
        rows.append(row)
        print(row)
    out = {"note": "post hoc exploration, seen seeds", "rows": rows,
           "ordered_count": sum(r["ordered_8_2_1_at250"] for r in rows), "n": len(rows)}
    (HERE / "posthoc_speed_amplitude.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("ordered at 250:", out["ordered_count"], "/", out["n"])


if __name__ == "__main__":
    main()
