"""Session 32 (2026-09-27, window closed), POST HOC on stored N29 / N29b / N29c blocks (20 seeds each, GPU), no training.
Generalisation steps of these blocks were never looked at. Stated before looking (per seed: mean over both directions of the log2
difference, b = min(gen, 2000) from step 0, exact one-sided sign test over non-tied seeds):
  N29   log2 b(@25) - log2 b(@50) > 0                         (replication of the 25-vs-50 contrast, 4th block)
  N29b  (a) log2 b(@50 attention reset) - log2 b(@50) > 0     (undoing the lock-in, K4d, brings the delay back)
        (b) log2 b(@50 attention reset) - log2 b(@50 MLP reset) > 0
  N29c  (descriptive) log2 b(@50 VO reset) - log2 b(@50 QK reset) > 0   (K4e ordering)
Caveat stated in advance: any re-initialisation costs time by itself; (b) and N29c compare two resets, (a) does not.
  python lab/confirm/speed_switch_resets_s32.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
CAP = 2000


def load(block: str) -> dict:
    pat = re.compile(rf"seed(\d+)_thr1_{block}_seed\d+_w0_(A|B)_to_{block}_seed\d+_w0_(A|B)_at(\d+)(?:_rs(\w+))?_devcuda$")
    out: dict = {}
    for d in (LAB / f"confirm/{block}_raw").iterdir():
        m = pat.search(d.name)
        assert m, d.name
        s, a, b, t, rs = int(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5) or "none"
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        assert r["status"] == "completed", d.name
        g = (r.get("events") or {}).get("generalization_step")
        out.setdefault(s, {})[(a + b, int(t), rs)] = math.log2(min(g, CAP) if g is not None else CAP)
    return out


def contrast(runs: dict, x: tuple, y: tuple) -> dict:
    d = np.array([((v[("AB",) + x] - v[("AB",) + y]) + (v[("BA",) + x] - v[("BA",) + y])) / 2 for v in runs.values()])
    nz = d[np.abs(d) > 1e-9]
    k, n = int((nz > 0).sum()), len(nz)
    return {"n": len(d), "mean": float(d.mean()), "median": float(np.median(d)), "pos": k, "nonzero": n,
            "p_one_sided": sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0}


def main() -> None:
    n29, n29b, n29c = load("n29"), load("n29b"), load("n29c")
    out = {"note": "post hoc exploration; times of these blocks never looked at before",
           "N29_25_vs_50": contrast(n29, (25, "none"), (50, "none")),
           "N29b_a_attn_vs_normal": contrast(n29b, (50, "attn"), (50, "none")),
           "N29b_b_attn_vs_mlp": contrast(n29b, (50, "attn"), (50, "mlp")),
           "N29b_descr_mlp_vs_normal": contrast(n29b, (50, "mlp"), (50, "none")),
           "N29c_vo_vs_qk": contrast(n29c, (50, "vo"), (50, "qk")),
           "N29c_descr_vo_vs_normal": contrast(n29c, (50, "vo"), (50, "none")),
           "N29c_descr_qk_vs_normal": contrast(n29c, (50, "qk"), (50, "none"))}
    (LAB / "confirm/speed_switch_resets_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
