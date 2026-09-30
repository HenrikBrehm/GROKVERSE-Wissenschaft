"""EXP-123 post hoc (session 57 cycle 7, reading fixed in JOURNAL before computing): within an arm, does t_swap follow the time t_0.3
at which the W_E top-5 concentration first reaches 0.30 (R5 spectra, grid 250)? Spearman rho(t_0.3, t_swap) per arm over units with
observed t_swap and t_0.3, one-sided permutation p (20 000, fixed seed). Reading per arm R and D_0: 'gekoppelt' rho >= 0.5 and p < 0.05;
'nicht gekoppelt' rho < 0.2; else 'unklar'. E2_0 descriptive only. Comparison: rho(t_0.3, t_gen).
  python lab/experiments/EXP-123-commutativity-stages/posthoc_within_arm_s57.py
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "confirm"))
import posthoc_route_s57 as P  # noqa: E402
from R5_posthoc_share_speed_s38 import spearman  # noqa: E402

LEVEL = 0.30


def perm_p(x: list, y: list, rng: np.random.Generator, n: int = 20000) -> tuple[float, float]:
    rho = spearman(x, y)
    return rho, (1 + sum(spearman(x, rng.permutation(y)) >= rho for _ in range(n))) / (n + 1)


def main() -> None:
    rows = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))["rows"]
    rng = np.random.default_rng(57)
    out: dict = {}
    for arm in ("R", "D_0", "E2_0"):
        t03, tsw, tgen, never = [], [], [], 0
        for r in rows:
            if r["arm"] != arm or r["status"] != "ok" or not r["t_swap"]:
                continue
            S, st = P.spectra(r["seed"], r["unit"], arm)
            hit = [int(s) for s, row in zip(st, S) if P.conc(row) >= LEVEL]
            if not hit:
                never += 1
                continue
            t03.append(hit[0]); tsw.append(r["t_swap"]); tgen.append(r["t_gen"])
        rho, p = perm_p(t03, tsw, rng)
        g = [(a, b) for a, b in zip(t03, tgen) if b]
        rg, pg = perm_p([a for a, _ in g], [b for _, b in g], rng) if len(g) >= 5 else (None, None)
        reading = ("gekoppelt" if rho >= 0.5 and p < 0.05 else "nicht gekoppelt" if rho < 0.2 else "unklar")
        out[arm] = {"n": len(t03), "never_reached": never, "rho_t03_tswap": rho, "p": p, "rho_t03_tgen": rg, "p_tgen": pg,
                    "n_tgen": len(g), "t03_median": float(np.median(t03)), "tswap_median": float(np.median(tsw)),
                    "reading": reading if arm != "E2_0" else "beschreibend"}
    (HERE / "posthoc_within_arm_s57.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
