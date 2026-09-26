"""EXP-050: does the transformer select frequencies by the coherent mask spectrum M0c or by M0? UNTESTED.

Per init seed i (180-189), six GPU runs of 2000 steps (add mod 113, transformer, freq_ban.py --split-file): modes
quadlm, anti, sym x arms F, G. Delta_pow_mode = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)] from the W_E spectrum at step 2000.
H50a (M0c selects):      D = Delta_pow_quadlm - Delta_pow_anti > 0 (same M0, counts, mirror pairs; M0c top vs chance).
H50b (M0 still steers):  Delta_pow_anti > 0.     One-sided sign-flip tests, Holm over {a, b}.
Secondary (reported): D_sym = Delta_pow_sym - Delta_pow_anti (confounded by the mirror-pair count), manipulation check
Delta_pow_quadlm > 0, accuracies/gen per mode (mirror pairs may change memorization speed, He et al. 2026).
Validity: all six runs of a seed completed, 2000 steps, cuda, p 113 / add, split hash = content of the .npy, finite spectra;
< 8 valid seeds -> 'nicht auswertbar'. Definition: README.md.
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

SEEDS = range(180, 190)
STEP, ALPHA, MIN_VALID = 2000, 0.05, 8


def spow(pw: np.ndarray, S) -> float:
    return float(pw[[k - 1 for k in S]].sum())


def delta_pow(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float:
    return float(np.log(spow(pF, F) / spow(pF, G)) + np.log(spow(pG, G) / spow(pG, F)))


def one_sided_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def holm(ps: dict[str, float]) -> dict[str, bool]:
    out, m = {}, len(ps)
    for i, (k, p) in enumerate(sorted(ps.items(), key=lambda kv: kv[1])):
        if p >= ALPHA / (m - i):
            for k2, _ in sorted(ps.items(), key=lambda kv: kv[1])[i:]:
                out[k2] = False
            break
        out[k] = True
    return out


def spectrum(s: int, mode: str, arm: str) -> tuple[np.ndarray | None, str, dict]:
    stem = f"split_add113_seed{s}_{mode}_{arm}"
    r = load_run(find_run(HERE / "raw", f"*_seed{s}_thr*_{stem}{FB_SUFFIX}"),
                 Expect(seed=s, device=DEV, max_steps=STEP, split_file=HERE / f"splits/{stem}.npy",
                        config={"p": 113, "task": "add", "arch": "transformer"}, at=(STEP,)))
    if r.status != "ok":
        return None, f"{r.status}: {r.reason}", {}
    info = {"gen": r.res["events"].get("generalization_step"), "test_acc": r.res["final_acc"]["test"],
            "train_acc": r.res["final_acc"]["train"]}
    return r.spectrum(STEP), "", info


def row(s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    meta = json.loads((HERE / f"splits/split_add113_seed{s}_sym_F.json").read_text(encoding="utf-8"))
    F, G = meta["targets_F"], meta["targets_G"]
    r.update({"F": F, "G": G})
    for mode in ("quadlm", "anti", "sym"):
        pw = {}
        for arm in "FG":
            pw[arm], why, info = spectrum(s, mode, arm)
            if pw[arm] is None:
                r["reason"] = f"{mode}_{arm}: {why}"
                return r
            r[f"{mode}_{arm}"] = info
        r[f"Delta_pow_{mode}"] = delta_pow(pw["F"], pw["G"], F, G)
    r["valid"] = True
    r["D"] = r["Delta_pow_quadlm"] - r["Delta_pow_anti"]
    r["D_sym"] = r["Delta_pow_sym"] - r["Delta_pow_anti"]
    return r


def selftest() -> None:
    assert one_sided_p(np.ones(10)) == 1 / 1024 and one_sided_p(np.array([1.0, -1.0])) == 0.75
    pF, pG = np.ones(56), np.ones(56)
    pF[[0, 1]] = 10.0
    pG[[20, 21]] = 10.0
    assert delta_pow(pF, pG, [1, 2], [21, 22]) > 0 and abs(delta_pow(np.ones(56), np.ones(56), [1], [2])) < 1e-12
    assert holm({"a": 0.01, "b": 0.03}) == {"a": True, "b": True}
    assert holm({"a": 0.03, "b": 0.04}) == {"a": False, "b": False}
    assert holm({"a": 0.001, "b": 0.2}) == {"a": True, "b": False}
    print("[exp050] selftest ok", flush=True)


def main() -> None:
    if sys.argv[1:] == ["--selftest"]:
        selftest()
        return
    rows = [row(s) for s in SEEDS]
    valid = [r for r in rows if r["valid"]]
    out: dict = {"rows": rows, "n_valid": len(valid)}
    if len(valid) < MIN_VALID:
        out["verdict_a"] = out["verdict_b"] = "nicht auswertbar"
    else:
        D = np.array([r["D"] for r in valid])
        A = np.array([r["Delta_pow_anti"] for r in valid])
        S = np.array([r["Delta_pow_sym"] for r in valid])
        Q = np.array([r["Delta_pow_quadlm"] for r in valid])
        DS = np.array([r["D_sym"] for r in valid])
        ps = {"a": one_sided_p(D), "b": one_sided_p(A)}
        sig = holm(ps)
        out.update({"D_mean": float(D.mean()), "Delta_pow_anti_mean": float(A.mean()), "Delta_pow_sym_mean": float(S.mean()),
                    "Delta_pow_quadlm_mean": float(Q.mean()), "D_sym_mean_secondary": float(DS.mean()),
                    "p_D_sym_secondary": one_sided_p(DS),
                    "p_a": ps["a"], "p_b": ps["b"], "holm": sig, "p_quadlm_manipulation": one_sided_p(Q),
                    "n_D_positive": int((D > 0).sum()), "n_anti_positive": int((A > 0).sum())})
        out["verdict_a"] = ("M0c selektiert (quadlm > anti)" if D.mean() > 0 and sig["a"] else
                            "richtungsgleich, n. s." if D.mean() > 0 else "widerspricht (anti >= quadlm)")
        out["verdict_b"] = ("anti steuert trotzdem (M0-Anteil)" if A.mean() > 0 and sig["b"] else
                            "richtungsgleich, n. s." if A.mean() > 0 else "anti steuert nicht")
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
