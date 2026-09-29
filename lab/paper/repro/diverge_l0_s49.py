"""Session 49: where do the repro L0 runs leave the frozen L0 runs? First spectrum step with a difference, per run (read only)."""
import json
from pathlib import Path

import numpy as np

R = Path("lab/paper/repro/out/l0/add113_steps30000_cuda/runs")
F = Path("lab/confirm/l0_raw")
ref = {r["seed"]: r for r in json.loads(Path("lab/confirm/L0_summary.json").read_text(encoding="utf-8"))["rows"]}
new = {r["seed"]: r for r in json.loads(Path("lab/paper/repro/out/l0/add113_steps30000_cuda/l0_summary.json").read_text(encoding="utf-8"))["rows"]}
out = []
for s in range(3720, 3730):
    for bs in (256, 64):
        d_new = abs(new[s][f"dpow_iid{bs}"] - ref[s][f"dpow_iid{bs}"])
        for arm in "FG":
            a = R / f"seed{s}_{arm}_bs{bs}"
            b = F / f"EXP-018_baseline_seed{s}_thr1_l0_seed{s}_{arm}_bs{bs}_devcuda"
            sa, ta = np.load(a / "spectra.npy"), np.load(a / "spectra_steps.npy").tolist()
            sb, tb = np.load(b / "spectra.npy"), np.load(b / "spectra_steps.npy").tolist()
            first = next((t for t in sorted(set(ta) & set(tb)) if not np.array_equal(sa[ta.index(t)], sb[tb.index(t)])), None)
            ra = json.loads((a / "result.json").read_text(encoding="utf-8"))
            rb = json.loads((b / "result.json").read_text(encoding="utf-8"))
            out.append({"seed": s, "bs": bs, "arm": arm, "first_diff_step": first, "dpow_absdiff": round(d_new, 6),
                        "gen_new": ra["generalization_step"], "gen_frozen": (rb.get("events") or {}).get("generalization_step"),
                        "train_final_new": ra["final_acc"]["train"], "train_final_frozen": (rb.get("final_acc") or {}).get("train")})
for o in out:
    print(o)
Path("lab/paper/repro/diverge_l0_s49.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
