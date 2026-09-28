"""EXP-081 (pilot, exploration): which optimizer clock fixes the frequency choice? Definition and readings: README.md,
Nachtrag a + d (fixed before any EXP-081 run). Run under guarded_run.py with the global python.

pi as EXP-056/059 (share of the A choice in the log energy ratio, mean of both switch directions), each against the pure
A/B runs of the SAME beta cell. Validity per seed and cell: all needed runs ok through the shared loader, m reset recorded,
L(A) - L(B) >= 2 (else the cell is 'nicht auswertbar' for that seed).

Part A (N38, momentum tail): drop(cell) = pi_normal(25) - pi_m(25) per seed. Primary: c = drop(b1_095) - drop(b1_08), paired,
one-sided exact sign test (zeros dropped). Reading: 'N38 gestuetzt' if p < 0.05 and the cell means are ordered
drop(0.8) < drop(0.9) < drop(0.95); 'gegen N38' if the median of c <= 0; else 'unklar'. Fewer than 8 seeds valid in all
three cells -> 'nicht auswertbar'. Descriptive: tail_est = drop / slope, slope = (pi_n30 - pi_n20) / 10 of the cell means,
against the predicted tails 4.0-4.5 / 8.7-10.8 / 16-24.
Part B (N37 scaling hypothesis): d(cell) = pi(cell, 33) - pi(ref, 33), paired, 95 % percentile bootstrap CI (10 000
resamples, rng 81). 'N37 gestuetzt' if mean d(b2_095) > +0.3 and mean d(b2_0995) < -0.3 and both CIs exclude 0;
'N37 verworfen' if both CIs lie inside [-0.15, +0.15]; else 'unklar'. t = 25/45 descriptive. < 8 valid pairs -> 'nicht auswertbar'.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from math import comb
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(HERE))
from result_loader import Expect, find_run, load_run  # noqa: E402
import design as D  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp056", LAB / "experiments/EXP-056-overlap-persistence/analyze.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)

SPL, RAW, SUF = HERE / "splits", HERE / "raw", "_devcuda"
PRESET = (0.9, 0.98)
MIN_VALID, ALPHA, N_BOOT = 8, 0.05, 10_000
PRED_TAIL = {"b1_08": (3.99, 4.5), "ref": (8.65, 10.8), "b1_095": (16.0, 24.0)}   # clock_predictions.pre_and_tail, r = 1 ... 0


def tags(cell: str) -> str:
    b1, b2 = D.CELLS[cell]
    return (f"_b1{float(b1)!r}" if b1 is not None else "") + (f"_b2{float(b2)!r}" if b2 is not None else "")


def load(s: int, cell: str, kind: str, t: int = 0, rom: bool = False) -> np.ndarray | str:
    """kind 'A'/'B': pure run (2000 steps); 'AB'/'BA': switch at t, then 2000 steps. Returns the group power at the end."""
    first, second = kind[0], kind[1:] or None
    steps = D.BUDGET + (t if second else 0)
    pat = (f"EXP-0*_baseline_seed{s}_thr*_{D.stem(s, first)}" + (f"_to_{D.stem(s, second)}_at{t}" if second else "")
           + ("_rom" if rom else "") + tags(cell) + SUF)
    b1, b2 = D.CELLS[cell]
    L = load_run(find_run(RAW, pat),
                 Expect(seed=s, device="cuda", max_steps=steps, split_file=SPL / f"{D.stem(s, first)}.npy", test_file=SPL / f"seed{s}_test.npy",
                        switch_file=SPL / f"{D.stem(s, second)}.npy" if second else None,
                        config={"p": 113, "task": "add", "beta1": b1 if b1 is not None else PRESET[0],
                                "beta2": b2 if b2 is not None else PRESET[1]},
                        snapshots_at=(steps,)))
    tag = f"{cell}:{kind}@{t}{'_rom' if rom else ''}"
    if L.status != "ok":
        return f"{tag}: {L.status}: {L.reason}"
    if rom and L.res.get("events", {}).get("reset_optim_part", {}).get("check") is not True:
        return f"{tag}: partial reset not recorded"
    return A._a43.group_power(L.snapshot(steps), "add", 113)[0]


def cell_pis(s: int, cell: str, F: list[int], G: list[int]) -> dict:
    pure = {k: load(s, cell, k) for k in ("A", "B")}
    normal, rom = D.switch_times(cell)
    sw = {(r, t, k): load(s, cell, k, t, r) for r, ts in ((False, normal), (True, rom)) for t in ts for k in ("AB", "BA")}
    bad = [v for v in list(pure.values()) + list(sw.values()) if isinstance(v, str)]
    if bad:
        return {"valid": False, "n_bad": len(bad), "reason": "; ".join(bad[:3])}
    LA, LB = A.logratio(pure["A"], F, G), A.logratio(pure["B"], F, G)
    if not LA - LB >= 2.0:
        return {"valid": False, "reason": f"L(A) - L(B) = {LA - LB:.2f} < 2"}
    out = {"valid": True, "LA_minus_LB": LA - LB}
    for (r, t, _k) in sw:
        if _k == "AB":
            L = {"A": LA, "B": LB, "AB": A.logratio(sw[(r, t, "AB")], F, G), "BA": A.logratio(sw[(r, t, "BA")], F, G)}
            out[f"pi_{'m' if r else 'n'}{t}"] = A.pi_of(L)["pi"]
    return out


def sign_test_greater(c: np.ndarray) -> dict:
    """One-sided exact sign test for median(c) > 0; zeros dropped."""
    pos, n = int((c > 0).sum()), int((c != 0).sum())
    p = sum(comb(n, k) for k in range(pos, n + 1)) / 2 ** n if n else 1.0
    return {"n_pos": pos, "n": n, "p": float(p)}


def verdict_a(drops: dict[str, np.ndarray]) -> dict:
    """drops: cell -> per-seed drop, aligned over seeds valid in all three beta1 cells."""
    n = len(drops["ref"])
    if n < MIN_VALID:
        return {"n": n, "verdict": "nicht auswertbar"}
    c = drops["b1_095"] - drops["b1_08"]
    st = sign_test_greater(c)
    means = {k: float(v.mean()) for k, v in drops.items()}
    ordered = means["b1_08"] < means["ref"] < means["b1_095"]
    if st["p"] < ALPHA and ordered:
        v = "N38 gestuetzt"
    elif float(np.median(c)) <= 0:
        v = "gegen N38"
    else:
        v = "unklar"
    return {"n": n, "contrast_mean": float(c.mean()), "contrast_median": float(np.median(c)), "sign_test": st,
            "drop_means": means, "ordered": ordered, "verdict": v}


def boot_ci(d: np.ndarray, seed: int = 81) -> list[float]:
    rng = np.random.default_rng(seed)
    m = d[rng.integers(0, len(d), size=(N_BOOT, len(d)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def verdict_b(d: dict[str, np.ndarray]) -> dict:
    """d: cell -> paired pi(cell, 33) - pi(ref, 33) over the seeds valid in that cell and ref."""
    if min(len(v) for v in d.values()) < MIN_VALID:
        return {"n": {k: len(v) for k, v in d.items()}, "verdict": "nicht auswertbar"}
    res = {k: {"n": len(v), "mean": float(v.mean()), "ci95": boot_ci(v)} for k, v in d.items()}
    lo, hi = res["b2_095"], res["b2_0995"]
    excl0 = lambda r: r["ci95"][0] > 0 or r["ci95"][1] < 0   # noqa: E731
    inside = lambda r: -0.15 <= r["ci95"][0] and r["ci95"][1] <= 0.15   # noqa: E731
    if lo["mean"] > 0.3 and hi["mean"] < -0.3 and excl0(lo) and excl0(hi):
        v = "N37 gestuetzt"
    elif inside(lo) and inside(hi):
        v = "N37 verworfen"
    else:
        v = "unklar"
    return {**res, "verdict": v}


def main() -> None:
    rows = {}
    for s in D.SEEDS:
        meta = json.loads((SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        rows[s] = {cell: cell_pis(s, cell, F, G) for cell in D.CELLS}
    okA = [s for s in D.SEEDS if all(rows[s][c]["valid"] for c in D.PART_A_CELLS)]
    drops = {c: np.array([rows[s][c]["pi_n25"] - rows[s][c]["pi_m25"] for s in okA]) for c in D.PART_A_CELLS}
    out = {"part_A": verdict_a(drops)}
    desc = {}
    for c in D.PART_A_CELLS:
        ok = [s for s in D.SEEDS if rows[s][c]["valid"]]
        if not ok:
            continue
        mean = {k: float(np.mean([rows[s][c][k] for s in ok])) for k in ("pi_n20", "pi_n25", "pi_n30", "pi_m25")}
        slope = (mean["pi_n30"] - mean["pi_n20"]) / 10
        drop = mean["pi_n25"] - mean["pi_m25"]
        desc[c] = {"n": len(ok), **mean, "slope": slope, "drop": drop, "tail_est": drop / slope if slope > 0 else None,
                   "tail_pred": PRED_TAIL[c]}
    out["part_A_descriptive"] = desc
    d = {}
    for c in D.PART_B_CELLS:
        ok = [s for s in D.SEEDS if rows[s][c]["valid"] and rows[s]["ref"]["valid"]]
        d[c] = np.array([rows[s][c]["pi_n33"] - rows[s]["ref"]["pi_n33"] for s in ok])
    out["part_B"] = verdict_b(d)
    out["part_B_descriptive"] = {c: {f"pi_n{t}": (float(np.mean(v)) if (v := [rows[s][c][f"pi_n{t}"] for s in D.SEEDS if rows[s][c]["valid"]]) else None)
                                     for t in D.T_B} for c in ("ref",) + D.PART_B_CELLS}
    out["validity"] = {c: sum(rows[s][c]["valid"] for s in D.SEEDS) for c in D.CELLS}
    out["rows"] = {str(s): r for s, r in rows.items()}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert tags("ref") == "" and tags("b1_08") == "_b10.8" and tags("b2_0995") == "_b20.995"
    assert D.switch_times("ref") == ((20, 25, 30, 33, 45), (25,)) and D.switch_times("b2_095") == ((25, 33, 45), ())
    assert len(D.jobs()) == 500 and len(D.smoke()) == 4
    assert abs(sign_test_greater(np.ones(10))["p"] - 1 / 1024) < 1e-15
    assert abs(sign_test_greater(np.array([1.0] * 9 + [-1.0]))["p"] - 11 / 1024) < 1e-15
    base = np.linspace(0.05, 0.3, 10)
    assert verdict_a({"b1_08": base * 0.4, "ref": base, "b1_095": base * 2})["verdict"] == "N38 gestuetzt"
    assert verdict_a({"b1_08": base * 2, "ref": base, "b1_095": base * 0.4})["verdict"] == "gegen N38"
    assert verdict_a({"b1_08": base[:7], "ref": base[:7], "b1_095": base[:7]})["verdict"] == "nicht auswertbar"
    noisy = np.array([0.1, -0.1] * 5)
    assert verdict_a({"b1_08": base, "ref": base * 1.1, "b1_095": base + noisy + 0.01})["verdict"] == "unklar"
    z = np.linspace(-0.05, 0.05, 10)
    assert verdict_b({"b2_095": z, "b2_0995": z})["verdict"] == "N37 verworfen"
    assert verdict_b({"b2_095": z + 0.5, "b2_0995": z - 0.5})["verdict"] == "N37 gestuetzt"
    assert verdict_b({"b2_095": z + 0.2, "b2_0995": z})["verdict"] == "unklar"
    assert verdict_b({"b2_095": z[:7], "b2_0995": z})["verdict"] == "nicht auswertbar"
    print("[exp081] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
