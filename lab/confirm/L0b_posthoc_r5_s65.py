"""L0b, POST HOC and DESCRIPTIVE (not part of the registered H1-H4 family): does R5 ("engineered splits generalise
earlier than a random split of the same size") also hold under i.i.d. minibatch AdamW (batch 16, weight decay 0.1)?
Rule 20b asked for K2 AND R5 under minibatch; L0 had no random arm, L0b has one (R, same size, same test set).

Written in session 65 (2026-10-01, ~01:00 Berlin) BEFORE any L0b result was read (the block was still running; this
script refuses to run until all 420 runs load through the frozen loader of confirm_l0b.py).

Per seed s (70 seeds, manifest bce36b1a), arm iid16w (primary) and stride16w (secondary):
  x_s = log2 t_gen(R) - mean(log2 t_gen(F), log2 t_gen(G)),   t_gen = first step with test acc >= 0.95 (trainer
  transitions, primary), runs that never generalise censored at the budget 30 000 (as H4 in confirm_l0b.py).
Reading, fixed now (iid16w): mean x > 0 with bootstrap 95 % CI lower bound > 0 (10 000 resamples over seeds, rng 65)
and x > 0 in >= 80 % of seeds -> "R5 haelt unter Minibatch (beschreibend)"; CI upper bound < 0 -> "umgekehrt";
otherwise "unklar". Censoring: if R is censored in >= 50 % of seeds, the reading is additionally marked "untere
Schranke" (x is then a lower bound). Reported beside it: geometric-mean ratio 2^mean(x) against R5's full-batch
x6.5 (different construction, wd 1, full batch - no test of equality), censoring counts per split and arm.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/confirm/L0b_posthoc_r5_s65.py
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("confirm_l0b_frozen", LAB / "tools/confirm_l0b.py")
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)


def reading(x: np.ndarray, n_cens_R: int, rng: np.random.Generator) -> dict:
    m = rng.choice(x, (10_000, len(x)), replace=True).mean(1)
    lo, hi = float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))
    share = float((x > 0).mean())
    if lo > 0 and share >= 0.8:
        v = "R5 haelt unter Minibatch (beschreibend)"
    elif hi < 0:
        v = "umgekehrt"
    else:
        v = "unklar"
    if n_cens_R >= 0.5 * len(x):
        v += " (untere Schranke: R oft zensiert)"
    return {"mean_log2": float(x.mean()), "ci95": [lo, hi], "ratio_geo": float(2 ** x.mean()), "share_positive": share,
            "n": int(len(x)), "reading": v}


def main() -> None:
    man = json.loads((LAB / "confirm/L0b_manifest.json").read_text(encoding="utf-8"))
    bud = man["budget"]
    out: dict = {"manifest_commit": man["commit"], "note": "post hoc, descriptive, not part of the registered family"}
    rng = np.random.default_rng(65)
    for arm, order in man["arms"].items():
        xs, cens = [], {a: 0 for a in cl.SPLITS}
        for s in man["seeds"]:
            t = {}
            for a in cl.SPLITS:
                v = cl.one_run(man, s, a, order)
                if isinstance(v, str):
                    raise SystemExit(f"[r5-post] not all runs load ({v}); run only after the whole block")
                t[a] = float(v["t_gen"]) if v["t_gen"] else float(bud)
                cens[a] += v["t_gen"] is None
            xs.append(np.log2(t["R"]) - (np.log2(t["F"]) + np.log2(t["G"])) / 2)
        out[arm] = {**reading(np.array(xs), cens["R"], rng), "censored": cens}
    (LAB / "confirm/L0b_posthoc_r5_s65.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
