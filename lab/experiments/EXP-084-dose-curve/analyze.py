"""EXP-084 analysis (session 31, EXPLORATION, reading rules fixed before any run; see README).

Per unit u and arm: trainer event (first test >= 0.95, `events.generalization_step`), censored at 4000 if absent; bounded time
b = min(event, 4000). Runs are loaded through the common loader (seed, device, budget, split and test hash, finite spectrum at 250;
runs stop 100 steps after the event, so only >= 250 completed steps are required).
Reading (descriptive, per unit, arms ordered R < e0.5 < ... < e32 as increasing concentration):
  monotone   Spearman(concentration rank, log2 b) <= -0.8 in >= 8/10 units
  reversal   b(e32) > b(e8) in >= 7/10 units (and median log2(b(e32) / b(e8)) >= 0.25)
  saturation |median log2(b(e32) / b(e8))| <= 0.25
Several readings can hold at once (e.g. monotone up to e8 and saturating). Also: W_E power share on the targets at step 250,
final test accuracy, M0 target share per arm (from splits/u{u}.json).
  python lab/experiments/EXP-084-dose-curve/analyze.py [--selftest]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from result_loader import Expect, load_run  # noqa: E402

ARMS = ("R", "e0.5", "e1", "e2", "e4", "e8", "e16", "e32")
SEED0, N_UNITS, CAP = 2780, 10, 4000


def run_dir(u: int, arm: str) -> Path:
    return HERE / "raw" / f"EXP-018_baseline_seed{SEED0 + u}_thr1_u{u}_{arm}_devcuda"


def load(u: int, arm: str, tg: list[int]) -> dict | str:
    L = load_run(run_dir(u, arm), Expect(seed=SEED0 + u, device="cuda", max_steps=CAP, min_steps_completed=250,
                                         split_file=HERE / "splits" / f"u{u}_{arm}.npy", test_file=HERE / "splits" / f"u{u}_test.npy",
                                         config={"p": 113, "task": "add", "arch": "transformer"}, at=(250,)))
    if L.status != "ok":
        return f"u{u}:{arm}: {L.status}: {L.reason}"
    g = (L.res.get("events") or {}).get("generalization_step")
    if g is None and L.res["steps_completed"] < CAP:
        return f"u{u}:{arm}: stopped at {L.res['steps_completed']} without an event"
    pw = L.spectrum(250)
    return {"b": min(g, CAP) if g is not None else CAP, "observed": g is not None,
            "we_share_250": float(pw[[k - 1 for k in tg]].sum() / pw.sum()), "test_final": (L.res.get("final_acc") or {}).get("test")}


def avg_rank(v: np.ndarray) -> np.ndarray:
    """Ranks 0..n-1 with ties sharing their average rank (no scipy in the global Python)."""
    v = np.asarray(v, dtype=float)
    r = np.empty(len(v))
    for x in np.unique(v):
        idx = np.flatnonzero(v == x)
        r[idx] = np.mean(np.flatnonzero(np.sort(v) == x))
    return r


def spear(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = avg_rank(x), avg_rank(y)
    return float(np.corrcoef(rx, ry)[0, 1]) if np.std(ry) > 0 else 0.0


def reading(units: list[dict[str, float]]) -> dict:
    """units: per unit {arm: bounded time}."""
    rho = [spear(np.arange(len(ARMS)), np.log2([u[a] for a in ARMS])) for u in units]
    r32 = np.array([math.log2(u["e32"] / u["e8"]) for u in units])
    med = float(np.median(r32))
    out = {"spearman_per_unit": rho, "n_monotone": int(sum(r <= -0.8 for r in rho)), "log2_e32_over_e8_median": med,
           "n_e32_slower_than_e8": int((r32 > 0).sum())}
    out["monotone"] = out["n_monotone"] >= 8
    out["reversal"] = out["n_e32_slower_than_e8"] >= 7 and med >= 0.25
    out["saturation"] = abs(med) <= 0.25
    return out


def main() -> None:
    units, rows, bad = [], [], []
    for u in range(N_UNITS):
        meta = json.loads((HERE / "splits" / f"u{u}.json").read_text(encoding="utf-8"))
        r = {a: load(u, a, meta["targets"]) for a in ARMS}
        errs = [v for v in r.values() if isinstance(v, str)]
        if errs:
            bad += errs
            continue
        units.append({a: float(r[a]["b"]) for a in ARMS})
        rows.append({"unit": u, **{a: {**r[a], "m0_target_share": meta["arms"][a]["m0_target_share"]} for a in ARMS}})
    out = {"n_units_ok": len(units), "broken": bad}
    if len(units) == N_UNITS:
        out["reading"] = reading(units)
        out["per_arm"] = {a: {"median_b": float(np.median([u[a] for u in units])),
                              "observed": sum(1 for r in rows if r[a]["observed"]),
                              "we_share_250_mean": float(np.mean([r[a]["we_share_250"] for r in rows])),
                              "m0_target_share_mean": float(np.mean([r[a]["m0_target_share"] for r in rows]))} for a in ARMS}
    else:
        out["reading"] = "nicht auswertbar (fehlende oder defekte Läufe)"
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    mono = [{a: 3000 / (1 + i) for i, a in enumerate(ARMS)} for _ in range(10)]
    r = reading(mono)
    assert r["monotone"] and not r["reversal"] and not r["saturation"], r
    sat = [{**u, "e16": u["e8"], "e32": u["e8"]} for u in mono]
    r = reading(sat)
    assert r["saturation"] and not r["reversal"] and r["monotone"], r            # both readings may hold (rho ~ -0.98 with ties)
    rev = [{**u, "e32": 2 * u["e8"]} for u in mono]
    r = reading(rev)
    assert r["reversal"] and not r["saturation"], r
    assert list(avg_rank(np.array([5.0, 1.0, 5.0, 3.0]))) == [2.5, 0.0, 2.5, 1.0]
    flat = [{a: 2000.0 for a in ARMS} for _ in range(10)]
    r = reading(flat)
    assert not r["monotone"] and r["saturation"] and not r["reversal"], r
    assert run_dir(6, "e0.5").name == "EXP-018_baseline_seed2786_thr1_u6_e0.5_devcuda"
    print("[EXP-084 analyze] selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv[1:] else main()
