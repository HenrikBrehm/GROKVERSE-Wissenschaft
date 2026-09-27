"""P2d/P2e post hoc, EXPLORATION (session 28; seeds seen for K2-function, never for the target order). Question: is the fine
order of the targets (N39) a transient of early training or does it persist after generalization in the transformer?
Fixed before looking: mean within-arm Spearman(mask spectrum M0 of the split, W_E power of the 5 targets) over time; for add 113
also M0c; generalization step (first test acc >= 0.9 event of freq_ban) reported. Reads spectra.npy of the stored runs (not
through the frozen loaders; exploration). mul 113: spectra.npy is the plain DFT, so the group-basis power of the W_E snapshots
(steps 0, 500, 1000, 2000, 4000, 8000) is used instead (a first run used spectra.npy for mul by mistake: rho ~ 0, discarded). Mask spectra: confirm_splits.m0 (task-specific group basis) and m0c_add (add 113)."""
import json, sys
from pathlib import Path
import numpy as np
LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools")); sys.path.insert(0, str(LAB / "confirm"))
import confirm_splits as cs
from P1_posthoc_within import m0c_add
from rank_tools import spearman
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
from analyze import group_power
out = {}
for name, raw, spl, task, p, glob in (("add113", "p2d_raw", "p2d_splits", "add", 113, "*p2d_seed*_devcuda"),
                                      ("mul113", "p2e_raw", "p2e_splits", "mul", 113, "*p2e_mul113_*_mul113_devcuda"),
                                      ("add97", "p2e_raw", "p2e_splits", "add", 97, "*p2e_add97_*_add97_devcuda")):
    rows, gens = {}, []
    for d in sorted((LAB / "confirm" / raw).glob(glob)):
        stem = d.name.split("thr1_")[1].rsplit("_devcuda", 1)[0]
        if name != "add113":
            stem = stem.rsplit(f"_{task}{p}", 1)[0]
        meta = json.loads((LAB / "confirm" / spl / f"{stem}.json").read_text(encoding="utf-8"))
        T = meta["targets"]; sel = [k - 1 for k in T]
        idx = np.load(LAB / "confirm" / spl / f"{stem}.npy")
        preds = {"M0": cs.m0(idx, task, p)[sel]}
        if name == "add113":
            preds["M0c"] = m0c_add(idx, p)[sel]
        if task == "mul":                                  # spectra.npy is the plain DFT over the token index, not the group basis:
            ws = list(np.load(d / "we_snapshot_steps.npy"))  # use the W_E snapshots in the group basis (as P1 power_at)
            W = np.load(d / "we_snapshots.npy").astype(np.float64)
            sp, st = np.array([group_power(W[i], task, p)[0] for i in range(len(ws))]), ws
        else:
            sp, st = np.load(d / "spectra.npy"), list(np.load(d / "spectra_steps.npy"))
        gens.append((json.loads((d / "result.json").read_text(encoding="utf-8")).get("events") or {}).get("generalization_step"))
        for i, s in enumerate(st):
            for k, x in preds.items():
                rows.setdefault((k, int(s)), []).append(spearman(x, sp[i][sel]))
    g = [x for x in gens if x is not None]
    out[name] = {"arms": len(gens), "gen_step_median": float(np.median(g)) if g else None, "n_gen": len(g),
                 "rho_by_step": {f"{k}@{s}": round(float(np.mean(v)), 3) for (k, s), v in sorted(rows.items()) if s in (0, 250, 500, 1000, 2000, 3000, 4000, 6000, 8000)}}
    print(name, json.dumps(out[name]), flush=True)
(LAB / "confirm/P2de_posthoc_time.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
