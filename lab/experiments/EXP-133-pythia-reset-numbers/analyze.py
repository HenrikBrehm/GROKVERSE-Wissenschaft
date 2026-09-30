"""EXP-133 analysis (session 62, written before any EXP-133 run; readings in README.md, same rules as EXP-127).

Runs EXP-127's analyze.py (loaded by file path, unchanged) on this folder's raw runs and writes the summary HERE (not into
EXP-127). Adds descriptive top-5 frequencies of the residual change U per run and the paired EXP-127 values.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-133-pythia-reset-numbers/analyze.py [--root DIR] [--steps N]
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
_spec = importlib.util.spec_from_file_location("exp127_analyze", LAB / "experiments/EXP-127-pretrained-lm/analyze.py")
a127 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a127)                  # by path: several experiments have a module called "analyze"
READING_DE = {"K2 haelt beim Nachtrainieren": "gesteuert (neue Zahlzeilen)", "bricht": "nicht gesteuert (Rumpf)"}


def main() -> None:
    if "--root" not in sys.argv:
        sys.argv += ["--root", str(HERE / "raw")]
    steps = int(sys.argv[sys.argv.index("--steps") + 1]) if "--steps" in sys.argv else 4000
    a127.HERE = HERE                            # EXP-127's main writes summary_steps<N>.json into its HERE
    a127.main()
    path = HERE / f"summary_steps{steps}.json"
    out = json.loads(path.read_text(encoding="utf-8"))
    root = Path(out["root"])
    tops = {}
    for s in a127.SEEDS:
        for arm in "FG":
            r = a127.load(root, s, arm, steps)
            if isinstance(r, str):
                continue
            u = a127.power(a127.residual(r["in"][-1], r["in"][0]))
            tops[f"{s}{arm}"] = [int(k) + 1 for k in np.argsort(u)[::-1][:5]]
    out["reading_exp133"] = READING_DE.get(out["reading"], out["reading"])
    out["top5_residual_in"] = tops
    ref = LAB / "experiments/EXP-127-pretrained-lm/summary_steps4000.json"
    if ref.exists():
        out["exp127_paired_dpow_update_in"] = [r["dpow_update_in"] for r in json.loads(ref.read_text(encoding="utf-8"))["rows"]]
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("reading_exp133", "top5_residual_in")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
