"""Session 34, EXPLORATION on N28 only (after M_clean was contradicted, switch_cleanup_s34.py). P3's s_new / total shares stay
unread so that P3 can serve as a check. Per run X->Y@25: s_old, s_new (targets of Y), s_tot = s_old + s_new at step 275;
delay rank with censored runs (no event within the horizon) ranked as slowest (ties). Spearman per run (n = 60, directions pooled;
exploratory, not independent). Prints rho for s_old, s_new, s_tot, and s_new - s_old.
  python lab/confirm/switch_stall_explore_s34.py [N28|P3]"""
import json, math, re, sys
import numpy as np
import switch_cleanup_s34 as sc


def rows(name: str, t: int = 25) -> list[tuple]:
    raw_, spl_, pre, w = sc.BLOCKS[name]
    raw, spl = sc.LAB / raw_, sc.LAB / spl_
    out = []
    for d in raw.iterdir():
        m = re.search(rf"seed(\d+)_thr1_{pre}_seed\d+_{w}_(A|B)_to_{pre}_seed\d+_{w}_(A|B)_at{t}_devcuda$", d.name)
        if not m:
            continue
        s, x, y = int(m.group(1)), m.group(2), m.group(3)
        tg = json.loads((spl / f"{pre}_seed{s}_{w}.json").read_text(encoding="utf-8"))["targets"]
        dy = sc.run_dir(raw, pre, w, s, y, None, None)
        g, gy = sc.gen(d), sc.gen(dy)
        if not gy:
            continue
        delay = math.log2(g / gy) if g else math.inf
        so, sn = sc.shares(d, tg[x], t + 250, None)[0], sc.shares(d, tg[y], t + 250, None)[0]
        out.append((s, so, sn, delay))
    return out


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "N28"
    R = rows(name)
    so, sn, dl = (np.array([r[i] for r in R]) for i in (1, 2, 3))
    dl = np.where(np.isinf(dl), 1e9, dl)
    for lab, v in (("s_old", so), ("s_new", sn), ("s_tot", so + sn), ("s_new-s_old", sn - so)):
        print(f"{name}@25 n={len(R)} rho({lab}, delay) = {sc.spearman(v, dl):+.3f}")
    print(f"mean s_old {so.mean():.3f} s_new {sn.mean():.3f}")
