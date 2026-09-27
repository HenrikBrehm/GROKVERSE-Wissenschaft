"""EXP-062 (EXPLORATION, post hoc on stored EXP-056/058/059 spectra, no new training): is persistence retained OLD energy or suppressed NEW
energy? Run under guarded_run.py (uses the shared loader of EXP-056).

Per seed s (400-409), normal switch at t, direction X->Y (own = X targets, new = Y targets), W_E power spectra from the run.
Final (Y-step 2000): a = log E_own(switch) - log E_own(pure Y run)   (old energy retained beyond what pure Y training has)
                    b = log E_new(pure Y run) - log E_new(switch)   (new energy missing compared with pure Y training)
L_switch - L_pureY = a + b exactly (L = log E_own - log E_new), so a and b split the numerator of pi into two parts.
Early (Y-step 250): the same split using the spectra at t + 250 (switch) and 250 (pure Y).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
E59 = LAB / "experiments/EXP-059-momentum-exposure"
E56 = LAB / "experiments/EXP-056-overlap-persistence"
_spec = importlib.util.spec_from_file_location("exp059", E59 / "analyze.py")
B = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(B)
A = B.A
T = B.T_NORMAL


def spectra(d: Path) -> dict[int, np.ndarray]:
    sp, st = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy")
    return {int(k): sp[i] for i, k in enumerate(st)}


def run_dir(s: int, first: str, second: str | None, t: int | None) -> Path | None:
    st1 = A.stem(s, B.OM, first)
    if second is None:
        return A.find_run(E56 / "raw", f"EXP-0*_baseline_seed{s}_thr*_{st1}" + A.SUF)
    return A.find_run(B.root_for(t), f"EXP-0*_baseline_seed{s}_thr*_{st1}_to_{A.stem(s, B.OM, second)}_at{t}" + A.SUF)


def e(spec: np.ndarray, T_: list[int]) -> float:
    return float(spec[[k - 1 for k in T_]].sum())


def split(sw: dict, pure: dict, own: list[int], new: list[int], k_sw: int, k_pure: int) -> tuple[float, float]:
    a = np.log(e(sw[k_sw], own)) - np.log(e(pure[k_pure], own))
    b = np.log(e(pure[k_pure], new)) - np.log(e(sw[k_sw], new))
    return float(a), float(b)


def main() -> None:
    rows = []
    for s in B.SEEDS:
        meta = json.loads((A.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        pure = {x: spectra(run_dir(s, x, None, None)) for x in "AB"}
        for t in T:
            for first, second, own, new in (("A", "B", F, G), ("B", "A", G, F)):
                sw = spectra(run_dir(s, first, second, t))
                af, bf = split(sw, pure[second], own, new, t + 2000, 2000)
                ae, be = split(sw, pure[second], own, new, t + 250, 250)
                rows.append({"seed": s, "t": t, "dir": first + second, "a_final": af, "b_final": bf, "a_250": ae, "b_250": be})
    out = {"n": len(rows), "by_t": {}}
    for t in T:
        q = [r for r in rows if r["t"] == t]
        out["by_t"][str(t)] = {k: float(np.mean([r[k] for r in q])) for k in ("a_final", "b_final", "a_250", "b_250")}
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["by_t"], indent=1))


def selftest() -> None:
    sw = {10: np.array([4.0, 1.0, 1.0])}
    pure = {5: np.array([1.0, 2.0, 1.0])}
    a, b = split(sw, pure, [1], [2], 10, 5)
    Lsw, Lp = np.log(4.0 / 1.0), np.log(1.0 / 2.0)
    assert abs((a + b) - (Lsw - Lp)) < 1e-12 and abs(a - np.log(4)) < 1e-12 and abs(b - np.log(2)) < 1e-12
    print("[exp062] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
