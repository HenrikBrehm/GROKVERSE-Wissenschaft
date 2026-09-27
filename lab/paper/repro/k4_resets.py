#!/usr/bin/env python3
"""Reproduction script for K4d / K4e (Section 3.5, Fig. 3): partial resets at a data switch after t = 50 steps
(N29b, manifest db31564: attention vs MLP reset; N29c, manifest 3c9cb63: value path vs query/key reset). Session 27, UNTESTED
(needs the train.py equivalence check first, see README).

From scratch: builds the splits of N29b/N29c (EXP-053 overlap_split, omega = 0, calibrated eps), trains per seed A->B and B->A at
t = 50 for 50 + 4000 steps with the lean trainer repro/train.py (--save-model) in three arms (normal and two --reset-at-switch parts:
the named weights back to their init values, their AdamW state cleared), then removes the old / new target frequencies from W_E[:p] of
each final model (as k4c.py) and measures accuracy on the held-out test set of the seed. Per seed and arm, mean over both directions:
  R(arm) = acc_new - acc_old     (R > 0: the final model relies on the OLD targets)
  n29b:  H1 = R(normal) - R(rsattn) - 0.5 > 0      H2 = R(rsmlp) - R(rsattn) - 0.3 > 0
  n29c:  H1 = R(normal) - R(rsvo)   - 0.5 > 0      H2 = R(rsqk)  - R(rsvo)   - 0.3 > 0
Same statistics as the frozen analyses (one-sided t-test, Holm over {H1, H2}, bootstrap 95 % CI; helpers from confirm_p1).
--compare prints the per-arm mean R against lab/confirm/<BLOCK>_summary.json (same seeds) and fails above --tol.

  python lab/tools/guarded_run.py -- python lab/paper/repro/k4_resets.py --block n29b --smoke        # 1 seed, 300 steps, CPU
  python lab/tools/guarded_run.py -- C:/Users/henri/Documents/Brain/GROKVERSE_Wissenschaft/.venv-gpu/Scripts/python.exe lab/paper/repro/k4_resets.py --block n29c --device cuda --workers 8 --compare
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
sys.path.insert(0, str(HERE))
import k4c  # noqa: E402  (complement/accuracy/ablate, path setup, confirm_p1 helpers, overlap_split)

LAB, T, BUDGET = k4c.LAB, 50, 4000
BLOCKS = {  # frozen definitions of N29b / N29c (confirm_n29b.py, confirm_n29c.py)
    "n29b": {"seeds": (2300, 2319), "arms": {"normal": None, "rsattn": "attn", "rsmlp": "mlp"}, "reset": "rsattn", "control": "rsmlp",
             "summary": "N29b_summary.json"},
    "n29c": {"seeds": (2320, 2339), "arms": {"normal": None, "rsvo": "vo", "rsqk": "qk"}, "reset": "rsvo", "control": "rsqk",
             "summary": "N29c_summary.json"},
}
MIN_DIFF = {"H1": 0.5, "H2": 0.3}


def cached(out: Path, s: int, steps: int, part: str | None) -> bool:
    """Reuse a run only if result.json (written last) matches seed, switch step, length and reset part (as k4c.cached)."""
    f = out / "result.json"
    if not (f.exists() and (out / "model_final.pt").exists()):
        return False
    r = json.loads(f.read_text(encoding="utf-8"))
    return (r.get("seed"), r.get("switch_step"), r.get("steps"), r.get("reset_at_switch")) == (s, T, steps, part)


def run(a: argparse.Namespace, s: int, part: str | None, first: Path, second: Path, test: Path, out: Path) -> Path:
    if not cached(out, s, T + a.budget, part):
        cmd = [sys.executable, str(HERE / "train.py"), "--seed", str(s), "--split-file", str(first), "--switch-split-file", str(second),
               "--switch-step", str(T), "--test-file", str(test), "--steps", str(T + a.budget), "--device", a.device,
               "--threads", str(a.threads), "--save-model", "--out", str(out)]
        if part:
            cmd += ["--reset-at-switch", part]
        subprocess.run(cmd, check=True)
    return out


def contrasts(r: dict, blk: dict) -> dict[str, float]:
    return {"H1": r["R_normal"] - r[f"R_{blk['reset']}"] - MIN_DIFF["H1"],
            "H2": r[f"R_{blk['control']}"] - r[f"R_{blk['reset']}"] - MIN_DIFF["H2"]}


def statistics(rows: list[dict], blk: dict) -> dict:
    X = {k: np.array([contrasts(r, blk)[k] for r in rows]) for k in MIN_DIFF}
    if len(rows) < 3:
        return {k: {"mean_diff": float(v.mean() + MIN_DIFF[k])} for k, v in X.items()}
    tt = {k: k4c.c1.t_test_secondary(v) for k, v in X.items()}
    ph = k4c.c1.holm({k: v["p_one_sided"] for k, v in tt.items()})
    rng = np.random.default_rng(29)
    return {k: {"mean_diff": float(v.mean() + MIN_DIFF[k]), "sd": float(v.std(ddof=1)), "p_holm": ph[k],
                "ci95_minus_min": k4c.c1.boot_ci(v, rng), "n_positive": int((v > 0).sum())} for k, v in X.items()}


def main() -> None:
    ap = argparse.ArgumentParser(description="K4d/K4e reproduction (N29b/N29c construction)")
    ap.add_argument("--block", required=True, choices=tuple(BLOCKS))
    ap.add_argument("--budget", type=int, default=BUDGET)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--threads", type=int, default=1)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--out", default=None)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--tol", type=float, default=0.05, help="max |mean R - frozen mean R| per arm for --compare")
    a = ap.parse_args()
    blk = BLOCKS[a.block]
    if a.compare and (a.smoke or not a.device.startswith("cuda") or a.budget != BUDGET):
        raise SystemExit("--compare needs the full budget on cuda (N29b/N29c ran on the GPU), not --smoke")
    seeds = list(range(blk["seeds"][0], blk["seeds"][1] + 1))
    out_dir = Path(a.out) if a.out else HERE / "out" / f"k4_resets_{a.block}"
    if a.smoke:
        seeds, a.budget, out_dir = seeds[:1], 300, out_dir.with_name(out_dir.name + "_smoke")
    root = out_dir / f"budget{a.budget}_{a.device.replace(':', '')}"
    (root / "splits").mkdir(parents=True, exist_ok=True)
    eps = json.loads(k4c.CAL.read_text(encoding="utf-8"))["levels"][str(k4c.OMEGA)]["eps"]
    jobs, meta = [], {}
    for s in seeds:
        F, G = k4c.ov.targets(s)
        d = k4c.ov.build(s, k4c.OMEGA, eps)
        files = {}
        for k in ("A", "B", "test"):
            f = root / "splits" / f"seed{s}_{k}.npy"
            if f.exists() and not np.array_equal(np.load(f), d[k].astype(np.int64)):
                raise SystemExit(f"{f} differs from the deterministic construction")
            np.save(f, d[k].astype(np.int64))
            files[k] = f
        meta[s] = {"F": F, "G": G, "test": d["test"].astype(np.int64)}
        for arm, part in blk["arms"].items():
            for first, second, tag in ((files["A"], files["B"], "AB"), (files["B"], files["A"], "BA")):
                jobs.append(((s, arm, tag), part, first, second, files["test"], root / "runs" / f"seed{s}_{tag}_{arm}"))
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        outs = dict(zip([j[0] for j in jobs], ex.map(lambda j: run(a, j[0][0], j[1], j[2], j[3], j[4], j[5]), jobs)))
    torch.set_num_threads(4)                  # as the frozen N29b/N29c analysis (p2.load_model_bytes)
    rows = []
    for s in seeds:
        F, G, test = meta[s]["F"], meta[s]["G"], meta[s]["test"]
        r: dict = {"seed": s}
        bases = []
        for arm in blk["arms"]:
            ev = {tag: k4c.ablate(s, outs[(s, arm, tag)], *((F, G) if tag == "AB" else (G, F)), test) for tag in ("AB", "BA")}
            bases += [e["base"] for e in ev.values()]
            r[f"R_{arm}"] = float(np.mean([ev[k]["acc_new"] - ev[k]["acc_old"] for k in ("AB", "BA")]))
        r["generalised"] = min(bases) >= 0.9
        rows.append(r)
    out: dict = {"block": a.block, "budget": a.budget, "device": a.device, "n": len(rows), "min_diff": MIN_DIFF,
                 "n_generalised": sum(r["generalised"] for r in rows),
                 "mean_R": {arm: float(np.mean([r[f"R_{arm}"] for r in rows])) for arm in blk["arms"]},
                 **statistics(rows, blk), "rows": rows}
    if a.compare:
        ref = json.loads((LAB / "confirm" / blk["summary"]).read_text(encoding="utf-8"))
        ref_rows = {r["seed"]: r for r in ref["rows"] if not r.get("technical")}
        both = [r for r in rows if r["seed"] in ref_rows]
        diff = {arm: abs(float(np.mean([r[f"R_{arm}"] for r in both])) - float(np.mean([ref_rows[r["seed"]][f"R_{arm}"] for r in both])))
                for arm in blk["arms"]} if both else {}
        out["compare"] = {"n_seeds": len(both), "mean_abs_diff_R": diff,
                          "max_seed_abs_diff_R": max(abs(r[f"R_{arm}"] - ref_rows[r["seed"]][f"R_{arm}"]) for r in both for arm in blk["arms"]) if both else None}
    (root / f"k4_resets_{a.block}_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1), flush=True)
    if a.compare and (not out["compare"]["n_seeds"] or max(out["compare"]["mean_abs_diff_R"].values()) > a.tol):
        raise SystemExit(f"[k4_resets] does not reproduce {a.block} within tol {a.tol}")


if __name__ == "__main__":
    main()
