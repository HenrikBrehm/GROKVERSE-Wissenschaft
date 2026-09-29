"""EXP-107 independent recheck (session 46). numpy only; does not import analyze.py / design.py / result_loader / EXP-043.
  PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 python lab/tools/guarded_run.py -- python lab/experiments/EXP-107-lockin-epochs/recheck_s46.py
W_E group power at step 5000 (add mod 113): P_k = 2 (C_k^2 + S_k^2)/113, k = 1..56, summed over d_model, computed with explicit
cos/sin sums (not FFT). L = log[P(F targets)/P(G targets)];
pi(t) = ((L_FG - L_G)/(L_F - L_G) + (L_GF - L_F)/(L_G - L_F)) / 2.
Own bootstrap: percentile, 20 000 resamples, rng 4646 (different from analyze.py on purpose).
summary.json is read only after everything is computed.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
E100 = REPO / "lab/experiments/EXP-100-set-vs-order"
SPL = E100 / "splits"
SEEDS = range(3700, 3708)
TS = (100, 200, 375, 750, 1500)
TOTAL = 5000
P = 113
N_TRAIN = 3831
B = 256


def idx_hash(path: Path) -> str:
    a = np.sort(np.asarray(np.load(path), dtype=np.int64)).astype("<i8")
    return hashlib.sha256(a.tobytes()).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def power(W: np.ndarray) -> np.ndarray:
    X = W[:P].astype(np.float64)
    a = np.arange(P)
    k = np.arange(1, (P - 1) // 2 + 1)
    ang = 2 * np.pi * np.outer(k, a) / P
    C, S = np.cos(ang) @ X, np.sin(ang) @ X            # [56, d]
    return (2.0 * (C ** 2 + S ** 2) / P).sum(axis=1)


def load(d: Path, s: int, first: str, second: str | None, t: int | None, max_steps: int, issues: list) -> np.ndarray:
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    ff = r.get("fingerprint_fields", {})
    chk = [(r.get("status") == "completed", "status"), (r.get("steps_completed") == max_steps, "steps_completed"),
           (r.get("max_steps") == max_steps, "max_steps"), (r.get("batch_size") == B, "batch_size"),
           (r.get("order") == "iid", "order"), (r.get("seed") == s, "seed"),
           (r["config"]["p"] == P and r["config"]["task"] == "add", "config"),
           (r.get("switch_step") == t, "switch_step"),
           (r.get("split_hash") == idx_hash(SPL / f"seed{s}_{first}.npy"), "split_hash"),
           (ff.get("split_file_sha256") == file_hash(SPL / f"seed{s}_{first}.npy"), "split_file_sha256"),
           (r.get("test_hash") == idx_hash(SPL / f"seed{s}_test.npy"), "test_hash")]
    if second is None:
        chk.append((r.get("switch_hash") is None, "switch_hash none"))
    else:
        chk += [(r.get("switch_hash") == idx_hash(SPL / f"seed{s}_{second}.npy"), "switch_hash"),
                (ff.get("switch_split_file_sha256") == file_hash(SPL / f"seed{s}_{second}.npy"), "switch_file_sha256"),
                (r.get("events", {}).get("switch", {}).get("step") == t, "switch event step")]
    for ok, name in chk:
        if not ok:
            issues.append(f"{d.name}: {name}")
    steps = np.load(d / "we_snapshot_steps.npy").tolist()
    if steps.count(TOTAL) != 1:
        issues.append(f"{d.name}: snapshot {TOTAL} count {steps.count(TOTAL)}")
    W = np.load(d / "we_snapshots.npy")[steps.index(TOTAL)]
    if not np.isfinite(W).all():
        issues.append(f"{d.name}: non-finite")
    return power(W)


def one(root: Path, pat: str) -> Path:
    h = sorted(root.glob(pat))
    if len(h) != 1:
        raise SystemExit(f"{pat}: {len(h)} matches")
    return h[0]


def boot(x: np.ndarray, rng: np.random.Generator, n: int = 20_000) -> list[float]:
    m = x[rng.integers(0, len(x), size=(n, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def main() -> None:
    issues: list[str] = []
    rows = []
    for s in SEEDS:
        T = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        F, G = [k - 1 for k in T["F"]], [k - 1 for k in T["G"]]
        lr = lambda pw: float(np.log(pw[F].sum() / pw[G].sum()))   # noqa: E731
        LF = lr(load(one(E100 / "raw", f"EXP-018_baseline_seed{s}_thr*_seed{s}_F_bs256_devcuda"), s, "F", None, None, 30000, issues))
        LG = lr(load(one(E100 / "raw", f"EXP-018_baseline_seed{s}_thr*_seed{s}_G_bs256_devcuda"), s, "G", None, None, 30000, issues))
        row = {"seed": s, "LF": LF, "LG": LG}
        for t in TS:
            LFG = lr(load(one(HERE / "raw", f"EXP-020_baseline_seed{s}_thr*_seed{s}_F_to_seed{s}_G_at{t}_bs256_devcuda"), s, "F", "G", t, TOTAL, issues))
            LGF = lr(load(one(HERE / "raw", f"EXP-020_baseline_seed{s}_thr*_seed{s}_G_to_seed{s}_F_at{t}_bs256_devcuda"), s, "G", "F", t, TOTAL, issues))
            row[f"pi_{t}"] = ((LFG - LG) / (LF - LG) + (LGF - LF) / (LG - LF)) / 2
        rows.append(row)
    rng = np.random.default_rng(4646)
    col = {t: np.array([r[f"pi_{t}"] for r in rows]) for t in TS}
    pi = {t: {"mean": float(col[t].mean()), "ci95": boot(col[t], rng), "min": float(col[t].min()), "max": float(col[t].max())} for t in TS}
    d = boot(col[750] - col[375], rng)
    ts, ms = [0] + list(TS), [0.0] + [pi[t]["mean"] for t in TS]
    half = next((ts[i - 1] + (0.5 - ms[i - 1]) * (ts[i] - ts[i - 1]) / (ms[i] - ms[i - 1])
                 for i in range(1, len(ts)) if ms[i - 1] < 0.5 <= ms[i]), None)
    mine = {"issues": issues, "n_runs": 8 * (2 + 2 * len(TS)), "min_LF_minus_LG": min(r["LF"] - r["LG"] for r in rows),
            "pi": pi, "d_750_minus_375_ci95": d, "t_half_steps": half, "t_half_epochs": None if half is None else half / (N_TRAIN / B),
            "per_seed_pi_100": col[100].tolist(), "per_seed_pi_200": col[200].tolist(), "rows": rows}
    # --- only now read summary.json ---
    S = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))
    diffs = []
    srows = {r["seed"]: r for r in S["rows"]}
    for r in rows:
        for t in TS:
            v = srows[r["seed"]].get(f"pi_{t}")
            if v is None or abs(v - r[f"pi_{t}"]) > 1e-6:
                diffs.append(f"seed {r['seed']} pi_{t}: summary {v} vs {r[f'pi_{t}']}")
    Sp = S["primary"]
    for t in TS:
        v = Sp["pi"][str(t)]["mean"]
        if abs(v - pi[t]["mean"]) > 1e-6:
            diffs.append(f"mean pi_{t}: {v} vs {pi[t]['mean']}")
    if abs(Sp["t_half_steps"] - half) > 1e-6:
        diffs.append(f"t_half: {Sp['t_half_steps']} vs {half}")
    ci_cmp = {t: {"summary": Sp["pi"][str(t)]["ci95"], "mine": pi[t]["ci95"]} for t in TS}
    ci_cmp["d_750_375"] = {"summary": Sp["d_750_minus_375_ci95"], "mine": d}
    m = {t: pi[t]["mean"] for t in TS}
    rd = ("Epochen-Uhr gestuetzt" if m[375] < 0.5 < m[750] and d[0] > 0 else "frueher als in Epochen" if m[375] >= 0.5
          else "spaeter als in Epochen" if m[750] < 0.5 <= m[1500] else "keine Festlegung bis 100 Epochen" if m[1500] < 0.5 else "gemischt")
    mine.update({"reading_mine": rd, "reading_summary": Sp["reading"], "n_summary": Sp["n"], "diffs_gt_1e-6": diffs, "ci_compare": ci_cmp})
    (HERE / "recheck_s46.json").write_text(json.dumps(mine, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in mine.items() if k != "rows"}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
