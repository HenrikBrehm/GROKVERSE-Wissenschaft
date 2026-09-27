"""EXP-064 post hoc (session 23, descriptive, after N29): absolute W_E energy of old vs new targets per final model (2000 steps after the switch)
vs the ablation contrast. Question: at t = 25, is old energy larger while removing the new targets hurts more (energy/function dissociation)?
Run: python lab/tools/guarded_run.py -- python lab/experiments/EXP-064-functional-regimes/posthoc_energy.py
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as X  # noqa: E402

rows = []
for s in X.B.SEEDS:
    meta = json.loads((X.A.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    test = np.load(X.A.SPL / f"seed{s}_test.npy")
    for t in X.TS:
        for first, second, old, new in (("A", "B", F, G), ("B", "A", G, F)):
            st1, st2 = X.A.stem(s, X.B.OM, first), X.A.stem(s, X.B.OM, second)
            d = X.A.find_run(HERE / "raw", f"EXP-0*_baseline_seed{s}_thr*_{st1}_to_{st2}_at{t}{X.A.SUF}")
            m = X.E51.load_model(d)
            W = m.W_E.detach().numpy().astype(np.float64)[:X.P]
            eo, en = (float((X.G61.project(W, S) ** 2).sum()) for S in (old, new))
            acc = lambda Wr: X.E55.evaluate(m, Wr, test)["acc"]   # noqa: E731
            rows.append({"seed": s, "t": t, "dir": first + second, "logE_old_new": float(np.log(eo / en)), "base": acc(None),
                         "acc_noold": acc(W - X.G61.project(W, old)), "acc_nonew": acc(W - X.G61.project(W, new))})
for t in X.TS:
    r = [x for x in rows if x["t"] == t]
    diss = [x for x in r if x["logE_old_new"] > 0 and x["acc_noold"] > x["acc_nonew"]]
    print(t, "E_old>E_new", sum(x["logE_old_new"] > 0 for x in r), "/", len(r), "| function uses new (acc_noold > acc_nonew)",
          sum(x["acc_noold"] > x["acc_nonew"] for x in r), "| both (dissociation)", len(diss),
          "| median logE", round(float(np.median([x["logE_old_new"] for x in r])), 2))
(HERE / "posthoc_energy.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
