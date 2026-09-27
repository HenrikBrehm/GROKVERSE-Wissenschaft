"""Session 34, POST HOC on stored switch blocks, no training. Question (N43, programme B): why does a data switch at t = 25 delay
grokking, with ~90 % of the delay in the gap between memorisation and generalisation (session 32)?

Hypothesis M_clean (stated before reading any per-seed value used here): at t = 25 the old targets stay in W_E next to the new
ones (spectral coexistence, EXP-062) although the network switches to the new ones functionally (K4c); generalisation has to wait
until weight decay has cleared the unused old energy ("clean-up"). Prediction: runs with MORE old-target energy shortly after the
switch are delayed MORE.

Fixed before reading (N28 = discovery set, P3 w0 = replication with the unchanged script; both blocks' generalisation times were
read in session 32, their spectra shares at step t+250 were not):
- run X->Y@25; old targets = targets of X, new = targets of Y (split metadata); s_old = share of W_E power (spectra.npy, k = 1..56)
  on the old targets at step 275 (first stored spectrum after the switch, t + 250).
- delay = log2(gen(X->Y@25) / gen(Y only)), gen = trainer event (first test >= 0.95, counted from step 0). Runs without an event
  (censored) are excluded and counted.
- per seed: mean of both directions (A->B, B->A) over the directions that have a delay -> one value per seed (independence).
- PRIMARY: Spearman rho(s_old, delay) over seeds, one-sided permutation p (10 000 permutations, seeded).
  M_clean supported in a block if rho >= 0.3 and p < 0.05; contradicted if rho <= 0; otherwise unclear.
  Overall verdict: "supported" only if N28 AND P3 are supported; "contradicted" if either is contradicted; else "unclear".
- Descriptive: mean s_old at 275 and at the last spectrum before gen (does the old share fall before generalisation?),
  same rho with the ABSOLUTE old power, and rho(s_old, delay) at t = 50 (N28 only; no prediction).
  python lab/confirm/switch_cleanup_s34.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
BLOCKS = {"N28": ("confirm/n28_raw", "confirm/n28_splits", "n28", "w0"), "P3": ("confirm/p3_raw", "confirm/p3_splits", "p3", "w0")}
OUT = LAB / "confirm/switch_cleanup_s34.json"


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def perm_p(x: np.ndarray, y: np.ndarray, r: float, n: int = 10000) -> float:
    rng = np.random.default_rng(34)
    return float((1 + sum(spearman(x, rng.permutation(y)) >= r for _ in range(n))) / (n + 1))


def run_dir(raw: Path, pre: str, w: str, s: int, x: str, y: str | None, t: int | None) -> Path | None:
    pat = f"seed{s}_thr1_{pre}_seed{s}_{w}_{x}" + (f"_to_{pre}_seed{s}_{w}_{y}_at{t}_devcuda" if y else "_devcuda")
    hits = [d for d in raw.iterdir() if d.name.endswith(pat)]
    return hits[0] if len(hits) == 1 else None


def gen(d: Path) -> int | None:
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    return (r.get("events") or {}).get("generalization_step")


def shares(d: Path, old: list[int], step: int, g: int | None) -> tuple[float, float, float | None]:
    S, st = np.load(d / "spectra.npy"), list(np.load(d / "spectra_steps.npy"))
    i = st.index(step)
    idx = [k - 1 for k in old]
    before = [j for j, v in enumerate(st) if g is not None and v < g]
    s_gen = float(S[before[-1], idx].sum() / S[before[-1]].sum()) if before else None
    return float(S[i, idx].sum() / S[i].sum()), float(S[i, idx].sum()), s_gen


def block(name: str, t: int) -> dict:
    raw_, spl_, pre, w = BLOCKS[name]
    raw, spl = LAB / raw_, LAB / spl_
    seeds = sorted({int(m.group(1)) for d in raw.iterdir() if (m := re.search(rf"seed(\d+)_thr1_{pre}_seed\d+_{w}_A_devcuda$", d.name))})
    rows, censored = [], 0
    for s in seeds:
        tg = json.loads((spl / f"{pre}_seed{s}_{w}.json").read_text(encoding="utf-8"))["targets"]
        vals = []
        for x, y in (("A", "B"), ("B", "A")):
            d_sw, d_y = run_dir(raw, pre, w, s, x, y, t), run_dir(raw, pre, w, s, y, None, None)
            if d_sw is None or d_y is None:
                continue
            g_sw, g_y = gen(d_sw), gen(d_y)
            if not g_sw or not g_y:
                censored += 1
                continue
            s_old, p_old, s_gen = shares(d_sw, tg[x], t + 250, g_sw)
            vals.append((s_old, p_old, s_gen, math.log2(g_sw / g_y)))
        if vals:
            v = np.array([[a, b, c if c is not None else np.nan, e] for a, b, c, e in vals])
            rows.append({"seed": s, "s_old": float(v[:, 0].mean()), "p_old": float(v[:, 1].mean()),
                         "s_old_before_gen": float(np.nanmean(v[:, 2])) if not np.all(np.isnan(v[:, 2])) else None,
                         "delay": float(v[:, 3].mean()), "n_dir": len(vals)})
    x = np.array([r["s_old"] for r in rows]); y = np.array([r["delay"] for r in rows]); pa = np.array([r["p_old"] for r in rows])
    rho = spearman(x, y)
    res = {"block": name, "t": t, "n_seeds": len(rows), "censored_runs": censored, "rho": rho, "p_one_sided": perm_p(x, y, rho),
           "rho_abs_power": spearman(pa, y), "mean_s_old_275": float(x.mean()), "mean_delay_log2": float(y.mean()),
           "mean_s_old_before_gen": float(np.mean([r["s_old_before_gen"] for r in rows if r["s_old_before_gen"] is not None])),
           "rows": rows}
    res["verdict"] = "supported" if rho >= 0.3 and res["p_one_sided"] < 0.05 else ("contradicted" if rho <= 0 else "unclear")
    return res


def main() -> None:
    out = {"N28@25": block("N28", 25), "P3@25": block("P3", 25), "N28@50 (descriptive)": block("N28", 50)}
    v = [out["N28@25"]["verdict"], out["P3@25"]["verdict"]]
    out["overall"] = "supported" if v == ["supported"] * 2 else ("contradicted" if "contradicted" in v else "unclear")
    for k, r in out.items():
        if isinstance(r, dict):
            print(f"{k}: n={r['n_seeds']} censored={r['censored_runs']} rho={r['rho']:+.3f} p={r['p_one_sided']:.4f} "
                  f"rho_abs={r['rho_abs_power']:+.3f} s_old@t+250={r['mean_s_old_275']:.3f} s_old_before_gen={r['mean_s_old_before_gen']:.3f} "
                  f"delay={r['mean_delay_log2']:+.3f} -> {r['verdict']}")
    print("overall:", out["overall"])
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
