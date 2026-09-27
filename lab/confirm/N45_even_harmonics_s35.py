"""N45 (session 35, exploration on seen seeds): are the non-target W_E top-5 members EVEN harmonics fold(2k) of the own targets
in the transformer (P1 add 113) but not in the shared-embedding MLP (EXP-045)?

Rule fixed in lab/NOVEL_DIRECTIONS.md (N45) before this script was run. Count exactly as EXP-021 (analyze.py there): K = W_E top-5
at step 2000 (spectra.npy, ties broken by lower k), per non-target member m of K (m not in the own targets T) a hit if
m in H = {fold(n k): k in T} minus T, chance q = |H| / (56 - |T|), one-sided Poisson-binomial tail. n = 2 (even, fold(2k)) and
n = 3 (odd, fold(3k), secondary). Analysis only, no training.
  python lab/tools/guarded_run.py -- python lab/confirm/N45_even_harmonics_s35.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
P, M, STEP = 113, 5, 2000


def fold(x: int) -> int:
    x %= P
    return min(x, P - x)


def top_at(d: Path) -> set[int] | None:
    f = d / "result.json"
    if not f.exists() or json.loads(f.read_text(encoding="utf-8")).get("status") != "completed":
        return None
    spec, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
    if STEP not in steps:
        return None
    pw = spec[steps.index(STEP)]
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:M]}


def tail(ps: list[float], k: int) -> float:
    dp = np.zeros(len(ps) + 1)
    dp[0] = 1.0
    for q in ps:
        dp[1:] = dp[1:] * (1 - q) + dp[:-1] * q
        dp[0] *= 1 - q
    return float(dp[k:].sum())


def count(runs: list[dict], n: int) -> dict:
    hits, qs = 0, []
    for r in runs:
        T = r["T"]
        H = {fold(n * k) for k in T} - T
        for m in r["K"] - T:
            hits += m in H
            qs.append(len(H) / (56 - len(T)))
    return {"n_nontarget": len(qs), "hits": hits, "share": hits / len(qs) if qs else None,
            "expected_share": float(np.mean(qs)) if qs else None, "p": tail(qs, hits) if qs else None}


def group(kind: str) -> tuple[list[dict], int]:
    out, missing = [], 0
    if kind == "transformer_P1":
        seeds, raw, spl = range(1000, 1050), LAB / "confirm/raw", LAB / "confirm/splits"
        name = lambda s, a: f"EXP-016_baseline_seed{s}_thr1_confirm_exp1_eps2.0_add113_seed{s}_{a}_devcuda"   # noqa: E731
        meta = lambda s, a: spl / f"confirm_exp1_eps2.0_add113_seed{s}_{a}.json"                            # noqa: E731
    else:
        e = LAB / "experiments/EXP-045-mlp-steering"
        seeds, raw, spl = range(90, 100), e / "raw", e / "splits"
        name = lambda s, a: f"EXP-045_baseline_seed{s}_thr1_split_add113_seed{s}_eps2.0_{a}_mlp_devcuda"     # noqa: E731
        meta = lambda s, a: spl / f"split_add113_seed{s}_eps2.0_{a}.json"                                    # noqa: E731
    for s in seeds:
        for a in "FG":
            K = top_at(raw / name(s, a))
            if K is None:
                missing += 1
                continue
            T = set(json.loads(meta(s, a).read_text(encoding="utf-8"))["targets"])
            out.append({"src": f"{kind}/{s}{a}", "K": K, "T": T})
    return out, missing


def reading(t2: dict, m2: dict) -> str:
    sig = lambda c: c["p"] is not None and c["p"] < 0.01          # noqa: E731
    if not sig(t2):
        return "(iii) transformer shows no even-harmonic excess: contradicts the EXP-016 exploration; wait for EXP-021"
    if m2["n_nontarget"] < 8:
        return "MLP not evaluable (< 8 non-target members)"
    if m2["p"] >= 0.05:
        return "(i) even harmonics in W_E only in the transformer (exploration)"
    if sig(m2):
        return "(ii) even harmonics also in the MLP W_E: not transformer-specific"
    return "unclear (MLP 0.01 <= p < 0.05)"


def main() -> None:
    res = {}
    for kind in ("transformer_P1", "mlp_EXP045"):
        runs, missing = group(kind)
        res[kind] = {"n_runs": len(runs), "missing": missing, "even_2k": count(runs, 2), "odd_3k": count(runs, 3)}
    res["reading"] = reading(res["transformer_P1"]["even_2k"], res["mlp_EXP045"]["even_2k"])
    (LAB / "confirm/N45_even_harmonics_s35.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
