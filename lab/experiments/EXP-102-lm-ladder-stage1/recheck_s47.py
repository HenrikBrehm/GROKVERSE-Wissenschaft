"""Independent recheck of EXP-102 pilot_summary.json (session 47). Own code, no import of analyze.py/design.py.
Power via explicit DFT matrix (not np.fft). Writes recheck_s47.json next to this file. Trains nothing."""
import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P, STEP = 113, 2000
SEEDS = list(range(3800, 3810))
RUNG = {"r0": (0, 0, 0, "answer"), "op": (1, 0, 0, "answer"), "fs": (0, 1, 0, "answer"), "tie": (0, 1, 1, "answer"),
        "all": (0, 1, 0, "all"), "allnb": (0, 1, 0, "all_but_b"),
        "tieall": (0, 1, 1, "all"), "tieallnb": (0, 1, 1, "all_but_b")}
RR = ["all", "allnb", "tieall", "tieallnb"]
n = np.arange(P)
K = np.arange(1, 57)
ANG = 2 * np.pi * np.outer(K, n) / P
C, S = np.cos(ANG), np.sin(ANG)

issues, script_hashes, gen = [], set(), {}


def pw(W):
    W = W.astype(np.float64)
    re, im = C @ W, S @ W
    return 2.0 * (re ** 2 + im ** 2).sum(1) / P


def load(s, sp, r):
    op, fs, tie, loss = RUNG[r]
    name = f"lad_seed{s}_seed{s}_{sp}_op{op}_fs{fs}_tie{tie}_loss{loss}_B0_steps{STEP}_thr1_cuda"
    d = HERE / "raw" / name
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    splitf = HERE / "splits" / f"seed{s}_{sp}.npy"
    chk = {"status": res.get("status") == "completed", "steps": res.get("steps_completed") == STEP == res.get("steps"),
           "op": bool(res.get("op_token")) == bool(op), "fs": bool(res.get("full_softmax")) == bool(fs),
           "tie": bool(res.get("tie")) == bool(tie), "loss": res.get("loss") == loss, "seed": res.get("seed") == s,
           "run_id": res.get("run_id") == name,
           "split": res.get("split_sha256") == hashlib.sha256(splitf.read_bytes()).hexdigest()}
    for k, ok in chk.items():
        if not ok:
            issues.append([name, k])
    script_hashes.add(res.get("script_sha256"))
    g = gen.setdefault((r, sp), {"n": 0, "gen": 0, "acc": []})
    g["n"] += 1
    g["gen"] += res.get("events", {}).get("generalization_step") is not None
    g["acc"].append(float(res["curve"][-1][2]))
    if res["curve"][-1][0] != STEP:
        issues.append([name, f"last curve step {res['curve'][-1][0]}"])
    steps = np.load(d / "we_snapshot_steps.npy")
    idx = np.where(steps == STEP)[0]
    if len(idx) != 1:
        issues.append([name, "no step 2000 snapshot"])
        return None
    W = np.load(d / "we_snapshots.npy")[idx[0]]
    if W.shape[0] != P:
        issues.append([name, f"snapshot rows {W.shape}"])
    return pw(W[:P])


def main():
    D = {r: {} for r in RUNG}
    share = {r: [] for r in RR}
    for s in SEEDS:
        T = json.loads((HERE / "splits" / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        iF, iG = np.array(T["F"]) - 1, np.array(T["G"]) - 1
        for r in RUNG:
            pF, pG = load(s, "F", r), load(s, "G", r)
            D[r][s] = float(np.log(pF[iF].sum()) - np.log(pF[iG].sum()) + np.log(pG[iG].sum()) - np.log(pG[iF].sum()))
        for r in RR:
            pR = load(s, "R", r)
            share[r].append(float(pR[np.concatenate([iF, iG])].sum() / pR.sum()))
    ref = json.loads((HERE / "pilot_summary.json").read_text(encoding="utf-8"))
    out = {"rungs": {}, "diffs": {}}
    cmp = []
    for r in RUNG:
        x = np.array([D[r][s] for s in SEEDS])
        row = {"mean": float(x.mean()), "n_pos": int((x > 0).sum()), "per_seed": [round(v, 4) for v in x]}
        cmp.append(abs(row["mean"] - ref["rungs"][r]["mean"]))
        if r != "r0":
            dv = x - np.array([D["r0"][s] for s in SEEDS])
            row["diff_vs_r0"] = float(dv.mean())
            cmp.append(abs(row["diff_vs_r0"] - ref["rungs"][r]["diff_vs_r0"]["mean"]))
        if row["n_pos"] != ref["rungs"][r]["n_pos"]:
            issues.append([r, "n_pos mismatch"])
        out["rungs"][r] = row
    for a, b in (("all", "allnb"), ("tieall", "tieallnb")):
        m = float(np.mean([D[a][s] - D[b][s] for s in SEEDS]))
        out["diffs"][f"{a}_minus_{b}"] = m
        cmp.append(abs(m - ref[f"{a}_minus_{b}"]["mean"]))
    out["R_target_share"] = {r: float(np.mean(v)) for r, v in share.items()}
    cmp += [abs(out["R_target_share"][r] - ref["R_target_share"][r]["mean"]) for r in RR]
    out["max_abs_diff_vs_pilot"] = float(max(cmp))
    out["generalization"] = {f"{r}_{sp}": {"n": g["n"], "n_gen": int(g["gen"]), "mean_final_test_acc": float(np.mean(g["acc"]))}
                             for (r, sp), g in sorted(gen.items())}
    out["script_sha256_distinct"] = sorted(h for h in script_hashes if h)
    out["issues"] = issues
    (HERE / "recheck_s47.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rungs"}, indent=1))
    print({r: (round(v["mean"], 4), v["n_pos"]) for r, v in out["rungs"].items()})


if __name__ == "__main__":
    main()
