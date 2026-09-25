"""EXP-009 exploratory controls (post hoc, NOT part of the pre-registered decision).

1. Cross-seed control: rank of seed A's K_final in seed B's init spectrum (A != B, same group).
   If the t=0 effect came from a frequency-dependent init artifact or a universal frequency
   preference, mismatched pairs would show it too; if it is seed-specific they sit at ~0.5.
2. Effect size at t=0: share of K_final inside the init top-5 / top-10, and how often the
   init-strongest frequency ends up in K_final (chance 5/56 = 0.089).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from commitment import GROUPS, M, N_FREQ, SEEDS, ranks_desc, spectrum

HERE = Path(__file__).resolve().parent
P = 113


def main() -> None:
    summary = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
    k_final = {r["run"]: np.array(r["k_final"]) - 1 for r in summary["runs"]}
    out = {}
    for g, pat in GROUPS.items():
        dirs = [Path(str(pat).format(s=s)) for s in SEEDS]
        init_rank = {d.name: ranks_desc(spectrum(d, 0, P)) for d in dirs}
        own, cross = [], []
        for a in dirs:
            ka = k_final[a.name]
            for b in dirs:
                nr = float(((init_rank[b.name][ka] - 1) / (N_FREQ - 1)).mean())
                (own if a == b else cross).append(nr)
        in5 = np.mean([np.mean(init_rank[d.name][k_final[d.name]] <= 5) for d in dirs])
        in10 = np.mean([np.mean(init_rank[d.name][k_final[d.name]] <= 10) for d in dirs])
        top1 = np.mean([int(np.argmin(init_rank[d.name])) in set(k_final[d.name]) for d in dirs])
        out[g] = {"own_mean": float(np.mean(own)), "cross_mean": float(np.mean(cross)),
                  "cross_sd": float(np.std(cross)), "share_kfinal_in_init_top5": float(in5),
                  "share_kfinal_in_init_top10": float(in10),
                  "share_init_top1_in_kfinal": float(top1)}
        print(f"{g:7s} own={np.mean(own):.3f} cross={np.mean(cross):.3f}±{np.std(cross):.3f} "
              f"K_final in init top5={in5:.2f} (chance {M / N_FREQ:.2f}) top10={in10:.2f} "
              f"(chance {10 / N_FREQ:.2f}) init-top1 in K_final={top1:.1f} (chance {M / N_FREQ:.2f})")
    (HERE / "controls.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
