"""EXP-014: does the final frequency set follow the init or the train split? (UNTESTED)

Read-only. Cross runs: raw/EXP-014_baseline_..._seed{i}_thr4_split{j}; baselines: EXP-003d raw_d.
Definition and decision rule: README.md.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
BASE = LAB / "experiments/EXP-003-early-prediction/raw_d/EXP-001_baseline_t2000_m5_seed{s}_thr4"
CROSS = HERE / "raw/EXP-014_baseline_t2000_m5_seed{i}_thr4_split{j}"
SEEDS = list(range(10, 20))
M, N_FREQ, ALPHA, MIN_VALID, N_MC = 5, 56, 0.05, 8, 20_000


def load(d: Path):
    return (json.loads((d / "result.json").read_text(encoding="utf-8")),
            np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist())


def row(i: int) -> dict:
    j = SEEDS[(SEEDS.index(i) + 1) % len(SEEDS)]
    r: dict = {"init": i, "split": j, "valid": False}
    try:
        c, cs, cst = load(Path(str(CROSS).format(i=i, j=j)))
        bi, bis, bist = load(Path(str(BASE).format(s=i)))
        bj, _, _ = load(Path(str(BASE).format(s=j)))
    except FileNotFoundError as e:
        r["reason"] = f"missing {e.filename}"
        return r
    if any(x["status"] != "completed" or x["events"].get("generalization_step") is None
           for x in (c, bi, bj)):
        r["reason"] = "not completed or not crossed"
        return r
    if c["split_hash"] != bj["split_hash"] or c.get("split_seed") != j:
        r["reason"] = "split mismatch"
        return r
    if not np.allclose(cs[cst.index(0)], bis[bist.index(0)], rtol=1e-6):
        r["reason"] = "init mismatch"
        return r
    kc, ki, kj = set(c["final_top_m_freqs"]), set(bi["final_top_m_freqs"]), set(bj["final_top_m_freqs"])
    r.update({"valid": True, "K_cross": sorted(kc), "K_init": sorted(ki), "K_split": sorted(kj),
              "ov_init": len(kc & ki), "ov_split": len(kc & kj)})
    r["D"] = r["ov_split"] - r["ov_init"]
    return r


def two_sided_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float((np.abs((flips * d).mean(axis=1)) >= abs(d.mean()) - 1e-12).mean())


def chance_p(mean_ov: float, n: int) -> float:
    """P(mean overlap of n pairs of random 5-sets >= observed), Monte Carlo."""
    rng = np.random.default_rng(0)
    a = rng.random((N_MC, n, N_FREQ)).argsort(axis=2)[:, :, :M]
    b = rng.random((N_MC, n, N_FREQ)).argsort(axis=2)[:, :, :M]
    ov = (a[..., :, None] == b[..., None, :]).sum(axis=(-1, -2))   # [N_MC, n]
    null = ov.mean(axis=1)
    return float((np.sum(null >= mean_ov - 1e-12) + 1) / (N_MC + 1))


PAIRS = [(10, 11), (12, 13), (14, 15), (16, 17), (18, 19)]   # Nachtrag a: disjoint, both directions


def cross_row(i: int, j: int) -> dict:
    """Like row(), but for an explicit (init i, split j) cross run."""
    r: dict = {"init": i, "split": j, "valid": False}
    try:
        c, cs, cst = load(Path(str(CROSS).format(i=i, j=j)))
        bi, bis, bist = load(Path(str(BASE).format(s=i)))
        bj, _, _ = load(Path(str(BASE).format(s=j)))
    except FileNotFoundError as e:
        r["reason"] = f"missing {e.filename}"
        return r
    if any(x["status"] != "completed" or x["events"].get("generalization_step") is None for x in (c, bi, bj)):
        r["reason"] = "not completed or not crossed"
        return r
    if c["split_hash"] != bj["split_hash"] or c.get("split_seed") != j:
        r["reason"] = "split mismatch"
        return r
    if not np.allclose(cs[cst.index(0)], bis[bist.index(0)], rtol=1e-6):
        r["reason"] = "init mismatch"
        return r
    kc, ki, kj = set(c["final_top_m_freqs"]), set(bi["final_top_m_freqs"]), set(bj["final_top_m_freqs"])
    r.update({"valid": True, "ov_init": len(kc & ki), "ov_split": len(kc & kj)})
    return r


def one_sided_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def main() -> None:
    """Primary since Nachtrag a: pair units u = (a, b), D_u = sum of ov_split - ov_init over both
    cross directions; one-sided sign-flip over the 5 independent units (split > init)."""
    units = []
    for a, b in PAIRS:
        ab, ba = cross_row(a, b), cross_row(b, a)
        u = {"pair": [a, b], "valid": ab["valid"] and ba["valid"], "rows": [ab, ba]}
        if u["valid"]:
            u["D"] = (ab["ov_split"] + ba["ov_split"]) - (ab["ov_init"] + ba["ov_init"])
        units.append(u)
    valid = [u for u in units if u["valid"]]
    out: dict = {"units": units, "n_valid_units": len(valid)}
    if len(valid) < 5:          # with 4 units the smallest one-sided p is 1/16 > 0.05
        out["verdict"] = "nicht auswertbar"
    else:
        D = np.array([u["D"] for u in valid], dtype=float)
        p = one_sided_p(D)
        rows = [r for u in valid for r in u["rows"]]
        oi = float(np.mean([r["ov_init"] for r in rows]))
        osp = float(np.mean([r["ov_split"] for r in rows]))
        out.update({"D_mean": float(D.mean()), "p_one_sided": p, "ov_init_mean": oi, "ov_split_mean": osp,
                    "p_ov_init_vs_chance": chance_p(oi, len(rows)),
                    "p_ov_split_vs_chance": chance_p(osp, len(rows)),
                    "verdict": "Split dominiert" if D.mean() > 0 and p < ALPHA else
                    ("Init dominiert (Richtung entgegen Erwartung)" if D.mean() < 0 else "kein Nachweis")})
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "units"}, indent=1))
    for u in units:
        print(u)


if __name__ == "__main__":
    main()
