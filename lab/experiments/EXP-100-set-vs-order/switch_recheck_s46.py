"""EXP-100 switch part, independent numpy-only recheck (session 46) of switch_summary.json (primary) and
switch_horizon_posthoc_s46.json (horizon). Does not import analyze/design/result_loader/switch_* or EXP-043 code; definitions
re-implemented from reading them. Group power via explicit cos/sin projections (not FFT). Writes switch_recheck_s46.json.
The two JSONs are read only after all numbers are computed.
  PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1 python lab/tools/guarded_run.py -- python lab/experiments/EXP-100-set-vs-order/switch_recheck_s46.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SPL = HERE / "splits"
SEEDS = range(3700, 3708)
TS = (25, 50)
H = (2000, 2500, 5000, 10000, 20000, 30000)
ARMS = {"fb": ("", 2000, 0), "iid256": ("_bs256", 30000, 256)}   # suffix, base steps, batch size (0 = full batch)
P = 113
TOL = 1e-6


def shash(path: Path) -> str:
    return hashlib.sha256(np.sort(np.load(path).astype(np.int64)).astype("<i8").tobytes()).hexdigest()


def gpower(W: np.ndarray) -> np.ndarray:
    X = W[:P].astype(np.float64)
    n = np.arange(P)
    out = np.empty(56)
    for k in range(1, 57):
        c = np.cos(2 * np.pi * k * n / P) @ X
        s = np.sin(2 * np.pi * k * n / P) @ X
        out[k - 1] = (2 * (c ** 2 + s ** 2) / P).sum()
    return out


def one_dir(root: Path, pat: str) -> Path:
    hits = sorted(root.glob(pat))
    assert len(hits) == 1, (pat, hits)
    return hits[0]


def load(d: Path, s: int, total: int, bs, first: str, second, t, need: tuple) -> dict:
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    errs: list[str] = []

    def chk(c, m):
        if not c:
            errs.append(m)
    chk(r.get("status") == "completed", f"status {r.get('status')}")
    chk(r.get("seed") == s, "seed")
    chk(r.get("max_steps") == total and r.get("steps_completed") == total, f"steps {r.get('steps_completed')}/{total}")
    chk(r.get("device") == "cuda", "device")
    chk(r.get("switch_step") == t, f"switch_step {r.get('switch_step')}")
    chk(r.get("batch_size") == bs, f"batch_size {r.get('batch_size')}")
    chk(r.get("split_hash") == shash(SPL / f"seed{s}_{first}.npy"), "split_hash")
    chk(r.get("test_hash") == shash(SPL / f"seed{s}_test.npy"), "test_hash")
    if second is not None:
        chk(r.get("switch_hash") == shash(SPL / f"seed{s}_{second}.npy"), "switch_hash")
    cfg = r.get("config")
    cfg = cfg if isinstance(cfg, dict) else {}
    chk(cfg.get("p") == 113 and cfg.get("task") == "add", "config")
    steps = np.load(d / "we_snapshot_steps.npy")
    W = np.load(d / "we_snapshots.npy")
    pw = {}
    for h in need:
        i = np.flatnonzero(steps == h)
        if len(i) != 1:
            errs.append(f"no snapshot {h}")
            continue
        pw[h] = gpower(W[i[0]])
        chk(np.isfinite(pw[h]).all(), f"nonfinite {h}")
    return {"pw": pw, "errs": errs}


def logr(pw, F, G) -> float:
    return float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))


def pi(LF, LG, LFG, LGF) -> float:
    return ((LFG - LG) / (LF - LG) + (LGF - LF) / (LG - LF)) / 2


def boot(x, seed=100, nb=10_000) -> list[float]:
    x = np.asarray(x, float)
    m = x[np.random.default_rng(seed).integers(0, len(x), size=(nb, len(x)))].mean(axis=1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def compute() -> dict:
    errors: list[str] = []
    prim = {f"{a}_{t}": [] for a in ARMS for t in TS}
    hor = {f"{t}@{h}": [] for t in TS for h in H}
    sep_h = {h: [] for h in H}
    sep_end = {a: [] for a in ARMS}
    for s in SEEDS:
        T = json.loads((SPL / f"seed{s}.json").read_text(encoding="utf-8"))["targets"]
        F, G = T["F"], T["G"]
        for arm, (suf, base, bs) in ARMS.items():
            hz = H if arm == "iid256" else ()
            pure = {x: load(one_dir(HERE / "raw", f"EXP-018_baseline_seed{s}_thr*_seed{s}_{x}{suf}_devcuda"),
                            s, base, bs, x, None, None, (base,) + hz) for x in "FG"}
            sw = {(a, b, t): load(one_dir(HERE / "raw_switch",
                                          f"EXP-020_baseline_seed{s}_thr*_seed{s}_{a}_to_seed{s}_{b}_at{t}{suf}_devcuda"),
                                  s, base + t, bs, a, b, t, (base + t,) + hz)
                  for t in TS for a, b in (("F", "G"), ("G", "F"))}
            for k, v in list(pure.items()) + list(sw.items()):
                errors += [f"seed {s} {arm} {k}: {e}" for e in v["errs"]]
            LF, LG = logr(pure["F"]["pw"][base], F, G), logr(pure["G"]["pw"][base], F, G)
            sep_end[arm].append(LF - LG)
            for t in TS:
                prim[f"{arm}_{t}"].append(pi(LF, LG, logr(sw[("F", "G", t)]["pw"][base + t], F, G),
                                             logr(sw[("G", "F", t)]["pw"][base + t], F, G)))
            for h in hz:
                lf, lg = logr(pure["F"]["pw"][h], F, G), logr(pure["G"]["pw"][h], F, G)
                sep_h[h].append(lf - lg)
                for t in TS:
                    hor[f"{t}@{h}"].append(pi(lf, lg, logr(sw[("F", "G", t)]["pw"][h], F, G),
                                              logr(sw[("G", "F", t)]["pw"][h], F, G)))
    A = {k: np.array(v) for k, v in prim.items()}
    d_fb, d_mb = A["fb_50"] - A["fb_25"], A["iid256_50"] - A["iid256_25"]
    dh = {h: np.array(hor[f"50@{h}"]) - np.array(hor[f"25@{h}"]) for h in H}
    return {"n_errors": len(errors), "errors": errors,
            "L_F_minus_L_G_end": {a: [float(x) for x in v] for a, v in sep_end.items()},
            "primary": {"pi_rows": {k: [float(x) for x in v] for k, v in prim.items()},
                        "pi_means": {f"pi_{k}": float(v.mean()) for k, v in A.items()},
                        "d_fb": {"mean": float(d_fb.mean()), "ci95": boot(d_fb)},
                        "d_mb": {"mean": float(d_mb.mean()), "ci95": boot(d_mb)},
                        "d_mb_minus_d_fb": {"mean": float((d_mb - d_fb).mean()), "ci95": boot(d_mb - d_fb)}},
            "horizon": {"L_F_minus_L_G_mean": {str(h): float(np.mean(v)) for h, v in sep_h.items()},
                        "pi_rows": {k: [float(x) for x in v] for k, v in hor.items()},
                        "pi": {k: {"mean": float(np.mean(v)), "ci95": boot(v)} for k, v in hor.items()},
                        "d50_minus_25": {str(h): {"mean": float(v.mean()), "ci95": boot(v)} for h, v in dh.items()}}}


def compare(out: dict) -> dict:
    cmp, flags = {}, []
    ss = json.loads((HERE / "switch_summary.json").read_text(encoding="utf-8"))
    pp = ss["primary"]
    for k in ("d_fb", "d_mb", "d_mb_minus_d_fb"):
        cmp[f"primary.{k}"] = (out["primary"][k]["mean"], pp[k]["mean"], out["primary"][k]["ci95"], pp[k]["ci95"])
    for k, v in out["primary"]["pi_means"].items():
        cmp[f"primary.{k}"] = (v, pp["pi_means"][k], None, None)
    n_rows = 0
    for r in ss["rows"]:
        i = r["seed"] - 3700
        for k, v in out["primary"]["pi_rows"].items():
            if f"pi_{k}" in r:
                n_rows += 1
                if abs(v[i] - r[f"pi_{k}"]) > TOL:
                    flags.append(f"row seed {r['seed']} pi_{k}: mine {v[i]} vs theirs {r[f'pi_{k}']}")
        if r.get("errors"):
            flags.append(f"their row seed {r['seed']} errors: {r['errors']}")
    hp = json.loads((HERE / "switch_horizon_posthoc_s46.json").read_text(encoding="utf-8"))
    for k, v in out["horizon"]["pi"].items():
        cmp[f"horizon.pi.{k}"] = (v["mean"], hp["pi"][k]["mean"], v["ci95"], hp["pi"][k]["ci95"])
    for h in map(str, H):
        v = out["horizon"]["d50_minus_25"][h]
        cmp[f"horizon.d.{h}"] = (v["mean"], hp["d50_minus_25"][h]["mean"], v["ci95"], hp["d50_minus_25"][h]["ci95"])
        cmp[f"horizon.sep.{h}"] = (out["horizon"]["L_F_minus_L_G_mean"][h], hp["L_F_minus_L_G_mean"][h], None, None)
    maxdiff = 0.0
    for k, (a, b, ca, cb) in cmp.items():
        maxdiff = max(maxdiff, abs(a - b))
        if abs(a - b) > TOL:
            flags.append(f"{k} mean: mine {a} vs theirs {b}")
        if ca is not None and max(abs(x - y) for x, y in zip(ca, cb)) > TOL:
            flags.append(f"{k} ci: mine {ca} vs theirs {cb}")
    return {"n_compared_summaries": len(cmp), "n_compared_rows": n_rows, "max_abs_mean_diff": maxdiff,
            "n_flags": len(flags), "flags": flags,
            "their_reading": {k: pp.get(k) for k in ("n", "reference", "minibatch")}}


def main() -> None:
    out = compute()
    out["compare"] = compare(out)
    (HERE / "switch_recheck_s46.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("n_errors", "errors", "L_F_minus_L_G_end", "compare")}, indent=1, ensure_ascii=False))
    print(json.dumps({k: out["primary"][k] for k in ("pi_means", "d_fb", "d_mb", "d_mb_minus_d_fb")}, indent=1))
    print(json.dumps({"d50_minus_25": out["horizon"]["d50_minus_25"],
                      "pi": {k: round(v["mean"], 4) for k, v in out["horizon"]["pi"].items()}}, indent=1))


if __name__ == "__main__":
    main()
