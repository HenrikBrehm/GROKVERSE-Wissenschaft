"""EXP-029 post hoc control (session 7, after the result): rho(W_E, M0 of the own mask) vs rho(W_E, M0 of the other nine
seeds' masks) in the same memorisation window. A generic artefact (norm growth, shared spectral shape) would give
similar foreign values. Baselines 10-19 (confirmation data) and study seeds 0-9 (exploration data)."""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[0]
ROOT = HERE.parents[2]
sys.path.insert(0, str(EXP / "EXP-015-mask-spectrum"))
sys.path.insert(0, str(EXP / "EXP-001-freq-ban"))
from mask_spectrum import m0, mask_matrix  # noqa: E402
import freq_ban as fb  # noqa: E402

B = fb.fourier_basis(113)


def spearman(x, y):
    return float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1])


def series_baseline(s):
    d = EXP / "EXP-003-early-prediction" / "raw_d" / f"EXP-001_baseline_t2000_m5_seed{s}_thr4"
    r = json.loads((d / "result.json").read_text())
    tr = r["transitions"]["primary"]
    return np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy"), tr


def series_study(s):
    d = ROOT / f"training/runs/txf_add_p113_wd1.0_frac0.3_seed{s}_arch25k"
    E = np.load(d / "embeddings.npy")
    run = json.loads((d / "run.json").read_text())
    S = np.array([fb.freq_power(W[:113].astype(np.float64), B) for W in E])
    return S, np.array(run["logged_steps"]), run["transitions"]["primary"]


out = {}
for name, seeds, fn in (("baselines_10_19", range(10, 20), series_baseline), ("study_0_9", range(10), series_study)):
    M = {s: m0(mask_matrix(s)) for s in seeds}
    rows = []
    for s in seeds:
        S, st, tr = fn(s)
        mem, gen = tr["memorization"]["first_crossing_step"], tr["generalization"]["first_crossing_step"]
        win = np.flatnonzero((st >= mem) & (st < gen))
        own = float(np.mean([spearman(S[i], M[s]) for i in win]))
        foreign = float(np.mean([np.mean([spearman(S[i], M[t]) for i in win]) for t in seeds if t != s]))
        own0 = spearman(S[0], M[s])
        rows.append({"seed": s, "own_memo": own, "foreign_memo": foreign, "own_init": own0})
        print(name, s, "own %.3f foreign %.3f" % (own, foreign))
    out[name] = {"rows": rows, "own_mean": float(np.mean([r["own_memo"] for r in rows])),
                 "foreign_mean": float(np.mean([r["foreign_memo"] for r in rows])),
                 "n_own_gt_foreign": int(sum(r["own_memo"] > r["foreign_memo"] for r in rows))}
    print(name, {k: v for k, v in out[name].items() if k != "rows"})
(HERE / "posthoc_foreign_mask.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
