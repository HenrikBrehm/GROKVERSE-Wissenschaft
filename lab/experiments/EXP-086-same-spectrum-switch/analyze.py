"""EXP-086 (pilot, session 32, fixed before any run): does a switch between two splits with the SAME target frequencies (A -> A2,
disjoint pairs, matched strength, fresh phases) cost grokking time like a switch to other frequencies (A -> B)? Definition: README.md.
Reads result.json fields (seed, split_file, switch_split_file, switch_step, events.generalization_step) of
  EXP-086 raw (A2 only; A<->A2 at 25/50; R1, R2 only; R1<->R2 at 25)  and  EXP-056 raw (A only, B only, A<->B at 25; omega 0).
Per seed: C_X(t) = mean over both directions of log2 b(switch) - log2 b(destination only); b = min(event, cap) from step 0,
cap 2000 for the A/A2/B arms and 12000 for the R arms. Checks: one test set and one initialisation per seed.
  primary      D = C_AB(25) - C_AA2(25) > 0      exact one-sided sign test over non-tied seeds ('gestützt' at p < 0.05)
  descriptive  C_AA2(25), C_AA2(50), C_RR(25): mean, sign counts
  python lab/experiments/EXP-086-same-spectrum-switch/analyze.py [--selftest]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
SEEDS = tuple(range(400, 410))
CAP_A, CAP_R = 2000, 12000


def arm_name(path: str | None) -> str | None:
    if path is None:
        return None
    stem = Path(path).stem                                   # seed400_w0_A / seed400_A2 / seed400_R1
    return stem.split("_")[-1]


def collect() -> dict:
    runs: dict = {}
    for root, cap_of in ((HERE / "raw", None), (LAB / "experiments/EXP-056-overlap-persistence/raw", None)):
        for f in root.glob("*/result.json"):
            r = json.loads(f.read_text(encoding="utf-8"))
            if r.get("status") != "completed" or r["seed"] not in SEEDS:
                continue
            if "_w200_" in r["split_file"] or "_w400_" in r["split_file"]:
                continue
            first, second = arm_name(r["split_file"]), arm_name(r.get("switch_split_file"))
            key = first if second is None else (first + ">" + second, r["switch_step"])
            cap = CAP_R if first.startswith("R") else CAP_A
            g = (r.get("events") or {}).get("generalization_step")
            runs.setdefault(r["seed"], {})[key] = {"lb": math.log2(min(g, cap) if g is not None else cap), "th": r["test_hash"],
                                                   "init": r["init_checksum_shared"]}
    return runs


def cost(v: dict, x: str, y: str, t: int) -> float:
    return ((v[(f"{x}>{y}", t)]["lb"] - v[y]["lb"]) + (v[(f"{y}>{x}", t)]["lb"] - v[x]["lb"])) / 2


def sign(d: np.ndarray) -> dict:
    nz = d[np.abs(d) > 1e-9]
    k, n = int((nz > 0).sum()), len(nz)
    return {"mean": float(d.mean()), "pos": k, "nonzero": n, "p_one_sided": sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0}


def evaluate(runs: dict) -> dict:
    need = ["A", "B", "A2", ("A>B", 25), ("B>A", 25), ("A>A2", 25), ("A2>A", 25), ("A>A2", 50), ("A2>A", 50),
            "R1", "R2", ("R1>R2", 25), ("R2>R1", 25)]
    ok, bad = {}, []
    for s in SEEDS:
        v = runs.get(s, {})
        miss = [k for k in need if k not in v]
        if miss:
            bad.append(f"seed {s}: missing {miss[:3]}")
            continue
        if len({x["th"] for x in v.values()}) != 1 or len({x["init"] for x in v.values()}) != 1:
            bad.append(f"seed {s}: test set or init differs")
            continue
        ok[s] = v
    out: dict = {"n_valid": len(ok), "broken": bad}
    if len(ok) < 8:
        out["reading"] = "nicht auswertbar"
        return out
    cab = np.array([cost(v, "A", "B", 25) for v in ok.values()])
    caa = np.array([cost(v, "A", "A2", 25) for v in ok.values()])
    out |= {"primary_D_AB_minus_AA2": sign(cab - caa), "C_AB_25": sign(cab), "C_AA2_25": sign(caa),
            "C_AA2_50": sign(np.array([cost(v, "A", "A2", 50) for v in ok.values()])),
            "C_RR_25": sign(np.array([cost(v, "R1", "R2", 25) for v in ok.values()]))}
    out["reading"] = "gestützt" if out["primary_D_AB_minus_AA2"]["p_one_sided"] < 0.05 else "nicht gestützt"
    return out


def main() -> None:
    out = evaluate(collect())
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


def selftest() -> None:
    assert arm_name("lab/x/seed400_w0_A.npy") == "A" and arm_name("lab/y/seed401_A2.npy") == "A2" and arm_name(None) is None
    mk = lambda lb: {"lb": lb, "th": "t", "init": "i"}   # noqa: E731
    v = {"A": mk(9.0), "B": mk(9.0), "A2": mk(9.0), ("A>B", 25): mk(10.0), ("B>A", 25): mk(10.0), ("A>A2", 25): mk(9.0),
         ("A2>A", 25): mk(9.0), ("A>A2", 50): mk(8.5), ("A2>A", 50): mk(8.5), "R1": mk(12.0), "R2": mk(12.0),
         ("R1>R2", 25): mk(12.5), ("R2>R1", 25): mk(12.5)}
    e = evaluate({s: v for s in SEEDS})
    assert e["reading"] == "gestützt" and abs(e["primary_D_AB_minus_AA2"]["mean"] - 1.0) < 1e-12 and e["C_AA2_25"]["nonzero"] == 0
    assert abs(e["C_AA2_50"]["mean"] + 0.5) < 1e-12 and abs(e["C_RR_25"]["mean"] - 0.5) < 1e-12
    same = {**v, ("A>A2", 25): mk(10.0), ("A2>A", 25): mk(10.0)}
    assert evaluate({s: same for s in SEEDS})["reading"] == "nicht gestützt"
    assert evaluate({s: v for s in SEEDS[:7]})["reading"] == "nicht auswertbar"
    print("[exp086] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
