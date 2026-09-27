"""Session 34, post hoc ADDENDUM to switch_deficit_s34.py (after its result R = 1.98 / 1.61): the mean excluded censored switch runs
(the slowest). Here medians over ALL switch runs@25 whose destination-only run has an event: observed delay of a censored run =
+inf; predicted delay from s_new as in switch_deficit_s34.py (same fit). Reports median predicted vs median observed delay.
Descriptive, no verdict change."""
import json, math, re
import numpy as np
import switch_cleanup_s34 as sc

for name in ("N28", "P3"):
    raw_, spl_, pre, w = sc.BLOCKS[name]
    raw, spl = sc.LAB / raw_, sc.LAB / spl_
    tg = lambda s: json.loads((spl / f"{pre}_seed{s}_{w}.json").read_text(encoding="utf-8"))["targets"]  # noqa: E731
    base, sw = {}, []
    for d in raw.iterdir():
        if (m := re.search(rf"seed(\d+)_thr1_{pre}_seed\d+_{w}_(A|B)_devcuda$", d.name)):
            s, x = int(m.group(1)), m.group(2); g = sc.gen(d)
            base[(s, x)] = (sc.shares(d, tg(s)[x], 250, None)[0], math.log2(g) if g else None)
        elif (m := re.search(rf"seed(\d+)_thr1_{pre}_seed\d+_{w}_(A|B)_to_{pre}_seed\d+_{w}_(A|B)_at25_devcuda$", d.name)):
            s, y = int(m.group(1)), m.group(3); g = sc.gen(d)
            sw.append((s, y, sc.shares(d, tg(s)[y], 275, None)[0], math.log2(g) if g else math.inf))
    fit = np.array([(sh, lg) for sh, lg in base.values() if lg is not None]); b, a = np.polyfit(fit[:, 0], fit[:, 1], 1)
    pr, ob = [], []
    for s, y, sn, lg in sw:
        ly = base[(s, y)][1]
        if ly is None:
            continue
        pr.append(a + b * sn - ly); ob.append(lg - ly)
    pr, ob = np.array(pr), np.array(ob)
    print(f"{name}@25 n={len(ob)} (censored {int(np.isinf(ob).sum())}): median pred {np.median(pr):+.3f}  median obs {np.median(ob):+.3f}  ratio {np.median(pr)/np.median(ob):.2f}")
