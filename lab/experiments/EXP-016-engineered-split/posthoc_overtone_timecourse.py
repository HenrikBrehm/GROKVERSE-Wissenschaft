"""Post hoc (session 5, Codex item 5): time course of the 2k components within the SAME seeds.
Study runs seeds 0-9 (embeddings.npy, 125 logged steps). For every pair (k, h = fold(2k)) in the final W_E top-5 with h the
weaker member: power ratio h/k and the rank of h over training; generalization step from run.json for reference."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[0] / "EXP-001-freq-ban"))
import freq_ban as fb  # noqa: E402

P = 113
B = fb.fourier_basis(P)
pairs = [(r["seed"], r["k"], r["h"]) for r in
         json.loads((HERE / "posthoc_overtone_test.json").read_text())["rows"] if r["power_ratio_h_over_k"] < 1]
out = []
for s, k, h in pairs:
    d = ROOT / f"training/runs/txf_add_p113_wd1.0_frac0.3_seed{s}_arch25k"
    E = np.load(d / "embeddings.npy")
    run = json.loads((d / "run.json").read_text())
    steps = run["logged_steps"]
    gen = (run.get("transition") or {}).get("test_generalized_step") or (run.get("transitions") or {})
    ratio, rank_h = [], []
    for W in E:
        pw = fb.freq_power(W[:P].astype(np.float64), B)
        ratio.append(float(pw[h - 1] / pw[k - 1]))
        rank_h.append(int(np.argsort(np.argsort(-pw))[h - 1]) + 1)
    idx = [0, len(steps) // 8, len(steps) // 4, len(steps) // 2, 3 * len(steps) // 4, len(steps) - 1]
    out.append({"seed": s, "k": k, "h": h, "gen": gen if isinstance(gen, (int, float)) else None,
                "at": {int(steps[i]): (round(ratio[i], 3), rank_h[i]) for i in idx},
                "first_step_h_in_top5": next((int(st) for st, rk in zip(steps, rank_h) if rk <= 5), None)})
for o in out:
    print(o)
(HERE / "posthoc_overtone_timecourse.json").write_text(json.dumps(out, indent=1))
