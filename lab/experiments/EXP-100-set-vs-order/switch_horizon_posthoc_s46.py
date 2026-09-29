"""EXP-100 switch part, POST HOC (session 46, after switch_analyze.py was read): is the missing lock-in under minibatch a
minibatch effect or a horizon effect? switch_analyze.py reads fb 2000 steps after the switch but iid256 30 000 steps after it.
Here pi(t) for iid256 is recomputed from the stored W_E snapshots at the same ABSOLUTE step h in the switch runs and the pure
runs (h = 2000, 2500, 5000, 10000, 20000, 30000; at h = 2000 the switch runs had 1975 / 1950 steps after the switch, close to
the fb reading). Same pi and loader as switch_analyze.py. Descriptive, 8 pilot seeds, not a registered reading.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-100-set-vs-order/switch_horizon_posthoc_s46.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
sys.path.insert(0, str(HERE))
import analyze as A  # noqa: E402
import design as D  # noqa: E402
import switch_analyze as S  # noqa: E402
from result_loader import Expect, find_run, load_run  # noqa: E402

H = (2000, 2500, 5000, 10000, 20000, 30000)


def snaps_pure(s: int, x: str) -> dict:
    L = load_run(find_run(HERE / "raw", f"EXP-018_baseline_seed{s}_thr*_seed{s}_{x}{A.suffix('iid256')}{A.SUF}"),
                 Expect(seed=s, device="cuda", max_steps=30000, split_file=A.SPL / f"seed{s}_{x}.npy",
                        test_file=A.SPL / f"seed{s}_test.npy", config={"p": 113, "task": "add"}, snapshots_at=H))
    assert L.status == "ok", L.reason
    return {h: A._a43.group_power(L.snapshot(h), "add", 113)[0] for h in H}


def snaps_switch(s: int, a: str, b: str, t: int) -> dict:
    total = 30000 + t
    L = load_run(find_run(HERE / "raw_switch", f"EXP-020_baseline_seed{s}_thr*_seed{s}_{a}_to_seed{s}_{b}_at{t}{A.suffix('iid256')}{A.SUF}"),
                 Expect(seed=s, device="cuda", max_steps=total, split_file=A.SPL / f"seed{s}_{a}.npy",
                        test_file=A.SPL / f"seed{s}_test.npy", switch_file=A.SPL / f"seed{s}_{b}.npy",
                        config={"p": 113, "task": "add"}, snapshots_at=H))
    assert L.status == "ok", L.reason
    return {h: A._a43.group_power(L.snapshot(h), "add", 113)[0] for h in H}


def main() -> None:
    res = {f"{t}@{h}": [] for t in D.SWITCH_T for h in H}
    sep = {h: [] for h in H}
    for s in D.SEEDS:
        T = json.loads((A.SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        F, G = T["F"], T["G"]
        pF, pG = snaps_pure(s, "F"), snaps_pure(s, "G")
        sw = {(a, b, t): snaps_switch(s, a, b, t) for t in D.SWITCH_T for a, b in (("F", "G"), ("G", "F"))}
        for h in H:
            LF, LG = S.logratio(pF[h], F, G), S.logratio(pG[h], F, G)
            sep[h].append(LF - LG)
            for t in D.SWITCH_T:
                res[f"{t}@{h}"].append(S.pi_pair(LF, LG, S.logratio(sw[("F", "G", t)][h], F, G), S.logratio(sw[("G", "F", t)][h], F, G)))
    out = {"note": "post hoc, descriptive (8 pilot seeds)", "L_F_minus_L_G_mean": {h: float(np.mean(v)) for h, v in sep.items()},
           "pi": {k: {"mean": float(np.mean(v)), "ci95": A.boot_ci(np.array(v))} for k, v in res.items()},
           "d50_minus_25": {h: {"mean": float(np.mean(np.array(res[f"50@{h}"]) - np.array(res[f"25@{h}"]))),
                                "ci95": A.boot_ci(np.array(res[f"50@{h}"]) - np.array(res[f"25@{h}"]))} for h in H}}
    (HERE / "switch_horizon_posthoc_s46.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
