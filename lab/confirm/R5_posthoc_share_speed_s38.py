"""R5 post hoc (session 38, exploration, after the frozen analysis): does the early W_E target share predict speed
*within* an arm across units?

Question: R5 shows arm means ordered alike in speed and in the W_E target share at step 250 (E8 > E2 > E1 > R ~ D).
If the speed-up runs through the early target signal, then within an arm, units with a higher share at 250 should
generalize earlier (Spearman rho(share, log2 b) < 0). Expectation written before computing: clearly negative in E1
(times spread 1000-8000), weaker in E2/E8 (times compressed). A null within arms would mean the arm-level order is
set by the construction, not by unit-to-unit variation of the early signal.
Not a confirmation: seeds seen, post hoc, several tests. Reads only lab/confirm/R5_summary.json.
"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SUMMARY = ROOT / "lab/confirm/R5_summary.json"
OUT = Path(__file__).with_suffix(".json")
ARMS = ("E8_0", "E2_0", "E2_1", "E1_0", "R", "D_0", "D_1")
N_PERM = 20000


def ranks(x):
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(len(x))
    r[order] = np.arange(len(x))
    for v in np.unique(x):                      # average ranks for ties (censored times tie at 8000)
        m = x == v
        r[m] = r[m].mean()
    return r


def spearman(x, y):
    rx, ry = ranks(x), ranks(y)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    return float((rx * ry).sum() / np.sqrt((rx ** 2).sum() * (ry ** 2).sum()))


def perm_p_less(x, y, rng):
    """one-sided permutation p for rho < 0"""
    obs = spearman(x, y)
    null = np.array([spearman(x, rng.permutation(y)) for _ in range(N_PERM)])
    return obs, float(((null <= obs).sum() + 1) / (N_PERM + 1))


def main():
    rows = [r for r in json.loads(SUMMARY.read_text())["rows"] if not r["technical"]]
    rng = np.random.default_rng(20260928)
    out = {"n_units": len(rows), "n_perm": N_PERM, "arms": {}}
    for arm in ARMS:
        share = [r["we_share_250"][arm] for r in rows]
        logb = [np.log2(r["times"][arm][0]) for r in rows]
        n_obs = sum(r["times"][arm][1] for r in rows)
        rho, p = perm_p_less(share, logb, rng)
        out["arms"][arm] = {"rho": rho, "p_one_sided_less": p, "n_observed": n_obs,
                            "share_sd": float(np.std(share, ddof=1)), "logb_sd": float(np.std(logb, ddof=1))}
        print(f"{arm:5s} rho={rho:+.2f} p={p:.4f} observed={n_obs}/20 sd(share)={np.std(share, ddof=1):.3f} "
              f"sd(log2 b)={np.std(logb, ddof=1):.2f}")
    OUT.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
