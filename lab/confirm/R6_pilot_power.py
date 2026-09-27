"""R6 pilot values and power (session 32, Codex MAJOR 3): per-seed C(25) and C(25) - C(50) of the stored N28 block and C(25) of P3,
computed EXACTLY as confirm_r6 does (b = min(gen, 2000) counted from step 0, common cap for every arm), and the power of the full R6
decision rule (p = max(sign-flip, exact sign), Holm over H1/H2 at 0.05) by resampling N28 SEEDS (both quantities of a seed together).
The flip test is Monte Carlo here (2000 flips per replicate; confirm_r6 enumerates exactly): an approximation, reported as such.
Seen data only; no training.   python lab/confirm/R6_pilot_power.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
CAP, REPS, FLIPS, SEED = 2000, 2000, 2000, 32


def b_of(d: Path) -> float:
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    assert r["status"] == "completed", d.name
    g = (r.get("events") or {}).get("generalization_step")
    return float(min(g, CAP)) if g is not None else float(CAP)


def block(raw: Path, tag: str, ts: tuple[int, ...]) -> dict[int, dict]:
    pat = re.compile(rf"seed(\d+)_thr1_{tag}_seed\d+_w0_(A|B)(?:_to_{tag}_seed\d+_w0_(A|B)_at(\d+)(_rom)?)?_devcuda$")
    out: dict[int, dict] = {}
    for d in raw.iterdir():
        m = pat.search(d.name)
        if not m or m.group(5):
            continue
        s, a, b, t = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        if b is not None and int(t) not in ts:
            continue
        out.setdefault(s, {})[a if b is None else (a + b, int(t))] = b_of(d)
    return out


def cost(b: dict, t: int) -> float:
    return ((math.log2(b[("AB", t)]) - math.log2(b["B"])) + (math.log2(b[("BA", t)]) - math.log2(b["A"]))) / 2


def p_rule(x: np.ndarray, rng: np.random.Generator) -> float:
    nz = x[np.abs(x) > 1e-9]
    k, n = int((nz > 0).sum()), len(nz)
    ps = sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0
    fl = rng.choice(np.array([-1.0, 1.0]), size=(FLIPS, len(x))) @ x
    pf = float((fl >= x.sum() - 1e-12).sum() + 1) / (FLIPS + 1)
    return max(ps, pf)


def main() -> None:
    n28 = block(LAB / "confirm/n28_raw", "n28", (25, 50))
    p3 = block(LAB / "confirm/p3_raw", "p3", (25,))
    H1 = np.array([cost(b, 25) for b in n28.values()])
    H2 = np.array([cost(b, 25) - cost(b, 50) for b in n28.values()])
    P3 = np.array([cost(b, 25) for b in p3.values()])
    rng = np.random.default_rng(SEED)
    power = {}
    for n in (10, 15, 20, 25):
        ok = 0
        for _ in range(REPS):
            i = rng.integers(0, len(H1), n)
            p1, p2 = p_rule(H1[i], rng), p_rule(H2[i], rng)
            lo, hi = sorted((p1, p2))
            ok += (2 * lo < 0.05) and (hi < 0.05)          # Holm over 2: both rejected
        power[n] = ok / REPS
    out = {"note": "seen data; hypothesis selected on N28, so the effect is optimistic (winner's curse)", "cap": CAP,
           "N28": {"n": len(H1), "H1_mean": float(H1.mean()), "H1_sd": float(H1.std(ddof=1)), "H1_pos": int((H1 > 1e-9).sum()),
                   "H2_mean": float(H2.mean()), "H2_sd": float(H2.std(ddof=1)), "H2_pos": int((H2 > 1e-9).sum()),
                   "H1": H1.round(4).tolist(), "H2": H2.round(4).tolist()},
           "P3_w0_C25": {"n": len(P3), "mean": float(P3.mean()), "sd": float(P3.std(ddof=1)), "pos": int((P3 > 1e-9).sum())},
           "power_both_rejected": power, "reps": REPS, "flips_mc": FLIPS, "rng_seed": SEED}
    (LAB / "confirm/R6_pilot_power.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "N28"}, indent=1))
    print({k: v for k, v in out["N28"].items() if k not in ("H1", "H2")})


if __name__ == "__main__":
    main()
