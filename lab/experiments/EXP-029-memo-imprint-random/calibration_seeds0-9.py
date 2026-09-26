import json, sys
from pathlib import Path
import numpy as np
ROOT = Path("C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft")
sys.path.insert(0, str(ROOT / "lab/experiments/EXP-001-freq-ban")); sys.path.insert(0, str(ROOT / "lab/experiments/EXP-015-mask-spectrum"))
import freq_ban as fb
from mask_spectrum import m0, mask_matrix
B = fb.fourier_basis(113)
sp = lambda x, y: float(np.corrcoef(np.argsort(np.argsort(x)), np.argsort(np.argsort(y)))[0, 1])
for s in range(10):
    d = ROOT / f"training/runs/txf_add_p113_wd1.0_frac0.3_seed{s}_arch25k"
    E = np.load(d / "embeddings.npy"); run = json.loads((d / "run.json").read_text()); st = np.array(run["logged_steps"])
    tr = run["transitions"]["primary"]; mem, gen = tr["memorization"]["first_crossing_step"], tr["generalization"]["first_crossing_step"]
    M = m0(mask_matrix(s))
    grid = [i for i, t in enumerate(st) if t >= mem and t < gen]
    i_g = int(np.argmin(np.abs(st - (gen + 25))))
    print(s, "memo %.3f" % np.mean([sp(fb.freq_power(E[i][:113].astype(np.float64), B), M) for i in grid]),
          "at gen+25 (step %d) %.3f" % (st[i_g], sp(fb.freq_power(E[i_g][:113].astype(np.float64), B), M)))
