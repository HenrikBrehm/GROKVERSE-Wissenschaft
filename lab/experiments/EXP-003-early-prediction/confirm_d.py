"""EXP-003d: confirm F6@2000 on fresh transformer seeds 10-19 (runs made by freq_ban.py baseline).

UNTESTED until the runs exist. See CONFIRM_d.md. Read-only analysis of raw_d/.
"""
from __future__ import annotations

import json
import subprocess
import sys

import numpy as np

from early_predict import ALPHA, HERE, N_PERM, PERM_SEED, ROOT, TOP_K_FREQ, perm_null, spearman

RAW = HERE / "raw_d"
SEEDS = range(10, 20)
RUN_ID = "EXP-001_baseline_t2000_m5_seed{s}_thr4"
CAP = 15_000
CENSORED_VALUE = CAP + 1
MAX_CENSORED = 2
PRIMARY_STEP = 2000
SECONDARY_STEPS = (1000, 4000)


def top_k_share(power: np.ndarray, k: int = TOP_K_FREQ) -> float:
    return float(np.sort(power)[::-1][:k].sum() / power.sum())


def load(seed: int) -> dict:
    d = RAW / RUN_ID.format(s=seed)
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    if res.get("status") != "completed":
        raise ValueError(f"seed {seed}: status {res.get('status')!r}, not completed")
    spectra, steps = np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()
    gen = res["events"].get("generalization_step")
    row = {"seed": seed, "generalization_step": gen if gen is not None else CENSORED_VALUE,
           "censored": gen is None, "split_hash": res.get("split_hash"),
           "sec_per_step": res.get("sec_per_step")}
    for t in (PRIMARY_STEP, *SECONDARY_STEPS):
        row[f"F6_at_{t}"] = top_k_share(spectra[steps.index(t)])
    return row


def main() -> int:
    rows = [load(s) for s in SEEDS]
    n_cens = sum(r["censored"] for r in rows)
    y = np.array([r["generalization_step"] for r in rows], dtype=float)
    rng = np.random.default_rng(PERM_SEED)
    stats = {}
    for t in (PRIMARY_STEP, *SECONDARY_STEPS):
        x = np.array([r[f"F6_at_{t}"] for r in rows])
        rho = spearman(x, y)
        stats[t] = {"rho": rho, "p_less": float((perm_null(y, x, rng) <= rho + 1e-12).mean())}
    prim = stats[PRIMARY_STEP]
    if n_cens > MAX_CENSORED:
        verdict = "technisch nicht auswertbar"
    elif prim["rho"] >= 0:
        verdict = "widerspricht"
    elif prim["p_less"] < ALPHA:
        verdict = "bestätigt"
    else:
        verdict = "richtungsgleich, nicht signifikant"
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()
    out = {"experiment": "EXP-003d", "code_commit": commit, "verdict": verdict,
           "n_censored": n_cens, "stats": {str(k): v for k, v in stats.items()}, "rows": rows,
           "n_perm": N_PERM, "env": {"python": sys.version.split()[0], "numpy": np.__version__}}
    (HERE / "summary_d.json").write_text(json.dumps(out, indent=2, ensure_ascii=False),
                                         encoding="utf-8")
    print(verdict, {k: (round(v["rho"], 3), round(v["p_less"], 4)) for k, v in stats.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
