"""Post hoc (session 20, 2026-09-27): does the planted frequency choice persist AFTER grokking, or decay?
Motivation: Zhou, Zhang, Xu (CiCP 2026 / arXiv 2405.17479) see sampling-induced frequencies fade on the test set once the
true frequencies are learned. Here every frequency set is a valid solution, so K2 predicts persistence.
Descriptive only, saved runs only (spectra every 250 steps, W_E power per frequency 1..56). Per run: share of W_E power in
the own target set T (5 of 56) and in the other arm's set, and |top-5 ∩ T|, at the first logged step >= gen and at 2000."""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
rows = []
for seed in range(10, 20):
    tg = {}
    for arm, suf in (("F", ""), ("G", "_G")):
        tg[arm] = set(json.loads((HERE / f"splits/split_seed{seed}_eps2.0{suf}.json").read_text(encoding="utf-8"))["targets"])
    for arm, suf in (("F", ""), ("G", "_G")):
        d = HERE / f"raw/EXP-016_baseline_seed{seed}_thr4_split_seed{seed}_eps2.0{suf}"
        res = json.loads((d / "result.json").read_text(encoding="utf-8"))
        S = np.load(d / "spectra.npy").astype(np.float64)
        steps = np.load(d / "spectra_steps.npy")
        assert S.shape[1] == 56, S.shape
        gen = res["transitions"]["primary"]["generalization"]["first_crossing_step"]
        own, oth = tg[arm], tg["G" if arm == "F" else "F"]
        share = lambda i, T: float(S[i, [k - 1 for k in T]].sum() / S[i].sum())
        top5 = lambda i: set(int(k) + 1 for k in np.argsort(-S[i])[:5])
        ig = int(np.searchsorted(steps, gen))
        rows.append({"seed": seed, "arm": arm, "gen": gen, "step_at_gen": int(steps[ig]),
                     "own_share": {int(steps[i]): round(share(i, own), 4) for i in range(len(steps))},
                     "other_share": {int(steps[i]): round(share(i, oth), 4) for i in range(len(steps))},
                     "own_top5_at_gen": len(top5(ig) & own), "own_top5_at_2000": len(top5(len(steps) - 1) & own),
                     "final_test_acc": res["final_acc"]["test"]})
d = np.array([r["own_share"][2000] - r["own_share"][r["step_at_gen"]] for r in rows])
lag = np.array([2000 - r["step_at_gen"] for r in rows])
summary = {"n_runs": len(rows), "null_share_5_of_56": round(5 / 56, 4),
           "own_share_at_gen_mean": round(float(np.mean([r["own_share"][r["step_at_gen"]] for r in rows])), 4),
           "own_share_at_2000_mean": round(float(np.mean([r["own_share"][2000] for r in rows])), 4),
           "other_share_at_2000_mean": round(float(np.mean([r["other_share"][2000] for r in rows])), 4),
           "delta_own_share_gen_to_2000": {"mean": round(float(d.mean()), 4), "sd": round(float(d.std(ddof=1)), 4),
                                           "n_up": int((d > 0).sum()), "n_down": int((d < 0).sum())},
           "steps_after_gen": {"min": int(lag.min()), "max": int(lag.max())},
           "own_top5_at_gen_mean": float(np.mean([r["own_top5_at_gen"] for r in rows])),
           "own_top5_at_2000_mean": float(np.mean([r["own_top5_at_2000"] for r in rows])),
           "note": "20 runs from 10 init seeds (F and G arm share the init; seeds are not fully independent, FINDINGS K2 caveat). Descriptive."}
(HERE / "posthoc_postgen_persistence.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1), encoding="utf-8")
print(json.dumps(summary, indent=1))
for r in rows:
    print(r["seed"], r["arm"], r["gen"], r["own_share"][r["step_at_gen"]], r["own_share"][2000], r["own_top5_at_gen"], r["own_top5_at_2000"])
