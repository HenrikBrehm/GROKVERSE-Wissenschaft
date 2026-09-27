"""EXP-059/058 post hoc, EXPLORATION (session 28). Hypothesis fixed before computing: zeroing Adam's first moment at the switch
('rom') lowers pi (known, K4b) but NOT the preserved order of the old targets (C2 measure) -> momentum carries set-level
exposure, the within-set order is already in W_E. Paired by (seed, direction, t) for t in {25, 30, 35, 50}: difference
normal - rom of (a) the order measure and (b) the old-target power share at the end (a pi-like set measure computed here the
same way for both arms). Mean, SD, paired exact... Monte-Carlo sign-flip two-sided p. Seeds 400-409 seen."""
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
runs = {}
for raw in (E59 / "raw", E58 / "raw"):
    for d in sorted(raw.glob("EXP-020_*_devcuda")):
        name = d.name.rsplit("_devcuda", 1)[0]; tail = name.split("_at")[1]
        t, v = (int(tail), "normal") if tail.isdigit() else (int(tail.split("_")[0]), tail.split("_", 1)[1])
        if v not in ("normal", "rom"):
            continue
        s = int(name.split("_seed")[1].split("_")[0]); first = "A" if f"w0_A_to_seed{s}_w0_B" in name else "B"
        T = json.loads((SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))["targets"]
        old, new = [k - 1 for k in T[first]], [k - 1 for k in T["B" if first == "A" else "A"]]
        ws, W = list(np.load(d / "we_snapshot_steps.npy")), np.load(d / "we_snapshots.npy").astype(np.float64)
        if t not in ws or t + 2000 not in ws:
            continue
        a, b = (group_power(W[ws.index(k)], "add", 113)[0] for k in (t, t + 2000))
        runs[(v, t, s, first)] = {"order": spearman(a[old], b[old]), "old_share": float(b[old].sum() / (b[old].sum() + b[new].sum()))}
rng = np.random.default_rng(59)
out = {}
for t in (25, 30, 35, 50):
    keys = [k[2:] for k in runs if k[0] == "normal" and k[1] == t and ("rom", t) + k[2:] in runs]
    for m in ("order", "old_share"):
        d = np.array([runs[("normal", t) + k][m] - runs[("rom", t) + k][m] for k in keys])
        flips = rng.choice((-1.0, 1.0), size=(100_000, len(d)))
        p = float(((np.abs((flips * d).mean(1)) >= abs(d.mean())).sum() + 1) / 100_001)
        out[f"{m}@{t}"] = {"n": len(d), "mean_normal_minus_rom": round(float(d.mean()), 3), "sd": round(float(d.std(ddof=1)), 3), "p_two": round(p, 4)}
print(json.dumps(out, indent=1))
(LAB / "confirm/EXP059_posthoc_rom_order.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
