"""EXP-059/058 post hoc, EXPLORATION (session 28; seeds 400-409 seen). Programme B, 'what locks in?'.
Question: does the preserved ORDER of the old targets (C2 measure: Spearman over the five old targets between W_E power at the
switch t and at t + 2000) grow with t in step with the persistence index pi, or does it saturate earlier (order fixed before the
set)? Fixed before looking: per t in {10, 15, 20, 25, 30, 35, 50}, mean over 20 runs (10 seeds x 2 directions) of that rho,
next to pi_normal_mean from EXP-059's summary; descriptive also the zeroed-first-moment arms ('rom', t = 25..50) and t = 25
variants of EXP-058. Reading: order ~ saturated while pi is still low -> the within-set structure locks in before the set;
parallel rise -> one phenomenon at two resolutions."""
import json, sys
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "confirm")); sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
from analyze import group_power
from rank_tools import spearman
E59, E58, E56 = (next((LAB / "experiments").glob(f"EXP-0{n}*")) for n in (59, 58, 56))
SPL = E56 / "splits"
pi = json.loads((E59 / "summary.json").read_text(encoding="utf-8"))
res = {}
for raw in (E59 / "raw", E58 / "raw"):
    for d in sorted(raw.glob("EXP-020_*_devcuda")):
        name = d.name.rsplit("_devcuda", 1)[0]
        tail = name.split("_at")[1]
        t, variant = (int(tail), "normal") if tail.isdigit() else (int(tail.split("_")[0]), tail.split("_", 1)[1])
        s = int(name.split("_seed")[1].split("_")[0])
        first = "A" if f"w0_A_to_seed{s}_w0_B" in name else "B"
        T = json.loads((SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))["targets"][first]; sel = [k - 1 for k in T]
        ws, W = list(np.load(d / "we_snapshot_steps.npy")), np.load(d / "we_snapshots.npy").astype(np.float64)
        if t not in ws or t + 2000 not in ws:
            continue
        a, b = (group_power(W[ws.index(k)], "add", 113)[0][sel] for k in (t, t + 2000))
        res.setdefault((variant, t), []).append(spearman(a, b))
out = {f"{v}@{t}": {"n": len(r), "mean_rho_order": round(float(np.mean(r)), 3), "sd": round(float(np.std(r, ddof=1)), 3),
                    "pi_mean": (pi["pi_normal_mean"] if v == "normal" else pi["pi_rom_mean"] if v == "rom" else {}).get(str(t))}
       for (v, t), r in sorted(res.items())}
print(json.dumps(out, indent=1))
(LAB / "confirm/EXP059_posthoc_order_clock.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
