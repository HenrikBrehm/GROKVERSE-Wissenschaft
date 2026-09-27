"""EXP-046, descriptive addition announced before the runs (Nachtrag s13, NOT pre-registered as a test): Top-3 Delta per seed.
Session 20. Reads the saved spectra (irrep power k = 1..29 at step 2000) and the target sets from summary.json."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as a  # noqa: E402

rows = [r for r in json.loads((HERE / "summary.json").read_text(encoding="utf-8"))["rows"] if r.get("valid")]
out = []
for r in rows:
    K3 = {}
    for arm in "FG":
        d = a.run_dir(r["seed"], arm)
        S, st = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
        pw = S[st.index(2000)]
        K3[arm] = {int(k) + 1 for k in np.argsort(-pw)[:3]}
    F, G = set(r["F"]), set(r["G"])
    out.append({"seed": r["seed"], "Delta_top3": len(K3["F"] & F) + len(K3["G"] & G) - len(K3["F"] & G) - len(K3["G"] & F)})
D = np.array([o["Delta_top3"] for o in out])
res = {"n": len(D), "Delta_top3_mean": float(D.mean()), "n_positive": int((D > 0).sum()), "max_possible": 6,
       "p_sign_flip_descriptive": a.one_sided_p(D), "rows": out}
(HERE / "posthoc_top3.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
print({k: v for k, v in res.items() if k != "rows"})
