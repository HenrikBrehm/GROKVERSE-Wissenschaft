"""EXP-074 preparation (post hoc, exploration, numpy only): persistence pi (EXP-056/059 definition) of the add-113 reset arms at t = 50
(EXP-067: rsattn/rsmlp/rsunembed, EXP-069: rsqk/rsvo) against normal (EXP-059, t = 50), seeds 400-409. Reads the final W_E snapshots of
completed runs; checks status and step count only (no full loader). Gives the add-113 reference for the EXP-074 readings.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[2]
E = LAB / "experiments"
SPL = E / "EXP-056-overlap-persistence/splits"
P, T = 113, 50
ARMS = {"normal": (E / "EXP-059-momentum-exposure/raw", ""), "rsattn": (E / "EXP-067-exclusion-part/raw", "_rsattn"),
        "rsmlp": (E / "EXP-067-exclusion-part/raw", "_rsmlp"), "rsunembed": (E / "EXP-067-exclusion-part/raw", "_rsunembed"),
        "rsqk": (E / "EXP-069-attention-part/raw", "_rsqk"), "rsvo": (E / "EXP-069-attention-part/raw", "_rsvo")}


def power(d: Path, steps: int) -> np.ndarray:
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    assert res["status"] == "completed" and res["steps_completed"] == steps, d
    snaps, st = np.load(d / "we_snapshots.npy"), list(np.load(d / "we_snapshot_steps.npy"))
    X = snaps[st.index(steps)].astype(np.float64)[:P]
    sq = (np.abs(np.fft.fft(X, axis=0)) ** 2).sum(1)
    return 2.0 * sq[1:(P - 1) // 2 + 1] / P


def one(root: Path, pat: str) -> Path:
    hits = [h for h in root.glob(pat) if h.is_dir()]
    assert len(hits) == 1, (pat, hits)
    return hits[0]


def main() -> None:
    rows = []
    for s in range(400, 410):
        meta = json.loads((SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        lr = lambda pw: float(np.log(pw[[k - 1 for k in F]].sum() / pw[[k - 1 for k in G]].sum()))   # noqa: E731
        LA = lr(power(one(E / "EXP-056-overlap-persistence/raw", f"EXP-018_baseline_seed{s}_thr1_seed{s}_w0_A_devcuda"), 2000))
        LB = lr(power(one(E / "EXP-056-overlap-persistence/raw", f"EXP-018_baseline_seed{s}_thr1_seed{s}_w0_B_devcuda"), 2000))
        r = {"seed": s}
        for arm, (root, suf) in ARMS.items():
            L = {k: lr(power(one(root, f"EXP-020_baseline_seed{s}_thr1_seed{s}_w0_{k[0]}_to_seed{s}_w0_{k[1]}_at{T}{suf}_devcuda"), T + 2000))
                 for k in ("AB", "BA")}
            r[arm] = ((L["AB"] - LB) / (LA - LB) + (L["BA"] - LA) / (LB - LA)) / 2
        rows.append(r)
    out = {"median_pi": {a: float(np.median([r[a] for r in rows])) for a in ARMS},
           "median_dpi_vs_normal": {a: float(np.median([r["normal"] - r[a] for r in rows])) for a in ARMS if a != "normal"},
           "n_dpi_gt_0.3": {a: int(sum(r["normal"] - r[a] > 0.3 for r in rows)) for a in ARMS if a != "normal"}, "rows": rows}
    (Path(__file__).parent / "reference_add113.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
