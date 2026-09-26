"""EXP-021: confirmation that non-target W_E top-5 frequencies under engineered splits are fold(2k) of own targets.
Runs: EXP-016 seeds 16-19 (F, G) and EXP-020 seeds 30-34 (only-F, only-G); K = W_E top-5 at step 2000. Definition: README."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
P, M, STEP = 113, 5, 2000


def fold(x: int) -> int:
    x %= P
    return min(x, P - x)


def top_at(d: Path) -> set[int] | None:
    if not (d / "result.json").exists() or json.loads((d / "result.json").read_text())["status"] != "completed":
        return None
    spec, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
    if STEP not in steps:
        return None
    pw = spec[steps.index(STEP)]
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:M]}


def runs() -> list[dict]:
    out = []
    for s in range(16, 20):
        for arm, suf, other in (("F", "", "_G"), ("G", "_G", "")):
            d = EXP / f"EXP-016-engineered-split/raw/EXP-016_baseline_seed{s}_thr4_split_seed{s}_eps2.0{suf}"
            meta = lambda x: set(json.loads((EXP / f"EXP-016-engineered-split/splits/split_seed{s}_eps2.0{x}.json")
                                            .read_text())["targets"])
            out.append({"src": f"EXP-016/{s}{arm}", "K": top_at(d), "T": meta(suf), "T_other": meta(other)})
    for s in range(30, 35):
        meta = json.loads((EXP / f"EXP-020-data-switch/splits/seed{s}.json").read_text())["targets"]
        for arm, other in (("F", "G"), ("G", "F")):
            d = EXP / f"EXP-020-data-switch/raw/EXP-018_baseline_seed{s}_thr4_seed{s}_train_{arm}"
            out.append({"src": f"EXP-020/{s}{arm}", "K": top_at(d), "T": set(meta[arm]), "T_other": set(meta[other])})
    return out


def tail(ps: list[float], k: int) -> float:
    dp = np.zeros(len(ps) + 1)
    dp[0] = 1.0
    for q in ps:
        dp[1:] = dp[1:] * (1 - q) + dp[:-1] * q
        dp[0] *= 1 - q
    return float(dp[k:].sum())


def count(rs: list[dict], key: str) -> dict:
    hits, qs = 0, []
    for r in rs:
        T, Tt = r["T"], r[key]
        H = {fold(2 * k) for k in Tt} - T
        for m in r["K"] - T:
            hits += m in H
            qs.append(len(H) / (56 - len(T)))
    return {"n_nontarget": len(qs), "hits": hits, "share": hits / len(qs) if qs else None,
            "expected": float(sum(qs)), "p": tail(qs, hits) if qs else None}


def main() -> None:
    rs = [r for r in runs() if r["K"] is not None]
    own, ctrl = count(rs, "T"), count(rs, "T_other")
    if own["n_nontarget"] < 8:
        verdict = "nicht auswertbar"
    elif own["p"] < 0.01 and own["share"] >= 0.5:
        verdict = "bestätigt"
    elif own["p"] < 0.05:
        verdict = "schwach"
    else:
        verdict = "nicht bestätigt"
    out = {"n_runs": len(rs), "own_targets": own, "control_other_arm": ctrl, "verdict": verdict,
           "runs": [{**r, "K": sorted(r["K"]), "T": sorted(r["T"]), "T_other": sorted(r["T_other"])} for r in rs]}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "runs"}, indent=1))


if __name__ == "__main__":
    main()
