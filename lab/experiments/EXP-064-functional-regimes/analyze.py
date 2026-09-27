"""EXP-064 (pilot): are the two spectral signatures (EXP-062) functional? Definition: README.md (registered before any EXP-064 run).
Run under guarded_run.py. Final model of each switch run; W_E[:113] projected onto the complement of the old (resp. new) target frequencies;
accuracy on the common test set of the seed.
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


G61 = _load("exp061", "experiments/EXP-061-grad-alignment/analyze.py")
E55 = _load("exp055", "experiments/EXP-055-ablation-dose/analyze.py")
A, B, E51 = G61.A, G61.B, G61.E51
TS, P, ACC_MIN, NEED = (25, 50), 113, 0.9, 8


def one(s: int, t: int, first: str, second: str, old: list[int], new: list[int], test: np.ndarray) -> dict | str:
    st1, st2 = A.stem(s, B.OM, first), A.stem(s, B.OM, second)
    d = A.find_run(HERE / "raw", f"EXP-0*_baseline_seed{s}_thr*_{st1}_to_{st2}_at{t}{A.SUF}")
    L = A.load_run(d, A.Expect(seed=s, device=A.DEV, max_steps=t + 2000, split_file=A.SPL / f"{st1}.npy", test_file=A.SPL / f"seed{s}_test.npy",
                               switch_file=A.SPL / f"{st2}.npy", config={"p": 113, "task": "add"}, snapshots_at=(t + 2000,), files=("model_final.pt",)))
    if L.status != "ok":
        return f"{first}{second}@{t}: {L.status}: {L.reason}"
    m = E51.load_model(L.path)
    W = m.W_E.detach().numpy().astype(np.float64)[:P]
    acc = lambda Wr: E55.evaluate(m, Wr, test)["acc"]   # noqa: E731
    return {"base": acc(None), "acc_old": acc(W - G61.project(W, old)), "acc_new": acc(W - G61.project(W, new))}


def verdict(rows: list[dict]) -> str:
    ok = [r for r in rows if r["valid"]]
    if len(ok) < NEED:
        return "nicht auswertbar"
    v1 = sum((r["new50"] - r["old50"]) > (r["new25"] - r["old25"]) for r in ok) >= NEED
    v2 = sum(r["old25"] < ACC_MIN and r["new25"] < ACC_MIN for r in ok) >= NEED
    v3 = sum(r["new50"] >= ACC_MIN for r in ok) >= NEED
    if v1 and v2 and v3:
        return "funktionale Zwei Regime (Pilot)"
    if v1:
        return "Funktion folgt dem Spektrum, Regime nicht scharf"
    return "Spektralsignaturen nicht funktional"


def main() -> None:
    rows = []
    for s in B.SEEDS:
        meta = json.loads((A.SPL / f"seed{s}_w0.json").read_text(encoding="utf-8"))
        F, G = meta["targets"]["A"], meta["targets"]["B"]
        test = np.load(A.SPL / f"seed{s}_test.npy")
        r, bad, base = {"seed": s}, [], []
        for t in TS:
            res = [one(s, t, "A", "B", F, G, test), one(s, t, "B", "A", G, F, test)]
            if any(isinstance(x, str) for x in res):
                bad += [x for x in res if isinstance(x, str)]
                continue
            base += [x["base"] for x in res]
            r[f"old{t}"] = float(np.mean([x["acc_old"] for x in res]))
            r[f"new{t}"] = float(np.mean([x["acc_new"] for x in res]))
        r["base_min"] = float(min(base)) if base else None
        r["valid"] = not bad and min(base) >= ACC_MIN
        if not r["valid"]:
            r["reason"] = "; ".join(bad[:2]) or f"base accuracy < {ACC_MIN}"
        rows.append(r)
    ok = [r for r in rows if r["valid"]]
    out = {"n_valid": len(ok), "verdict": verdict(rows),
           "mean": {k: float(np.mean([r[k] for r in ok])) for k in ("old25", "new25", "old50", "new50")} if ok else {}, "rows": rows}
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


def selftest() -> None:
    mk = lambda o25, n25, o50, n50: {"valid": True, "old25": o25, "new25": n25, "old50": o50, "new50": n50}   # noqa: E731
    assert verdict([mk(0.5, 0.5, 0.3, 0.95)] * 10) == "funktionale Zwei Regime (Pilot)"
    assert verdict([mk(0.95, 0.5, 0.3, 0.8)] * 10) == "Funktion folgt dem Spektrum, Regime nicht scharf"
    assert verdict([mk(0.5, 0.9, 0.9, 0.5)] * 10) == "Spektralsignaturen nicht funktional"
    assert verdict([mk(0.5, 0.5, 0.3, 0.95)] * 7) == "nicht auswertbar"
    print("[exp064] selftest ok", flush=True)


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
