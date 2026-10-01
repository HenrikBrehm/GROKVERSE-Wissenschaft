"""EXP-143 analysis (session 70, written before any p-9973 training result was seen; readings Q1-Q3 as in README.md).

Per arm (seed, set R/F, order iid/stride): status, steps, gen step, final test accuracy (common 20 000-pair sample), W_E
top-5 at the last stored spectrum, target power share and median ratio, k = 101 and the stride family
{k : |99 k mod 9973| <= 26} (max power / median, best rank, power share against the uniform share). Trajectory of these numbers every 5000 steps with --traj.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-143-ledoux-regime/analyze.py [--traj] [--root DIR]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P, S = 9973, 99
# S70 review H3 (before any p-9973 result): the stride family is every k with a small residue |S*k mod P|, not
# neighbours k +- 1 (1913/1915 have residues ~ +-100). RESIDUE_MAX 26 = residue of LeDoux's F = 101.
RESIDUE_MAX = 26
STRIDE_FAMILY = tuple(k for k in range(1, (P - 1) // 2 + 1) if min(S * k % P, P - S * k % P) <= RESIDUE_MAX)
STRIDE_BANDS = {"k101": (101,), "family": STRIDE_FAMILY}


def targets(seed: int) -> list[int]:
    meta = json.loads((HERE / "splits" / "meta.json").read_text())
    return meta[f"split_add9973_n300000_seed{seed}_F"]["targets"]


def readout(power: np.ndarray, T: list[int]) -> dict:
    med = float(np.median(power))
    rank = np.empty(len(power), int)
    rank[np.argsort(-power)] = np.arange(1, len(power) + 1)      # 1 = largest
    top5 = sorted((np.argsort(-power)[:5] + 1).tolist())
    out = {"top5": top5, "target_share": float(power[[k - 1 for k in T]].sum() / power.sum()),
           "target_median_ratio": float(np.median(power[[k - 1 for k in T]]) / med),
           "targets_in_top5": len(set(top5) & set(T))}
    for name, band in STRIDE_BANDS.items():
        out[f"{name}_max_ratio"] = float(max(power[k - 1] for k in band) / med)
        out[f"{name}_best_rank"] = int(min(rank[k - 1] for k in band))
        out[f"{name}_in_top5"] = bool(set(top5) & set(band))
    out["family_share"] = float(power[[k - 1 for k in STRIDE_FAMILY]].sum() / power.sum())
    out["family_share_null"] = len(STRIDE_FAMILY) / len(power)       # uniform-spectrum reference
    return out


def load(root: Path) -> list[dict]:
    rows = []
    for d in sorted(root.iterdir()):
        f = d / "result.json"
        if not d.is_dir() or not f.exists():
            continue
        r = json.loads(f.read_text())
        m = re.search(r"seed(\d+)_([FR])\.npy$", r["split_file"])
        seed, arm = int(m.group(1)), m.group(2)
        row = {"seed": seed, "wd": float(r["config"]["weight_decay"]), "set": arm, "order": r.get("order", "iid"),
               "status": r["status"],
               "steps": r.get("steps_completed"), "gen": (r.get("events") or {}).get("generalization_step"),
               "test_last": (r["dense"]["test_acc"] or [None])[-1] if r.get("dense") else None,
               "test_final": (r.get("final_acc") or {}).get("test"), "dir": d}
        sp, st = d / "spectra.npy", d / "spectra_steps.npy"
        if sp.exists() and st.exists():
            S, steps = np.load(sp), np.load(st)
            T = targets(seed)
            row["spec_step"] = int(steps[-1])
            row.update(readout(S[-1], T))
            row["traj"] = [(int(s), readout(S[i], T)) for i, s in enumerate(steps)]
        rows.append(row)
    return rows


def gen_ok(row: dict | None) -> bool | None:
    return None if row is None else row["gen"] is not None


def reading(rows: list[dict], seed: int, wd: float) -> dict:
    sel = [r for r in rows if r["seed"] == seed and r["wd"] == wd]
    get = lambda s, o: next((r for r in sel if r["set"] == s and r["order"] == o), None)  # noqa: E731
    fi, ri, fs, rs = get("F", "iid"), get("R", "iid"), get("F", "stride"), get("R", "stride")
    done = lambda r: r is not None and r["status"] == "completed"   # noqa: E731
    partial = [f"{r['set']}-{r['order']} {r['status']} bei {r['steps']}" for r in (fi, ri, fs, rs)
               if r is not None and r["status"] != "completed"]   # S70 review M3: killed/diverged arms stay visible
    out_partial = {"teilweise": partial} if partial else {}
    out = {}
    if done(fi) and done(ri):
        g = (gen_ok(fi), gen_ok(ri))
        out["Q1"] = {(True, False): "Inhalt ersetzt Reihenfolge auch im LeDoux-Regime (Pilot)",
                     (False, False): "im Budget keine Aussage",
                     (True, True): "mit unserem Modell generalisiert auch Zufall + i.i.d. (anders als bei LeDoux' Modell)",
                     (False, True): "unklar"}[g]
    else:
        out["Q1"] = "offen (Arme nicht fertig)"
    if done(rs):
        stride_top = rs.get("family_in_top5")
        out["Q2"] = ("LeDoux-Effekt mit unserem Modell reproduziert" if gen_ok(rs) and stride_top
                     else "nicht im Budget (R-stride generalisiert nicht)" if not gen_ok(rs)     # review H1
                     else f"generalisiert ohne Stride-Familie in den Top-5 (Familienanteil {rs['family_share']:.3f})")
    else:
        out["Q2"] = "offen"
    if done(fs) and "top5" in fs:
        nt, st = fs["targets_in_top5"], fs.get("family_in_top5")
        q3 = ("Menge gewinnt" if nt >= 3 and not st else "Reihenfolge gewinnt" if st and nt <= 1
              else "beide" if st and nt >= 2 else "unklar")
        if not gen_ok(fs):            # review M1: a memorising W_E can show the targets from the mask alone
            q3 = f"nur beschreibend, nicht generalisiert (Muster wäre: {q3})"
        out["Q3"] = f"{q3} (gen {fs['gen']}; F-Ziele in Top-5 {nt}; Stride-Familie in Top-5 {bool(st)}; Familienanteil {fs['family_share']:.3f})"
    else:
        out["Q3"] = "offen"
    return {**out, **out_partial}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(HERE / "raw"))
    ap.add_argument("--traj", action="store_true")
    a = ap.parse_args()
    rows = load(Path(a.root))
    if not rows:
        raise SystemExit(f"no runs under {a.root}")
    keys = ("seed", "wd", "set", "order", "status", "steps", "gen", "test_last", "test_final", "spec_step", "top5",
            "targets_in_top5", "target_median_ratio", "k101_max_ratio", "k101_best_rank", "family_max_ratio",
            "family_best_rank", "family_share", "family_share_null")
    for r in rows:
        print({k: (round(r[k], 4) if isinstance(r.get(k), float) else r.get(k)) for k in keys})
        if a.traj and "traj" in r:
            for s, ro in r["traj"]:
                print(f"   step {s:>7}: top5 {ro['top5']}, T/med {ro['target_median_ratio']:.2f}, "
                      f"k101 {ro['k101_max_ratio']:.2f} (rank {ro['k101_best_rank']}), "
                      f"family share {ro['family_share']:.4f} (null {ro['family_share_null']:.4f}, best rank {ro['family_best_rank']})")
    for seed, wd in sorted({(r["seed"], r["wd"]) for r in rows}):
        tag = "primär" if wd == 0.1 else "Nebenarm"   # S70 Nachtrag c: wd 0.1 primary, preset wd 1.0 secondary
        print(f"seed {seed} wd {wd} ({tag}):", json.dumps(reading(rows, seed, wd), ensure_ascii=False))


if __name__ == "__main__":
    main()
