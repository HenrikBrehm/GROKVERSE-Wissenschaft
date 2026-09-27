#!/usr/bin/env python3
"""Reproduction script for K4c (Section 3.4, Fig. 3): after a data switch at t = 25 the final model relies on the NEW target frequencies,
after t = 50 on the OLD ones (N29, manifest 087e042). Session 26, UNTESTED (needs the train.py equivalence check first).

From scratch: builds the N29 splits (EXP-053 overlap_split, omega = 0, calibrated eps), trains per seed A->B and B->A at t in {25, 50} for
t + 4000 steps with the lean trainer repro/train.py (--save-model), removes the old / new target frequencies from W_E[:p] of the final
model (projection onto the complement of their cos/sin subspace, rest of the network unchanged) and measures accuracy on the held-out
test set of the seed. Per seed and t: acc_old / acc_new = mean over both directions.
  H1 (hold at 50):   (acc_new(50) - acc_old(50)) - 0.3 > 0        H2 (switch at 25):   (acc_old(25) - acc_new(25)) - 0.3 > 0
Same statistics as the frozen analysis (one-sided t-test, Holm over {H1, H2}, bootstrap 95% CI; helpers imported from confirm_p1).
--compare-n29 prints the largest per-seed deviation of acc_old/acc_new from lab/confirm/N29_summary.json (same seeds 2250-2269).

  python lab/tools/guarded_run.py -- python lab/paper/repro/k4c.py --smoke                  # 1 seed, 300 steps after the switch, CPU
  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/paper/repro/k4c.py --device cuda --workers 8 --compare-n29
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "experiments/EXP-053-p3-overlap-design"))
sys.path.insert(0, str(ROOT / "training"))
import confirm_p1 as c1  # noqa: E402  (t_test_secondary, boot_ci, holm of the frozen analyses)
import overlap_split as ov  # noqa: E402  (split construction of N28/N29)
from grokverse.config import get_config  # noqa: E402
from grokverse.models import build_model  # noqa: E402

P, OMEGA, MIN_DIFF, BUDGET, TS = 113, 0.0, 0.3, 4000, (25, 50)
CAL = LAB / "experiments/EXP-053-p3-overlap-design/calibration.json"


def complement(W: np.ndarray, T: list[int]) -> np.ndarray:
    """W [p, d] minus its projection onto the real Fourier subspace of the frequencies T (as EXP-061 project / N29)."""
    a = np.arange(P)
    Bm = np.concatenate([np.stack([np.cos(2 * np.pi * k * a / P), np.sin(2 * np.pi * k * a / P)], 1) for k in T], 1)
    Q, _ = np.linalg.qr(Bm)
    return W - Q @ (Q.T @ W)


@torch.no_grad()
def accuracy(model: torch.nn.Module, W_rows: np.ndarray | None, idx: np.ndarray) -> float:
    """Accuracy on pairs idx (flat a*p+b) with W_E[:p] optionally replaced (as EXP-055 evaluate: input [a, b, '='], '=' = p)."""
    saved = model.W_E.data.clone()
    if W_rows is not None:
        model.W_E.data[:P] = torch.from_numpy(W_rows).to(model.W_E.dtype)
    a, b = idx // P, idx % P
    x = torch.from_numpy(np.stack([a, b, np.full(len(idx), P)], 1)).long()
    acc = float((model.logits_last(x)[:, :P].double().argmax(-1) == torch.from_numpy((a + b) % P).long()).double().mean())
    model.W_E.data.copy_(saved)
    return acc


def run(a: argparse.Namespace, s: int, t: int, first: Path, second: Path, test: Path, out: Path) -> Path:
    if not cached(out, s, t, t + a.budget):
        cmd = [sys.executable, str(HERE / "train.py"), "--seed", str(s), "--split-file", str(first), "--switch-split-file", str(second),
               "--switch-step", str(t), "--test-file", str(test), "--steps", str(t + a.budget), "--device", a.device,
               "--threads", str(a.threads), "--save-model", "--out", str(out)]
        subprocess.run(cmd, check=True)
    return out


def cached(out: Path, s: int, t: int, steps: int) -> bool:
    """Reuse a run only if result.json (written last) exists and matches seed, switch step and length (review s26, point 1)."""
    f = out / "result.json"
    if not (f.exists() and (out / "model_final.pt").exists()):
        return False
    r = json.loads(f.read_text(encoding="utf-8"))
    return (r.get("seed"), r.get("switch_step"), r.get("steps")) == (s, t, steps)


def ablate(s: int, out: Path, old: list[int], new: list[int], test: np.ndarray) -> dict:
    res = json.loads((out / "result.json").read_text(encoding="utf-8"))
    model = build_model(get_config("arch25k", seed=s, steps=res["steps"], threads=1))
    model.load_state_dict(torch.load(out / "model_final.pt", map_location="cpu"))
    model.eval()
    W = model.W_E.detach().numpy().astype(np.float64)[:P]
    return {"base": accuracy(model, None, test), "acc_old": accuracy(model, complement(W, old), test),
            "acc_new": accuracy(model, complement(W, new), test)}


def main() -> None:
    ap = argparse.ArgumentParser(description="K4c reproduction (N29 construction)")
    ap.add_argument("--seeds", default="2250-2269")
    ap.add_argument("--budget", type=int, default=BUDGET)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default=str(HERE / "out" / "k4c"))
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--compare-n29", action="store_true")
    ap.add_argument("--tol", type=float, default=0.02, help="max |mean acc - N29 mean| per quantity for --compare-n29 (per-seed deviations only reported)")
    a = ap.parse_args()
    if a.compare_n29 and (a.smoke or not a.device.startswith("cuda") or a.budget != BUDGET):
        raise SystemExit("--compare-n29 needs the full budget on cuda (N29 ran on the GPU), not --smoke")
    lo, hi = (int(x) for x in a.seeds.split("-"))
    seeds = list(range(lo, hi + 1))
    if a.smoke:
        seeds, a.budget, a.out = seeds[:1], 300, str(Path(a.out).with_name(Path(a.out).name + "_smoke"))
    root = Path(a.out) / f"budget{a.budget}_{a.device.replace(':', '')}"
    (root / "splits").mkdir(parents=True, exist_ok=True)
    eps = json.loads(CAL.read_text(encoding="utf-8"))["levels"][str(OMEGA)]["eps"]
    jobs, meta = [], {}
    for s in seeds:
        F, G = ov.targets(s)
        d = ov.build(s, OMEGA, eps)
        files = {}
        for k in ("A", "B", "test"):
            f = root / "splits" / f"seed{s}_{k}.npy"
            if f.exists() and not np.array_equal(np.load(f), d[k].astype(np.int64)):
                raise SystemExit(f"{f} differs from the deterministic construction")
            np.save(f, d[k].astype(np.int64))
            files[k] = f
        meta[s] = {"F": F, "G": G, "test": d["test"].astype(np.int64)}
        for t in TS:
            for first, second, tag in ((files["A"], files["B"], "AB"), (files["B"], files["A"], "BA")):
                jobs.append((s, t, tag, first, second, files["test"], root / "runs" / f"seed{s}_{tag}_at{t}"))
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        outs = dict(zip([(s, t, tag) for s, t, tag, *_ in jobs], ex.map(lambda j: run(a, j[0], j[1], j[3], j[4], j[5], j[6]), jobs)))
    torch.set_num_threads(4)                  # as p2.load_model_bytes in the N29 analysis (review s26, point 4)
    rows = []
    for s in seeds:
        F, G, test = meta[s]["F"], meta[s]["G"], meta[s]["test"]
        ev = {(t, tag): ablate(s, outs[(s, t, tag)], *((F, G) if tag == "AB" else (G, F)), test) for t in TS for tag in ("AB", "BA")}
        r = {"seed": s, "base_min": min(e["base"] for e in ev.values())}
        for t in TS:
            r[f"old{t}"] = float(np.mean([ev[(t, k)]["acc_old"] for k in ("AB", "BA")]))
            r[f"new{t}"] = float(np.mean([ev[(t, k)]["acc_new"] for k in ("AB", "BA")]))
        rows.append(r)
    X = {"H1": np.array([(r["new50"] - r["old50"]) - MIN_DIFF for r in rows]), "H2": np.array([(r["old25"] - r["new25"]) - MIN_DIFF for r in rows])}
    out: dict = {"budget": a.budget, "device": a.device, "n": len(rows), "min_diff": MIN_DIFF,
                 "n_generalised": sum(r["base_min"] >= 0.9 for r in rows)}
    if len(rows) >= 3:
        tt = {k: c1.t_test_secondary(v) for k, v in X.items()}
        ph = c1.holm({k: v["p_one_sided"] for k, v in tt.items()})
        rng = np.random.default_rng(29)
        for k, v in X.items():
            out[k] = {"mean_diff": float(v.mean() + MIN_DIFF), "sd": float(v.std(ddof=1)), "p_holm": ph[k],
                      "ci95_minus_min": c1.boot_ci(v, rng), "n_positive": int((v > 0).sum())}
    else:
        out.update({k: {"mean_diff": float(v.mean() + MIN_DIFF)} for k, v in X.items()})
    out["rows"] = rows
    if a.compare_n29:
        ref = {r["seed"]: r for r in json.loads((LAB / "confirm" / "N29_summary.json").read_text(encoding="utf-8"))["rows"] if not r.get("technical")}
        qs, both = ("old25", "new25", "old50", "new50"), [r for r in rows if r["seed"] in ref]
        mean_diff = {q: abs(float(np.mean([r[q] for r in both])) - float(np.mean([ref[r["seed"]][q] for r in both]))) for q in qs} if both else {}
        out["compare_n29"] = {"n_seeds": len(both), "mean_abs_diff": mean_diff,     # gate: means (GPU nondeterminism moves single seeds, review s26 point 3)
                              "max_seed_abs_diff": max(abs(r[q] - ref[r["seed"]][q]) for r in both for q in qs) if both else None}
    (root / "k4c_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1), flush=True)
    if a.compare_n29 and (not out["compare_n29"]["n_seeds"] or max(out["compare_n29"]["mean_abs_diff"].values()) > a.tol):
        raise SystemExit(f"[k4c] does not reproduce N29 within tol {a.tol}")


if __name__ == "__main__":
    main()
