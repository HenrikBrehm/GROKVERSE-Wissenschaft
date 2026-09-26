"""GPU-001 (rule 16b/c): CPU regression, CPU-vs-GPU equivalence, GPU throughput. UNTESTED (written out of window).

Acceptance criteria are fixed in README.md BEFORE any GPU run. Pure reading of result.json / spectra.npy.
  regression   edited freq_ban.py on CPU reproduces the stored 50-step EXP-016 smoke exactly
  equivalence  GPU reruns of stored CPU runs (EXP-016 seeds 10-12, arm F, 2000 steps): criteria A1-A3
  throughput   s/step per process and aggregate steps/s for J = 1, 2, 4, 8 parallel GPU processes
Writes verdict_<mode>.json next to this file; exit 1 if a criterion fails (the queue stops on it).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
E16 = HERE.parent / "EXP-016-engineered-split"
SEEDS = (10, 11, 12)
CHECK_STEPS = (250, 500, 1000, 2000)
M = 5


def load(d: Path) -> dict:
    return json.loads((d / "result.json").read_text(encoding="utf-8"))


def top_at(d: Path, step: int) -> set[int]:
    spec, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
    pw = spec[steps.index(step)]
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:M]}


def regression() -> tuple[dict, bool]:
    name = "EXP-016_baseline_seed10_thr4_split_seed10_eps2.0"
    ref, new = load(E16 / "raw_smoke" / name), load(HERE / "raw_cpu_regression" / name)
    keys = ("train_loss", "train_acc", "test_loss", "test_acc")
    diffs = {k: float(np.max(np.abs(np.asarray(ref["dense"][k]) - np.asarray(new["dense"][k])))) for k in keys}
    same_top = ref["final_top_m_freqs"] == new["final_top_m_freqs"]
    ok = all(v == 0.0 for v in diffs.values()) and same_top and new.get("device") == "cpu"
    return {"max_abs_diff": diffs, "same_final_top5": same_top, "device": new.get("device"), "pass": ok}, ok


def equivalence() -> tuple[dict, bool]:
    rows, a1, a2_hits, a2_n, a3 = [], True, 0, 0, True
    for s in SEEDS:
        stem = f"split_seed{s}_eps2.0"
        dc = E16 / "raw" / f"EXP-016_baseline_seed{s}_thr4_{stem}"
        dg = HERE / "raw_equiv" / f"EXP-016_baseline_seed{s}_thr1_{stem}_devcuda"
        rc, rg = load(dc), load(dg)
        if rg.get("device") != "cuda" or rg["status"] != "completed" or rg["split_hash"] != rc["split_hash"]:
            return {"error": f"seed {s}: GPU run not completed / not cuda / other split"}, False
        ov = {t: len(top_at(dc, t) & top_at(dg, t)) for t in CHECK_STEPS}
        a1 &= ov[2000] >= 4                                        # A1: final top-5 overlap >= 4 in every seed
        for t in (250, 500, 1000):                                 # A2: >= 8 of 9 earlier comparisons with overlap >= 4
            a2_n += 1
            a2_hits += ov[t] >= 4
        gc, gg = rc["events"].get("generalization_step"), rg["events"].get("generalization_step")
        tol = max(100, 0.15 * gc) if gc else None                  # A3: same generalization outcome, step within tolerance
        a3_seed = (gc is None and gg is None) or (gc is not None and gg is not None and abs(gg - gc) <= tol)
        a3 &= a3_seed
        lc, lg = np.asarray(rc["dense"]["train_loss"]), np.asarray(rg["dense"]["train_loss"])
        n = min(len(lc), len(lg))
        st = np.asarray(rc["dense"]["train_steps"])[:n]
        rel = np.abs(lg[:n] - lc[:n]) / np.maximum(np.abs(lc[:n]), 1e-12)
        rows.append({"seed": s, "overlap_top5": ov, "gen_cpu": gc, "gen_gpu": gg, "A3_seed": a3_seed,
                     # Codex s12: dense train loss is logged every eval_every_train steps; report real step numbers
                     "rel_loss_diff_at_steps": {int(st[i]): float(rel[i]) for i in (1, 10, 50) if i < n},
                     "first_step_rel_diff_gt_1pct": next((int(st[i]) for i in range(n) if rel[i] > 0.01), None),
                     "sec_per_step_cpu": rc["sec_per_step"], "sec_per_step_gpu": rg["sec_per_step"],
                     "cuda_max_mem_mb": rg.get("cuda_max_mem_mb"),
                     "final_test_acc_cpu": rc["final_acc"]["test"], "final_test_acc_gpu": rg["final_acc"]["test"]})
    a2 = a2_hits >= 8
    ok = bool(a1 and a2 and a3)
    return {"rows": rows, "A1": bool(a1), "A2_hits": f"{a2_hits}/{a2_n}", "A2": bool(a2), "A3": bool(a3),
            "pass": ok}, ok


def throughput() -> tuple[dict, bool]:
    """Codex s12: a level counts only if all J processes completed on cuda; pass needs J = 1 complete."""
    levels = {}
    for J in (1, 2, 4, 8):
        sps = []
        for i in range(1, J + 1):
            for d in (HERE / "raw_par" / f"J{J}_{i}").glob("*/result.json"):
                r = json.loads(d.read_text(encoding="utf-8"))
                if r["status"] == "completed" and r.get("device") == "cuda" and r.get("steps_completed") == 500:
                    sps.append((r["sec_per_step"], r.get("cuda_max_mem_mb")))
        complete = len(sps) == J
        mean_sps = float(np.mean([x[0] for x in sps])) if sps else None
        levels[f"J{J}"] = {"n_completed": len(sps), "complete": complete, "sec_per_step_mean": mean_sps,
                           "aggregate_steps_per_s": len(sps) / mean_sps if sps else 0.0,
                           "max_mem_mb": max((x[1] or 0) for x in sps) if sps else None}
    ok = levels["J1"]["complete"]
    return {"levels": levels, "pass": ok}, ok


def main() -> None:
    mode = sys.argv[1]
    res, ok = {"regression": regression, "equivalence": equivalence, "throughput": throughput}[mode]()
    (HERE / f"verdict_{mode}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res, indent=1))
    print(f"[gpu001] {mode}: {'PASS' if ok else 'FAIL'}", flush=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
