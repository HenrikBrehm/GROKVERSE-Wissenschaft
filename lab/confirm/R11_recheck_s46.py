"""R11 independent recheck (session 46). Numpy only; does NOT import confirm_r11 / confirm_p1 / bound_block / result_loader /
pi_persistence / EXP-043 analyze. Recomputes pi(25), pi(50) per task and seed from the raw W_E snapshots, the three hypotheses per
task (one-sided t-test, Holm over 6, own percentile bootstrap), checks run integrity, then compares with R11_summary.json
(read only after the own numbers are computed). Writes lab/confirm/R11_recheck_s46.json.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
CONF = LAB / "confirm"
RAW, SPL = CONF / "r11_raw", CONF / "r11_splits"
SEEDS = list(range(3620, 3650))
TASKS = (("add", 97), ("mul", 113))
BUDGET, SWITCH, MIN_GAP, MAX_EXCL, HALF = 2000, (25, 50), 2.0, 4, 0.5
GEN = {113: 3}          # mul: generator of Z_113^* (checked below to be primitive)
N_BOOT = 20_000


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def stem(task, p, s, arm):
    return f"r11_{task}{p}_seed{s}_{'test' if arm == 'test' else 'train_' + arm}"


def run_name(task, p, s, kind):
    f, g = stem(task, p, s, "F"), stem(task, p, s, "G")
    if kind in ("F", "G"):
        return f"EXP-043_baseline_seed{s}_thr1_{stem(task, p, s, kind)}_{task}{p}_devcuda"
    return f"EXP-044_baseline_seed{s}_thr1_{f}_to_{g}_at{kind}_{task}{p}_devcuda"


def group_rows(task, p):
    """Row indices of W_E in group order: add -> 0..p-1 (Z_p); mul -> g^i mod p, i = 0..p-2 (Z_{p-1} via discrete log)."""
    if task == "add":
        return np.arange(p)
    g = GEN[p]
    el = [1]
    for _ in range(p - 2):
        el.append(el[-1] * g % p)
    assert len(set(el)) == p - 1, "not primitive"
    return np.array(el)


def power(W, task, p):
    """Power per frequency k = 1..(n-1)//2 via explicit cos/sin projection (no FFT): 2/n * sum_d (C_k^2 + S_k^2)."""
    X = W[group_rows(task, p)].astype(np.float64)
    n = X.shape[0]
    K = (n - 1) // 2
    j = np.arange(n)[None, :]
    k = np.arange(1, K + 1)[:, None]
    ang = 2 * np.pi * ((k * j) % n) / n
    C, S = np.cos(ang) @ X, np.sin(ang) @ X
    return 2.0 * ((C ** 2).sum(1) + (S ** 2).sum(1)) / n


def t_sf(t, df):
    """P(T >= t) for Student t via s = sqrt(df) tan(theta): density ~ cos^(df-1)(theta) on (-pi/2, pi/2); Simpson."""
    def simpson(a, b, m=200_001):
        x = np.linspace(a, b, m)
        y = np.cos(x) ** (df - 1)
        h = (b - a) / (m - 1)
        return h / 3 * (y[0] + y[-1] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum())
    th = math.atan(t / math.sqrt(df))
    return float(simpson(th, math.pi / 2) / simpson(-math.pi / 2, math.pi / 2))


def ttest_p(x):
    n = len(x)
    t = x.mean() / (x.std(ddof=1) / math.sqrt(n))
    return float(t), t_sf(t, n - 1)


def holm(p):
    keys = sorted(p, key=p.get)
    out, run = {}, 0.0
    for i, k in enumerate(keys):
        run = max(run, min(1.0, (len(keys) - i) * p[k]))
        out[k] = run
    return out


def boot(x, rng, B=N_BOOT):
    idx = rng.integers(0, len(x), size=(B, len(x)))
    m = x[idx].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def check_run(task, p, s, kind, issues):
    d = RAW / run_name(task, p, s, kind)
    tag = f"{task}{p}:{s}:{kind}"
    if not (d / "result.json").exists():
        issues.append(f"{tag}: missing")
        return None
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    t = 0 if kind in ("F", "G") else int(kind)
    exp_steps = BUDGET + t
    first = "G" if kind == "G" else "F"
    c = r.get("config", {})
    ff = r.get("fingerprint_fields", {})
    probs = []
    if r.get("status") != "completed":
        probs.append(f"status {r.get('status')}")
    if r.get("steps_completed") != exp_steps or r.get("max_steps") != exp_steps:
        probs.append(f"steps {r.get('steps_completed')}/{r.get('max_steps')} != {exp_steps}")
    if r.get("seed") != s or c.get("p") != p or c.get("task") != task or r.get("device") != "cuda":
        probs.append("seed/p/task/device")
    if (c.get("lr"), c.get("weight_decay"), c.get("train_frac"), c.get("beta1"), c.get("beta2")) != (1e-3, 1.0, 0.3, 0.9, 0.98):
        probs.append("hyperparameters")
    if Path(r.get("split_file", "")).name != stem(task, p, s, first) + ".npy":
        probs.append("split_file")
    if ff.get("split_file_sha256") != sha256(SPL / f"{stem(task, p, s, first)}.npy"):
        probs.append("split sha")
    if ff.get("test_file_sha256") != sha256(SPL / f"{stem(task, p, s, 'test')}.npy"):
        probs.append("test sha")
    if t:
        if r.get("switch_step") != t or ff.get("switch_split_file_sha256") != sha256(SPL / f"{stem(task, p, s, 'G')}.npy"):
            probs.append("switch")
    elif r.get("switch_split_file") is not None:
        probs.append("unexpected switch")
    if r.get("pre_switch_betas") is not None or r.get("pre_switch_grad_every", 1) != 1 or r.get("lr_scale") != 1.0:
        probs.append("pre-switch options")
    steps = np.load(d / "we_snapshot_steps.npy")
    snaps = np.load(d / "we_snapshots.npy")
    if int(steps[-1]) != exp_steps or len(steps) != len(snaps):
        probs.append(f"last snapshot {steps[-1]}")
    W = snaps[list(steps).index(exp_steps)] if exp_steps in list(steps) else None
    if W is None or not np.isfinite(W).all():
        probs.append("snapshot non-finite/missing")
    if probs:
        issues.append(f"{tag}: " + ", ".join(probs))
    return W


def main():
    issues = []
    dirs = sorted(x.name for x in RAW.iterdir() if x.is_dir())
    expected = sorted(run_name(t, p, s, k) for t, p in TASKS for s in SEEDS for k in ("F", "G", "25", "50"))
    integ = {"n_dirs": len(dirs), "n_expected": len(expected), "n_unique_expected": len(set(expected)),
             "extra": sorted(set(dirs) - set(expected)), "missing": sorted(set(expected) - set(dirs))}
    rows, res = {}, {}
    for task, p in TASKS:
        key = f"{task}{p}"
        rows[key] = []
        for s in SEEDS:
            meta = json.loads((SPL / f"r11_{task}{p}_seed{s}.json").read_text(encoding="utf-8"))
            F, G = meta["targets"]["F"], meta["targets"]["G"]
            if meta["seed"] != s or len(F) != 5 or len(G) != 5 or set(F) & set(G):
                issues.append(f"{key}:{s}: bad target meta")
            L = {}
            for kind in ("F", "G", "25", "50"):
                W = check_run(task, p, s, kind, issues)
                pw = power(W, task, p)
                L[kind] = float(np.log(pw[np.array(F) - 1].sum() / pw[np.array(G) - 1].sum()))
            gap = L["F"] - L["G"]
            row = {"seed": s, "LF_minus_LG": gap, "valid": gap >= MIN_GAP}
            for t in SWITCH:
                row[f"pi_{t}"] = (L[str(t)] - L["G"]) / gap
            rows[key].append(row)
    pvals, X = {}, {}
    for task, p in TASKS:
        key = f"{task}{p}"
        ok = [r for r in rows[key] if r["valid"]]
        p25 = np.array([r["pi_25"] for r in ok])
        p50 = np.array([r["pi_50"] for r in ok])
        res[key] = {"n": len(ok), "n_excluded": 30 - len(ok), "evaluable": 30 - len(ok) <= MAX_EXCL,
                    "pi_means": {"25": float(p25.mean()), "50": float(p50.mean())}}
        for h, x in (("H1", p50 - p25), ("H2", p50 - HALF), ("H3", HALF - p25)):
            X[(key, h)] = x
            tt, pv = ttest_p(x)
            pvals[f"{key}:{h}"] = pv
            res[key][h] = {"mean": float(x.mean()), "sd": float(x.std(ddof=1)), "t": tt, "p": pv, "n_positive": int((x > 0).sum())}
    ph = holm(pvals)
    rng = np.random.default_rng(46046)
    rng_rep = np.random.default_rng(11)          # replicate the original's resampling stream (rng.choice, 10000, same order)
    for (key, h), x in X.items():
        ci = boot(x, rng)
        rep = np.array([rng_rep.choice(x, len(x)).mean() for _ in range(10_000)])
        e = res[key][h]
        e.update(p_holm=ph[f"{key}:{h}"], ci95_own=ci,
                 ci95_replicated_stream=[float(np.quantile(rep, 0.025)), float(np.quantile(rep, 0.975))])
        e["verdict"] = "bestätigt" if e["p_holm"] < 0.05 and ci[0] > 0 else "nicht bestätigt"

    # ---- only now read the original summary
    summ = json.loads((CONF / "R11_summary.json").read_text(encoding="utf-8"))
    hyp = summ["hypotheses"]
    cmp, flags = {}, []
    for key in res:
        o = hyp["tasks"][key]
        cmp[key] = {"n": [res[key]["n"], o.get("n")], "n_excluded": [res[key]["n_excluded"], o.get("n_excluded")]}
        for t in ("25", "50"):
            a, b = res[key]["pi_means"][t], o["pi_means"][t]
            cmp[key][f"pi_mean_{t}"] = [a, b, abs(a - b)]
            if abs(a - b) > 1e-6:
                flags.append(f"{key} pi_mean_{t} diff {a - b:.3g}")
        for h in ("H1", "H2", "H3"):
            m, oh = res[key][h], o[h]
            c = {f: [m[f], oh[f], abs(m[f] - oh[f])] for f in ("mean", "sd", "p", "p_holm")}
            c["n_positive"] = [m["n_positive"], oh["n_positive"]]
            c["ci95_own_vs_orig"] = [m["ci95_own"], oh["ci95"]]
            c["ci95_replicated_diff"] = max(abs(u - v) for u, v in zip(m["ci95_replicated_stream"], oh["ci95"]))
            c["verdict"] = [m["verdict"], oh["verdict"]]
            cmp[key][h] = c
            if c["mean"][2] > 1e-6 or c["sd"][2] > 1e-6 or c["n_positive"][0] != c["n_positive"][1]:
                flags.append(f"{key}:{h} mean/sd/npos differ")
            if abs(m["p"] - oh["p"]) > 1e-6 * max(1e-12, oh["p"]) + 1e-12:
                flags.append(f"{key}:{h} p rel diff {abs(m['p'] - oh['p']) / max(oh['p'], 1e-300):.2g}")
            if c["verdict"][0] != c["verdict"][1]:
                flags.append(f"{key}:{h} verdict differs")
            if c["ci95_replicated_diff"] > 1e-9:
                flags.append(f"{key}:{h} replicated-stream CI differs {c['ci95_replicated_diff']:.2g}")
    # per-seed rows
    row_diff = 0.0
    for key in res:
        orows = {r["seed"]: r for r in summ["rows"][key]}
        for r in rows[key]:
            o = orows[r["seed"]]
            row_diff = max(row_diff, abs(r["LF_minus_LG"] - o["LF_minus_LG"]))
            if r["valid"] != o["valid"]:
                flags.append(f"{key}:{r['seed']} validity differs")
            if r["valid"]:
                row_diff = max(row_diff, abs(r["pi_25"] - o["pi_25"]), abs(r["pi_50"] - o["pi_50"]))
    out = {"integrity": integ, "run_issues": issues, "results": res, "comparison": cmp, "max_row_abs_diff": row_diff,
           "orig_reading": hyp.get("reading"), "orig_n_technical": hyp.get("n_technical"), "flags": flags,
           "min_LF_minus_LG": {k: min(r["LF_minus_LG"] for r in v) for k, v in rows.items()}, "rows": rows}
    (CONF / "R11_recheck_s46.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("rows", "results")}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
