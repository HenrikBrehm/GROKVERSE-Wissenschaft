"""EXP-067 (pilot): which part of the rest carries the exclusion of new frequencies at t = 50? Definition: README.md (registered before any run).
Run under guarded_run.py. a, b as EXP-062/063 (final spectra vs the pure EXP-056 runs); function as EXP-064 (descriptive).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, LAB / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


R = _load("exp062", "experiments/EXP-062-rate-race/analyze.py")
G61 = _load("exp061", "experiments/EXP-061-grad-alignment/analyze.py")
E55 = _load("exp055", "experiments/EXP-055-ablation-dose/analyze.py")
A, B, E51 = R.A, R.B, G61.E51
T, P = 50, 113
PARTS = ("attn", "mlp", "unembed")
ARMS = {"normal": (B.root_for(T), ""), "rsrest": (LAB / "experiments/EXP-063-exclusion-locus/raw", "_rsrest")} | \
       {f"rs{x}": (HERE / "raw", f"_rs{x}") for x in PARTS}


def run_dir(s: int, first: str, second: str, arm: str) -> Path | str:
    root, suf = ARMS[arm]
    d = A.find_run(root, f"EXP-0*_baseline_seed{s}_thr*_{A.stem(s, B.OM, first)}_to_{A.stem(s, B.OM, second)}_at{T}{suf}{A.SUF}")
    if d is None:
        return f"{arm} {first}{second}: fehlt"
    res = json.loads((d / "result.json").read_text(encoding="utf-8"))
    if res.get("status") != "completed" or res.get("steps_completed") != T + 2000:
        return f"{arm} {first}{second}: not completed"
    if arm != "normal":
        ev = res.get("events", {}).get("reset_at_switch", {})
        if ev.get("which") != arm[2:] or ev.get("check") is not True:
            return f"{arm} {first}{second}: reset not recorded"
    return d


def function(d: Path, old: list[int], new: list[int], test: np.ndarray) -> dict | None:
    if not (d / "model_final.pt").exists():
        return None
    m = E51.load_model(d)
    W = m.W_E.detach().numpy().astype(np.float64)[:P]
    acc = lambda Wr: E55.evaluate(m, Wr, test)["acc"]   # noqa: E731
    return {"base": acc(None), "acc_old": acc(W - G61.project(W, old)), "acc_new": acc(W - G61.project(W, new))}


def classify(db: np.ndarray) -> str:
    if len(db) < 8:
        return "nicht auswertbar"
    if (db > 1).sum() >= 8:
        return "trägt den Ausschluss mit"
    if (db < 0.5).sum() >= 8:
        return "allein nicht nötig"
    return "unklar"


def seed_row(s: int) -> dict:
    meta = json.loads((A.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
    F, G = meta["targets"]["A"], meta["targets"]["B"]
    test = np.load(A.SPL / f"seed{s}_test.npy")
    pure = {x: R.spectra(R.run_dir(s, x, None, None)) for x in "AB"}
    r, bad = {"seed": s}, []
    for arm in ARMS:
        aa, bb, fo, fn = [], [], [], []
        for first, second, own, new in (("A", "B", F, G), ("B", "A", G, F)):
            d = run_dir(s, first, second, arm)
            if isinstance(d, str):
                bad.append(d)
                continue
            a, b = R.split(R.spectra(d), pure[second], own, new, T + 2000, 2000)
            aa.append(a)
            bb.append(b)
            if arm.startswith("rs") and arm[2:] in PARTS and (f := function(d, own, new, test)):
                fo.append(f["acc_old"])
                fn.append(f["acc_new"])
        if len(aa) == 2:
            r[f"a_{arm}"], r[f"b_{arm}"] = float(np.mean(aa)), float(np.mean(bb))
        if len(fo) == 2:
            r[f"accold_{arm}"], r[f"accnew_{arm}"] = float(np.mean(fo)), float(np.mean(fn))
    r["valid"] = not bad
    if bad:
        r["reason"] = "; ".join(bad[:3])
    return r


def main() -> None:
    rows = [seed_row(s) for s in B.SEEDS]
    ok = [r for r in rows if r["valid"]]
    out = {"n_valid": len(ok), "verdict": {}, "db": {}}
    for x in PARTS:
        db = np.array([r["b_normal"] - r[f"b_rs{x}"] for r in ok])
        out["verdict"][x] = classify(db)
        out["db"][x] = db.tolist()
    keys = [k for k in (ok[0] if ok else {}) if k.startswith(("a_", "b_", "accold_", "accnew_"))]
    out["mean"] = {k: float(np.mean([r[k] for r in ok if k in r])) for k in keys}
    out["rows"] = rows
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    assert classify(np.ones(7) * 3) == "nicht auswertbar"
    assert classify(np.r_[np.ones(8) * 2, 0, 0]) == "trägt den Ausschluss mit"
    assert classify(np.r_[np.zeros(8), 2, 2]) == "allein nicht nötig"
    assert classify(np.r_[np.ones(5) * 2, np.zeros(5)]) == "unklar"
    assert set(ARMS) == {"normal", "rsrest", "rsattn", "rsmlp", "rsunembed"}
    print("[exp067] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
