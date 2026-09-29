"""Independent recheck of the N54b confirmation (session 47), own numpy code; no import of confirm_n54b/confirm_p1.

Reads lab/confirm/n54b_raw (ignores *.stale_*), recomputes pi, t_half, alpha, H1/H2 and two robustness checks,
compares with lab/confirm/N54B_summary.json, writes lab/confirm/N54B_recheck_s47.json.
"""
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CONF = ROOT / "lab" / "confirm"
RAW = CONF / "n54b_raw"
P = 113
STEP = 5000
man = json.loads((CONF / "N54B_manifest.json").read_text(encoding="utf-8"))
summ = json.loads((CONF / "N54B_summary.json").read_text(encoding="utf-8"))
SEEDS, LRS, BS = man["seeds"], man["lrs"], man["batches"]
GRID = {int(k): v for k, v in man["grid"].items()}


# ---------- Student t CDF via regularized incomplete beta (Numerical Recipes continued fraction) ----------
def betacf(a, b, x):
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / d if abs(d) > 1e-300 else 1e300
    h = d
    for m in range(1, 500):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; c = 1 + aa / c
        d = 1 / (d if abs(d) > 1e-300 else 1e-300); c = c if abs(c) > 1e-300 else 1e-300
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; c = 1 + aa / c
        d = 1 / (d if abs(d) > 1e-300 else 1e-300); c = c if abs(c) > 1e-300 else 1e-300
        de = d * c; h *= de
        if abs(de - 1) < 1e-15:
            break
    return h


def ibeta(a, b, x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lb) * betacf(a, b, x) / a
    return 1 - math.exp(lb) * betacf(b, a, 1 - x) / b


def t_sf(t, df):
    """P(T > t)."""
    x = df / (df + t * t)
    tail = 0.5 * ibeta(df / 2, 0.5, x)
    return tail if t > 0 else 1 - tail


def p_greater(x, mu0):
    x = np.asarray(x, float); n = len(x)
    return t_sf((x.mean() - mu0) / (x.std(ddof=1) / math.sqrt(n)), n - 1)


def boot_ci(x, rng, B=20000):
    x = np.asarray(x, float)
    m = x[rng.integers(0, len(x), (B, len(x)))].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


# ---------- data ----------
def rdir(name):
    d = RAW / name
    return d if d.is_dir() else None


def pure_name(s, arm, bs, lr):
    return f"EXP-018_baseline_seed{s}_thr1_n54b_seed{s}_{arm}_bs{bs}{'' if lr == 0.001 else '_lr0.002'}_devcuda"


def sw_name(s, a, b, t, bs, lr):
    return (f"EXP-020_baseline_seed{s}_thr1_n54b_seed{s}_{a}_to_n54b_seed{s}_{b}_at{t}_bs{bs}"
            f"{'' if lr == 0.001 else '_lr0.002'}_devcuda")


def gpower(W):
    X = W[:P].astype(np.float64)
    sq = (np.abs(np.fft.fft(X, axis=0)) ** 2).sum(1)
    return 2.0 * sq[1:(P - 1) // 2 + 1] / P          # index k-1 -> frequency k (k and P-k combined)


issues = []
expected = {}
for s in SEEDS:
    for lr in LRS:
        for bs in BS:
            expected[pure_name(s, "F", bs, lr)] = (s, lr, bs, None)
            expected[pure_name(s, "G", bs, lr)] = (s, lr, bs, None)
            for t in GRID[bs]:
                expected[sw_name(s, "F", "G", t, bs, lr)] = (s, lr, bs, t)
                expected[sw_name(s, "G", "F", t, bs, lr)] = (s, lr, bs, t)
present = sorted(p.name for p in RAW.iterdir() if p.is_dir() and ".stale_" not in p.name)
extra = sorted(set(present) - set(expected)); missing = sorted(set(expected) - set(present))
n_ok = 0
for name, (s, lr, bs, t) in expected.items():
    d = rdir(name)
    if d is None or not (d / "result.json").exists():
        issues.append(f"missing {name}"); continue
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    c = r.get("config", {})
    bad = []
    if r.get("status") != "completed": bad.append(f"status={r.get('status')}")
    if r.get("steps_completed") != STEP or r.get("max_steps") != STEP or c.get("steps") != STEP: bad.append("steps")
    if r.get("batch_size") != bs: bad.append(f"bs={r.get('batch_size')}")
    if abs(c.get("lr", -1) - lr) > 1e-12: bad.append(f"lr={c.get('lr')}")
    if r.get("seed") != s or c.get("seed") != s: bad.append("seed")
    if t is not None and r.get("switch_step") != t: bad.append(f"switch={r.get('switch_step')}")
    if t is None and r.get("switch_step") not in (None,): bad.append(f"pure has switch={r.get('switch_step')}")
    steps = np.load(d / "we_snapshot_steps.npy").tolist()
    if STEP not in steps: bad.append("no 5000 snapshot")
    if bad: issues.append(f"{name}: {bad}")
    else: n_ok += 1

N_PAIRS = {s: int(len(np.load(CONF / "n54b_splits" / f"n54b_seed{s}_F.npy"))) for s in SEEDS}
TARGETS = {s: json.loads((CONF / "n54b_splits" / f"n54b_seed{s}.json").read_text(encoding="utf-8"))["targets"] for s in SEEDS}


def Lval(name, s):
    d = RAW / name
    steps = np.load(d / "we_snapshot_steps.npy").tolist()
    W = np.load(d / "we_snapshots.npy")[steps.index(STEP)]
    pw = gpower(W)
    f = sum(pw[k - 1] for k in TARGETS[s]["F"]); g = sum(pw[k - 1] for k in TARGETS[s]["G"])
    return math.log(f / g)


def t_half(ts, pis):
    xs = [0.0] + [float(t) for t in ts]; ys = [0.0] + list(pis)
    for i in range(1, len(xs)):
        if ys[i] >= 0.5 and ys[i - 1] < 0.5:
            return xs[i - 1] + (0.5 - ys[i - 1]) * (xs[i] - xs[i - 1]) / (ys[i] - ys[i - 1]), False
    return xs[-1], True


def slope(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    return float(((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) ** 2).sum())


rows = {}
for lr in LRS:
    for s in SEEDS:
        rec = {"pi": {}, "th": {}, "cens": {}, "th_mono": {}, "gap": {}, "valid": True}
        for bs in BS:
            LF = Lval(pure_name(s, "F", bs, lr), s); LG = Lval(pure_name(s, "G", bs, lr), s)
            rec["gap"][bs] = LF - LG
            if LF - LG < 0.5: rec["valid"] = False
            pis = []
            for t in GRID[bs]:
                a = (Lval(sw_name(s, "F", "G", t, bs, lr), s) - LG) / (LF - LG)
                b = (Lval(sw_name(s, "G", "F", t, bs, lr), s) - LF) / (LG - LF)
                pis.append((a + b) / 2)
            rec["pi"][bs] = dict(zip(GRID[bs], pis))
            rec["th"][bs], rec["cens"][bs] = t_half(GRID[bs], pis)
            rec["th_mono"][bs], _ = t_half(GRID[bs], np.maximum.accumulate(pis))
        lx = [math.log(N_PAIRS[s] / bs) for bs in BS]
        rec["alpha"] = slope(lx, [math.log(rec["th"][bs]) for bs in BS])
        rec["alpha_mono"] = slope(lx, [math.log(rec["th_mono"][bs]) for bs in BS])
        rec["alpha_1024_256"] = slope(lx[:2], [math.log(rec["th"][bs]) for bs in BS[:2]])
        rec["alpha_256_64"] = slope(lx[1:], [math.log(rec["th"][bs]) for bs in BS[1:]])
        rows[(lr, s)] = rec

rng = np.random.default_rng(470047)
lo, hi = LRS
valid1 = [s for s in SEEDS if rows[(lo, s)]["valid"]]
pairs = [s for s in SEEDS if rows[(lo, s)]["valid"] and rows[(hi, s)]["valid"]]
a1 = np.array([rows[(lo, s)]["alpha"] for s in valid1])
a2 = np.array([rows[(hi, s)]["alpha"] for s in SEEDS if rows[(hi, s)]["valid"]])
d = np.array([rows[(hi, s)]["alpha"] - rows[(lo, s)]["alpha"] for s in pairs])
p1 = max(p_greater(a1, 0.3), p_greater(-a1, -0.7))
p2 = p_greater(d, 0.0)
order = sorted([("H1", p1), ("H2", p2)], key=lambda z: z[1])
holm, run = {}, 0.0
for i, (h, p) in enumerate(order):
    run = max(run, min(1.0, (2 - i) * p)); holm[h] = run


def dstats(key):
    dd = np.array([rows[(hi, s)][key] - rows[(lo, s)][key] for s in pairs])
    return {"mean": float(dd.mean()), "sd": float(dd.std(ddof=1)), "ci95": boot_ci(dd, rng),
            "n_pos": int((dd > 0).sum()), "p_one_sided": p_greater(dd, 0.0),
            "alpha_lr1_mean": float(np.mean([rows[(lo, s)][key] for s in pairs])),
            "alpha_lr2_mean": float(np.mean([rows[(hi, s)][key] for s in pairs]))}


mine = {
    "H1": {"n_valid": len(valid1), "alpha_mean": float(a1.mean()), "alpha_sd": float(a1.std(ddof=1)),
           "ci95": boot_ci(a1, rng), "p": p1, "p_holm": holm["H1"],
           "n_censored": {bs: int(sum(rows[(lo, s)]["cens"][bs] for s in valid1)) for bs in BS}},
    "H2": {"n_valid_pairs": len(pairs), "d_alpha_mean": float(d.mean()), "d_alpha_sd": float(d.std(ddof=1)),
           "ci95": boot_ci(d, rng), "n_positive": int((d > 0).sum()), "p": p2, "p_holm": holm["H2"],
           "n_censored": {lr: {bs: int(sum(rows[(lr, s)]["cens"][bs] for s in SEEDS if rows[(lr, s)]["valid"])) for bs in BS} for lr in LRS}},
    "alpha_lr2_mean": float(a2.mean()),
    "t_half_mean": {lr: {bs: float(np.mean([rows[(lr, s)]["th"][bs] for s in SEEDS])) for bs in BS} for lr in LRS},
    "min_gap": float(min(min(r["gap"].values()) for r in rows.values())),
    "left_censored": {lr: {bs: int(sum(rows[(lr, s)]["pi"][bs][GRID[bs][0]] >= 0.5 for s in SEEDS)) for bs in BS} for lr in LRS},
    "n_nonmonotone_pi": {lr: {bs: int(sum(np.any(np.diff(list(rows[(lr, s)]["pi"][bs].values())) < 0) for s in SEEDS)) for bs in BS} for lr in LRS},
    "n_th_changed_by_mono": int(sum(abs(r["th"][bs] - r["th_mono"][bs]) > 1e-9 for r in rows.values() for bs in BS)),
}
robust = {"monotone_pi": dstats("alpha_mono"), "only_1024_256": dstats("alpha_1024_256"), "only_256_64": dstats("alpha_256_64")}
robust["monotone_pi"]["H1_p_tost"] = max(p_greater([rows[(lo, s)]["alpha_mono"] for s in valid1], 0.3),
                                        p_greater([-rows[(lo, s)]["alpha_mono"] for s in valid1], -0.7))

# ---------- compare with summary ----------
diffs = []
def cmp(label, a, b):
    diffs.append((label, float(a), float(b), abs(float(a) - float(b))))
H1s, H2s = summ["hypotheses"]["H1"], summ["hypotheses"]["H2"]
for k in ["alpha_mean", "alpha_sd", "p", "p_holm"]: cmp(f"H1.{k}", mine["H1"][k], H1s[k])
for k in ["d_alpha_mean", "d_alpha_sd", "p", "p_holm", "n_positive"]: cmp(f"H2.{k}", mine["H2"][k], H2s[k])
cmp("alpha_lr2_mean", mine["alpha_lr2_mean"], summ["secondary"]["lr0.002"]["alpha"]["mean"])
for lr in LRS:
    for bs in BS:
        cmp(f"t_half_mean lr{lr} B{bs}", mine["t_half_mean"][lr][bs], summ["secondary"][f"lr{lr}"]["t_half_mean"][str(bs)])
max_row = {"pi": 0.0, "th": 0.0, "alpha": 0.0}
for lrk, lst in summ["rows"].items():
    lr = float(lrk)
    for r in lst:
        m = rows[(lr, r["seed"])]
        if "alpha" in r: max_row["alpha"] = max(max_row["alpha"], abs(r["alpha"] - m["alpha"]))
        for bs in BS:
            if "th" in r: max_row["th"] = max(max_row["th"], abs(r["th"][str(bs)] - m["th"][bs]))
            if "pi" in r:
                for t in GRID[bs]:
                    max_row["pi"] = max(max_row["pi"], abs(r["pi"][str(bs)][str(t)] - m["pi"][bs][t]))

out = {"integrity": {"expected": len(expected), "present_nonstale": len(present), "ok": n_ok,
                     "extra": extra, "missing": missing, "issues": issues,
                     "stale_dirs": sorted(p.name for p in RAW.iterdir() if ".stale_" in p.name),
                     "n_pairs": sorted(set(N_PAIRS.values()))},
       "mine": json.loads(json.dumps(mine, default=str)),
       "robust": robust,
       "compare": [{"what": a, "mine": b, "summary": c, "absdiff": e} for a, b, c, e in diffs],
       "max_abs_diff_scalar": max(e for *_, e in diffs), "max_abs_diff_rows": max_row,
       "per_seed": {f"{lr}_{s}": {"alpha": rows[(lr, s)]["alpha"], "alpha_mono": rows[(lr, s)]["alpha_mono"],
                                  "th": rows[(lr, s)]["th"], "th_mono": rows[(lr, s)]["th_mono"]} for (lr, s) in rows}}
(CONF / "N54B_recheck_s47.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
print(json.dumps({k: out[k] for k in ["integrity", "mine", "robust", "max_abs_diff_scalar", "max_abs_diff_rows"]}, indent=1, default=str))
for c in out["compare"]: print(c)
