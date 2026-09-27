"""P2d/P2e post hoc, EXPLORATION (session 30; seeds seen for K2-function, Delta_pow never looked at beyond step 2000).
Question (reviewer: does the steering survive grokking?): does Delta_pow (P1 measure, F/G arms of a seed share the init) stay positive
long after generalization? Fixed before looking: per task, mean Delta_pow, 95 % bootstrap CI over seeds and the share of seeds > 0 at
every stored step up to the end (add 113: 4000; mul 113 / add 97: 8000); generalization steps from the freq_ban events.
Expectation written before the run: positive at every step after 500; it may shrink after grokking (weight decay prunes non-key
frequencies, but the key set itself is the steered one), so a decline is not a contradiction, a sign change in most seeds would be.
mul 113: group-basis power of the W_E snapshots (spectra.npy is the plain DFT), as in P2de_posthoc_time.py. Reads stored runs only.

  python lab/confirm/P2de_posthoc_dpow_time.py
"""
import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
from analyze import group_power  # noqa: E402
from confirm_p1 import delta_pow_checked  # noqa: E402

TASKS = (("add113", "p2d_raw", "p2d_splits", "add", 113, "EXP-016_baseline_seed{s}_thr1_p2d_seed{s}_{a}_devcuda", "p2d_seed{s}_{a}"),
         ("mul113", "p2e_raw", "p2e_splits", "mul", 113, "EXP-043_baseline_seed{s}_thr1_p2e_mul113_seed{s}_{a}_mul113_devcuda", "p2e_mul113_seed{s}_{a}"),
         ("add97", "p2e_raw", "p2e_splits", "add", 97, "EXP-043_baseline_seed{s}_thr1_p2e_add97_seed{s}_{a}_add97_devcuda", "p2e_add97_seed{s}_{a}"))


def spectra(d: Path, task: str, p: int) -> dict[int, np.ndarray]:
    if task == "mul":
        st, W = list(np.load(d / "we_snapshot_steps.npy")), np.load(d / "we_snapshots.npy").astype(np.float64)
        return {int(s): group_power(W[i], task, p)[0] for i, s in enumerate(st)}
    st, sp = list(np.load(d / "spectra_steps.npy")), np.load(d / "spectra.npy")
    return {int(s): sp[i] for i, s in enumerate(st)}


def main() -> None:
    rng = np.random.default_rng(30)
    out = {}
    for name, raw, spl, task, p, run, stem in TASKS:
        seeds = sorted({int(x.name.split("_seed")[1].split("_")[0]) for x in (LAB / "confirm" / raw).glob(run.format(s="*", a="F"))})
        per_step, gens = {}, []
        for s in seeds:
            dF, dG = (LAB / "confirm" / raw / run.format(s=s, a=a) for a in "FG")
            F = json.loads((LAB / "confirm" / spl / f"{stem.format(s=s, a='F')}.json").read_text(encoding="utf-8"))["targets"]
            G = json.loads((LAB / "confirm" / spl / f"{stem.format(s=s, a='G')}.json").read_text(encoding="utf-8"))["targets"]
            sF, sG = spectra(dF, task, p), spectra(dG, task, p)
            for d in (dF, dG):
                gens.append((json.loads((d / "result.json").read_text(encoding="utf-8")).get("events") or {}).get("generalization_step"))
            for t in sorted(set(sF) & set(sG)):
                v = delta_pow_checked(sF[t], sG[t], F, G)
                if v is not None:
                    per_step.setdefault(t, []).append(v)
        g = [x for x in gens if x is not None]
        res = {}
        for t, v in sorted(per_step.items()):
            v = np.array(v)
            boot = [rng.choice(v, len(v)).mean() for _ in range(5000)]
            res[str(t)] = {"n": int(v.size), "mean": round(float(v.mean()), 3),
                           "ci95": [round(float(np.quantile(boot, 0.025)), 3), round(float(np.quantile(boot, 0.975)), 3)],
                           "share_pos": round(float((v > 0).mean()), 3)}
        out[name] = {"seeds": len(seeds), "gen_step_median": float(np.median(g)) if g else None, "n_gen": len(g), "n_runs": len(gens),
                     "by_step": res}
        print(name, json.dumps({k: out[name][k] for k in ("seeds", "gen_step_median", "n_gen", "n_runs")}), flush=True)
        for t, r in res.items():
            print(f"   step {t:>5}: n {r['n']:3d}  mean {r['mean']:+.3f}  CI {r['ci95']}  share>0 {r['share_pos']:.2f}", flush=True)
    out["add113_decomposition"] = decomposition()   # added after the first run (session 30): own vs other targets, absolute power
    print("add113 decomposition (median over arms):", json.dumps(out["add113_decomposition"]), flush=True)
    (LAB / "confirm/P2de_posthoc_dpow_time.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


def decomposition() -> dict:
    """add 113: median absolute W_E power on the arm's own targets, on the other arm's targets, total, and own share, per step."""
    name, raw, spl, task, p, run, stem = TASKS[0]
    rows: dict[int, list[tuple[float, float, float]]] = {}
    for s in range(2230, 2250):
        for a, b in (("F", "G"), ("G", "F")):
            T = json.loads((LAB / "confirm" / spl / f"{stem.format(s=s, a=a)}.json").read_text(encoding="utf-8"))["targets"]
            U = json.loads((LAB / "confirm" / spl / f"{stem.format(s=s, a=b)}.json").read_text(encoding="utf-8"))["targets"]
            for t, pw in spectra(LAB / "confirm" / raw / run.format(s=s, a=a), task, p).items():
                rows.setdefault(t, []).append((pw[[k - 1 for k in T]].sum(), pw[[k - 1 for k in U]].sum(), pw.sum()))
    return {str(t): {"own": round(float(np.median([r[0] for r in v])), 3), "other": round(float(np.median([r[1] for r in v])), 4),
                     "total": round(float(np.median([r[2] for r in v])), 3),
                     "own_share": round(float(np.median([r[0] / r[2] for r in v])), 3)}
            for t, v in sorted(rows.items()) if t in (0, 500, 1000, 2000, 3000, 4000)}


if __name__ == "__main__":
    main()
