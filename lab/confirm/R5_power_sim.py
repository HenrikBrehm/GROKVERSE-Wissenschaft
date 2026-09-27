"""R5 sample size by simulating the COMPLETE decision rule (Codex design review s30, point 4). Session 30, numpy only, UNTESTED on pilot data.

Input: pilot restricted times per seed and arm (E, D, R), capped at CAP; censored runs enter as (last evaluated step, False).
Resampling model: seeds are drawn with replacement from the pilot (joint E/D/R rows keep their within-seed dependence); a shift
parameter `speedup` optionally multiplies the E times of the pilot by 2**(-extra) to probe smaller or larger true effects.
Decision rule per contrast X in {R, D} (as in R5_REGISTRATION_DRAFT.md after the Codex review):
  L_i = log2(min(t_X, CAP) / min(t_E, CAP));  p_L = one-sided sign-flip permutation p of mean L (Monte Carlo);
  p_sign = exact one-sided binomial p over the seeds whose order is determined under censoring;
  p_j = max(p_L, p_sign); Holm over the two contrasts at ALPHA. Power = share of simulated studies with both / each contrast confirmed.
Pilot sources (only after EXP-018 has run): EXP-018 summary_cuda.json rows (E, D, R) or, for E vs R only, EXP041_posthoc_speed.json.

  python lab/confirm/R5_power_sim.py --pilot lab/experiments/EXP-018-split-speed/summary_cuda.json --n 20 30 40 60
  python lab/confirm/R5_power_sim.py --selftest
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

CAP, ALPHA, N_FLIP, N_SIM = 8000, 0.05, 2000, 1000


def order(te: tuple[int, bool], tx: tuple[int, bool]) -> int | None:
    """+1 if E crossed strictly before X, -1 if X before E, None if tied or undetermined under censoring (EXP-018 order_sign)."""
    (ge, oe), (gx, ox) = te, tx
    if oe and ox:
        return None if ge == gx else (1 if ge < gx else -1)
    if oe and ge < gx:
        return 1
    if ox and gx < ge:
        return -1
    return None


def p_flip(L: np.ndarray, rng: np.random.Generator) -> float:
    signs = rng.choice((-1.0, 1.0), size=(N_FLIP, len(L)))
    return float(((signs * L).mean(axis=1) >= L.mean() - 1e-12).mean())


def p_binom(k: int, n: int) -> float:
    return 1.0 if n == 0 else sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n


def contrast_p(rows: list[dict], x: str, rng: np.random.Generator) -> float:
    L = np.array([math.log2(min(r[x][0], CAP) / min(r["E"][0], CAP)) for r in rows])
    det = [o for o in (order(r["E"], r[x]) for r in rows) if o is not None]
    return max(p_flip(L, rng), p_binom(sum(1 for o in det if o > 0), len(det)))


def holm_both(p: dict[str, float]) -> dict[str, bool]:
    ks = sorted(p, key=p.get)
    ok, out = True, {}
    for i, k in enumerate(ks):
        ok = ok and p[k] * (len(ks) - i) < ALPHA
        out[k] = ok
    return out


def shift_e(row: dict, extra: float) -> dict:
    ge, oe = row["E"]
    return {**row, "E": (max(25, int(round(ge * 2 ** (-extra) / 25)) * 25), oe) if oe else (ge, oe)}


def power(pilot: list[dict], n: int, extra: float, rng: np.random.Generator) -> dict[str, float]:
    hits = {"R": 0, "D": 0, "both": 0}
    for _ in range(N_SIM):
        rows = [shift_e(pilot[i], extra) for i in rng.integers(0, len(pilot), n)]
        dec = holm_both({x: contrast_p(rows, x, rng) for x in ("R", "D")})
        hits["R"] += dec["R"]
        hits["D"] += dec["D"]
        hits["both"] += dec["R"] and dec["D"]
    return {k: v / N_SIM for k, v in hits.items()}


def load_pilot(path: Path) -> list[dict]:
    """EXP-018 summary rows: gen_<arm>_primary = [step, observed]."""
    rows = json.loads(path.read_text(encoding="utf-8"))["rows"]
    return [{a: tuple(r[f"gen_{a}_primary"]) for a in "EDR"} for r in rows if r.get("valid")]


def selftest() -> None:
    rng = np.random.default_rng(0)
    assert order((700, True), (8000, False)) == 1 and order((900, True), (700, True)) == -1 and order((8000, False), (8000, False)) is None
    assert abs(p_binom(9, 9) - 1 / 512) < 1e-12 and p_binom(0, 0) == 1.0
    assert holm_both({"R": 0.001, "D": 0.04}) == {"R": True, "D": True} and holm_both({"R": 0.03, "D": 0.04})["R"] is False
    fast = [{"E": (700 + 25 * i, True), "D": (4000 + 100 * i, True), "R": (8000, False)} for i in range(10)]
    assert power(fast, 20, 0.0, rng)["both"] > 0.95
    null = [{"E": (3000 + 100 * i, True), "D": (3000 + 100 * ((i * 7) % 10), True), "R": (3000 + 100 * ((i * 3) % 10), True)} for i in range(10)]
    assert power(null, 20, 0.0, rng)["both"] < 0.1
    print("[R5_power_sim] selftest ok")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot")
    ap.add_argument("--n", type=int, nargs="+", default=[20, 30, 40, 60])
    ap.add_argument("--extra", type=float, nargs="+", default=[0.0], help="additional log2 speed-up of E over the pilot (negative = smaller effect)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    pilot = load_pilot(Path(a.pilot))
    rng = np.random.default_rng(5)
    out = {f"n{n}_extra{e:+g}": power(pilot, n, e, rng) for n in a.n for e in a.extra}
    print(json.dumps({"pilot_seeds": len(pilot), **out}, indent=1))


if __name__ == "__main__":
    main()
