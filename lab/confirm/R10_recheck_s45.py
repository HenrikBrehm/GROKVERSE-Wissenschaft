"""R10 independent recheck (session 45). Read-only; own code; does NOT import lab/tools/confirm_r10.py.

Definitions from lab/confirm/R10_REGISTRATION_DRAFT.md and EXP-056 README/analyze.py:
  L(run) = log[P(F)/P(G)] of the final W_E group power (add 113 DFT, k = 1..56, power 2|FFT_k|^2/n summed over d),
  F = targets of A, G = targets of B (r10_splits/r10_seed{s}_w0.json).
  pi_AB = (L(A->B) - L(B)) / (L(A) - L(B)), pi_BA = (L(B->A) - L(A)) / (L(B) - L(A)), pi = mean.
  Seed excluded if L(A) - L(B) < 2; > 8 excluded -> not evaluable; any technical failure -> not evaluable.
Stats: one-sided paired t (H1, H3: mean > 0), TOST +-0.05 (H2, p = max of both one-sided), Holm over 3,
95 % percentile bootstrap CI. Prints JSON to stdout; writes no files.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CONF = ROOT / "lab" / "confirm"
RAW, SPL = CONF / "r10_raw", CONF / "r10_splits"
P = 113
EQ = 0.05
ALPHA = 0.05
MIN_LAL = 2.0
MAX_EXCL = 8

REF = {"H1": {"mean": 0.14727, "ci": [0.1154, 0.1814], "npos": 45},
       "H2": {"mean": 0.05737, "p": 0.760},
       "H3": {"mean": 0.23365, "ci": [0.2011, 0.2656], "npos": 48},
       "cells": {"n24": 0.3457, "g8": 0.1984, "g24": 0.1120, "c8b": 0.1410}}


# ---------- t distribution via regularized incomplete beta (Lentz continued fraction) ----------
def _betacf(a: float, b: float, x: float) -> float:
    tiny, eps = 1e-300, 1e-15
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 10000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            return h
    raise RuntimeError("betacf did not converge")


def betainc(a: float, b: float, x: float) -> float:
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbt) * _betacf(b, a, 1.0 - x) / b


def t_sf(t: float, df: int) -> float:
    """P(T >= t)."""
    tail = 0.5 * betainc(df / 2.0, 0.5, df / (df + t * t))
    return tail if t >= 0 else 1.0 - tail


def selftest() -> None:
    # known values: t_{0.975, 10} = 2.228139, t_{0.95, 47} = 1.677927, t_{0.995, 3} = 5.840909
    for t, df, p in ((2.228139, 10, 0.025), (1.677927, 47, 0.05), (5.840909, 3, 0.005), (0.0, 5, 0.5)):
        assert abs(t_sf(t, df) - p) < 2e-6, (t, df, t_sf(t, df))
    assert abs(t_sf(-1.677927, 47) - 0.95) < 2e-6
    assert abs(betainc(2.0, 3.0, 0.4) - 0.5248) < 1e-9          # I_0.4(2,3) = 0.5248 exactly
    h = holm([0.01, 0.04, 0.03])
    assert np.allclose(h, [0.03, 0.06, 0.06])


# ---------- stats ----------
def one_sided(x: np.ndarray, mu: float = 0.0, greater: bool = True) -> float:
    n = len(x)
    t = (x.mean() - mu) / (x.std(ddof=1) / math.sqrt(n))
    return t_sf(t, n - 1) if greater else t_sf(-t, n - 1)


def holm(ps: list[float]) -> list[float]:
    m = len(ps)
    order = np.argsort(ps)
    out, run = [0.0] * m, 0.0
    for i, j in enumerate(order):
        run = max(run, min(1.0, (m - i) * ps[j]))
        out[j] = run
    return out


def boot_ci(x: np.ndarray, rng: np.random.Generator, B: int = 20000) -> list[float]:
    idx = rng.integers(0, len(x), size=(B, len(x)))
    means = x[idx].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


# ---------- run loading / checks ----------
def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sorted_hash(p: Path) -> str:
    idx = np.sort(np.asarray(np.load(p), dtype=np.int64))
    return hashlib.sha256(idx.astype("<i8").tobytes()).hexdigest()


def group_power(W: np.ndarray) -> np.ndarray:
    Fw = np.fft.fft(W[:P].astype(np.float64), axis=0)
    sq = (np.abs(Fw) ** 2).sum(axis=1)
    K = (P - 1) // 2
    return 2.0 * sq[1:K + 1] / P


def logratio(pw: np.ndarray, F: list[int], G: list[int]) -> float:
    return float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))


CELLS = {"n24": dict(t=24, c=1.0, psb=None, k=1, suf=""),
         "g8": dict(t=24, c=1.0, psb=None, k=8, suf="_ge8"),
         "g24": dict(t=24, c=1.0, psb=None, k=24, suf="_ge24"),
         "c8b": dict(t=3, c=8.0, psb=[0.2, 0.84], k=1, suf="_lrs8_psb0.2_0.84")}


def load(s: int, first: str, second: str | None, cell: str | None, budget: int, problems: list) -> float | None:
    st = lambda x: f"r10_seed{s}_w0_{x}"
    if second is None:
        name = f"EXP-018_baseline_seed{s}_thr1_{st(first)}_devcuda"
        t = 0
    else:
        c = CELLS[cell]
        t = c["t"]
        name = f"EXP-020_baseline_seed{s}_thr1_{st(first)}_to_{st(second)}_at{t}{c['suf']}_devcuda"
    d = RAW / name
    tag = f"s{s} {cell or 'pure'} {first}{'->' + second if second else ''}"
    if not (d / "result.json").exists():
        problems.append(f"{tag}: missing")
        return None
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    steps = budget + t
    bad = []
    if r.get("status") != "completed":
        bad.append(f"status {r.get('status')}")
    if r.get("steps_completed") != steps or r.get("max_steps") != steps:
        bad.append(f"steps {r.get('steps_completed')}/{r.get('max_steps')} != {steps}")
    if r.get("seed") != s or r.get("device") != "cuda":
        bad.append("seed/device")
    cfg = r["config"]
    if (cfg["p"], cfg["task"], cfg["lr"], cfg["weight_decay"], cfg["train_frac"], cfg["beta1"], cfg["beta2"]) != \
            (113, "add", 0.001, 1.0, 0.3, 0.9, 0.98):
        bad.append("config")
    ff = r["fingerprint_fields"]
    fa, ft = SPL / f"{st(first)}.npy", SPL / f"r10_seed{s}_test.npy"
    if ff.get("split_file_sha256") != sha_file(fa) or r.get("split_hash") != sorted_hash(fa):
        bad.append("split hash")
    if ff.get("test_file_sha256") != sha_file(ft) or r.get("test_hash") != sorted_hash(ft):
        bad.append("test hash")
    if second is not None:
        fb = SPL / f"{st(second)}.npy"
        if ff.get("switch_split_file_sha256") != sha_file(fb) or r.get("switch_hash") != sorted_hash(fb):
            bad.append("switch hash")
        ev = r.get("events", {})
        if ev.get("switch", {}).get("step") != t or ev["switch"].get("new_train_hash") != sorted_hash(fb):
            bad.append("switch event")
        c = CELLS[cell]
        if r.get("lr_scale") != c["c"] or r.get("pre_switch_betas") != c["psb"] or r.get("pre_switch_grad_every") != c["k"]:
            bad.append("cell params")
        if c["k"] > 1:
            ge = ev.get("pre_switch_grad_every", {})
            want = list(range(1, t + 1, c["k"]))
            if ge.get("k") != c["k"] or ge.get("eval_steps_pre_switch") != want:
                bad.append(f"grad plan {ge.get('eval_steps_pre_switch')} != {want}")
        elif "pre_switch_grad_every" in ev:
            bad.append("grad event with k=1")
        if c["psb"] is not None:
            pe = ev.get("pre_switch_betas", {})
            if not (pe.get("check") is True and pe.get("pre") == c["psb"] and pe.get("post") == [0.9, 0.98] and pe.get("step") == t):
                bad.append("beta switch event")
    else:
        if r.get("switch_step") is not None:
            bad.append("pure run has switch")
    ss = np.load(d / "we_snapshot_steps.npy").tolist()
    need = [0, steps] + ([t] if second else [])
    if not all(x in ss for x in need):
        bad.append(f"snapshots {ss}")
    if bad:
        problems.append(f"{tag}: " + "; ".join(bad))
        return None
    W = np.load(d / "we_snapshots.npy")[ss.index(steps)]
    if not np.isfinite(W).all():
        problems.append(f"{tag}: non-finite W_E")
        return None
    return W


def main() -> None:
    selftest()
    man = json.loads((CONF / "R10_manifest.json").read_text(encoding="utf-8"))
    seeds, budget = man["seeds"], man["budget"]
    assert seeds == list(range(3500, 3548)) and budget == 2000
    for c, v in man["cells"].items():
        assert (v["t"], v["c"], v["k"], v["psb"]) == (CELLS[c]["t"], CELLS[c]["c"], CELLS[c]["k"], CELLS[c]["psb"]), c
    n_dirs = len([p for p in RAW.iterdir() if p.is_dir()])
    problems: list[str] = []
    rows, excluded, technical = [], [], []
    for s in seeds:
        meta = json.loads((SPL / f"r10_seed{s}_w0.json").read_text(encoding="utf-8"))
        Fa, Gb = meta["targets"]["A"], meta["targets"]["B"]
        n0 = len(problems)
        W = {"A": load(s, "A", None, None, budget, problems), "B": load(s, "B", None, None, budget, problems)}
        for cell in CELLS:
            W[cell + "AB"] = load(s, "A", "B", cell, budget, problems)
            W[cell + "BA"] = load(s, "B", "A", cell, budget, problems)
        if len(problems) > n0:
            technical.append(s)
            continue
        L = {k: logratio(group_power(w), Fa, Gb) for k, w in W.items()}
        lal = L["A"] - L["B"]
        if lal < MIN_LAL:
            excluded.append(s)
            continue
        row = {"seed": s, "LA_minus_LB": lal}
        for cell in CELLS:
            ab = (L[cell + "AB"] - L["B"]) / lal
            ba = (L[cell + "BA"] - L["A"]) / (-lal)
            row["pi_" + cell] = (ab + ba) / 2
        rows.append(row)
    out: dict = {"n_run_dirs": n_dirs, "n_technical": len(technical), "technical_seeds": technical,
                 "n_excluded": len(excluded), "excluded_seeds": excluded, "problems": problems, "n": len(rows)}
    if technical or len(excluded) > MAX_EXCL:
        out["reading"] = "nicht auswertbar"
        print(json.dumps(out, indent=1))
        return
    pi = {c: np.array([r["pi_" + c] for r in rows]) for c in CELLS}
    stat = {"H1": pi["n24"] - pi["g8"], "H2": pi["g8"] - pi["c8b"], "H3": pi["n24"] - pi["g24"]}
    raw_p = {"H1": one_sided(stat["H1"]), "H3": one_sided(stat["H3"]),
             "H2": max(one_sided(stat["H2"], -EQ, True), one_sided(stat["H2"], EQ, False))}
    keys = ["H1", "H2", "H3"]
    ph = dict(zip(keys, holm([raw_p[k] for k in keys])))
    rng = np.random.default_rng(45)
    res, confirmed = {}, []
    for k in keys:
        x = stat[k]
        ci = boot_ci(x, rng)
        if k == "H2":
            ok = ph[k] < ALPHA
        else:
            ok = ph[k] < ALPHA and ci[0] > 0 and x.mean() > 0
        res[k] = {"mean": float(x.mean()), "sd": float(x.std(ddof=1)), "ci95": ci, "n_positive": int((x > 0).sum()),
                  "p": raw_p[k], "p_holm": ph[k], "confirmed": bool(ok)}
        if ok:
            confirmed.append(k)
    reading = "Auswertungen-Befund bestätigt" if len(confirmed) == 3 else ("teilweise: " + ", ".join(confirmed) if confirmed else "keine")
    d = stat["H3"] - stat["H1"]
    out.update({"hypotheses": res, "reading": reading,
                "e24_minus_e8": {"mean": float(d.mean()), "ci95": boot_ci(d, rng)},
                "cell_means_pi": {c: float(v.mean()) for c, v in pi.items()}})
    # comparison with R10_summary.json (per-seed deterministic, 1e-6)
    summ = json.loads((CONF / "R10_summary.json").read_text(encoding="utf-8"))
    sh = summ["hypotheses"]
    srows = {r["seed"]: r for r in summ["rows"]}
    maxdiff = 0.0
    for r in rows:
        sr = srows[r["seed"]]
        for c in CELLS:
            maxdiff = max(maxdiff, abs(r["pi_" + c] - sr["pi_" + c]))
        maxdiff = max(maxdiff, abs(r["LA_minus_LB"] - sr["LA_minus_LB"]))
    cmp = {"max_abs_diff_per_seed_pi_and_LAL": maxdiff}
    for k in keys:
        for f in ("mean", "sd", "p", "p_holm"):
            cmp[f"{k}.{f}"] = abs(res[k][f] - sh[k][f]) / (abs(sh[k][f]) if f.startswith("p") and sh[k][f] > 0 else 1.0)
        cmp[f"{k}.n_positive_equal"] = res[k]["n_positive"] == sh[k]["n_positive"]
        cmp[f"{k}.ci_diff"] = [res[k]["ci95"][i] - sh[k]["ci95"][i] for i in (0, 1)]
    for c in CELLS:
        cmp[f"cell.{c}"] = abs(out["cell_means_pi"][c] - sh["cell_means"]["pi"][c])
    cmp["reading_equal"] = reading == sh["reading"]
    cmp["n_equal"] = len(rows) == sh["n"]
    out["compare_summary (p fields: relative diff)"] = cmp
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
