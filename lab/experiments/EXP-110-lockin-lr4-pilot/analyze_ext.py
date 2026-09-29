"""EXP-110 B 64 extension (session 47, written after the extension runs finished but before reading them; reading in README):
pi at B 64, lr 4e-3 over the merged grid (first grid + EXT), t_half by the same first-upward-crossing rule.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-110-lockin-lr4-pilot/analyze_ext.py
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("exp110_analyze", HERE / "analyze.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)
REF = {3700: {"lr1e-3": 244.5, "lr2e-3": 205.2}, 3701: {"lr1e-3": 325.6, "lr2e-3": 225.2}}   # EXP-108 / EXP-109 summaries


def main() -> None:
    D, bs = A.D, 64
    out = {}
    for s in D.SEEDS:
        T = json.loads((A.SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        F, G = T["F"], T["G"]
        sfx = f"_bs{bs}_lr{D.LR!r}_devcuda"
        pure = {x: A.power(f"EXP-018_baseline_seed{s}_thr1_seed{s}_{x}{sfx}", s, x, None, bs) for x in "FG"}
        ts = sorted(set(D.GRID[bs]) | set(D.EXT[bs]))
        sw = {(a, t): A.power(f"EXP-020_baseline_seed{s}_thr1_seed{s}_{a}_to_seed{s}_{b}_at{t}{sfx}", s, a, b, bs)
              for t in ts for a, b in (("F", "G"), ("G", "F"))}
        bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
        if bad:
            out[s] = {"error": bad[0]}
            continue
        LF, LG = A.lr_(pure["F"], F, G), A.lr_(pure["G"], F, G)
        pi = {t: ((A.lr_(sw[("F", t)], F, G) - LG) / (LF - LG) + (A.lr_(sw[("G", t)], F, G) - LF) / (LG - LF)) / 2 for t in ts}
        th, c = A.t_half(pi)
        rel = "Umkehr" if th > REF[s]["lr1e-3"] else "keine Beschleunigung" if th > REF[s]["lr2e-3"] else "beschleunigt"
        out[s] = {"pi": {t: round(v, 3) for t, v in pi.items()}, "t_half": th, "censored": c, "vs_ref": rel, "ref": REF[s]}
    both = [v.get("vs_ref") for v in out.values()]
    reading = "Umkehr" if all(b == "Umkehr" for b in both) else "keine Beschleunigung" if all(b in ("Umkehr", "keine Beschleunigung") for b in both) else "beschreiben"
    res = {"rows": out, "reading": reading}
    (HERE / "ext_summary.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
