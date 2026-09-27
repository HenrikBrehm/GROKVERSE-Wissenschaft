#!/usr/bin/env python3
"""EXP-078 trainer: lab/paper/repro/train.py with the two-layer model (session 26, UNTESTED).

Same CLI as repro/train.py (split, steps, device, spectra every 250 steps and at the end, optional model saving); only the model factory is
replaced by TwoLayerTransformer (two_layer.py). Everything else (seed order, data, AdamW, loss, spectra) is the lean trainer's code.
Switch and reset options are rejected (EXP-078 has no switch). result.json gets "model": "EXP-078 TwoLayerTransformer".

  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-078-two-layer-steering/train2l.py --seed S --split-file F.npy --steps 10000 --device cuda --out DIR
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "paper" / "repro"))
import train as lean  # noqa: E402  (lab/paper/repro/train.py)
from two_layer import TwoLayerTransformer  # noqa: E402

if __name__ == "__main__":
    if any(x in sys.argv for x in ("--switch-split-file", "--switch-step", "--reset-at-switch", "--compare-to")):
        raise SystemExit("EXP-078: no switch, reset or comparison options")
    lean.build_model = TwoLayerTransformer        # the only change: model factory used inside lean.train()
    lean.main()
    out = Path(sys.argv[sys.argv.index("--out") + 1]) / "result.json"
    res = json.loads(out.read_text(encoding="utf-8"))
    res["model"] = "EXP-078 TwoLayerTransformer (lab/experiments/EXP-078-two-layer-steering/two_layer.py)"
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
