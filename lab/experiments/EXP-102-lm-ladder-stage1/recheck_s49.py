"""Independent recheck (session 49, verifier) of EXP-102 'r0 lang' (analyze_r0long.py) and EXP-112 '10k' (analyze_10k.py).
Own numpy code, does not import the lab analysis modules. Reads raw run artifacts only; writes recheck_s49.json.
Delta_pow definition (reimplemented): power_k = 2 * sum_d |DFT_k(W_E[:113, d])|^2 / 113, k = 1..56 (over number tokens);
Delta = log(P_F(T_F) / P_F(T_G)) + log(P_G(T_G) / P_G(T_F)), T_X = target frequency set X of the seed (splits/seedS.json).
Bootstrap: percentile, 20 000 resamples, own rng (seed 4949) -> small CI differences to the lab scripts are expected.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-102-lm-ladder-stage1/recheck_s49.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

E102 = Path(__file__).resolve().parent
E112 = E102.parent / "EXP-112-lm-ladder-minibatch"
P, SEEDS, NB = 113, range(3800, 3810), 20_000
RNG = np.random.default_rng(4949)
ISSUES: list[str] = []


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def spectrum(W: np.ndarray) -> np.ndarray:
    W = W.astype(np.float64)
    assert W.shape[0] == P, W.shape
    n = np.arange(P)
    k = np.arange(1, (P - 1) // 2 + 1)
    ang = 2 * np.pi * np.outer(k, n) / P                   # explicit DFT, not np.fft, as independent path
    re, im = np.cos(ang) @ W, -np.sin(ang) @ W
    return 2.0 * (re ** 2 + im ** 2).sum(1) / P


def delta(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float:
    fF, fG = np.array(F) - 1, np.array(G) - 1
    a, b, c, d = pF[fF].sum(), pF[fG].sum(), pG[fF].sum(), pG[fG].sum()
    assert min(a, b, c, d) > 0
    return float(np.log(a / b) + np.log(d / c))


def boot(v: np.ndarray) -> list[float]:
    m = v[RNG.integers(0, len(v), (NB, len(v)))].mean(1)
    return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]


def targets(s: int) -> dict:
    T = json.loads((E102 / "splits" / f"seed{s}.json").read_text(encoding="utf-8"))
    assert T["seed"] == s
    F, G = T["targets"]["F"], T["targets"]["G"]
    assert len(F) == 5 and len(G) == 5 and not set(F) & set(G) and all(1 <= k <= 56 for k in F + G)
    return T["targets"]


def load(root: Path, s: int, x: str, flags: str, B: int, steps: int, want: tuple, expect: dict) -> dict:
    d = root / f"lad_seed{s}_seed{s}_{x}_{flags}_B{B}_steps{steps}_thr1_cuda"
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    chk = {"status": r["status"] == "completed", "steps_completed": r["steps_completed"] == steps, "steps": r["steps"] == steps,
           "seed": r["seed"] == s, "batch": r["batch_size"] == B,
           "split_file": r["split_file"].endswith(f"splits/seed{s}_{x}.npy"),
           "split_sha": r["split_sha256"] == sha(E102 / "splits" / f"seed{s}_{x}.npy"),
           "no_nonfinite_event": "nonfinite_step" not in r["events"]}
    chk.update({k: r[k] == v for k, v in expect.items()})
    W, S = np.load(d / "we_snapshots.npy"), [int(v) for v in np.load(d / "we_snapshot_steps.npy")]
    chk["finite"] = bool(np.isfinite(W).all())
    chk["shape"] = W.shape[1] == P and W.shape[0] == len(S)
    chk["steps_unique"] = len(set(S)) == len(S)
    chk["has_steps"] = all(t in S for t in want)
    bad = [k for k, ok in chk.items() if not ok]
    if bad:
        ISSUES.append(f"{d.name}: failed {bad}")
    curve = r["curve"] if isinstance(r["curve"], list) else json.loads(r["curve"])
    last = curve[-1]
    return {"pow": {t: spectrum(W[S.index(t)]) for t in want}, "gen": r["events"].get("generalization_step"),
            "final_test_acc": float(last[2]), "final_eval_step": int(last[0]), "script": r["script_sha256"],
            "commit": r.get("commit"), "max_test_acc": float(max(c[2] for c in curve))}


def r0long() -> dict:
    rows, meta = [], {"r0_script": set(), "all_script": set(), "r0_commit": set(), "all_commit": set()}
    raw = E102 / "raw"
    pilot_eq = []
    for s in SEEDS:
        T = targets(s)
        r0 = {x: load(E102 / "raw_r0long30k", s, x, "op0_fs0_tie0_lossanswer", 0, 30000, (2000, 10000, 30000),
                      {"op_token": False, "full_softmax": False, "tie": False, "loss": "answer"}) for x in "FG"}
        al = {x: load(E102 / "raw_long60k", s, x, "op0_fs1_tie0_lossall", 0, 60000, (10000, 30000),
                      {"op_token": False, "full_softmax": True, "tie": False, "loss": "all"}) for x in "FG"}
        for x in "FG":
            meta["r0_script"].add(r0[x]["script"]); meta["all_script"].add(al[x]["script"])
            meta["r0_commit"].add(r0[x]["commit"]); meta["all_commit"].add(al[x]["commit"])
            pd = raw / f"lad_seed{s}_seed{s}_{x}_op0_fs0_tie0_lossanswer_B0_steps2000_thr1_cuda"
            if (pd / "we_snapshots.npy").exists():   # sanity: pilot r0 at 2000 vs long r0 at 2000 (same seed/split)
                Wp, Sp = np.load(pd / "we_snapshots.npy"), [int(v) for v in np.load(pd / "we_snapshot_steps.npy")]
                pilot_eq.append(float(np.abs(spectrum(Wp[Sp.index(2000)]) - r0[x]["pow"][2000]).max()))
        row = {"seed": s, "targets": T}
        row.update({f"r0_{t}": delta(r0["F"]["pow"][t], r0["G"]["pow"][t], T["F"], T["G"]) for t in (2000, 10000, 30000)})
        row.update({f"all_{t}": delta(al["F"]["pow"][t], al["G"]["pow"][t], T["F"], T["G"]) for t in (10000, 30000)})
        row["r0_gen"] = [r0[x]["gen"] for x in "FG"]
        row["r0_final_test_acc"] = [r0[x]["final_test_acc"] for x in "FG"]
        row["all_gen"] = [al[x]["gen"] for x in "FG"]
        rows.append(row)
    g = lambda k: np.array([r[k] for r in rows])   # noqa: E731
    drift, gap30, gap10 = g("r0_30000") - g("r0_2000"), g("all_30000") - g("r0_30000"), g("all_10000") - g("r0_10000")
    cd, c30, c10 = boot(drift), boot(gap30), boot(gap10)
    out = {"means": {k: float(g(k).mean()) for k in ("r0_2000", "r0_10000", "r0_30000", "all_10000", "all_30000")},
           "r0_drift_30k_minus_2k": {"mean": float(drift.mean()), "ci95": cd, "n_pos": int((drift > 0).sum())},
           "all_minus_r0_30k": {"mean": float(gap30.mean()), "ci95": c30, "n_neg": int((gap30 < 0).sum())},
           "all_minus_r0_10k": {"mean": float(gap10.mean()), "ci95": c10, "n_neg": int((gap10 < 0).sum())},
           "reading_drift": "r0 stabil" if cd[0] <= 0 <= cd[1] else f"r0 driftet ({'hoch' if cd[0] > 0 else 'runter'})",
           "reading_gap": ("Abstand bleibt bei gleicher Schrittzahl" if c30[1] < 0 else "kein Abstand" if c30[0] <= 0 <= c30[1]
                           else "all groesser"),
           "meta": {k: sorted(map(str, v)) for k, v in meta.items()},
           "pilot_r0_2000_vs_long_r0_2000_max_abs_power_diff": {"n": len(pilot_eq), "max": max(pilot_eq) if pilot_eq else None},
           "rows": rows}
    return out


def tenk() -> dict:
    flags = {"r0B": ("op0_fs0_tie0_lossanswer", {"op_token": False, "full_softmax": False, "tie": False, "loss": "answer"}),
             "lmnbB": ("op1_fs1_tie1_lossall_but_b", {"op_token": True, "full_softmax": True, "tie": True, "loss": "all_but_b"})}
    D = {r: {5000: [], 10000: []} for r in flags}
    runs = {r: [] for r in flags}
    scripts = set()
    for s in SEEDS:
        T = targets(s)
        for r, (fl, exp) in flags.items():
            L = {x: load(E112 / "raw_10k", s, x, fl, 256, 10000, (5000, 10000), exp) for x in "FG"}
            for x in "FG":
                scripts.add(L[x]["script"])
                runs[r].append({"seed": s, "split": x, "gen": L[x]["gen"], "final_test_acc": L[x]["final_test_acc"],
                                "final_eval_step": L[x]["final_eval_step"], "max_test_acc": L[x]["max_test_acc"]})
            for t in (5000, 10000):
                D[r][t].append(delta(L["F"]["pow"][t], L["G"]["pow"][t], T["F"], T["G"]))
    out = {}
    for r in flags:
        g = [u["gen"] for u in runs[r]]
        out[r] = {"generalized_event": sum(v is not None for v in g),
                  "generalized_by_5000": sum(v is not None and v <= 5000 for v in g),
                  "final_test_acc_ge_0.95": sum(u["final_test_acc"] >= 0.95 for u in runs[r]),
                  **{str(t): {"mean": float(np.mean(D[r][t])), "ci95": boot(np.array(D[r][t])), "per_seed": D[r][t]} for t in (5000, 10000)},
                  "runs": runs[r]}
    d = np.array(D["lmnbB"][10000]) - np.array(D["r0B"][10000])
    c = boot(d)
    out["lmnbB_minus_r0B_10k"] = {"mean": float(d.mean()), "ci95": c, "n_neg": int((d < 0).sum()), "per_seed": d.tolist(),
                                  "boot_share_upper_lt_0_note": "CI upper vs 0 is the deciding margin"}
    ng = out["lmnbB"]["generalized_event"]
    out["reading"] = "bleibt schwaecher" if c[1] < 0 else "nur verzoegert" if ng >= 16 else "unklar"
    out["reading_if_final_acc_used"] = ("bleibt schwaecher" if c[1] < 0 else "nur verzoegert"
                                        if out["lmnbB"]["final_test_acc_ge_0.95"] >= 16 else "unklar")
    # robustness of the CI-vs-0 decision: share of bootstrap means >= 0 and CIs over several rng seeds
    uppers = []
    for sd in range(20):
        rg = np.random.default_rng(1000 + sd)
        m = d[rg.integers(0, len(d), (10_000, len(d)))].mean(1)
        uppers.append(float(np.quantile(m, 0.975)))
    out["lmnbB_minus_r0B_10k"]["ci_upper_over_20_rng_seeds"] = [min(uppers), max(uppers)]
    out["script_sha256"] = sorted(scripts)
    return out


def main() -> None:
    res = {"EXP-102_r0long": r0long(), "EXP-112_10k": tenk(), "issues": ISSUES,
           "method": {"bootstrap": f"percentile, {NB} resamples, rng 4949", "gen_threshold": "test acc >= 0.95 at an eval (every 25 steps)"}}
    (E102 / "recheck_s49.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    brief = {k: {kk: vv for kk, vv in v.items() if kk not in ("rows",)} if isinstance(v, dict) else v for k, v in res.items()}
    for r in ("r0B", "lmnbB"):
        brief["EXP-112_10k"][r] = {k: v for k, v in brief["EXP-112_10k"][r].items() if k != "runs"}
    print(json.dumps(brief, indent=1, default=str))


if __name__ == "__main__":
    main()
