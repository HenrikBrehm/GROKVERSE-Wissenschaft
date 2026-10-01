"""EXP-139 post hoc (session 69, written before reading this quantity): is W_E steered in cells that never generalize?

EXP-139 measures Delta_pow only after generalization. In the cells without learning (401/9425 and 503/14000, 0/6 arms
generalized within 30 000 steps) the spectra were stored but Delta_pow was never read. Question: does the data
selection shape the number embeddings without the generalizing solution (memorization only)?
Measure per seed: Delta_pow (analyze.delta_pow) between F and G at the last stored snapshot (30 000) and at 2000;
placebo q90/q99 as analyze.placebo_q (same salt) from the same spectra.
Reading per cell (fixed before reading): Delta_pow(30 000) > q99 in all 3 seeds -> 'W_E gesteuert ohne
Generalisierung'; <= q90 in >= 2 seeds -> 'keine Steuerung ohne Generalisierung'; else 'unklar'.
Comparison (already read in session 68): 401/14 000 Delta_pow before gen 5.4-7.1, after gen 7.9-11.6.
Post hoc, exploratory; 3 seeds, one budget.
Usage: PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-139-pair-count/posthoc_nolearn_s69.py
"""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("exp139_analyze", HERE / "analyze.py")
an = importlib.util.module_from_spec(spec)
spec.loader.exec_module(an)

CELLS = ((401, "n9425"), (503, "n14000"))


def main() -> None:
    out = []
    for p, cell in CELLS:
        rows = []
        for s in an.mj.SEEDS:
            F, G = an.load(p, cell, s, "F"), an.load(p, cell, s, "G")
            if isinstance(F, str) or isinstance(G, str):
                rows.append({"seed": s, "problem": F if isinstance(F, str) else G})
                continue
            last = min(F["last_step"], G["last_step"])
            a, b = F["snaps"][last], G["snaps"][last]
            q90, q99, _ = an.placebo_q(a, b, F["T"], G["T"], s)
            rows.append({"seed": s, "gen": [F["gen"], G["gen"]], "last_step": last,
                         "dpow_last": an.delta_pow(a, b, F["T"], G["T"]), "q90": q90, "q99": q99,
                         "dpow_2000": an.delta_pow(F["snaps"][an.STEP], G["snaps"][an.STEP], F["T"], G["T"]),
                         "top5_own_last": [len(an.top5(a) & set(F["T"])), len(an.top5(b) & set(G["T"]))]})
        ev = [r for r in rows if r.get("dpow_last") is not None]
        if len(ev) == 3 and all(r["dpow_last"] > r["q99"] for r in ev):
            verdict = "W_E gesteuert ohne Generalisierung"
        elif sum(r["dpow_last"] <= r["q90"] for r in ev) >= 2:
            verdict = "keine Steuerung ohne Generalisierung"
        else:
            verdict = "unklar"
        out.append({"p": p, "cell": cell, "verdict": verdict, "rows": rows})
    print(json.dumps(out, indent=1))
    (HERE / "posthoc_nolearn_s69.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
