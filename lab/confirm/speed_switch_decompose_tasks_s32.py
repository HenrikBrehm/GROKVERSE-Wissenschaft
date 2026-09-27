"""Session 32 (2026-09-27), POST HOC on EXP-044 (add 97, mul 113; 10 seeds; F->G), no training. Same decomposition as
speed_switch_decompose_s32.py (gen = mem + gap; delay of F->G@t against G only, runs with all four events observed).
Stated before looking: at t = 25 the gap carries more than half of the delay in both tasks.  python lab/confirm/speed_switch_decompose_tasks_s32.py
"""
import json
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
RAW = LAB / "experiments/EXP-044-generalize-lockin/raw"
PAT = re.compile(r"_seed(\d+)_thr1_(add97|mul113)_seed\d+_train_(F|G)(?:_to_\w+?_seed\d+_train_G_at(\d+))?_(?:add97|mul113)_devcuda$")


def main() -> None:
    R: dict = {}
    for d in RAW.iterdir():
        m = PAT.search(d.name)
        s, task, arm, t = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        tr = json.loads((d / "result.json").read_text(encoding="utf-8"))["transitions"]["primary"]
        R.setdefault(task, {}).setdefault(s, {})[arm if t is None else int(t)] = (tr["memorization"]["first_crossing_step"], tr["generalization"]["first_crossing_step"])
    out = {}
    for task, ss in sorted(R.items()):
        for t in (25, 50, 150):
            dm, dg = [], []
            for v in ss.values():
                (m1, g1), (m0, g0) = v[t], v["G"]
                if None in (m1, g1, m0, g0):
                    continue
                dm.append(m1 - m0)
                dg.append((g1 - m1) - (g0 - m0))
            dm, dg = np.array(dm, float), np.array(dg, float)
            tot = float((dm + dg).mean()) if len(dm) else float("nan")
            out[f"{task}_t{t}"] = {"pairs": len(dm), "delta_mem": float(dm.mean()) if len(dm) else None,
                                   "delta_gap": float(dg.mean()) if len(dg) else None, "delta_gen": tot,
                                   "gap_share": float(dg.mean() / tot) if len(dm) and tot else None}
    (LAB / "confirm/speed_switch_decompose_tasks_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
