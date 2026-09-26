"""Post hoc (session 7, exploratory, seeds 0-9 = EXP-015 exploration seeds): Spearman(W_E power spectrum at step t, M0 of
the training mask) over training, relative to memorisation and generalisation steps. Question (N13): is the mask imprint
strongest in the memorisation phase and does it fade after generalisation?"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parents[0] / "EXP-001-freq-ban"))
import freq_ban as fb  # noqa: E402
from mask_spectrum import m0, mask_matrix  # noqa: E402

P = 113
B = fb.fourier_basis(P)


def spearman(x, y):
    return float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1])


res = []
for s in range(10):
    d = ROOT / f"training/runs/txf_add_p113_wd1.0_frac0.3_seed{s}_arch25k"
    E = np.load(d / "embeddings.npy")
    run = json.loads((d / "run.json").read_text())
    steps = np.array(run["logged_steps"])
    tr = run["transitions"]["primary"]
    mem, gen = tr["memorization"]["first_crossing_step"], tr["generalization"]["first_crossing_step"]
    M = m0(mask_matrix(s))
    rho = np.array([spearman(fb.freq_power(W[:P].astype(np.float64), B), M) for W in E])
    phase = lambda lo, hi: float(rho[(steps >= lo) & (steps < hi)].mean()) if ((steps >= lo) & (steps < hi)).any() else None
    r = {"seed": s, "mem": mem, "gen": gen, "rho_init": float(rho[0]), "rho_pre_mem": phase(1, mem),
         "rho_memo": phase(mem, gen), "rho_memo_first_half": phase(mem, (mem + gen) // 2),
         "rho_memo_second_half": phase((mem + gen) // 2, gen), "rho_post_gen": phase(gen, 10 ** 9),
         "rho_final": float(rho[-1]), "argmax_step": int(steps[int(np.argmax(rho))])}
    res.append(r)
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
keys = ("rho_init", "rho_pre_mem", "rho_memo_first_half", "rho_memo_second_half", "rho_post_gen", "rho_final")
print("means:", {k: round(float(np.mean([r[k] for r in res if r[k] is not None])), 3) for k in keys})
(HERE / "posthoc_m0_timecourse.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
