"""EXP-011: does the final frequency set follow the swapped init NORM alone? (UNTESTED)

Read-only analysis. Reuses the pair logic of EXP-010 (same baselines, same T/S pairs,
same validity checks). Definition and decision rule: README.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-010-init-swap"))
import analyze as a10  # noqa: E402

MAG = HERE / "raw/EXP-011_init_magswap_t2000_m5_seed{s}_thr4"


def two_sided_sign_flip_p(d: np.ndarray) -> float:
    flips = np.array([[1 - 2 * ((i >> b) & 1) for b in range(len(d))] for i in range(2 ** len(d))])
    return float((np.abs((flips * d).mean(axis=1)) >= abs(d.mean()) - 1e-12).mean())


def main() -> None:
    mag = {r["seed"]: r for r in (a10.pair(s, MAG, "init_magswap") for s in a10.SEEDS)}
    full = {r["seed"]: r for r in (a10.pair(s) for s in a10.SEEDS)}
    out: dict = {"rows_mag": list(mag.values())}
    valid = [s for s in a10.SEEDS if mag[s]["valid"]]
    out["n_valid"] = len(valid)
    if len(valid) < a10.MIN_VALID:
        out["verdict_mag"] = "nicht auswertbar"
    else:
        d = np.array([mag[s]["d"] for s in valid], dtype=float)
        p = a10.sign_flip_p(d)
        out.update({"d_mag_mean": float(d.mean()), "p_mag": p,
                    "verdict_mag": "widerspricht" if d.mean() <= 0 else
                    ("steuerbar" if p < a10.ALPHA else "richtungsgleich, nicht signifikant")})
    both = [s for s in valid if full[s]["valid"]]
    out["n_both"] = len(both)
    if len(both) >= a10.MIN_VALID:            # secondary: direction share = d_swap - d_mag
        dd = np.array([full[s]["d"] - mag[s]["d"] for s in both], dtype=float)
        out["direction_share"] = {"mean": float(dd.mean()), "p_two_sided": two_sided_sign_flip_p(dd),
                                  "per_seed": dd.tolist()}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows_mag"}, indent=1))


if __name__ == "__main__":
    main()
