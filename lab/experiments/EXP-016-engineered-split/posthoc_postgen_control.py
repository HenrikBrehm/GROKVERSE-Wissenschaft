"""Post hoc control for posthoc_postgen_persistence.py (session 20, 2026-09-27). Is the rise of the target share after grokking
split-specific, or does every run concentrate its W_E power after generalization (weight decay)?
Random-split reference: study runs seeds 0-9 (same config as EXP-016, 25 000 steps, embeddings.npy). No fixed target set exists
there, so the set S is the top-5 at the first logged step >= gen (selection at gen biases the gen share UP, i.e. against
growth) and, as a second reading, the top-5 at the last step (biases the late share up). The same two readings are applied to
the EXP-016 runs. Share of W_E power in S at gen and at the logged step closest to gen + LAG (LAG = 750 and 1500, the range
of EXP-016). Descriptive only."""
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
LAGS = (750, 1500)


def readings(steps, S, gen):
    steps = np.asarray(steps)
    ig = int(np.searchsorted(steps, gen))
    top = lambda i: [int(k) for k in np.argsort(-S[i])[:5]]
    share = lambda i, idx: float(S[i, idx].sum() / S[i].sum())
    out = {"step_at_gen": int(steps[ig])}
    for name, idx in (("set_at_gen", top(ig)), ("set_at_end", top(len(steps) - 1))):
        out[name] = {"gen": round(share(ig, idx), 4)}
        for lag in LAGS:
            j = int(np.argmin(np.abs(steps - (steps[ig] + lag))))
            out[name][f"gen+{lag}"] = {"step": int(steps[j]), "share": round(share(j, idx), 4)}
    return out


rows = {"random_study": [], "engineered_exp016": []}
for s in range(10):
    d = ROOT / f"training/runs/txf_add_p113_wd1.0_frac0.3_seed{s}_arch25k"
    run = json.loads((d / "run.json").read_text(encoding="utf-8"))
    E = np.load(d / "embeddings.npy").astype(np.float64)
    S = np.stack([fb.freq_power(W[:P], B) for W in E])
    gen = run["transitions"]["primary"]["generalization"]["first_crossing_step"]
    rows["random_study"].append({"seed": s, "gen": gen, **readings(run["logged_steps"], S, gen)})
for seed in range(10, 20):
    for suf in ("", "_G"):
        d = HERE / f"raw/EXP-016_baseline_seed{seed}_thr4_split_seed{seed}_eps2.0{suf}"
        res = json.loads((d / "result.json").read_text(encoding="utf-8"))
        gen = res["transitions"]["primary"]["generalization"]["first_crossing_step"]
        steps = np.load(d / "spectra_steps.npy")
        rows["engineered_exp016"].append({"seed": seed, "arm": "G" if suf else "F", "gen": gen,
                                          **readings(steps, np.load(d / "spectra.npy").astype(np.float64), gen)})
summary = {}
for grp, rs in rows.items():
    for name in ("set_at_gen", "set_at_end"):
        for lag in LAGS:
            dl = np.array([r[name][f"gen+{lag}"]["share"] - r[name]["gen"] for r in rs
                           if r[name][f"gen+{lag}"]["step"] > r["step_at_gen"]])
            summary[f"{grp}|{name}|+{lag}"] = {
                "n": int(len(dl)), "share_gen_mean": round(float(np.mean([r[name]["gen"] for r in rs])), 4),
                "delta_mean": round(float(dl.mean()), 4) if len(dl) else None,
                "delta_sd": round(float(dl.std(ddof=1)), 4) if len(dl) > 1 else None, "n_up": int((dl > 0).sum())}
(HERE / "posthoc_postgen_control.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1), encoding="utf-8")
print(json.dumps(summary, indent=1))
