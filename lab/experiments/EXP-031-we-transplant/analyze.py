"""EXP-031 analysis (pre-registered in README.md): after a W_E transplant at step 500, does K follow donor A or run B?"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-001-freq-ban"))
import freq_ban as fb  # noqa: E402

P = 113
B_SEEDS = (0, 2, 4, 6, 8)


def final_set(seed: int) -> set[int]:
    return set(fb.top_frequencies(fb.freq_power(fb._stored_final_W_E(seed, P), fb.fourier_basis(P)), 5))


def main() -> None:
    rows = []
    for b in B_SEEDS:
        a = b + 1
        TA, TB = final_set(a), final_set(b)
        onlyA, onlyB = TA - TB, TB - TA
        for arm, rid in (("transplant", f"EXP-031_transplant_B{b}_A{a}"), ("control", f"EXP-031_control_B{b}")):
            f = HERE / "raw" / rid / "result.json"
            if not f.exists():
                continue
            r = json.loads(f.read_text())
            if not r.get("complete"):
                continue
            K = set(r["final_top5"])
            row = {"B": b, "A": a, "arm": arm, "K": sorted(K), "T_A": sorted(TA), "T_B": sorted(TB),
                   "d": len(K & onlyA) - len(K & onlyB), "test_acc_3000": r["curve"][-1][2],
                   "acc_after_transplant": r["acc_after_transplant"]}
            if arm == "transplant":
                S500A, S500B = set(r["top5_A_at_500"]), set(r["top5_B_at_500"])
                row["d_500sets"] = len(K & (S500A - S500B)) - len(K & (S500B - S500A))
            rows.append(row)
    tr = [x for x in rows if x["arm"] == "transplant"]
    co = [x for x in rows if x["arm"] == "control"]
    out = {"rows": rows, "n_transplant": len(tr), "n_control": len(co)}
    if len(tr) < 5 or len(co) < 5:
        out["verdict"] = "nicht auswertbar (unvollständig)"
    elif np.mean([x["d"] for x in co]) >= 0:
        out["verdict"] = "nicht auswertbar (Kontrolle findet nicht zu B)"
    else:
        dt = [x["d"] for x in tr]
        out.update(d_transplant=dt, d_control=[x["d"] for x in co])
        out["verdict"] = ("Abdruck kausal" if all(x > 0 for x in dt) else
                          "Daten/übrige Gewichte bestimmen" if np.mean(dt) <= 0 else "gemischt")
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
