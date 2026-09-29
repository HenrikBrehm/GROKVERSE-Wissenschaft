"""EXP-106 independent re-check (session 46). numpy only; does not import analyze.py/design.py/result_loader/confirm_p1
or EXP-043/EXP-100 code. Recomputes W_E group power (add mod 113, 2(C^2+S^2)/113 per k = 1..56, summed over d_model),
dpow, o shares, peak in O, t_gen from the dense log, integrity checks; compares with summary.json['primary'] afterwards.
  PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 python lab/tools/guarded_run.py -- python lab/experiments/EXP-106-l0-b16-long-epochs/recheck_s46.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SPL = REPO / "lab/experiments/EXP-100-set-vs-order/splits"
RAW = HERE / "raw"
SEEDS = list(range(3700, 3708))
O = [11, 12, 22, 23, 34, 45]
P, K, STEPS, WD, LR = 113, 56, 30000, 0.1, 1e-3
ARMS = {"fbw": (0, "iid", "_wd0.1"), "iid16w": (16, "iid", "_bs16_wd0.1"), "stride16w": (16, "stride", "_bs16_ordstride_wd0.1")}
NB, RNG = 20000, 4646
issues: list[str] = []


def power(W: np.ndarray) -> np.ndarray:
    x = np.arange(P)
    out = np.zeros(K)
    for k in range(1, K + 1):
        c = np.cos(2 * np.pi * k * x / P) @ W          # [d]
        s = np.sin(2 * np.pi * k * x / P) @ W
        out[k - 1] = (2.0 * (c ** 2 + s ** 2) / P).sum()
    return out


def sorted_hash(idx) -> str:
    return hashlib.sha256(np.sort(np.asarray(idx, dtype=np.int64)).astype("<i8").tobytes()).hexdigest()


def load(s: int, split: str, arm: str) -> dict:
    bs, order, suf = ARMS[arm]
    hits = sorted(RAW.glob(f"EXP-018_baseline_seed{s}_thr*_seed{s}_{split}{suf}_devcuda"))
    tag = f"{s} {split} {arm}"
    if len(hits) != 1:
        issues.append(f"{tag}: {len(hits)} dirs"); return {}
    d = hits[0]
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    c = r["config"]
    checks = {"status": r.get("status") == "completed", "steps": r.get("steps_completed") == STEPS and r.get("max_steps") == STEPS,
              "batch": (r.get("batch_size") or 0) == bs, "order": (r.get("order") or "iid") == order,
              "opt": (r.get("optimizer") or "adamw") == "adamw", "wd": c.get("weight_decay") == WD, "lr": c.get("lr") == LR,
              "p/task": c.get("p") == P and c.get("task") == "add", "seed": r.get("seed") == s,
              "split_hash": r.get("split_hash") == sorted_hash(np.load(SPL / f"seed{s}_{split}.npy")),
              "test_hash": r.get("test_hash") == sorted_hash(np.load(SPL / f"seed{s}_test.npy")),
              "split_file_sha": r["fingerprint_fields"].get("split_file_sha256") == hashlib.sha256((SPL / f"seed{s}_{split}.npy").read_bytes()).hexdigest(),
              "test_file_sha": r["fingerprint_fields"].get("test_file_sha256") == hashlib.sha256((SPL / f"seed{s}_test.npy").read_bytes()).hexdigest()}
    if bs:
        mb = r.get("events", {}).get("minibatch", {})
        checks["mb_event"] = mb.get("batch_size") == bs and (mb.get("order") or "iid") == order
    for k, ok in checks.items():
        if not ok:
            issues.append(f"{tag}: {k} fails")
    st = np.load(d / "we_snapshot_steps.npy").tolist()
    if st[-1] != STEPS:
        issues.append(f"{tag}: last snapshot {st[-1]}")
    W = np.load(d / "we_snapshots.npy")[st.index(STEPS)].astype(np.float64)[:P]
    pw = power(W)
    ts, ta = np.array(r["dense"]["test_steps"]), np.array(r["dense"]["test_acc"])
    hit = np.nonzero(ta >= 0.95)[0]
    tg = int(ts[hit[0]]) if len(hit) else None
    tr = (((r.get("transitions") or {}).get("primary") or {}).get("generalization") or {}).get("first_crossing_step")
    if tg != tr:
        issues.append(f"{tag}: t_gen dense {tg} vs transitions {tr}")
    return {"pw": pw, "tgen": tg, "o": float(pw[[k - 1 for k in O]].sum() / pw.sum()), "peak": int(np.argmax(pw)) + 1}


def dpow(pF, pG, F, G) -> float:
    s = lambda pw, S: pw[[k - 1 for k in S]].sum()   # noqa: E731
    return float(np.log(s(pF, F) / s(pF, G)) + np.log(s(pG, G) / s(pG, F)))


def ci(x) -> list[float]:
    x = np.asarray(x, float)
    m = x[np.random.default_rng(RNG).integers(0, len(x), (NB, len(x)))].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def main() -> None:
    rows = []
    for s in SEEDS:
        meta = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["F"], meta["targets"]["G"]
        row = {"seed": s}
        for arm in ARMS:
            a, b = load(s, "F", arm), load(s, "G", arm)
            row[arm] = {"dpow": dpow(a["pw"], b["pw"], F, G), "o": (a["o"] + b["o"]) / 2, "peaks": [a["peak"], b["peak"]],
                        "peakO": [a["peak"] in O, b["peak"] in O], "tgen": [a["tgen"], b["tgen"]]}
        for arm in ("iid16w", "stride16w"):
            r = load(s, "R", arm)
            row["R_" + arm] = {"o": r["o"], "peak": r["peak"], "peakO": r["peak"] in O, "tgen": r["tgen"]}
        rows.append(row)
    col = lambda arm, k: np.array([r[arm][k] for r in rows], float)   # noqa: E731
    res: dict = {"issues": issues, "n_seeds": len(rows)}
    res["dpow"] = {arm: {"mean": float(col(arm, "dpow").mean()), "ci95": ci(col(arm, "dpow"))} for arm in ARMS}
    res["o_share"] = {arm: float(col(arm, "o").mean()) for arm in ARMS}
    od = col("stride16w", "o") - col("iid16w", "o")
    res["o_diff_FG"] = {"mean": float(od.mean()), "ci95": ci(od)}
    res["stride_peak_in_O_FG"] = float(np.mean([p for r in rows for p in r["stride16w"]["peakO"]]))
    res["iid_peak_in_O_FG"] = float(np.mean([p for r in rows for p in r["iid16w"]["peakO"]]))
    rd = col("R_stride16w", "o") - col("R_iid16w", "o")
    res["R_o_diff"] = {"mean": float(rd.mean()), "ci95": ci(rd),
                       "mean_unseen_3703_3707": float(rd[3:].mean()), "median": float(np.median(rd))}
    res["R_stride_peak_in_O"] = float(np.mean(col("R_stride16w", "peakO")))
    res["R_iid_peak_in_O"] = float(np.mean(col("R_iid16w", "peakO")))
    res["R_per_seed"] = [{"seed": r["seed"], "o_iid": round(r["R_iid16w"]["o"], 4), "o_stride": round(r["R_stride16w"]["o"], 4),
                          "diff": round(r["R_stride16w"]["o"] - r["R_iid16w"]["o"], 4), "peak_iid": r["R_iid16w"]["peak"],
                          "peak_stride": r["R_stride16w"]["peak"], "tgen_iid": r["R_iid16w"]["tgen"],
                          "tgen_stride": r["R_stride16w"]["tgen"]} for r in rows]
    dd = col("stride16w", "dpow") - col("iid16w", "dpow")
    res["dpow_diff_stride_iid"] = {"mean": float(dd.mean()), "ci95": ci(dd)}
    lr = [np.log2(a / b) for r in rows for a, b in zip(r["stride16w"]["tgen"], r["iid16w"]["tgen"]) if a and b]
    lr_seed = [np.mean([np.log2(a / b) for a, b in zip(r["stride16w"]["tgen"], r["iid16w"]["tgen"]) if a and b]) for r in rows]
    res["tgen_log2_FG"] = {"n_pairs": len(lr), "mean": float(np.mean(lr)), "ci95_pairs": ci(lr), "ci95_seed_cluster": ci(lr_seed),
                           "n_positive": int(sum(x > 0 for x in lr))}
    rl = [np.log2(r["R_stride16w"]["tgen"] / r["R_iid16w"]["tgen"]) for r in rows if r["R_stride16w"]["tgen"] and r["R_iid16w"]["tgen"]]
    res["tgen_log2_R"] = {"n": len(rl), "mean": float(np.mean(rl)) if rl else None}
    res["n_generalised_FG"] = {arm: int(sum(t is not None for r in rows for t in r[arm]["tgen"])) for arm in ARMS}
    res["per_seed_FG"] = [{"seed": r["seed"], **{f"dpow_{a}": round(r[a]["dpow"], 4) for a in ARMS},
                           **{f"o_{a}": round(r[a]["o"], 4) for a in ARMS}, "peaks_stride": r["stride16w"]["peaks"],
                           "tgen_iid": r["iid16w"]["tgen"], "tgen_stride": r["stride16w"]["tgen"]} for r in rows]
    # comparison with analyze.py's summary (read only now)
    pr = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))["primary"]
    cmp = {}
    for arm in ARMS:
        cmp[f"dpow_{arm}"] = res["dpow"][arm]["mean"] - pr["dpow_end"][arm]["mean"]
        cmp[f"o_{arm}"] = res["o_share"][arm] - pr["o_share"][arm]
    cmp["dpow_diff"] = res["dpow_diff_stride_iid"]["mean"] - pr["dpow_stride_minus_iid"]["mean"]
    cmp["stride_peakO_FG"] = res["stride_peak_in_O_FG"] - pr["stride_peak_in_O_fraction"]
    cmp["R_stride_peakO"] = res["R_stride_peak_in_O"] - pr["R_stride_peak_in_O_fraction"]
    cmp["R_o_diff_unseen"] = res["R_o_diff"]["mean_unseen_3703_3707"] - pr["R_o_diff_unseen_mean"]
    cmp["tgen_log2"] = res["tgen_log2_FG"]["mean"] - pr["tgen_log2_stride_over_iid"]["mean"]
    cmp["tgen_n"] = res["tgen_log2_FG"]["n_pairs"] - pr["tgen_log2_stride_over_iid"]["n"]
    for arm in ARMS:
        cmp[f"ngen_{arm}"] = res["n_generalised_FG"][arm] - pr["n_generalised"][arm]
    res["diff_vs_summary"] = cmp
    res["flags_gt_1e-6"] = [k for k, v in cmp.items() if abs(v) > 1e-6]
    res["summary_cis"] = {"dpow": {a: pr["dpow_end"][a]["ci95"] for a in ARMS}, "o_diff": pr["o_diff_stride_minus_iid_ci95"],
                          "R_o_diff": pr["R_o_diff_ci95"], "tgen": pr["tgen_log2_stride_over_iid"]["ci95"],
                          "K2_B16": pr["K2_B16"], "Konflikt": pr["Konflikt"], "alone": pr["Reihenfolge_allein"]}
    (HERE / "recheck_s46.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
