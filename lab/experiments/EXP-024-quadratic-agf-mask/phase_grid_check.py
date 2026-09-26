"""EXP-024: does the utility top-5 survive a finer phase grid (32 x 32 instead of 16 x 16)? Codex review item 9."""
import json
import numpy as np
import utility_scan as us

rows = []
for seed in range(10, 20):
    for arm, suf in (("F", ""), ("G", "_G")):
        if (seed, arm) == (12, "G"):
            continue
        M = us.mask_from_idx(np.load(us.S16 / f"split_seed{seed}_eps2.0{suf}.npy"))
        T = json.loads((us.S16 / f"split_seed{seed}_eps2.0{suf}.json").read_text())["targets"]
        H = {us.fold(57 * t) for t in T}
        U = np.array([us.utility(M, k, n_phase=32) for k in range(1, us.K + 1)])
        top = set(int(k) for k in np.argsort(-U)[:5] + 1)
        rows.append((seed, arm, len(top & set(T)), len(top & H)))
        print(rows[-1], flush=True)
print("n", len(rows), "mean ov_F", np.mean([r[2] for r in rows]), "mean ov_H", np.mean([r[3] for r in rows]))
