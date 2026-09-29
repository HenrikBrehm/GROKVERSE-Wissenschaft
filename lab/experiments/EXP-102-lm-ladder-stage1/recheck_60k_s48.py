"""Independent recheck of EXP-102 'all 60k' follow-up (session 48). Own numpy code only."""
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LONG = HERE / "raw_long60k"
R0 = HERE / "raw"
SEEDS = list(range(3800, 3810))
P = 113
CHECK_STEPS = (10000, 30000, 60000)


def powers(w):
    """P_k = 2*sum_d |DFT_k|^2 / 113, k = 1..56."""
    f = np.fft.fft(np.asarray(w, dtype=np.float64), axis=0)
    return 2.0 * (np.abs(f[1:57]) ** 2).sum(axis=1) / P


def tsum(pw, targets):
    return float(sum(pw[k - 1] for k in targets))


def dpow(wf, wg, tf, tg):
    pf, pg = powers(wf), powers(wg)
    return math.log(tsum(pf, tf) / tsum(pf, tg)) + math.log(tsum(pg, tg) / tsum(pg, tf))


def load_long(seed, split):
    d = LONG / f"lad_seed{seed}_seed{seed}_{split}_op0_fs1_tie0_lossall_B0_steps60000_thr1_cuda"
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    snaps = np.load(d / "we_snapshots.npy")
    steps = np.load(d / "we_snapshot_steps.npy")
    return res, snaps, steps


def snap_at(snaps, steps, t):
    idx = np.where(steps == t)[0]
    if len(idx) != 1:
        raise ValueError(f"no unique snapshot at step {t}")
    return snaps[idx[0]]


def main():
    out = {"seeds": {}, "integrity": []}
    post_vals, paired, r0_vals = [], [], []
    at = {t: [] for t in CHECK_STEPS}
    for s in SEEDS:
        tg = json.loads((HERE / "splits" / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        tf_, tg_ = tg["F"], tg["G"]
        runs = {sp: load_long(s, sp) for sp in ("F", "G")}
        gens = {}
        for sp, (res, snaps, steps) in runs.items():
            ok = res.get("status") == "completed" and res.get("steps_completed") == 60000
            fin = bool(np.isfinite(snaps).all())
            if not ok or not fin or snaps.shape[1:2] != (P,):
                out["integrity"].append(f"{s}{sp}: status={res.get('status')} steps={res.get('steps_completed')} finite={fin} shape={snaps.shape}")
            gens[sp] = (res.get("events") or {}).get("generalization_step")
        # r0
        r0 = {}
        for sp in ("F", "G"):
            d = R0 / f"lad_seed{s}_seed{s}_{sp}_op0_fs0_tie0_lossanswer_B0_steps2000_thr1_cuda"
            r0[sp] = snap_at(np.load(d / "we_snapshots.npy"), np.load(d / "we_snapshot_steps.npy"), 2000)
        d_r0 = dpow(r0["F"], r0["G"], tf_, tg_)
        r0_vals.append(d_r0)
        rec = {"gen_F": gens["F"], "gen_G": gens["G"], "dpow_r0": d_r0,
               "n_snap": [int(runs[x][1].shape[0]) for x in ("F", "G")]}
        for t in CHECK_STEPS:
            v = dpow(snap_at(runs["F"][1], runs["F"][2], t), snap_at(runs["G"][1], runs["G"][2], t), tf_, tg_)
            rec[f"dpow_{t}"] = v
            at[t].append(v)
        if gens["F"] is not None and gens["G"] is not None:
            tp = min(60000, int(math.ceil((max(gens["F"], gens["G"]) + 2000) / 1000.0)) * 1000)
            v = dpow(snap_at(runs["F"][1], runs["F"][2], tp), snap_at(runs["G"][1], runs["G"][2], tp), tf_, tg_)
            rec.update(t_post=tp, dpow_post=v, paired_minus_r0=v - d_r0)
            post_vals.append(v)
            paired.append(v - d_r0)
        out["seeds"][str(s)] = rec
    rng = np.random.default_rng(48)
    pv = np.array(post_vals)
    boots = pv[rng.integers(0, len(pv), size=(20000, len(pv)))].mean(axis=1)
    ci = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]
    r0m = float(np.mean(r0_vals))
    out["summary"] = {
        "n_evaluable": len(post_vals),
        "not_evaluable": [s for s in out["seeds"] if "dpow_post" not in out["seeds"][s]],
        "mean_post": float(pv.mean()), "boot_ci95_mean_post": ci,
        "paired_mean": float(np.mean(paired)), "paired_n_negative": int((np.array(paired) < 0).sum()),
        "dpow_mean_at": {str(t): float(np.mean(at[t])) for t in CHECK_STEPS},
        "r0_mean": r0m, "r0_half": r0m / 2,
        "ci_contains_r0_half": ci[0] <= r0m / 2 <= ci[1],
    }
    out["summary"]["reading"] = "unklar" if (len(post_vals) >= 8 and out["summary"]["ci_contains_r0_half"]) else "see README rule"
    (HERE / "recheck_60k_s48.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["summary"], indent=1))
    print("integrity:", out["integrity"] or "ok")
    for s, r in out["seeds"].items():
        print(s, r["gen_F"], r["gen_G"], r.get("t_post"), round(r.get("dpow_post", float("nan")), 3), round(r["dpow_r0"], 3))


if __name__ == "__main__":
    main()
