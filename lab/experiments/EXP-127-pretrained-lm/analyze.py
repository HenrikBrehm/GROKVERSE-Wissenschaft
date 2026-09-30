"""EXP-127 pilot analysis (written in session 58 BEFORE any pilot run; readings in README.md).

Per seed s (arms F, G; same pretrained start, same test set):
  Delta_pow(update, in) = P1 Delta_pow on E_in(T) - E_in(0) of the 113 number rows (primary; the pretrained rows move little),
  Delta_pow(rows, in/out), Delta_pow(update, out) (secondary), held-out accuracy, ablation contrasts C_in/C_out/C_both.
Readings: gate = held-out >= 0.5 at the end in >= 3 of 4 runs, else 'nicht auswertbar (lernt nicht)';
  'K2 haelt beim Nachtrainieren' if gate and Delta_pow(update, in) > 1 in both seeds; 'bricht' if gate and
  |Delta_pow(update, in)| <= 1 in both; else 'unklar'. Descriptive: 'genutzt' if C_both > 0.3 in all 4 runs.
Runs that are missing / not completed / non-finite are reported as such ('fehlt' / 'defekt'), never as negative.
  python lab/tools/guarded_run.py -- python lab/experiments/EXP-127-pretrained-lm/analyze.py [--root <dir>] [--steps N]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P = 113
SEEDS = (4000, 4001)


def power(W: np.ndarray) -> np.ndarray:
    sq = (np.abs(np.fft.fft(W.astype(np.float64), axis=0)) ** 2).sum(1)
    return 2.0 * sq[1:(P - 1) // 2 + 1] / P


def delta_pow(pF, pG, F, G) -> float | None:
    s = lambda pw, S: float(pw[[k - 1 for k in S]].sum())   # noqa: E731
    v = [s(pF, F), s(pF, G), s(pG, F), s(pG, G)]
    return float(np.log(v[0] / v[1]) + np.log(v[3] / v[2])) if all(np.isfinite(x) and x > 0 for x in v) else None


def load(root: Path, seed: int, arm: str, steps: int) -> dict | str:
    hits = sorted(root.glob(f"pt_seed{seed}_seed{seed}_{arm}_steps{steps}_*"))
    if not hits:
        return "fehlt"
    if len(hits) > 1:
        return "defekt (mehrere Laufordner)"
    d = hits[0]
    if not (d / "result.json").exists():
        return "fehlt"
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    if r.get("status") != "completed":
        return f"defekt ({r.get('status')})"
    try:
        si, so = np.load(d / "in_snapshots.npy"), np.load(d / "out_snapshots.npy")
    except Exception as e:  # noqa: BLE001
        return f"defekt ({e})"
    if not (np.isfinite(si).all() and np.isfinite(so).all()) or r["curve"][-1][0] != steps:
        return "defekt (nicht endlich / Schritte)"
    return {"r": r, "in": si, "out": so}


def main() -> None:
    root = Path(sys.argv[sys.argv.index("--root") + 1]) if "--root" in sys.argv else HERE / "raw"
    steps = int(sys.argv[sys.argv.index("--steps") + 1]) if "--steps" in sys.argv else 4000
    rows, status = [], {}
    for s in SEEDS:
        runs = {arm: load(root, s, arm, steps) for arm in "FG"}
        status[s] = {arm: (v if isinstance(v, str) else "ok") for arm, v in runs.items()}
        if any(isinstance(v, str) for v in runs.values()):
            continue
        F_, G_ = runs["F"]["r"]["config"]["targets"]["F"], runs["F"]["r"]["config"]["targets"]["G"]
        row = {"seed": s}
        for side in ("in", "out"):
            pF, pG = (power(runs[a][side][-1]) for a in "FG")
            uF, uG = (power(runs[a][side][-1] - runs[a][side][0]) for a in "FG")
            row[f"dpow_rows_{side}"] = delta_pow(pF, pG, F_, G_)
            row[f"dpow_update_{side}"] = delta_pow(uF, uG, F_, G_)
        for a in "FG":
            ab = runs[a]["r"]["ablation"]
            row[f"test_{a}"] = runs[a]["r"]["curve"][-1][2]
            row[f"train_{a}"] = runs[a]["r"]["curve"][-1][1]
            for k in ("C_in", "C_out", "C_both"):
                row[f"{k}_{a}"] = ab[k]
        rows.append(row)
    tests = [r[f"test_{a}"] for r in rows for a in "FG"]
    gate = len(tests) == 4 and sum(t >= 0.5 for t in tests) >= 3
    du = [r["dpow_update_in"] for r in rows]
    if len(rows) < 2 or any(v is None for v in du):
        reading = "nicht auswertbar (Läufe fehlen/defekt)"
    elif not gate:
        reading = "nicht auswertbar (lernt nicht)"
    elif all(v > 1 for v in du):
        reading = "K2 haelt beim Nachtrainieren"
    elif all(abs(v) <= 1 for v in du):
        reading = "bricht"
    else:
        reading = "unklar"
    used = len(rows) == 2 and all(r[f"C_both_{a}"] > 0.3 for r in rows for a in "FG")
    out = {"reading": reading, "gate": gate, "genutzt_beschreibend": used, "status": status, "rows": rows, "steps": steps,
           "root": str(root)}
    (HERE / f"summary_steps{steps}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
