"""EXP-009: does the init spectrum know which frequencies a run will end up using?

Read-only analysis of stored study runs. No training. Definition and decision rule are fixed in
README.md (committed before this script existed).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

GROUPS = {
    "txf": ROOT / "training/runs/txf_add_p113_wd1.0_frac0.3_seed{s}_arch25k",
    "mlp512": ROOT / "training/runs/mlp_add_p113_wd1.0_frac0.3_seed{s}_arch25k",
    "mlp572": ROOT / "training/runs/mlp_add_p113_wd1.0_frac0.3_dm572_seed{s}_arch25k",
    "m2h": ROOT / "training/external/twohot10/runs/m2h_add_p113_wd1.0_frac0.3_seed{s}_arch25k",
}
SEEDS = range(10)
FINAL_STEP = 25_000
M = 5
N_FREQ = 56            # frequencies 1..(p-1)//2 for p = 113
N_MC = 100_000
MC_SEED = 0
ALPHA = 0.05
LOCK_MIN_OVERLAP = 4
GRID = [0, 500, 1000] + list(range(2000, 10_001, 1000)) + [12_000, 14_000, 16_000, 18_000,
                                                         20_000, 22_500, 25_000]


def spectrum(run_dir: Path, step: int, p: int) -> np.ndarray:
    """Power of frequencies 1..(p-1)//2 of the study's embedding object (rows [:p])."""
    sd = torch.load(run_dir / f"ckpt_step{step:06d}.pt", weights_only=True, map_location="cpu")
    w = sd["W_E"] if "W_E" in sd else sd["W_in"]
    x = w[:p].double().numpy()
    power = (np.abs(np.fft.rfft(x, axis=0)) ** 2).sum(axis=1)
    return power[1:(p - 1) // 2 + 1]


def ranks_desc(power: np.ndarray) -> np.ndarray:
    """rank[i] of frequency i+1, 1 = strongest."""
    order = np.argsort(-power, kind="stable")
    r = np.empty_like(order)
    r[order] = np.arange(1, len(power) + 1)
    return r


def analyse_run(run_dir: Path) -> dict:
    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    p = run["config"]["p"]
    assert (p - 1) // 2 == N_FREQ, p
    gen = run["transitions"]["primary"]["generalization"]["first_crossing_step"]
    k_final = np.argsort(-spectrum(run_dir, FINAL_STEP, p), kind="stable")[:M]   # 0-based idx
    norm_rank, overlap = {}, {}
    for t in GRID:
        r = ranks_desc(spectrum(run_dir, t, p))
        norm_rank[t] = float(((r[k_final] - 1) / (N_FREQ - 1)).mean())
        overlap[t] = int(np.isin(k_final, np.where(r <= M)[0]).sum())
    lock = None
    for t in GRID:
        if all(overlap[u] >= LOCK_MIN_OVERLAP for u in GRID if u >= t):
            lock = t
            break
    return {"run": run_dir.name, "gen": gen, "k_final": [int(k) + 1 for k in k_final],
            "norm_rank": norm_rank, "overlap_top5": overlap, "lock_step": lock}


def mc_null(n_runs: int, rng: np.random.Generator) -> np.ndarray:
    """Null distribution of the mean (over runs) of mean normalized rank of M random freqs."""
    chunk, out = 2000, []
    for start in range(0, N_MC, chunk):
        n = min(chunk, N_MC - start)
        picks = rng.random((n, n_runs, N_FREQ)).argsort(axis=2)[:, :, :M]   # M distinct ranks
        out.append((picks / (N_FREQ - 1)).mean(axis=(1, 2)))
    return np.concatenate(out)


def main() -> None:
    rows = {g: [analyse_run(Path(str(pat).format(s=s))) for s in SEEDS] for g, pat in GROUPS.items()}
    all_rows = [r for rs in rows.values() for r in rs]
    rng = np.random.default_rng(MC_SEED)
    null = mc_null(len(all_rows), rng)
    stat0 = float(np.mean([r["norm_rank"][0] for r in all_rows]))
    p0 = float((np.sum(null <= stat0) + 1) / (N_MC + 1))
    verdict = "Init traegt Information" if p0 < ALPHA else "kein Nachweis von Init-Information"
    null10 = mc_null(10, np.random.default_rng(MC_SEED + 1))
    per_group = {}
    for g, rs in rows.items():
        curve = {t: float(np.mean([r["norm_rank"][t] for r in rs])) for t in GRID}
        s0 = curve[0]
        locks = [(r["lock_step"], r["gen"]) for r in rs]
        per_group[g] = {
            "norm_rank_curve": curve,
            "p_t0_informative": float((np.sum(null10 <= s0) + 1) / (N_MC + 1)),
            "lock_vs_gen": locks,
            "share_lock_before_gen": float(np.mean([l is not None and gn is not None and l < gn
                                                    for l, gn in locks])),
            "median_lock_over_gen": float(np.median([l / gn for l, gn in locks
                                                     if l is not None and gn])),
        }
    summary = {"primary": {"stat_t0": stat0, "null_mean": float(null.mean()), "p": p0,
                           "n_runs": len(all_rows), "verdict": verdict},
               "per_group": per_group, "runs": all_rows}
    (HERE / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(f"PRIMARY t=0: rbar={stat0:.4f} null={null.mean():.4f} p={p0:.4f} -> {verdict}")
    for g, d in per_group.items():
        c = d["norm_rank_curve"]
        print(f"{g:7s} p0={d['p_t0_informative']:.3f} lock<gen={d['share_lock_before_gen']:.1f} "
              f"med L/g={d['median_lock_over_gen']:.2f} | "
              + " ".join(f"{t}:{c[t]:.2f}" for t in GRID))
        print("        (L,g):", d["lock_vs_gen"])


if __name__ == "__main__":
    main()
