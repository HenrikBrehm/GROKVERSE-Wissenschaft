"""Independent numpy-only recheck of EXP-108 (session 46). Reads summary.json only after computing."""
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
E100 = LAB / "experiments/EXP-100-set-vs-order"
E107 = LAB / "experiments/EXP-107-lockin-epochs"
SEEDS = range(3700, 3708)
TS = {64: (100, 200, 300, 450, 700), 1024: (25, 50, 75, 100, 150)}
N, TFB, P = 3831, 31.0, 113
issues = []
kk = np.arange(1, 57)[:, None] * np.arange(P)[None, :] * 2 * np.pi / P
COS, SIN = np.cos(kk), np.sin(kk)


def gp(W):
    X = W[:P]
    C, S = COS @ X, SIN @ X
    return 2 * ((C ** 2).sum(1) + (S ** 2).sum(1)) / P


def load(d, s, first, second, total, bs, t=None):
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    chk = [r.get("status") == "completed", r.get("steps_completed") == total, r.get("max_steps") == total,
           r.get("batch_size") == bs, r.get("seed") == s, r.get("device") == "cuda",
           str(r.get("split_file", "")).endswith(f"seed{s}_{first}.npy"),
           r.get("switch_step") == t,
           (r.get("switch_split_file") is None) if second is None else str(r.get("switch_split_file")).endswith(f"seed{s}_{second}.npy")]
    if not all(chk):
        issues.append(f"{d.name}: integrity {chk}")
    steps = np.load(d / "we_snapshot_steps.npy")
    i = np.where(steps == 5000)[0]
    if len(i) != 1:
        issues.append(f"{d.name}: no 5000 snapshot")
        return None
    W = np.load(d / "we_snapshots.npy")[i[0]]
    if not np.isfinite(W).all():
        issues.append(f"{d.name}: nonfinite")
    return gp(W)


def L(pw, F, G):
    return float(np.log(pw[np.array(F) - 1].sum() / pw[np.array(G) - 1].sum()))


def thalf(ts, ms):
    ts, ms = [0] + list(ts), [0.0] + list(ms)
    for i in range(1, len(ts)):
        if ms[i - 1] < 0.5 <= ms[i]:
            return ts[i - 1] + (0.5 - ms[i - 1]) * (ts[i] - ts[i - 1]) / (ms[i] - ms[i - 1]), False
    return float(ts[-1]), True


def slope(x, y):
    x, y = np.asarray(x), np.asarray(y)
    return float(((x - x.mean()) * (y - y.mean())).sum() / ((x - x.mean()) ** 2).sum())


r107 = {r["seed"]: r for r in json.loads((E107 / "summary.json").read_text(encoding="utf-8"))["rows"] if not r["errors"]}
rows = []
for s in SEEDS:
    T = json.loads((E100 / "splits" / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
    F, G = T["F"], T["G"]
    row = {"seed": s}
    for bs in (64, 1024):
        root, tot = (E100 / "raw", 30000) if bs == 64 else (HERE / "raw", 5000)
        pure = {x: load(root / f"EXP-018_baseline_seed{s}_thr1_seed{s}_{x}_bs{bs}_devcuda", s, x, None, tot, bs) for x in "FG"}
        LF, LG = L(pure["F"], F, G), L(pure["G"], F, G)
        row[f"sep_{bs}"] = LF - LG
        pi = {}
        for t in TS[bs]:
            fg = load(HERE / "raw" / f"EXP-020_baseline_seed{s}_thr1_seed{s}_F_to_seed{s}_G_at{t}_bs{bs}_devcuda", s, "F", "G", 5000, bs, t)
            gf = load(HERE / "raw" / f"EXP-020_baseline_seed{s}_thr1_seed{s}_G_to_seed{s}_F_at{t}_bs{bs}_devcuda", s, "G", "F", 5000, bs, t)
            pi[t] = ((L(fg, F, G) - LG) / (LF - LG) + (L(gf, F, G) - LF) / (LG - LF)) / 2
        row[f"pi_{bs}"] = pi
        row[f"th_{bs}"], row[f"cens_{bs}"] = thalf(TS[bs], [pi[t] for t in TS[bs]])
    t2 = (100, 200, 375, 750, 1500)
    row["th_256"], row["cens_256"] = thalf(t2, [r107[s][f"pi_{t}"] for t in t2])
    x = np.log([1.0, N / 1024, N / 256, N / 64])
    y = np.log([TFB, row["th_1024"], row["th_256"], row["th_64"]])
    row["alpha"] = slope(x, y)
    row["alpha_nofb"] = slope(x[1:], y[1:])
    rows.append(row)


def boot(a, seed=4646, n=10000):
    rng = np.random.default_rng(seed)
    m = a[rng.integers(0, len(a), (n, len(a)))].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


a = np.array([r["alpha"] for r in rows]); b = np.array([r["alpha_nofb"] for r in rows])
out = {"n": len(rows), "issues": issues,
       "alpha": {"mean": float(a.mean()), "ci95_own": boot(a)},
       "alpha_nofb": {"mean": float(b.mean()), "ci95_own": boot(b), "per_seed": b.tolist()},
       "n_censored": {bs: int(sum(r[f"cens_{bs}"] for r in rows)) for bs in (64, 256, 1024)},
       "t_half_mean": {bs: float(np.mean([r[f"th_{bs}"] for r in rows])) for bs in (64, 256, 1024)},
       "min_sep": {bs: float(min(r[f"sep_{bs}"] for r in rows)) for bs in (64, 1024)}}
# compare with summary (read only now)
S = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
diffs, maxd = [], 0.0
srow = {r["seed"]: r for r in S["rows"]}
for r in rows:
    q = srow.get(r["seed"])
    if q is None:
        diffs.append(f"seed {r['seed']} missing in summary"); continue
    pairs = [("alpha", r["alpha"], q["alpha"])] + [(f"th_{b}", r[f"th_{b}"], q[f"th_{b}"]) for b in (64, 256, 1024)]
    pairs += [(f"pi_{b}_{t}", r[f"pi_{b}"][t], q[f"pi_{b}"][str(t)]) for b in (64, 1024) for t in TS[b]]
    pairs += [(f"cens_{b}", float(r[f"cens_{b}"]), float(q[f"cens_{b}"])) for b in (64, 256, 1024)]
    for k, u, v in pairs:
        d = abs(u - v); maxd = max(maxd, d)
        if d > 1e-6:
            diffs.append(f"seed {r['seed']} {k}: {u} vs {v}")
pr = S["primary"]
for k, u, v in [("alpha_mean", out["alpha"]["mean"], pr["alpha"]["mean"])] + \
        [(f"th_mean_{b}", out["t_half_mean"][b], pr["t_half_mean"][str(b)]) for b in (64, 256, 1024)]:
    d = abs(u - v); maxd = max(maxd, d)
    if d > 1e-6:
        diffs.append(f"{k}: {u} vs {v}")
out.update({"summary_n": pr.get("n"), "summary_ci": pr["alpha"]["ci95"], "summary_reading": pr.get("reading"),
            "summary_ncens": pr.get("n_censored"), "max_abs_diff": maxd, "diffs": diffs, "rows": rows})
(HERE / "recheck_s46.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, default=float))
for r in rows:
    print(r["seed"], round(r["th_64"], 1), round(r["th_256"], 1), round(r["th_1024"], 1), round(r["alpha"], 3), round(r["alpha_nofb"], 3), r["cens_64"], r["cens_1024"])
