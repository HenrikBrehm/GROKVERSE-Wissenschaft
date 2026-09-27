"""EXP-077 (pilot): do splits whose only structure is the LEFT operand's token frequency steer the learned W_E frequencies?
Definition: README.md (fixed before any run). Run under guarded_run.py (imports torch via the shared loader).

Per seed s (770-779) and eps in {2.0 (primary), 1.0 (secondary)}: Delta_pow = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)] of the W_E power at
step 2000 (as P1); one-sided exact sign-flip test over valid seeds. Reading (pre-registered): see README.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
import confirm_p1 as c1  # noqa: E402  (delta_pow_checked, sign_flip_p, boot_ci)
from result_loader import Expect, find_run, load_run  # noqa: E402

SEEDS, STEP, MIN_VALID = range(770, 780), 2000, 8


def spectrum(s: int, eps: str, arm: str) -> np.ndarray | str:
    st = f"marg_seed{s}_eps{eps}_{arm}"
    L = load_run(find_run(HERE / "raw", f"EXP-016_baseline_seed{s}_thr1_{st}_devcuda"),
                 Expect(seed=s, device="cuda", max_steps=STEP, split_file=HERE / f"splits/{st}.npy",
                        config={"p": 113, "task": "add", "arch": "transformer"}, at=(STEP,)))
    if L.status != "ok":
        return f"{st}: {L.status}: {L.reason}"
    pw = np.asarray(L.spectrum(STEP), dtype=np.float64)
    return pw if pw.shape == (56,) else f"{st}: spectrum shape {pw.shape}"


def reading(n: int, mean: float, p: float) -> str:
    if n < MIN_VALID:
        return "nicht auswertbar"
    if mean >= 1.0 and p < 0.05:
        return "Randverteilung steuert (stützt erste Ordnung inkl. Fremd-Häufigkeiten)"
    if mean < 0.5:                  # Nachtrag b (session 26, before any run): p >= 0.2 alone is 'unklar'
        return "keine Steuerung über die Randverteilung (stützt 'nur Paarstruktur')"
    return "unklar"


def main() -> None:
    rng = np.random.default_rng(77)
    out: dict = {}
    for eps in ("2.0", "1.0"):
        rows = []
        for s in SEEDS:
            T = json.loads((HERE / f"splits/marg_seed{s}_eps{eps}_F.json").read_text(encoding="utf-8"))["targets_all"]
            pw = {a: spectrum(s, eps, a) for a in "FG"}
            bad = [v for v in pw.values() if isinstance(v, str)]
            d = None if bad else c1.delta_pow_checked(pw["F"], pw["G"], T["F"], T["G"])
            rows.append({"seed": s, "valid": d is not None, "Delta_pow": d, "reason": "; ".join(bad) or (None if d is not None else "Delta undefined")})
        D = np.array([r["Delta_pow"] for r in rows if r["valid"]])
        res = {"n_valid": int(len(D)), "rows": rows}
        if len(D) >= MIN_VALID:
            p = c1.sign_flip_p(D, rng)
            res.update(mean=float(D.mean()), sd=float(D.std(ddof=1)), p=p, ci95=c1.boot_ci(D, rng), n_positive=int((D > 0).sum()))
        res["reading"] = reading(len(D), res.get("mean", 0.0), res.get("p", 1.0)) if eps == "2.0" else "sekundär, nur berichtet"
        out[f"eps{eps}"] = res
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in out.items()}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
