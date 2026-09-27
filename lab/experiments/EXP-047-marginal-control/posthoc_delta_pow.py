"""EXP-047 post hoc (session 25, exploratory, stored runs only): Delta_pow (P1 measure, W_E power at 2000) for eng and shuf arms.
Question: does the shuffled control (same token frequencies, pair structure destroyed) show a small steering on the continuous measure?"""
import itertools, json, numpy as np
from pathlib import Path
H = Path(__file__).resolve().parent
def sp(s, kind, arm):
    d = H / f"raw/EXP-016_baseline_seed{s}_thr1_split_add113_seed{s}_{kind}_{arm}_devcuda"
    r = json.loads((d / "result.json").read_text()); assert r["status"] == "completed" and r["steps_completed"] >= 2000
    st = np.load(d / "spectra_steps.npy").tolist(); v = np.load(d / "spectra.npy")[st.index(2000)].astype(float)
    assert np.isfinite(v).all(); return v
S = lambda pw, K: pw[[k - 1 for k in K]].sum()
out = {}
for kind in ("eng", "shuf"):
    D = []
    for s in range(150, 160):
        T = {a: json.loads((H / f"splits/split_add113_seed{s}_{kind}_{a}.json").read_text())["targets"] for a in "FG"}
        pF, pG = sp(s, kind, "F"), sp(s, kind, "G")
        D.append(np.log(S(pF, T["F"]) / S(pF, T["G"])) + np.log(S(pG, T["G"]) / S(pG, T["F"])))
    D = np.array(D); fl = np.array(list(itertools.product((1, -1), repeat=10)))
    p = float(((fl * D).mean(1) >= D.mean() - 1e-12).mean())
    out[kind] = {"mean": float(D.mean()), "sd": float(D.std(ddof=1)), "n_pos": int((D > 0).sum()), "p_one_sided": p, "D": D.round(3).tolist()}
print(json.dumps(out, indent=1))
