"""Session 32 (2026-09-27, window closed), POST HOC exploration on stored EXP-041 runs, no training.

Question: does a 150-step prefix on the engineered split E speed up grokking when training then continues on an ordinary
random split R (same init, common test set T*)? Links the speed-up (R5) with the early lock-in (K4; EXP-041 P41a: the prefix
fixes the frequencies).
Stated before looking at any generalisation step of the switched runs:
  Q1  E->R@150 generalises earlier than R-only (paired by seed; R-only is censored at its horizon) -> exact one-sided sign test
      over seeds whose order is determined.
  Q2  (descriptive) R->E@150 against E-only: does a random prefix delay the engineered run?
gen = trainer event (first test >= 0.95 on T*); horizon = steps_completed. Seeds 20-29 (EXP-018 splits), CPU.
  python lab/confirm/speed_prefix_s32.py
"""
import glob
import json
import math
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
RAW = Path(glob.glob(str(LAB / "experiments/EXP-041*/raw"))[0])
KINDS = {"E": "EXP-018_baseline_seed{s}_thr4_seed{s}_train_E", "R": "EXP-018_baseline_seed{s}_thr4_seed{s}_train_R",
         "ER": "EXP-020_baseline_seed{s}_thr4_seed{s}_train_E_to_seed{s}_train_R_at150",
         "RE": "EXP-020_baseline_seed{s}_thr4_seed{s}_train_R_to_seed{s}_train_E_at150"}


def load(kind: str, s: int) -> dict:
    r = json.loads((RAW / KINDS[kind].format(s=s) / "result.json").read_text(encoding="utf-8"))
    assert r["status"] == "completed", r["run_id"]
    return {"gen": (r.get("events") or {}).get("generalization_step"), "h": r["steps_completed"],
            "test": round(float(r["final_acc"]["test"]), 3), "init": r["init_checksum_shared"], "test_hash": r["test_hash"]}


def order(a: dict, b: dict) -> int:
    """+1 if a strictly earlier than b, -1 if later, 0 if tie or undetermined (censoring)."""
    ga = a["gen"] if a["gen"] is not None else math.inf
    gb = b["gen"] if b["gen"] is not None else math.inf
    if ga == gb:
        return 0
    if ga < gb:
        return 1 if ga <= b["h"] else 0          # a observed before b's horizon
    return -1 if gb <= a["h"] else 0


def sign_p(k: int, n: int) -> float:
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0


def main() -> None:
    rows = []
    for s in range(20, 30):
        r = {k: load(k, s) for k in KINDS}
        assert len({v["init"] for v in r.values()}) == 1 and len({v["test_hash"] for v in r.values()}) == 1, s
        rows.append({"seed": s, **{k: [v["gen"], v["h"], v["test"]] for k, v in r.items()},
                     "Q1": order(r["ER"], r["R"]), "Q2_RE_later": -order(r["RE"], r["E"])})
    q1 = [x["Q1"] for x in rows if x["Q1"]]
    q2 = [x["Q2_RE_later"] for x in rows if x["Q2_RE_later"]]
    out = {"note": "post hoc exploration on seen seeds 20-29", "rows": rows,
           "Q1_ER_earlier": sum(v > 0 for v in q1), "Q1_determined": len(q1), "Q1_p_one_sided": sign_p(sum(v > 0 for v in q1), len(q1)),
           "Q2_RE_later": sum(v > 0 for v in q2), "Q2_determined": len(q2)}
    (LAB / "confirm/speed_prefix_s32.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for x in rows:
        print(x)
    print({k: v for k, v in out.items() if k != "rows"})


if __name__ == "__main__":
    main()
