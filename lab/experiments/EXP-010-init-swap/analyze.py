"""EXP-010: does the final frequency set follow swapped init coefficients? (UNTESTED)

Read-only analysis. Baselines: EXP-003d raw_d (freq_ban.py baseline, seeds 10-19, stop-after-gen 25).
Swaps: raw/ (freq_ban.py init_swap). Definition and decision rule: README.md.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
BASE = LAB / "experiments/EXP-003-early-prediction/raw_d/EXP-001_baseline_t2000_m5_seed{s}_thr4"
SWAP = HERE / "raw/EXP-010_init_swap_t2000_m5_seed{s}_thr4"
SEEDS = range(10, 20)
M, N_FREQ = 5, 56
ALPHA, MIN_VALID = 0.05, 8
N_MC, MC_SEED = 100_000, 0


def load(d: Path) -> tuple[dict, np.ndarray, list[int]]:
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    return res, np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()


def pair(seed: int) -> dict:
    row: dict = {"seed": seed, "valid": False}
    try:
        base, base_spec, base_steps = load(Path(str(BASE).format(s=seed)))
        swap, _, _ = load(Path(str(SWAP).format(s=seed)))
    except FileNotFoundError as e:
        row["reason"] = f"missing: {e.filename}"
        return row
    if base["status"] != "completed" or swap["status"] != "completed":
        row["reason"] = f"status base={base['status']} swap={swap['status']}"
        return row
    if base["split_hash"] != swap["split_hash"]:
        row["reason"] = "split_hash differs"
        return row
    ev = swap["events"]["init_swap"]
    if not np.allclose(base_spec[base_steps.index(0)], ev["power_before"], rtol=1e-5):
        row["reason"] = "baseline init spectrum != swap power_before"
        return row
    T = {k for k, _ in ev["pairs"]}
    S = {j for _, j in ev["pairs"]}
    kb, ks = set(base["final_top_m_freqs"]), set(swap["final_top_m_freqs"])
    d = (len(ks & S) - len(ks & T)) - (len(kb & S) - len(kb & T))
    gb, gs = base["events"].get("generalization_step"), swap["events"].get("generalization_step")
    init_rank = np.argsort(np.argsort(-np.asarray(ev["power_before"]), kind="stable"), kind="stable")
    row.update({"valid": True, "T": sorted(T), "S": sorted(S), "K_base": sorted(kb),
                "K_swap": sorted(ks), "d": d, "gen_base": gb, "gen_swap": gs,
                "delta_gen": None if gb is None or gs is None else gs - gb,
                "rbar0_base": float((init_rank[[k - 1 for k in kb]] / (N_FREQ - 1)).mean())})
    return row


def sign_flip_p(d: np.ndarray) -> float:
    obs = d.mean()
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= obs - 1e-12).mean())


def main() -> None:
    rows = [pair(s) for s in SEEDS]
    valid = [r for r in rows if r["valid"]]
    out: dict = {"rows": rows, "n_valid": len(valid)}
    if len(valid) < MIN_VALID:
        out["verdict"] = "nicht auswertbar"
    else:
        d = np.array([r["d"] for r in valid], dtype=float)
        p = sign_flip_p(d)
        out.update({"d_mean": float(d.mean()), "p": p,
                    "verdict": "widerspricht" if d.mean() <= 0 else
                    ("steuerbar" if p < ALPHA else "richtungsgleich, nicht signifikant")})
        rng = np.random.default_rng(MC_SEED)
        picks = rng.random((N_MC, len(valid), N_FREQ)).argsort(axis=2)[:, :, :M]
        null = (picks / (N_FREQ - 1)).mean(axis=(1, 2))
        rbar = float(np.mean([r["rbar0_base"] for r in valid]))
        p9 = float((np.sum(null <= rbar) + 1) / (N_MC + 1))
        out["exp009_replication"] = {"rbar0": rbar, "p": p9,
                                     "verdict": "repliziert" if p9 < ALPHA else "nicht repliziert"}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
