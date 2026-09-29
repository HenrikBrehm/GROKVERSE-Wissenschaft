"""Post hoc (session 47, reading fixed in JOURNAL before this code ran): is the lock-in clock just the memorization clock?
Per cell (batch size, lr): t_half from the pilots (full batch: EXP-100 switch pi(25)/pi(50); 1024: EXP-108; 256: EXP-107; 64: EXP-108;
lr 2e-3: EXP-109) and t_mem(q) = first logged step with train accuracy >= q in the pure F/G runs (mean over F and G).
Reading: 'gekoppelt' if max/min of t_half / t_mem(0.5) over all cells <= 1.5; 'nicht gekoppelt' if > 2.5; else 'unklar'.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-109-lockin-lr-pilot/memclock_posthoc_s47.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
N = 3831
SEEDS1 = range(3700, 3708)
SEEDS2 = (3700, 3701)


def th(pi: dict[int, float]) -> float:
    ts, ms = [0] + sorted(pi), [0.0] + [pi[t] for t in sorted(pi)]
    for i in range(1, len(ts)):
        if ms[i - 1] < 0.5 <= ms[i]:
            return ts[i - 1] + (0.5 - ms[i - 1]) * (ts[i] - ts[i - 1]) / (ms[i] - ms[i - 1])
    return float("nan")


def t_mem(d: Path, q: float) -> float:
    dn = json.loads((d / "result.json").read_text(encoding="utf-8"))["dense"]
    for s, a in zip(dn["train_steps"], dn["train_acc"]):
        if a >= q:
            return float(s)
    return float("nan")


def pure(root: Path, s: int, x: str, sfx: str) -> Path:
    hits = sorted(root.glob(f"EXP-018_baseline_seed{s}_thr*_seed{s}_{x}{sfx}"))
    assert len(hits) == 1, (root, s, x, sfx, hits)
    return hits[0]


def main() -> None:
    sw = {r["seed"]: r for r in json.loads((EXP / "EXP-100-set-vs-order/switch_summary.json").read_text(encoding="utf-8"))["rows"]}
    r107 = {r["seed"]: r for r in json.loads((EXP / "EXP-107-lockin-epochs/summary.json").read_text(encoding="utf-8"))["rows"]}
    r108 = {r["seed"]: r for r in json.loads((EXP / "EXP-108-lockin-batch-series/summary.json").read_text(encoding="utf-8"))["rows"]}
    r109 = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))["rows"]
    cells = {}
    for s in SEEDS1:
        rows = {
            ("lr1e-3", "full"): (th({25: sw[s]["pi_fb_25"], 50: sw[s]["pi_fb_50"]}), EXP / "EXP-100-set-vs-order/raw", "_devcuda"),
            ("lr1e-3", "1024"): (r108[s]["th_1024"], EXP / "EXP-108-lockin-batch-series/raw", "_bs1024_devcuda"),
            ("lr1e-3", "256"): (th({t: r107[s][f"pi_{t}"] for t in (100, 200, 375, 750, 1500)}), EXP / "EXP-100-set-vs-order/raw", "_bs256_devcuda"),
            ("lr1e-3", "64"): (r108[s]["th_64"], EXP / "EXP-100-set-vs-order/raw", "_bs64_devcuda"),
        }
        if s in SEEDS2:
            for b, sfx in (("full", "_lr0.002_devcuda"), ("1024", "_bs1024_lr0.002_devcuda"), ("256", "_bs256_lr0.002_devcuda"), ("64", "_bs64_lr0.002_devcuda")):
                rows[("lr2e-3", b)] = (r109[str(s)]["0" if b == "full" else b]["t_half"], HERE / "raw", sfx)
        for key, (t, root, sfx) in rows.items():
            m5 = np.mean([t_mem(pure(root, s, x, sfx), 0.5) for x in "FG"])
            m9 = np.mean([t_mem(pure(root, s, x, sfx), 0.9) for x in "FG"])
            cells.setdefault(key, []).append((s, t, m5, m9))
    out = {}
    for (lr, b), v in cells.items():
        a = np.array([x[1:] for x in v])
        out[f"{lr} {b}"] = {"n": len(v), "t_half": float(a[:, 0].mean()), "t_mem50": float(a[:, 1].mean()), "t_mem90": float(a[:, 2].mean()),
                            "ratio_th_mem50": float(np.mean(a[:, 0] / a[:, 1])), "ratio_th_mem90": float(np.mean(a[:, 0] / a[:, 2]))}
    r = [c["ratio_th_mem50"] for c in out.values()]
    spread = max(r) / min(r)
    reading = "gekoppelt" if spread <= 1.5 else "nicht gekoppelt" if spread > 2.5 else "unklar"
    x = np.log([N / int(k.split()[1]) for k in out if k.startswith("lr1e-3") and not k.endswith("full")])
    y = np.log([c["t_mem50"] for k, c in out.items() if k.startswith("lr1e-3") and not k.endswith("full")])
    res = {"cells": out, "ratio_spread_max_over_min": spread, "reading": reading,
           "alpha_mem50_lr1e-3_minibatch": float(np.polyfit(x, y, 1)[0])}
    (HERE / "memclock_posthoc_s47.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
