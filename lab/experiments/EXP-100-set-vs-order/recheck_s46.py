"""EXP-100 independent re-check (session 46). Reads raw/ and raw_fb30k/ directly; does NOT import analyze.py, design.py,
result_loader or confirm_p1 (definitions re-implemented from reading them). numpy only. Writes recheck_s46.json.
Compared with summary.json only at the very end (printed side by side)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SPL = HERE / "splits"
SEEDS = range(3700, 3708)
O = (11, 12, 22, 23, 34, 45)
P, K = 113, 56
N_BOOT, BOOT_SEED = 10_000, 46
# arm -> (root, run-id suffix, batch, order, steps)
ARMS = {"fb": ("raw", "", 0, "iid", 2000), "fb30k": ("raw_fb30k", "", 0, "iid", 30000),
        "iid256": ("raw", "_bs256", 256, "iid", 30000), "iid64": ("raw", "_bs64", 64, "iid", 30000),
        "stride256": ("raw", "_bs256_ordstride", 256, "stride", 30000), "stride64": ("raw", "_bs64_ordstride", 64, "stride", 30000)}
R_ARMS = ("iid256", "stride256", "iid64", "stride64")
ISSUES: list[str] = []


def shash(path: Path) -> str:
    return hashlib.sha256(np.sort(np.load(path).astype(np.int64)).astype("<i8").tobytes()).hexdigest()


def fsha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def power(W: np.ndarray) -> np.ndarray:
    """Power per k = 1..56 over the 113 number rows, summed over d_model; orthonormal real basis (2|X_k|^2 / n)."""
    X = np.asarray(W, dtype=np.float64)[:P]
    n = np.arange(P)
    out = np.empty(K)
    for k in range(1, K + 1):     # explicit DFT (no np.fft), independent of the EXP-043 implementation
        c, s = np.cos(2 * np.pi * k * n / P), np.sin(2 * np.pi * k * n / P)
        out[k - 1] = 2.0 * (((c @ X) ** 2).sum() + ((s @ X) ** 2).sum()) / P
    return out


def dpow(pF, pG, F, G) -> float:
    S = lambda pw, T: pw[[k - 1 for k in T]].sum()   # noqa: E731
    return float(np.log(S(pF, F) / S(pF, G)) + np.log(S(pG, G) / S(pG, F)))


def o_share(pw) -> float:
    return float(pw[[k - 1 for k in O]].sum() / pw.sum())


def peak_in_o(pw) -> bool:
    return int(np.argmax(pw)) + 1 in O


def load(s: int, split: str, arm: str) -> dict | None:
    root, suf, bs, order, steps = ARMS[arm]
    hits = sorted((HERE / root).glob(f"EXP-018_baseline_seed{s}_thr*_seed{s}_{split}{suf}_devcuda"))
    tag = f"{s} {split} {arm}"
    if len(hits) != 1:
        ISSUES.append(f"{tag}: {len(hits)} dirs")
        return None
    d = hits[0]
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    cfg = r.get("config", {})
    chk = {"status": (r.get("status"), "completed"), "seed": (r.get("seed"), s), "device": (r.get("device"), "cuda"),
           "cfg.device": (cfg.get("device"), "cuda"), "max_steps": (r.get("max_steps"), steps),
           "steps_completed": (r.get("steps_completed"), steps), "cfg.steps": (cfg.get("steps"), steps),
           "stop_after_gen": (r.get("stop_after_generalization"), steps),
           "batch_size": (r.get("batch_size") or 0, bs), "order": (r.get("order") or "iid", order),
           "optimizer": (r.get("optimizer") or "adamw", "adamw"), "wd": (cfg.get("weight_decay"), 1.0),
           "lr": (cfg.get("lr"), 0.001), "p": (cfg.get("p"), 113), "task": (cfg.get("task"), "add"),
           "split_hash": (r.get("split_hash"), shash(SPL / f"seed{s}_{split}.npy")),
           "test_hash": (r.get("test_hash"), shash(SPL / f"seed{s}_test.npy")),
           "split_file_sha": (r.get("fingerprint_fields", {}).get("split_file_sha256"), fsha(SPL / f"seed{s}_{split}.npy")),
           "test_file_sha": (r.get("fingerprint_fields", {}).get("test_file_sha256"), fsha(SPL / f"seed{s}_test.npy"))}
    if bs:
        mb = r.get("events", {}).get("minibatch", {})
        chk["mb.batch"] = (mb.get("batch_size"), bs)
        chk["mb.order"] = (mb.get("order"), order)
        chk["mb.spe"] = (mb.get("steps_per_epoch"), int(np.ceil(len(np.load(SPL / f"seed{s}_{split}.npy")) / bs)))
    else:
        chk["no_minibatch_event"] = ("minibatch" in r.get("events", {}), False)
    for k, (got, want) in chk.items():
        if got != want:
            ISSUES.append(f"{tag}: {k} {got!r} != {want!r}")
    W, st = np.load(d / "we_snapshots.npy"), np.load(d / "we_snapshot_steps.npy").tolist()
    if steps not in st or 2000 not in st or not np.isfinite(W).all():
        ISSUES.append(f"{tag}: snapshots missing/non-finite")
        return None
    gen = r.get("transitions", {}).get("primary", {}).get("generalization", {}).get("first_crossing_step")
    ts, ta = np.array(r["dense"]["test_steps"]), np.array(r["dense"]["test_acc"])
    hit = np.nonzero(ta >= 0.95)[0]
    gen_dense = int(ts[hit[0]]) if hit.size else None
    if gen != gen_dense:
        ISSUES.append(f"{tag}: t_gen transitions {gen} != dense {gen_dense}")
    spe = r.get("events", {}).get("minibatch", {}).get("steps_per_epoch", 1) if bs else 1
    return {"end": power(W[st.index(steps)]), "at2k": power(W[st.index(2000)]), "W2k": W[st.index(2000)],
            "Wall": {t: W[i] for i, t in enumerate(st) if t <= 2000}, "t_gen": gen, "spe": spe,
            "final_test": r.get("final_acc", {}).get("test"), "final_train": r.get("final_acc", {}).get("train")}


def boot(x: np.ndarray) -> list[float]:
    rng = np.random.default_rng(BOOT_SEED)
    m = x[rng.integers(0, len(x), size=(N_BOOT, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def main() -> None:
    # sanity: my power() equals an FFT-based version on one snapshot
    W0 = np.load(next((HERE / "raw").glob("EXP-018_*seed3700_F_devcuda")) / "we_snapshots.npy")[-1][:P].astype(np.float64)
    fft_pw = 2.0 * (np.abs(np.fft.fft(W0, axis=0)) ** 2).sum(axis=1)[1:K + 1] / P
    pw_diff = float(np.max(np.abs(power(W0) - fft_pw) / fft_pw))
    rows, runs = [], {}
    for s in SEEDS:
        meta = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["F"], meta["targets"]["G"]
        if set(F) & set(O) or set(G) & set(O) or set(F) & set(G):
            ISSUES.append(f"{s}: target sets overlap O or each other")
        row = {"seed": s}
        for arm in ARMS:
            a, b = load(s, "F", arm), load(s, "G", arm)
            runs[(s, "F", arm)], runs[(s, "G", arm)] = a, b
            if a is None or b is None:
                continue
            row[f"dpow_end_{arm}"] = dpow(a["end"], b["end"], F, G)
            row[f"dpow_2k_{arm}"] = dpow(a["at2k"], b["at2k"], F, G)
            row[f"o_{arm}"] = (o_share(a["end"]) + o_share(b["end"])) / 2
            row[f"peakO_{arm}"] = [peak_in_o(a["end"]), peak_in_o(b["end"])]
            row[f"tgen_{arm}"] = [a["t_gen"], b["t_gen"]]
            row[f"final_{arm}"] = [(a["final_train"], a["final_test"]), (b["final_train"], b["final_test"])]
        for arm in R_ARMS:
            r = load(s, "R", arm)
            if r is not None:
                row[f"R_o_{arm}"], row[f"R_peakO_{arm}"], row[f"R_tgen_{arm}"] = o_share(r["end"]), peak_in_o(r["end"]), r["t_gen"]
        rows.append(row)
    ok = [r for r in rows if all(f"dpow_end_{a}" in r for a in ("fb", "fb30k", "iid256", "iid64", "stride256"))]
    col = lambda k, rs=ok: np.array([r[k] for r in rs], dtype=float)   # noqa: E731
    res: dict = {"n_valid": len(ok), "power_impl_max_rel_diff_vs_fft": pw_diff, "issues": ISSUES, "arms": {}}
    for arm in ARMS:
        rs = [r for r in ok if f"dpow_end_{arm}" in r]
        res["arms"][arm] = {"n": len(rs), "dpow_end_mean": float(col(f"dpow_end_{arm}", rs).mean()),
                            "dpow_end_ci95": boot(col(f"dpow_end_{arm}", rs)),
                            "dpow_2k_mean": float(col(f"dpow_2k_{arm}", rs).mean()),
                            "o_share_mean": float(col(f"o_{arm}", rs).mean()),
                            "peak_in_O_fraction": float(np.mean([p for r in rs for p in r[f"peakO_{arm}"]])),
                            "n_generalised": int(sum(t is not None for r in rs for t in r[f"tgen_{arm}"])),
                            "n_runs": 2 * len(rs)}
    for B in (256, 64):
        st, iid = f"stride{B}", f"iid{B}"
        rs = [r for r in ok if f"o_{st}" in r and f"o_{iid}" in r]
        rr = [r for r in ok if f"R_o_{st}" in r and f"R_o_{iid}" in r]
        dd = col(f"dpow_end_{st}", rs) - col(f"dpow_end_{iid}", rs)
        res[f"B{B}"] = {"o_diff_FG_mean": float((col(f"o_{st}", rs) - col(f"o_{iid}", rs)).mean()),
                        "o_diff_FG_ci95": boot(col(f"o_{st}", rs) - col(f"o_{iid}", rs)),
                        "R_o_diff_mean": float((col(f"R_o_{st}", rr) - col(f"R_o_{iid}", rr)).mean()),
                        "R_o_diff_ci95": boot(col(f"R_o_{st}", rr) - col(f"R_o_{iid}", rr)),
                        "R_stride_peak_in_O_fraction": float(np.mean([r[f"R_peakO_{st}"] for r in rr])),
                        "R_n_generalised": {a: int(sum(r[f"R_tgen_{a}"] is not None for r in rr)) for a in (st, iid)},
                        "dpow_stride_minus_iid_mean": float(dd.mean()), "dpow_stride_minus_iid_ci95": boot(dd)}
    # fb vs fb30k: identical up to step 2000?
    cmp = []
    for s in SEEDS:
        for x in "FG":
            a, b = runs[(s, x, "fb")], runs[(s, x, "fb30k")]
            if a and b:
                cmp.append({t: float(np.max(np.abs(a["Wall"][t] - b["Wall"][t]))) for t in a["Wall"] if t in b["Wall"]})
    res["fb_vs_fb30k_max_abs_W_diff_by_step"] = {str(t): max(c[t] for c in cmp) for t in cmp[0]}
    res["fb_vs_fb30k_dpow2k_max_abs_diff"] = float(np.max(np.abs(col("dpow_2k_fb") - col("dpow_2k_fb30k"))))
    res["rows"] = rows
    (HERE / "recheck_s46.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    report(res)


def report(res: dict) -> None:
    print(f"n_valid {res['n_valid']}  power impl vs fft rel diff {res['power_impl_max_rel_diff_vs_fft']:.2e}")
    print("issues:", len(res["issues"]))
    for i in res["issues"]:
        print("  ", i)
    prim = json.loads((HERE / "summary.json").read_text(encoding="utf-8"))["primary"]
    print("\narm        n  dpow_end mine [CI]              | summary mean [CI]              | dpow2k mine / sum      | o mine / sum      | peakO | ngen mine/sum")
    for arm, m in res["arms"].items():
        se = prim.get("dpow_end", {}).get(arm, {})
        s2 = prim.get("dpow_2k", {}).get(arm)
        so = prim.get("o_share", {}).get(arm)
        sg = prim.get("n_generalised", {}).get(arm)
        flag = ""
        for mine, theirs in ((m["dpow_end_mean"], se.get("mean")), (m["dpow_2k_mean"], s2), (m["o_share_mean"], so)):
            if theirs is not None and abs(mine - theirs) > 1e-6:
                flag = " <-- DIFF"
        print(f"{arm:9s} {m['n']:2d}  {m['dpow_end_mean']:8.4f} [{m['dpow_end_ci95'][0]:7.3f},{m['dpow_end_ci95'][1]:7.3f}] | "
              f"{se.get('mean', float('nan')):8.4f} {se.get('ci95')} | {m['dpow_2k_mean']:8.4f} / {s2} | "
              f"{m['o_share_mean']:.5f} / {so} | {m['peak_in_O_fraction']:.3f} | {m['n_generalised']}/{m['n_runs']} vs {sg}{flag}")
    for B in (256, 64):
        b = res[f"B{B}"]
        sp = prim if B == 256 else prim.get("Konflikt_B64", {})
        print(f"\nB{B}: o(stride)-o(iid) F/G mean {b['o_diff_FG_mean']:.5f} CI {b['o_diff_FG_ci95']}  | summary CI {sp.get('o_diff_stride_minus_iid_ci95')}")
        print(f"      R o diff mean {b['R_o_diff_mean']:.5f} CI {b['R_o_diff_ci95']}  | summary {sp.get('R_o_diff_ci95')}")
        print(f"      R stride peak in O {b['R_stride_peak_in_O_fraction']}  | summary {sp.get('R_stride_peak_in_O_fraction')};"
              f" F/G stride peak in O {res['arms'][f'stride{B}']['peak_in_O_fraction']} | summary {sp.get('stride_peak_in_O_fraction')}")
        print(f"      dpow stride-iid mean {b['dpow_stride_minus_iid_mean']:.5f} CI {b['dpow_stride_minus_iid_ci95']} | summary {sp.get('dpow_stride_minus_iid')}")
        print(f"      R n_generalised {b['R_n_generalised']}")
    print("\nfb vs fb30k max |dW| by step:", res["fb_vs_fb30k_max_abs_W_diff_by_step"])
    print("fb vs fb30k max |dpow2k diff|:", res["fb_vs_fb30k_dpow2k_max_abs_diff"])
    print("summary readings:", {k: prim.get(k) for k in ("K2_MB", "Konflikt", "Reihenfolge_allein")},
          {k: prim.get("Konflikt_B64", {}).get(k) for k in ("Konflikt", "Reihenfolge_allein")})


if __name__ == "__main__":
    main()
