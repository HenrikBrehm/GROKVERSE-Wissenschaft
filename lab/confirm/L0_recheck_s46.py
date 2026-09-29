"""Independent re-check of the frozen L0 block (session 46, post hoc; numpy only).

Does NOT import confirm_l0 / bound_block / result_loader / confirm_p1 / EXP-043 code; definitions were only read.
Group power (add 113): P_k = 2 (C_k^2 + S_k^2) / 113 summed over d_model, k = 1..56, with C_k = sum_x W[x] cos(2 pi k x / 113)
and S_k likewise with sin (explicit trig basis, float64, no FFT).
Delta_pow = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)].
H1 = iid256, H2 = iid64: mean, own percentile bootstrap 95 % CI, n_positive, one-sided t-test (own t tail by Gauss-Legendre
integration of the theta-density cos^(df-1)), Holm over 2. Integrity checks and the Fassung-3 descriptive analyses
(post hoc). The summary is read only after everything is computed.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CONF = ROOT / "lab" / "confirm"
RAW, SPL, BIND = CONF / "l0_raw", CONF / "l0_splits", CONF / "l0_bindings"
SEEDS = list(range(3720, 3730))
ARMS = {"iid256": 256, "iid64": 64}
BUDGET = 30000
P = 113
K = (P - 1) // 2
LATE = (25000, 27500, 30000)
FB = "lab/experiments/EXP-001-freq-ban/freq_ban.py"

x = np.arange(P)
kk = np.arange(1, K + 1)
COS = np.cos(2 * np.pi * np.outer(kk, x) / P)  # [K, P]
SIN = np.sin(2 * np.pi * np.outer(kk, x) / P)


def power(W: np.ndarray) -> np.ndarray:
    W = np.asarray(W, dtype=np.float64)[:P]
    C, S = COS @ W, SIN @ W  # [K, d]
    return (2.0 * (C ** 2 + S ** 2) / P).sum(axis=1)


def dpow(pF, pG, F, G) -> float:
    s = lambda pw, T: float(sum(pw[k - 1] for k in T))  # noqa: E731
    return math.log(s(pF, F) / s(pF, G)) + math.log(s(pG, G) / s(pG, F))


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sorted_idx_hash(a: np.ndarray) -> str:
    return hashlib.sha256(np.sort(np.asarray(a, dtype=np.int64)).astype("<i8").tobytes()).hexdigest()


_GX, _GW = np.polynomial.legendre.leggauss(200)


def _int_sin_pow(n: int, upper: float) -> float:
    """int_0^upper sin(u)^n du by 200-point Gauss-Legendre (upper <= pi/2)."""
    u = 0.5 * upper * (_GX + 1.0)
    return float(0.5 * upper * np.sum(_GW * np.sin(u) ** n))


def t_upper_tail(t: float, df: int) -> float:
    """P(T >= t) for Student t with df. Under t = sqrt(df) tan(theta) the density in theta is prop. to cos^(df-1)(theta)
    on (-pi/2, pi/2); the tail beyond theta0 equals int_0^(pi/2-theta0) sin^(df-1) / (2 int_0^(pi/2) sin^(df-1))."""
    th = math.atan(abs(t) / math.sqrt(df))
    tail = _int_sin_pow(df - 1, math.pi / 2 - th) / (2.0 * _int_sin_pow(df - 1, math.pi / 2))
    return tail if t >= 0 else 1.0 - tail


def t_test(d: np.ndarray) -> dict:
    n = len(d)
    t = float(d.mean() / (d.std(ddof=1) / math.sqrt(n)))
    return {"t": t, "df": n - 1, "p_one_sided": t_upper_tail(t, n - 1)}


def boot(d: np.ndarray, rng: np.random.Generator, B: int = 20000) -> list[float]:
    idx = rng.integers(0, len(d), size=(B, len(d)))
    m = d[idx].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def holm(ps: dict) -> dict:
    keys = sorted(ps, key=ps.get)
    out, run = {}, 0.0
    for i, k in enumerate(keys):
        run = max(run, min(1.0, (len(keys) - i) * ps[k]))
        out[k] = run
    return out


def run_id(s: int, a: str, bs: int) -> str:
    return f"EXP-018_baseline_seed{s}_thr1_l0_seed{s}_{a}_bs{bs}_devcuda"


def load_bindings() -> dict:
    out = {}
    for f in sorted(BIND.glob("*.json")):
        b = json.loads(f.read_text(encoding="utf-8"))
        out.setdefault(b.get("run_dir"), []).append(b)
    return out


def check_run(s: int, a: str, bs: int, bindings: dict) -> tuple[dict, list[str]]:
    rid, errs = run_id(s, a, bs), []
    d = RAW / rid
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    sp, te = SPL / f"l0_seed{s}_{a}.npy", SPL / f"l0_seed{s}_test.npy"
    c = r.get("config", {})
    checks = {
        "status": r.get("status") == "completed", "steps_completed": r.get("steps_completed") == BUDGET,
        "max_steps": r.get("max_steps") == BUDGET, "seed": r.get("seed") == s and c.get("seed") == s,
        "batch_size": r.get("batch_size") == bs and r.get("events", {}).get("minibatch", {}).get("batch_size") == bs,
        "order": r.get("order") == "iid", "optimizer": r.get("optimizer") == "adamw",
        "weight_decay": c.get("weight_decay") == 1.0, "lr": c.get("lr") == 1e-3, "device": r.get("device") == "cuda" and c.get("device") == "cuda",
        "task_p_frac": c.get("task") == "add" and c.get("p") == P and c.get("train_frac") == 0.3,
        "betas": c.get("beta1") == 0.9 and c.get("beta2") == 0.98,
        "split_file_name": Path(str(r.get("split_file"))).name == sp.name and Path(str(r.get("test_file"))).name == te.name,
        "split_hash": r.get("split_hash") == sorted_idx_hash(np.load(sp)),
        "test_hash": r.get("test_hash") == sorted_idx_hash(np.load(te)),
        "split_file_sha256": r.get("fingerprint_fields", {}).get("split_file_sha256") == sha_file(sp),
        "test_file_sha256": r.get("fingerprint_fields", {}).get("test_file_sha256") == sha_file(te),
    }
    errs += [f"{rid}: {k}" for k, ok in checks.items() if not ok]
    bl = bindings.get(rid, [])
    if len(bl) != 1:
        errs.append(f"{rid}: {len(bl)} bindings")
    else:
        b = bl[0]
        if b.get("exit") != 0 or b.get("manifest_commit") != "26419818":
            errs.append(f"{rid}: binding exit/commit")
        cmd = b.get("cmd", [])
        g = lambda k: cmd[cmd.index(k) + 1] if k in cmd else None  # noqa: E731
        if FB not in cmd or g("--seed") != str(s) or g("--batch-size") != str(bs) or g("--split-file") != f"lab/confirm/l0_splits/{sp.name}" \
                or g("--steps") != str(BUDGET) or g("--device") != "cuda":
            errs.append(f"{rid}: binding cmd")
        for rel, h in b.get("files", {}).items():
            if sha_file(ROOT / rel) != h:
                errs.append(f"{rid}: binding hash differs for {Path(rel).name}")
        if not any(rel.endswith("we_snapshots.npy") for rel in b.get("files", {})):
            errs.append(f"{rid}: we_snapshots not bound")
    steps = np.load(d / "we_snapshot_steps.npy").tolist()
    snaps = np.load(d / "we_snapshots.npy")
    pw = {}
    for st in LATE:
        if st not in steps:
            errs.append(f"{rid}: snapshot {st} missing")
            continue
        W = snaps[steps.index(st)]
        if not np.isfinite(W).all():
            errs.append(f"{rid}: non-finite W_E at {st}")
        pw[st] = power(W)
    dense_last_train = r["dense"]["train_acc"][-1] if r["dense"]["train_steps"][-1] == BUDGET else None
    info = {"run_id": rid, "train_acc": r["final_acc"]["train"], "test_acc": r["final_acc"]["test"],
            "dense_train_acc_30000": dense_last_train, "pw": pw}
    return info, errs


def main() -> None:
    bindings = load_bindings()
    errs: list[str] = []
    rows, runs = [], []
    for s in SEEDS:
        meta = json.loads((SPL / f"l0_seed{s}.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["F"], meta["targets"]["G"]
        if meta.get("seed") != s or set(F) & set(G) or len(F) != 5 or len(G) != 5:
            errs.append(f"seed {s}: targets meta")
        row = {"seed": s}
        for arm, bs in ARMS.items():
            info = {a: check_run(s, a, bs, bindings) for a in "FG"}
            for a in "FG":
                errs += info[a][1]
                i = info[a][0]
                runs.append({"seed": s, "arm": arm, "split": a, "run_id": i["run_id"], "train_acc": i["train_acc"], "test_acc": i["test_acc"],
                             "dense_train_acc_30000": i["dense_train_acc_30000"]})
            pF, pG = info["F"][0]["pw"], info["G"][0]["pw"]
            late = [dpow(pF[st], pG[st], F, G) for st in LATE if st in pF and st in pG]
            row[f"dpow_{arm}"] = dpow(pF[BUDGET], pG[BUDGET], F, G)
            row[f"dpow_late_mean_{arm}"] = float(np.mean(late)) if len(late) == 3 else None
            row[f"both_train_ge_099_{arm}"] = bool(info["F"][0]["train_acc"] >= 0.99 and info["G"][0]["train_acc"] >= 0.99)
        rows.append(row)
    if len(runs) != 40 or len({r["run_id"] for r in runs}) != 40:
        errs.append("not 40 distinct runs")
    extra = set(bindings) - {r["run_id"] for r in runs}
    if extra:
        errs.append(f"bindings for unexpected run dirs: {sorted(extra)}")

    rng = np.random.default_rng(4646)
    hyp = {"H1": "iid256", "H2": "iid64"}
    X = {h: np.array([r[f"dpow_{a}"] for r in rows]) for h, a in hyp.items()}
    tt = {h: t_test(x) for h, x in X.items()}
    ph = holm({h: tt[h]["p_one_sided"] for h in hyp})
    H = {}
    for h, x in X.items():
        ci = boot(x, rng)
        H[h] = {"arm": hyp[h], "mean": float(x.mean()), "sd": float(x.std(ddof=1)), "ci95_own": ci, "n_positive": int((x > 0).sum()),
                "t": tt[h]["t"], "p": tt[h]["p_one_sided"], "p_holm": ph[h],
                "verdict_own": "bestätigt" if ph[h] < 0.05 and ci[0] > 0 else "nicht bestätigt"}

    desc = {}
    for arm in ARMS:
        ra = [r for r in runs if r["arm"] == arm]
        desc[arm] = {"n_train_below_099": sum(r["train_acc"] < 0.99 for r in ra),
                     "n_test_below_099": sum(r["test_acc"] < 0.99 for r in ra),
                     "train_acc_min": min(r["train_acc"] for r in ra), "test_acc_min": min(r["test_acc"] for r in ra),
                     "dpow_late_mean": float(np.mean([r[f"dpow_late_mean_{arm}"] for r in rows])),
                     "dpow_late_min": float(min(r[f"dpow_late_mean_{arm}"] for r in rows))}
    conv = [r for r in rows if r["both_train_ge_099_iid64"]]
    xc = np.array([r["dpow_iid64"] for r in conv])
    desc["H2_converged_subset"] = {"seeds": [r["seed"] for r in conv], "n": len(conv),
                                   "mean": float(xc.mean()) if len(xc) else None,
                                   "ci95_own": boot(xc, rng) if len(xc) >= 2 else None,
                                   "t_test": t_test(xc) if len(xc) >= 2 else None}

    # self-checks of own tools
    selfcheck = {"t_tail_t0": t_upper_tail(0.0, 9), "t_tail_df1_t1": t_upper_tail(1.0, 1),  # 0.5, 0.25
                 "t_tail_df9_t2.262": t_upper_tail(2.2621571627, 9),  # ~0.025
                 "power_parseval": None}
    Wt = np.random.default_rng(1).normal(size=(P, 4))
    Wc = Wt - Wt.mean(axis=0)
    selfcheck["power_parseval"] = float(power(Wc).sum() / (Wc ** 2).sum())  # 1.0 for odd P with zero mean

    # compare with summary only now
    summ = json.loads((CONF / "L0_summary.json").read_text(encoding="utf-8"))
    sh = summ["hypotheses"]
    cmp = {}
    flags = []
    for h in hyp:
        s_ = sh[h]
        cmp[h] = {"mean_diff": H[h]["mean"] - s_["mean"], "p_diff": H[h]["p"] - s_["p"], "p_holm_diff": H[h]["p_holm"] - s_["p_holm"],
                  "p_rel_diff": (H[h]["p"] - s_["p"]) / s_["p"], "n_positive_same": H[h]["n_positive"] == s_["n_positive"],
                  "summary_ci95": s_["ci95"], "own_ci95": H[h]["ci95_own"], "verdict_same": H[h]["verdict_own"] == s_["verdict"]}
        if abs(cmp[h]["mean_diff"]) > 1e-6:
            flags.append(f"{h} mean differs by {cmp[h]['mean_diff']:.3g}")
        if not cmp[h]["n_positive_same"] or not cmp[h]["verdict_same"]:
            flags.append(f"{h} n_positive/verdict differs")
    srows = {r["seed"]: r for r in summ["rows"]}
    maxrow = 0.0
    for r in rows:
        for arm in ARMS:
            dd = abs(r[f"dpow_{arm}"] - srows[r["seed"]][f"dpow_{arm}"])
            maxrow = max(maxrow, dd)
            if dd > 1e-6:
                flags.append(f"seed {r['seed']} {arm} row differs by {dd:.3g}")
    out = {"script": "lab/confirm/L0_recheck_s46.py", "post_hoc": True, "integrity_errors": errs, "n_runs": len(runs),
           "hypotheses": H, "descriptive_post_hoc": desc, "rows": rows, "runs": runs, "selfcheck": selfcheck,
           "compare_summary": {"per_hypothesis": cmp, "max_abs_row_diff": maxrow, "summary_verdict_n": sh.get("n"), "flags": flags}}
    (CONF / "L0_recheck_s46.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("integrity_errors", "n_runs", "hypotheses", "descriptive_post_hoc", "selfcheck", "compare_summary")},
                     indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
