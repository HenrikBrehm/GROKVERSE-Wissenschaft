"""Synthetic checks of analyze.py (Codex review): early/late switch, all-H, all-F, missing cell. Run via guarded_run.py."""
import contextlib
import io
import json
import tempfile
from pathlib import Path

import analyze as A

T = [16, 20, 25, 47, 49]
H = [A.fold(57 * t) for t in T]
OTHER = [1, 2, 3, 4, 5]


def spec(top):
    s = [1.0] * 56
    for i, k in enumerate(top):
        s[k - 1] = 10 - i
    return s


def make(tmp, fn, drop=None):
    for ts in A.TS:
        for s in A.SEEDS:
            if drop == (ts, s):
                continue
            d = tmp / "raw" / A.run_id(ts, s)
            d.mkdir(parents=True)
            r = {"complete": True, "args": {"steps": 5000, "alpha": 3.0, "switch_step": ts, "alpha_after": 0.0,
                                            "arm": "F", "init_seed": None},
                 "targets": T, "spectra": {"5000": {"weighted": spec(fn(ts, s)), "weighted_lin": spec(fn(ts, s))}},
                 "final_test_acc": 1.0, "gen_step_test95": 1400}
            (d / "result.json").write_text(json.dumps(r))


def verdict(fn, drop=None):
    tmp = Path(tempfile.mkdtemp())
    make(tmp, fn, drop)
    A.HERE = tmp
    with contextlib.redirect_stdout(io.StringIO()):
        A.main()
    return json.loads((tmp / "summary.json").read_text())


early = lambda ts, s: T if ts < 0 or ts >= 250 else H[:3] + OTHER[:2]
late = lambda ts, s: T if ts < 0 else H[:3] + OTHER[:2]
o = verdict(early); assert o["verdict"] == "Uhr ablesbar" and o["commit_interval"] == [50, 250], o["verdict"]
o = verdict(late); assert o["verdict"] == "Uhr ablesbar" and o["commit_interval"] == [2500, -1]
assert verdict(lambda ts, s: H[:3] + OTHER[:2])["verdict"].startswith("Uhr nicht ablesbar")
assert verdict(lambda ts, s: T)["verdict"].startswith("Uhr nicht ablesbar")
assert verdict(early, drop=(50, 12))["verdict"].startswith("nicht auswertbar")
print("all 5 synthetic checks passed")
