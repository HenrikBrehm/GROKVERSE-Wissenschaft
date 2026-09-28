"""R8 power (session 37, before freezing): resample the 10 EXP-086 pilot seed differences D = C_AB(25) - C_AA2(25) with
replacement, n in (20, 25, 30); power of p = max(p_flip exact, p_sign) < 0.05 at the pilot mean and with every value shifted
down by half the pilot mean (winner's curse). Rule (registration): smallest n with power >= 0.8 at half effect, else 30.
  python lab/confirm/R8_pilot_power.py > lab/confirm/R8_pilot_power.json
"""
import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "experiments/EXP-086-same-spectrum-switch"))
import analyze as a86  # noqa: E402
import confirm_r6 as r6  # noqa: E402

runs = a86.collect()
ok = {s: v for s, v in runs.items() if s in a86.SEEDS}
D = np.array([a86.cost(v, "A", "B", 25) - a86.cost(v, "A", "A2", 25) for v in ok.values()])
rng = np.random.default_rng(88)
out = {"pilot_D": D.round(4).tolist(), "pilot_mean": float(D.mean()), "pilot_sd": float(D.std(ddof=1)), "sims": 2000}
for label, shift in (("full", 0.0), ("half_effect_shift", D.mean() / 2)):
    out[label] = {}
    for n in (20, 25, 30):
        hits = 0
        for _ in range(out["sims"]):
            x = rng.choice(D - shift, size=n, replace=True)
            hits += max(r6.p_flip(x, rng), r6.p_sign(x)) < 0.05
        out[label][str(n)] = hits / out["sims"]
ns = [n for n in (20, 25, 30) if out["half_effect_shift"][str(n)] >= 0.8]
out["n_rule"] = ns[0] if ns else 30
print(json.dumps(out, indent=1))
