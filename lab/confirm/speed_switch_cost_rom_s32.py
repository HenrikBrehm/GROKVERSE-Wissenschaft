"""Session 32 (2026-09-27), POST HOC descriptive (archived after the source check): effect of zeroing Adam's first moment at the
switch (N28 '_rom' arms, --reset-optim-part m) on the switch cost, with the R6 definition (b = min(gen, 2000) from step 0).
Reported descriptively only (JOURNAL session 32, cycle 5 first used run-own horizons).  python lab/confirm/speed_switch_cost_rom_s32.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
PAT = re.compile(r"seed(\d+)_thr1_n28_seed\d+_w0_(A|B)(?:_to_n28_seed\d+_w0_(A|B)_at(\d+)(_rom)?)?_devcuda$")


def main() -> None:
    lb: dict = {}
    for d in (LAB / "confirm/n28_raw").iterdir():
        m = PAT.search(d.name)
        s, a, b, t, rom = int(m.group(1)), m.group(2), m.group(3), m.group(4), m.group(5)
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        g = (r.get("events") or {}).get("generalization_step")
        lb.setdefault(s, {})[a if b is None else (a + b, t + ("r" if rom else ""))] = math.log2(min(g, 2000) if g is not None else 2000)
    C = {k: np.array([((v[("AB", k)] - v["B"]) + (v[("BA", k)] - v["A"])) / 2 for v in lb.values()]) for k in ("25", "25r", "35r", "50")}
    d = C["25r"] - C["25"]
    out = {k: {"mean": float(v.mean()), "pos": int((v > 1e-9).sum()), "neg": int((v < -1e-9).sum())} for k, v in C.items()}
    out["rom25_minus_25"] = {"mean": float(d.mean()), "median": float(np.median(d)), "rom_earlier": int((d < -1e-9).sum()), "rom_later": int((d > 1e-9).sum())}
    (LAB / "confirm/speed_switch_cost_rom_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
