"""EXP-134 analysis (session 64, written before any run; readings in README "Vorab").
Primary (raw_ft, the text-pretrained arms): EXP-105 pilot rules (analyze_pilot) at step 6000 with the precedence
'nicht gelernt (Budget)' if train-fact accuracy < 0.1 in >= 3 of 4 runs.
Descriptive: the same numbers for the from-scratch LM1 partners (same model seed, splits, test set, fact and text stream;
confirmation block already seen), start check (pretrain.json sha + step-0 rows == phase-1 end rows), first step with held-out
accuracy >= 0.5 per run, text validation loss at the end of phase 1 and the number-row norm ratio phase-1 end / init.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-134-text-pretrain-steering/analyze.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
SPL = LAB / "confirm/lm1_splits"
PAIRS = [(4100, 4000), (4101, 4001)]


def _mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


AP = _mod("analyze_pilot_exp105", LAB / "experiments/EXP-105-lm-ladder-stage2/analyze_pilot.py")


def rows_for(root: Path, pretrained: bool) -> list[dict]:
    out = []
    for seed, pair in PAIRS:
        fF, fG = SPL / f"seed{pair}_F.npy", SPL / f"seed{pair}_G.npy"
        TF, TG = AP.targets(fF), AP.targets(fG)
        rF, rG = AP.load(root, seed, fF), AP.load(root, seed, fG)
        cF, cG = rF["res"]["config"], rG["res"]["config"]
        assert not [k for k in cF if k != "split_sha256" and cF[k] != cG.get(k)], (seed, "F and G configs differ")
        start = start_check(root, seed, fF, fG) if pretrained else None
        end = rF["steps"][-1]
        assert end == rG["steps"][-1] == 6000
        half = [next((int(r[0]) for r in x["res"]["curve"] if r[2] >= 0.5), None) for x in (rF, rG)]
        out.append({"seed": seed, "dpow_end": AP.A.delta_pow(rF["P"][end], rG["P"][end], TF, TG),
                    "start_check": start,
                    "test_acc": [rF["res"]["curve"][-1][2], rG["res"]["curve"][-1][2]],
                    "train_acc": [rF["res"]["curve"][-1][1], rG["res"]["curve"][-1][1]],
                    "val_loss": [rF["res"]["curve"][-1][3], rG["res"]["curve"][-1][3]],
                    "first_step_heldout_ge_0.5": half,
                    "gen": [rF["res"]["events"].get("generalization_step"), rG["res"]["events"].get("generalization_step")]})
    return out


def start_check(root: Path, seed: int, fF: Path, fG: Path) -> dict:
    """Review M2/M3: both arms must start from the recorded phase-1 checkpoint (sha) and their step-0 number rows must equal
    the phase-1 end snapshot (Delta_pow at step 0 is 0 by construction and checks nothing)."""
    out = {}
    for f in (fF, fG):
        d = next(x for x in root.iterdir() if x.name.startswith(f"lm2_seed{seed}_{f.stem}_steps"))
        side = json.loads((d / "pretrain.json").read_text(encoding="utf-8"))
        pre = HERE / "raw_pre" / side["pretrain_run"]
        assert hashlib.sha256((pre / "checkpoint.pt").read_bytes()).hexdigest() == side["pretrain_sha256"], (d, "sha")
        s0, p_end = np.load(d / "we_snapshots.npy")[0], np.load(pre / "we_snapshots.npy")[-1]
        out[f.stem] = float(np.abs(s0 - p_end).max())
        assert out[f.stem] < 1e-6, (d, "step-0 rows are not the phase-1 rows")
    return out


def reading(rows: list[dict]) -> str:
    tr = [x for r in rows for x in r["train_acc"]]
    if sum(x < 0.1 for x in tr) >= len(tr) - 1:
        return "nicht gelernt (Budget)"
    dp, acc = [r["dpow_end"] for r in rows], [x for r in rows for x in r["test_acc"]]
    big = all(d is not None and d > 1 for d in dp)
    return ("K2 haelt im LM" if big and sum(x > 0.5 for x in acc) >= len(acc) - 1 else
            "nur Repraesentation" if big and sum(x < 0.1 for x in acc) >= len(acc) - 1 else
            "bricht" if all(d is not None and abs(d) <= 1 for d in dp) else "unklar")


def phase1_info() -> dict:
    info = {}
    for d in sorted((HERE / "raw_pre").iterdir()):
        if not (d / "result.json").exists():
            continue
        r = json.loads((d / "result.json").read_text(encoding="utf-8"))
        W = np.load(d / "we_snapshots.npy")
        info[d.name] = {"status": r["status"], "val_loss_end": r["curve"][-1][3], "text_wraps": r["text_wraps"],
                        "num_row_norm_ratio_end_vs_init": float(np.linalg.norm(W[-1], axis=1).mean() / np.linalg.norm(W[0], axis=1).mean())}
    return info


def main() -> None:
    ft = rows_for(HERE / "raw_ft", True)
    scratch = rows_for(LAB / "confirm/lm1_raw", False)
    out = {"reading": reading(ft), "rows_text_pretrained": ft,
           "descriptive_from_scratch_LM1_partners": {"reading_same_rules": reading(scratch), "rows": scratch},
           "phase1": phase1_info()}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
