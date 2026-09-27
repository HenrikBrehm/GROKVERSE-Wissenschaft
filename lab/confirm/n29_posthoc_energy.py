"""N29 post hoc (session 23, after the frozen result, descriptive): W_E energy of old vs new targets per final model vs the functional contrast.
Run: python lab/tools/guarded_run.py -- python lab/confirm/n29_posthoc_energy.py"""
import sys, json, numpy as np
sys.path.insert(0, "lab/tools")
import confirm_n29 as n
from pathlib import Path
man = json.load(open("lab/confirm/N29_manifest.json", encoding="utf-8"))
rows = json.load(open("lab/confirm/N29_summary.json", encoding="utf-8"))["rows"]
out = []
for r in rows:
    s = r["seed"]
    meta = json.load(open(f"lab/confirm/n29_splits/n29_seed{s}_w0.json"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    for t in (25, 50):
        for first, second, old, new in (("A", "B", F, G), ("B", "A", G, F)):
            cmd = ["x", n.FB, "--seed", str(s), "--threads", "1", "--device", "cuda", "--split-file", str(n.SPL / f"{n.stem(s, first)}.npy"),
                   "--switch-split-file", str(n.SPL / f"{n.stem(s, second)}.npy"), "--switch-step", str(t)]
            d = n.run_dir(cmd)
            m = n.p2.load_model_bytes(n.BLOCK.bound_bytes(man, d / "model_final.pt"))
            W = m.W_E.detach().numpy().astype(np.float64)[:113]
            eo, en = (float((n.g61().project(W, S) ** 2).sum()) for S in (old, new))
            k = f"{t}{first}{second}"
            out.append({"seed": s, "t": t, "logE_old_over_new": float(np.log(eo / en)), "acc_diff_new_minus_old": r["runs"][k]["acc_new"] - r["runs"][k]["acc_old"]})
for t in (25, 50):
    x = np.array([o["logE_old_over_new"] for o in out if o["t"] == t]); y = np.array([o["acc_diff_new_minus_old"] for o in out if o["t"] == t])
    print(t, "median log(E_old/E_new)", round(float(np.median(x)), 2), "frac E_old>E_new", float((x > 0).mean()), "mean acc_new-acc_old", round(float(y.mean()), 3),
          "frac (E_old>E_new but function uses new)", float(((x > 0) & (y < 0)).mean()))
json.dump(out, open("lab/confirm/N29_posthoc_energy.json", "w"), indent=1)
