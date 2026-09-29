"""Independent recheck of EXP-110 summary.json / ext_summary.json (session 47). numpy only, own code.
Run: PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-110-lockin-lr4-pilot/recheck_s47.py
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
RAW = HERE / "raw"
SPL = LAB / "experiments/EXP-100-set-vs-order/splits"
SEEDS = (3700, 3701)
LR = 0.004
STEP = 5000
P = 113
GRID = {1024: [8, 12, 16, 20, 30, 40], 256: [20, 30, 40, 55, 75, 120],
        64: [50, 75, 100, 150, 200, 300, 400, 600, 900, 1400]}
issues = []


def load(name, seed, bs):
    d = RAW / name
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    cfg = r.get("config", {})
    checks = {"status": r.get("status") == "completed", "steps": r.get("steps_completed") == STEP,
              "max_steps": r.get("max_steps") == STEP, "bs": r.get("batch_size") == bs,
              "lr": cfg.get("lr") == LR, "seed": r.get("seed") == seed and cfg.get("seed") == seed,
              "task": cfg.get("task") == "add" and cfg.get("p") == P, "device": r.get("device") == "cuda"}
    bad = [k for k, v in checks.items() if not v]
    if bad:
        issues.append(f"{name}: {bad}")
    steps = list(np.load(d / "we_snapshot_steps.npy"))
    W = np.load(d / "we_snapshots.npy")[steps.index(STEP)][:P].astype(np.float64)
    sq = (np.abs(np.fft.fft(W, axis=0)) ** 2).sum(axis=1)
    return 2.0 * sq[1:57] / P  # k = 1..56


def logratio(pw, F, G):
    return float(np.log(sum(pw[k - 1] for k in F) / sum(pw[k - 1] for k in G)))


def thalf(ts, pis):
    xs, ys = [0] + list(ts), [0.0] + list(pis)
    for i in range(1, len(xs)):
        if ys[i - 1] < 0.5 <= ys[i]:
            return xs[i - 1] + (0.5 - ys[i - 1]) * (xs[i] - xs[i - 1]) / (ys[i] - ys[i - 1]), False
    return float(xs[-1]), True


def main():
    out = {}
    for s in SEEDS:
        T = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        F, G = T["F"], T["G"]
        out[str(s)] = {}
        for bs, ts in GRID.items():
            sfx = f"_bs{bs}_lr{LR}_devcuda"
            LF = logratio(load(f"EXP-018_baseline_seed{s}_thr1_seed{s}_F{sfx}", s, bs), F, G)
            LG = logratio(load(f"EXP-018_baseline_seed{s}_thr1_seed{s}_G{sfx}", s, bs), F, G)
            pis = []
            for t in ts:
                a = logratio(load(f"EXP-020_baseline_seed{s}_thr1_seed{s}_F_to_seed{s}_G_at{t}{sfx}", s, bs), F, G)
                b = logratio(load(f"EXP-020_baseline_seed{s}_thr1_seed{s}_G_to_seed{s}_F_at{t}{sfx}", s, bs), F, G)
                pis.append(((a - LG) / (LF - LG) + (b - LF) / (LG - LF)) / 2)
            th, c = thalf(ts, pis)
            th6, c6 = thalf(ts[:6], pis[:6])
            ncross = sum(1 for i in range(1, len(pis)) if (pis[i - 1] - 0.5) * (pis[i] - 0.5) < 0)
            out[str(s)][str(bs)] = {"sep": LF - LG, "pi": dict(zip(map(str, ts), pis)), "t_half": th, "censored": c,
                                    "t_half_first6": th6, "censored_first6": c6, "n_crossings_0.5": ncross}
    # compare
    S = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))["rows"]
    E = json.loads((HERE / "ext_summary.json").read_text(encoding="utf-8"))["rows"]
    diffs = {"sep": 0.0, "pi": 0.0, "t_half": 0.0, "ext_pi": 0.0, "ext_t_half": 0.0}
    for s in map(str, SEEDS):
        for bs in ("1024", "256", "64"):
            m, r = out[s][bs], S[s][bs]
            diffs["sep"] = max(diffs["sep"], abs(m["sep"] - r["sep"]))
            for t, v in r["pi"].items():
                diffs["pi"] = max(diffs["pi"], abs(m["pi"][t] - v))
            ref_th = m["t_half_first6"] if bs == "64" else m["t_half"]
            diffs["t_half"] = max(diffs["t_half"], abs(ref_th - r["t_half"]))
        for t, v in E[s]["pi"].items():
            diffs["ext_pi"] = max(diffs["ext_pi"], abs(out[s]["64"]["pi"][t] - v))
        diffs["ext_t_half"] = max(diffs["ext_t_half"], abs(out[s]["64"]["t_half"] - E[s]["t_half"]))
    r108 = {str(r["seed"]): r["th_64"] for r in json.loads((LAB / "experiments/EXP-108-lockin-batch-series/summary.json")
                                                          .read_text(encoding="utf-8"))["rows"]}
    r109 = json.loads((LAB / "experiments/EXP-109-lockin-lr-pilot/summary.json").read_text(encoding="utf-8"))["rows"]
    cmp = {s: {"lr4e-3": out[s]["64"]["t_half"], "lr2e-3": r109[s]["64"]["t_half"], "lr1e-3": r108.get(s),
               "4e-3_gt_1e-3": out[s]["64"]["t_half"] > r108.get(s, np.inf)} for s in map(str, SEEDS)}
    res = {"rows": out, "max_abs_diff_vs_summaries": diffs, "integrity_issues": issues, "b64_compare": cmp,
           "claim_both_seeds_4e3_gt_1e3": all(v["4e-3_gt_1e-3"] for v in cmp.values())}
    (HERE / "recheck_s47.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1, default=float))
    for s in out:
        print(s, "B64 pi:", {t: round(v, 3) for t, v in out[s]["64"]["pi"].items()}, "crossings", out[s]["64"]["n_crossings_0.5"])


if __name__ == "__main__":
    main()
