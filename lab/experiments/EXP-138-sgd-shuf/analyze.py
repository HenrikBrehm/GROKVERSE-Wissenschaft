"""EXP-138 analysis (readings fixed in README and here before any run, session 67).
Per clip value c and seed s: Delta_pow (P1 formula, additive DFT spectra.npy, k = 1..56) at step 2000 between the F and the G run,
separately for the engineered split (eng) and the count-matched control (shuf; same a/b token counts, pair structure destroyed).
Per clip value (4 seeds; pilot, no test):
  'Paarstruktur traegt'    : Delta_eng - Delta_shuf > 1 in 4/4 seeds
  'Haeufigkeiten tragen'   : Delta_shuf > 1 in >= 3/4 seeds
  (both labels can hold; neither -> 'unklar'); 'keine Steuerung' if |Delta_eng| <= 1 in >= 3/4 (overrides);
  < 4 complete seeds -> 'nicht auswertbar'.
Descriptive: Delta at 250, final train accuracy, clipped share.
  PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-138-sgd-shuf/analyze.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_jobs as mj  # noqa: E402

RAW = HERE / "raw"
SPL = HERE.parents[0] / "EXP-047-marginal-control" / "splits"


def delta_pow(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float | None:
    s = lambda pw, S: float(pw[[k - 1 for k in S]].sum())   # noqa: E731
    sums = [s(pF, F), s(pF, G), s(pG, G), s(pG, F)]
    if not all(np.isfinite(x) and x > 0 for x in sums):
        return None
    return float(np.log(sums[0] / sums[1]) + np.log(sums[2] / sums[3]))


def index_runs() -> dict:
    out = {}
    for f in RAW.glob("*/result.json"):
        r = json.loads(f.read_text(encoding="utf-8"))
        if r.get("status") != "completed" or r.get("max_steps") != 2000 or r.get("optimizer") != "sgdm":
            continue
        clip = (r.get("events", {}).get("sgd_clip") or {}).get("max_norm")
        key = (clip, Path(r["split_file"]).stem)
        out.setdefault(key, []).append(f.parent)
    return out


def load(idx: dict, clip: float, s: int, kind: str, arm: str) -> dict | str:
    st = f"split_add113_seed{s}_{kind}_{arm}"
    hits = idx.get((clip, st), [])
    if len(hits) != 1:
        return f"{st} clip {clip}: {len(hits)} runs"
    d = hits[0]
    r = json.loads((d / "result.json").read_text(encoding="utf-8"))
    steps = [int(x) for x in np.load(d / "spectra_steps.npy")]
    sp = np.load(d / "spectra.npy")
    if 2000 not in steps or 250 not in steps or not np.isfinite(sp).all():
        return f"{st}: spectra incomplete"
    T = json.loads((SPL / f"{st}.json").read_text(encoding="utf-8"))["targets"]
    return {"p2000": sp[steps.index(2000)], "p250": sp[steps.index(250)], "T": T,
            "train": (r.get("final_acc") or {}).get("train"),
            "clipped": (r["events"]["sgd_clip"]["clipped_steps"]) / 2000}


def reading(rows: list[dict]) -> str:
    if len(rows) < len(mj.SEEDS):
        return "nicht auswertbar"
    e = np.array([r["eng"] for r in rows])
    sh = np.array([r["shuf"] for r in rows])
    if (np.abs(e) <= 1).sum() >= 3:
        return "keine Steuerung"
    labels = []
    if ((e - sh) > 1).all():
        labels.append("Paarstruktur traegt")
    if (sh > 1).sum() >= 3:
        labels.append("Haeufigkeiten tragen")
    return " + ".join(labels) if labels else "unklar"


def main(loader=None) -> dict:
    idx = index_runs() if loader is None else None
    ld = loader or (lambda c, s, k, a: load(idx, c, s, k, a))
    out = {}
    for c in mj.CLIPS:
        rows, bad = [], []
        for s in mj.SEEDS:
            R = {(k, a): ld(c, s, k, a) for k in mj.KINDS for a in "FG"}
            b = [v for v in R.values() if isinstance(v, str)]
            if b:
                bad += b
                continue
            row = {"seed": s}
            for k in mj.KINDS:
                F, G = R[(k, "F")], R[(k, "G")]
                row[k] = delta_pow(F["p2000"], G["p2000"], F["T"], G["T"])
                row[k + "_250"] = delta_pow(F["p250"], G["p250"], F["T"], G["T"])
                row[k + "_train"] = [F["train"], G["train"]]
                row[k + "_clipped"] = [F["clipped"], G["clipped"]]
            if row["eng"] is None or row["shuf"] is None:
                bad.append(f"seed {s}: Delta undefined")
                continue
            rows.append(row)
        out[str(c)] = {"reading": reading(rows), "rows": rows, "problems": bad}
    return out


def selftest() -> None:
    rng = np.random.default_rng(0)

    def fake(eng_s, shuf_s):
        def ld(c, s, k, a):
            T = [1, 2, 3, 4, 5] if a == "F" else [6, 7, 8, 9, 10]
            v = np.ones(56) + 0.1 * rng.random(56)
            v[[t - 1 for t in T]] += eng_s if k == "eng" else shuf_s
            return {"p2000": v, "p250": v, "T": T, "train": 0.5, "clipped": 0.9}
        return ld
    assert all(v["reading"] == "Paarstruktur traegt" for v in main(fake(5.0, 0.0)).values())
    assert all(v["reading"] == "Paarstruktur traegt + Haeufigkeiten tragen" for v in main(fake(20.0, 2.0)).values())
    assert all(v["reading"] == "Haeufigkeiten tragen" for v in main(fake(5.0, 5.0)).values())
    assert all(v["reading"] == "keine Steuerung" for v in main(fake(0.0, 0.0)).values())
    assert all(v["reading"] == "nicht auswertbar" for v in main(lambda *a: "x").values())
    print("[exp138] selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        res = main()
        (HERE / "summary.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        for c, v in res.items():
            print(c, v["reading"], [(r["seed"], round(r["eng"], 2), round(r["shuf"], 2)) for r in v["rows"]], v["problems"])
