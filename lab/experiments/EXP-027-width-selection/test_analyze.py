"""Synthetic checks of EXP-027 analyze.py (Codex review): trend, no trend, fidelity gate, provenance. Via guarded_run.py."""
import contextlib
import importlib.util
import io
import json
import tempfile
from pathlib import Path

import numpy as np

spec_ = importlib.util.spec_from_file_location("a27", Path(__file__).resolve().parent / "analyze.py")
A = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(A)
T = [16, 20, 25, 47, 49]
H = [A.fold(57 * t) for t in T]


def make(tmp, tilt, acc=1.0, lr=1e-3):
    rng = np.random.default_rng(1)
    A.E26, A.HERE = tmp / "e26", tmp / "e27"
    for w in A.WIDTHS:
        for s in A.SEEDS:
            sp = rng.uniform(0.8, 1.2, 56)
            for k in H:
                sp[k - 1] *= 1 + tilt(w)
            args = {**A.REG, "lr": lr, "seed": s, "alpha": 3.0 if w == 512 else 0.0, "switch_step": 0 if w == 512 else -1,
                    "alpha_after": 0.0, "width": w, "split_dir": "x/EXP-016-engineered-split/splits"}
            f = A.path(w, s); f.parent.mkdir(parents=True)
            f.write_text(json.dumps({"complete": True, "args": args, "targets": T, "final_train_acc": 1.0,
                                     "final_test_acc": acc, "gen_step_test95": 1400,
                                     "spectra": {"5000": {"weighted": sp.tolist()}}}))


def run(**kw):
    tmp = Path(tempfile.mkdtemp()); make(tmp, **kw)
    with contextlib.redirect_stdout(io.StringIO()):
        A.main()
    return json.loads((A.HERE / "summary.json").read_text())


o = run(tilt=lambda w: 0.5 * np.log2(512 / w)); assert o["verdict"] == "bestätigt", o["verdict"]
o = run(tilt=lambda w: 0.0); assert o["verdict"] != "bestätigt", o["verdict"]
o = run(tilt=lambda w: 0.0, acc=0.5); assert o["verdict"].startswith("nicht auswertbar (Güte"), o["verdict"]
o = run(tilt=lambda w: 0.0, lr=3e-3); assert o["verdict"].startswith("nicht auswertbar (Raster"), o["verdict"]
print("all 4 synthetic checks passed")
