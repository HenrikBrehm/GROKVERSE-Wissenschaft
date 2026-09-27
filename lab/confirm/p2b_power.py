"""P2b power (session 22, Codex review point 5): resample the 47 seed-level R values of P2 (already seen, 2000-step survivors), shift the
mean, and apply BOTH registered decision criteria (worst-case Holm 3p < 0.05 of the one-sided t-test and lower 95 % bootstrap bound of
mean R >= log 1.05) at effective n = 90 and 100. Fixed RNG; pure numpy. Output: p2b_power.json next to this file.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))
import confirm_p1 as c1  # noqa: E402

N_SIM, N_BOOT, MEF = 400, 400, float(np.log(1.05))


def power(R: np.ndarray, n: int, shift: float, sd_scale: float, rng: np.random.Generator) -> float:
    base = R.mean() + (R - R.mean()) * sd_scale + shift
    hit = 0
    for _ in range(N_SIM):
        x = rng.choice(base, n)
        p = c1.t_test_secondary(x)["p_one_sided"]
        lo = np.quantile([rng.choice(x, n).mean() for _ in range(N_BOOT)], 0.025)
        hit += (3 * p < 0.05) and lo >= MEF
    return hit / N_SIM


def main() -> None:
    R = np.array([r["R"] for r in json.loads((HERE / "P2_summary.json").read_text(encoding="utf-8"))["rows"] if r.get("valid")])
    rng = np.random.default_rng(2022)
    out = {"n_pilot": len(R), "mean_pilot": float(R.mean()), "sd_pilot": float(R.std(ddof=1)), "grid": []}
    for shift in (0.0, -0.02, -0.04):
        for sd_scale in (1.0, 1.25):
            for n in (90, 100):
                pw = power(R, n, shift, sd_scale, rng)
                out["grid"].append({"shift": shift, "sd_scale": sd_scale, "n": n, "power": pw})
                print(f"mean {R.mean() + shift:.3f} sd x{sd_scale} n {n}: power {pw:.2f}", flush=True)
    (HERE / "p2b_power.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
