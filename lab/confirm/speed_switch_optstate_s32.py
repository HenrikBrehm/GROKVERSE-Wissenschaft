"""Session 32 (2026-09-27), POST HOC (skeptic point 3): does Adam's state carry the switch cost at 25?
EXP-058 (seeds 400-409, EXP-056 splits, GPU): switch at 25 plain, 'rom' (first moment zeroed), 'romoments' (first and second moment
zeroed), 'ro' (whole optimizer reset); destination-only runs from EXP-056 omega 0 (same splits, test set, init; checked).
C as in R6 (cap 2000 from step 0). Stated before looking: under a representation account C(25) stays > 0 (majority of seeds) in every
reset arm; if the optimizer state carried the cost, 'romoments' and 'ro' would bring C(25) to ~0.
  python lab/confirm/speed_switch_optstate_s32.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
DIRS = [LAB / "experiments/EXP-058-optim-part/raw", LAB / "experiments/EXP-056-overlap-persistence/raw"]
PAT = re.compile(r"seed(\d+)_thr1_seed\d+_w0_(A|B)(?:_to_seed\d+_w0_(A|B)_at25(_\w+)?)?_devcuda$")


def main() -> None:
    lb: dict = {}
    src: dict = {}
    for root in DIRS:
        for d in root.iterdir():
            m = PAT.search(d.name)
            if not m:
                continue
            s, a, b, v = int(m.group(1)), m.group(2), m.group(3), (m.group(4) or "_plain").lstrip("_")
            key = a if b is None else (a + b, v)
            if key in lb.get(s, {}):              # EXP-056 also has a plain @25 arm; keep EXP-058's (first dir) and note it
                continue
            r = json.loads((d / "result.json").read_text(encoding="utf-8"))
            g = (r.get("events") or {}).get("generalization_step")
            lb.setdefault(s, {})[key] = (math.log2(min(g, 2000) if g is not None else 2000), r["test_hash"], r["init_checksum_shared"])
            src.setdefault(s, {})[key] = root.parent.name
    for s, v in lb.items():
        assert len({x[1] for x in v.values()}) == 1 and len({x[2] for x in v.values()}) == 1, s
    out = {}
    for arm in ("plain", "rom", "romoments", "ro"):
        c = np.array([((v[("AB", arm)][0] - v["B"][0]) + (v[("BA", arm)][0] - v["A"][0])) / 2 for v in lb.values()])
        out[arm] = {"mean": float(c.mean()), "pos": int((c > 1e-9).sum()), "neg": int((c < -1e-9).sum()), "n": len(c)}
    out["prediction_representation_account"] = all(out[a]["pos"] > out[a]["n"] / 2 for a in ("rom", "romoments", "ro"))
    (LAB / "confirm/speed_switch_optstate_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
