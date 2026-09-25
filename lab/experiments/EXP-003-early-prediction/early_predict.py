"""EXP-003: do early (<= step 2000) quantities predict the generalization step across seeds?

Read-only analysis of stored study runs (training/runs/*_arch25k). No training. Definition,
features and decision rule are fixed in README.md (committed before this script existed).
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUNS = ROOT / "training" / "runs"

EARLY_STEP = 2000
MID_STEP = 1000
NORM_REF_STEP = 500
TOP_K_FREQ = 8
N_PERM = 20_000
PERM_SEED = 0
MIN_ABS_RHO = 0.5
ALPHA = 0.05

GROUPS = {
    "explore_txf": "txf_add_p113_wd1.0_frac0.3_seed{s}_arch25k",
    "confirm_mlp512": "mlp_add_p113_wd1.0_frac0.3_seed{s}_arch25k",
    "confirm_mlp572": "mlp_add_p113_wd1.0_frac0.3_dm572_seed{s}_arch25k",
}
SEEDS = range(10)
FEATURES = ["F1_test_loss", "F2_test_loss_delta", "F3_log_train_loss",
            "F4_param_norm", "F5_norm_ratio", "F6_WE_top8_conc"]


def value_at(steps: list[int], values: list[float], step: int) -> float:
    idx = steps.index(step)   # raises if the grid does not contain the step: fail loudly
    return float(values[idx])


def param_norm(sd: dict[str, torch.Tensor]) -> float:
    return float(torch.sqrt(sum((v.double() ** 2).sum() for v in sd.values())))


def fourier_top_k_concentration(w_e: torch.Tensor, p: int, k: int) -> float:
    """Share of W_E[:p] power in the k strongest non-constant frequencies (1..(p-1)//2)."""
    x = w_e[:p].double().numpy()
    spec = np.fft.rfft(x, axis=0)                # (p//2 + 1, d_model)
    power = (np.abs(spec) ** 2).sum(axis=1)[1:(p - 1) // 2 + 1]
    return float(np.sort(power)[::-1][:k].sum() / power.sum())


def load_ckpt(run_dir: Path, step: int) -> dict[str, torch.Tensor]:
    return torch.load(run_dir / f"ckpt_step{step:06d}.pt", weights_only=True, map_location="cpu")


def embedding_matrix(sd: dict[str, torch.Tensor], emb_obj: str | None) -> torch.Tensor:
    """The study's embedding object: W_E, or the a-token half of W_in for the two-hot MLP."""
    if "W_E" in sd:
        return sd["W_E"]
    if emb_obj == "W_in_a_half":
        return sd["W_in"]   # caller slices [:p] = the a-token rows
    raise ValueError(f"no embedding object for keys {sorted(sd)} / {emb_obj!r}")


def features_for(run_id: str, runs_root: Path = RUNS) -> dict:
    run_dir = runs_root / run_id
    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    dense, p = run["dense"], run["config"]["p"]
    gen = run["transitions"]["primary"]["generalization"]["first_crossing_step"]
    if gen is None:
        raise ValueError(f"{run_id}: no generalization crossing")
    tl2 = value_at(dense["test_steps"], dense["test_loss"], EARLY_STEP)
    tl1 = value_at(dense["test_steps"], dense["test_loss"], MID_STEP)
    trl = value_at(dense["train_steps"], dense["train_loss"], EARLY_STEP)
    sd_early, sd_ref = load_ckpt(run_dir, EARLY_STEP), load_ckpt(run_dir, NORM_REF_STEP)
    n_early = param_norm(sd_early)
    return {
        "run_id": run_id, "seed": run["config"]["seed"], "arch": run["config"]["arch"],
        "split_hash": run.get("split_hash"), "generalization_step": gen,
        "F1_test_loss": tl2, "F2_test_loss_delta": tl2 - tl1,
        "F3_log_train_loss": float(np.log10(trl)), "F4_param_norm": n_early,
        "F5_norm_ratio": n_early / param_norm(sd_ref),
        "F6_WE_top8_conc": fourier_top_k_concentration(
            embedding_matrix(sd_early, run.get("embedding_object")), p, TOP_K_FREQ),
    }


def avg_ranks(v: np.ndarray) -> np.ndarray:
    """Ranks with ties averaged (generalization steps tie on the 25-step grid)."""
    order = np.argsort(v, kind="stable")
    ranks = np.empty(len(v))
    ranks[order] = np.arange(len(v), dtype=float)
    for val in np.unique(v):
        tied = v == val
        ranks[tied] = ranks[tied].mean()
    return ranks


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.corrcoef(avg_ranks(x), avg_ranks(y))[0, 1])


def perm_null(y: np.ndarray, x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    return np.array([spearman(x, rng.permutation(y)) for _ in range(N_PERM)])


def main() -> int:
    rows = {g: [features_for(pat.format(s=s)) for s in SEEDS] for g, pat in GROUPS.items()}
    rng = np.random.default_rng(PERM_SEED)
    stats: dict[str, dict] = {}
    for g, rs in rows.items():
        y = np.array([r["generalization_step"] for r in rs], dtype=float)
        stats[g] = {}
        for f in FEATURES:
            x = np.array([r[f] for r in rs])
            rho, null = spearman(x, y), perm_null(y, x, rng)
            stats[g][f] = {"rho": rho,
                           "p_two_sided": float((np.abs(null) >= abs(rho) - 1e-12).mean()),
                           "p_greater": float((null >= rho - 1e-12).mean()),
                           "p_less": float((null <= rho + 1e-12).mean())}

    explore = stats["explore_txf"]
    cand = max(FEATURES, key=lambda f: abs(explore[f]["rho"]))
    has_cand = abs(explore[cand]["rho"]) >= MIN_ABS_RHO
    confirmations = {}
    if has_cand:
        side = "p_greater" if explore[cand]["rho"] > 0 else "p_less"
        for g in ("confirm_mlp512", "confirm_mlp572"):
            confirmations[g] = {"rho": stats[g][cand]["rho"], "p_one_sided": stats[g][cand][side],
                                "passes": stats[g][cand][side] < ALPHA}
        n_pass = sum(c["passes"] for c in confirmations.values())
        verdict = {2: "bestätigt", 1: "teilweise", 0: "nicht bestätigt"}[n_pass]
    else:
        verdict = "kein Kandidat (|rho| < 0.5 in der Exploration)"

    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()
    summary = {"experiment": "EXP-003", "code_commit": commit, "n_perm": N_PERM,
               "perm_seed": PERM_SEED, "candidate": cand if has_cand else None,
               "confirmations": confirmations, "verdict": verdict, "stats": stats,
               "env": {"python": sys.version.split()[0], "torch": torch.__version__,
                       "numpy": np.__version__}}
    (HERE / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False),
                                       encoding="utf-8")
    with open(HERE / "features.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows["explore_txf"][0].keys()) + ["group"])
        w.writeheader()
        for g, rs in rows.items():
            for r in rs:
                w.writerow({**r, "group": g})
    print(json.dumps({k: summary[k] for k in ("candidate", "confirmations", "verdict")},
                     indent=2, ensure_ascii=False))
    for g in stats:
        print(g, {f: round(stats[g][f]["rho"], 3) for f in FEATURES})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
