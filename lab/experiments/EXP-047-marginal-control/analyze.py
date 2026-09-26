"""EXP-047: does split steering (K2) work through the token counts or through the pair structure? UNTESTED.

Per init seed i (150-159), four GPU runs of 2000 steps (add mod 113, transformer): eng_F, eng_G, shuf_F, shuf_G.
K = top-5 W_E frequencies at step 2000 (spectra.npy of freq_ban.py). Delta_kind = ov(K_F, F) + ov(K_G, G) - ov(K_F, G) - ov(K_G, F).
H47a (counts steer):          Delta_shuf > 0, one-sided sign-flip test.
H47b (pairs add beyond counts): D = Delta_eng - Delta_shuf > 0, one-sided sign-flip test.   Holm over {a, b}.
Definition: README.md.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "training"))
from grokverse.data import split_hash  # noqa: E402
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from result_loader import Expect, find_run, load_run  # noqa: E402  (Astra 16: shared loader)
from paket_a_device import DEV, FB_SUFFIX, TR_SUFFIX  # noqa: E402  (session 15: CPU fallback for programme A)

SEEDS = range(150, 160)
M, STEP, ALPHA, MIN_VALID = 5, 2000, 0.05, 8


def top(pw: np.ndarray) -> set[int]:
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:M]}


def one_sided_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def K_of(s: int, kind: str, arm: str) -> tuple[set[int] | None, str, dict]:
    stem = f"split_add113_seed{s}_{kind}_{arm}"
    r = load_run(find_run(HERE / "raw", f"*_seed{s}_thr*_{stem}{FB_SUFFIX}"),
                 Expect(seed=s, device=DEV, max_steps=STEP, split_file=HERE / f"splits/{stem}.npy",
                        config={"p": 113, "task": "add"}, at=(STEP,)))
    if r.status != "ok":
        return None, f"{r.status}: {r.reason}", {}
    info = {"gen": r.res["events"].get("generalization_step"), "test_acc": r.res["final_acc"]["test"],
            "train_acc": r.res["final_acc"]["train"]}
    return top(r.spectrum(STEP)), "", info


def row(s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    for kind in ("eng", "shuf"):
        T, K = {}, {}
        for arm in "FG":
            T[arm] = set(json.loads((HERE / f"splits/split_add113_seed{s}_{kind}_{arm}.json").read_text(encoding="utf-8"))
                         ["targets"])
            K[arm], why, info = K_of(s, kind, arm)
            if K[arm] is None:
                r["reason"] = f"{kind}_{arm}: {why}"
                return r
            r[f"{kind}_{arm}"] = {"K": sorted(K[arm]), **info}
        r[f"Delta_{kind}"] = (len(K["F"] & T["F"]) + len(K["G"] & T["G"]) - len(K["F"] & T["G"]) - len(K["G"] & T["F"]))
    r["valid"] = True
    r["D"] = r["Delta_eng"] - r["Delta_shuf"]
    return r


def selftest() -> None:
    assert one_sided_p(np.ones(10)) == 1 / 1024
    assert one_sided_p(np.array([1.0, -1.0])) == 0.75
    assert top(np.array([0, 5, 1, 4, 3, 2, 9.0])) == {2, 4, 5, 6, 7}
    print("[exp047] selftest ok", flush=True)


def main() -> None:
    if sys.argv[1:] == ["--selftest"]:
        selftest()
        return
    rows = [row(s) for s in SEEDS]
    valid = [r for r in rows if r["valid"]]
    out: dict = {"rows": rows, "n_valid": len(valid)}
    if len(valid) < MIN_VALID:
        out["verdict"] = "nicht auswertbar"
    else:
        De = np.array([r["Delta_eng"] for r in valid], float)
        Ds = np.array([r["Delta_shuf"] for r in valid], float)
        D = De - Ds
        pa, pb = one_sided_p(Ds), one_sided_p(D)
        order = sorted((("a", pa), ("b", pb)), key=lambda x: x[1])
        sig, still = {}, True
        for i, (h, pv) in enumerate(order):
            sig[h] = still and pv < ALPHA / (2 - i)
            still = sig[h]
        out.update({"Delta_eng_mean": float(De.mean()), "p_eng_manipulation": one_sided_p(De),
                    "Delta_shuf_mean": float(Ds.mean()), "p_a": pa, "D_mean": float(D.mean()), "p_b": pb,
                    "holm_a": sig["a"], "holm_b": sig["b"]})
        out["verdict_a"] = ("Häufigkeiten steuern mit" if Ds.mean() > 0 and sig["a"] else
                            "richtungsgleich, n. s." if Ds.mean() > 0 else "keine Steuerung über Häufigkeiten")
        out["verdict_b"] = ("Paarstruktur trägt über die Häufigkeiten hinaus" if D.mean() > 0 and sig["b"] else
                            "richtungsgleich, n. s." if D.mean() > 0 else "widerspricht")
    (HERE / "summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
