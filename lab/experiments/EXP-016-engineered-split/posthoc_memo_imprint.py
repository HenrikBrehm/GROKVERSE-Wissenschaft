"""Post hoc (session 7, not pre-registered): in the transformer on engineered splits, is the target set F already in the
W_E top-5 during the memorisation phase (after train >= 0.99, before test >= 0.95)? Spectra every 250 steps."""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
rows = []
for d in sorted((HERE / "raw").glob("EXP-016_baseline_seed*_eps2.0*")):
    r = json.loads((d / "result.json").read_text())
    if r.get("status") != "done" and r.get("status") != "completed":
        pass
    meta = json.loads(Path(str(Path(r["split_file"]).with_suffix(".json"))).read_text()) if Path(
        str(Path(r["split_file"]).with_suffix(".json"))).exists() else None
    if meta is None:
        continue
    F = set(meta["targets"])
    S, st = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy")
    tr = r["transitions"]["primary"]
    mem, gen = tr["memorization"]["first_crossing_step"], tr["generalization"]["first_crossing_step"]
    ov = {int(t): len(set(int(k) for k in np.argsort(-S[i])[:5] + 1) & F) for i, t in enumerate(st)}
    sh = {int(t): float(S[i][[k - 1 for k in F]].sum() / S[i].sum()) for i, t in enumerate(st)}
    rows.append({"run": d.name, "mem": mem, "gen": gen, "ov": ov, "share": sh})
    print(d.name[-28:], "mem", mem, "gen", gen, "ov_F", [ov[t] for t in sorted(ov)], "share@250 %.3f" % sh.get(250, np.nan))
pre = [x for x in rows if x["mem"] is not None and x["gen"] is not None and x["mem"] <= 250 < x["gen"]]
print("runs with step 250 inside memorisation phase:", len(pre), "of", len(rows))
if pre:
    print("mean ov_F @250 %.2f, @final %.2f, @0 %.2f" % (np.mean([x["ov"][250] for x in pre]),
          np.mean([x["ov"][max(x["ov"])] for x in pre]), np.mean([x["ov"][0] for x in pre])))
(HERE / "posthoc_memo_imprint.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
