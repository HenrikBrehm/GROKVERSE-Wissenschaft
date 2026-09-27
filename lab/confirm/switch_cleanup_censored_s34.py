"""Session 34, post hoc ADDENDUM to switch_cleanup_s34.py (written after its result): the primary analysis excluded runs without a
generalisation event (N28@25: 13, P3@25: 16), i.e. the slowest runs. If M_clean were right, these should carry MORE old-target
share at t+250 than the runs that generalised. Descriptive: mean s_old for censored vs event runs, and the one-sided
permutation p of (censored - event). No verdict change: the pre-stated verdict stays."""
import json
import numpy as np
from pathlib import Path
import switch_cleanup_s34 as sc

for name in ("N28", "P3"):
    raw_, spl_, pre, w = sc.BLOCKS[name]
    raw, spl = sc.LAB / raw_, sc.LAB / spl_
    cen, ev = [], []
    for d in raw.iterdir():
        m = __import__("re").search(rf"seed(\d+)_thr1_{pre}_seed\d+_{w}_(A|B)_to_{pre}_seed\d+_{w}_(A|B)_at25_devcuda$", d.name)
        if not m:
            continue
        s, x = int(m.group(1)), m.group(2)
        tg = json.loads((spl / f"{pre}_seed{s}_{w}.json").read_text(encoding="utf-8"))["targets"]
        so = sc.shares(d, tg[x], 275, None)[0]
        (ev if sc.gen(d) else cen).append(so)
    cen, ev = np.array(cen), np.array(ev)
    diff = cen.mean() - ev.mean(); allv = np.concatenate([cen, ev]); rng = np.random.default_rng(34)
    p = (1 + sum((lambda q: q[:len(cen)].mean() - q[len(cen):].mean())(rng.permutation(allv)) >= diff for _ in range(10000))) / 10001
    print(f"{name}@25: censored n={len(cen)} s_old={cen.mean():.3f}  event n={len(ev)} s_old={ev.mean():.3f}  diff={diff:+.3f} p_one_sided={p:.3f}")
