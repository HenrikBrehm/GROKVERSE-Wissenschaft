"""EXP-049: does data-split steering (K2) hold in a 4x wider transformer (d_model 512 vs 128)? UNTESTED.

Per init seed i (170-179): arms F and G at d = 128 and d = 512, 2000 steps, GPU.
Primary (preregistered, README): Delta_pow at d = 512, Delta_pow_i = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)],
one-sided sign-flip test over the valid seeds. Secondary (reported): Delta_pow at d = 128, paired difference 512 - 128,
top-5 Delta, effective number of frequencies, accuracies. Validity: all four runs of a seed completed, 2000 steps, cuda,
d_model as requested, split hash = content of the .npy; < 8 valid seeds -> 'nicht auswertbar'.
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

SEEDS = range(170, 180)
WIDTHS = (128, 512)
M, STEP, ALPHA, MIN_VALID = 5, 2000, 0.05, 8


def top(pw: np.ndarray) -> set[int]:
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:M]}


def spow(pw: np.ndarray, S) -> float:
    return float(pw[[k - 1 for k in S]].sum())


def delta_pow(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float:
    return float(np.log(spow(pF, F) / spow(pF, G)) + np.log(spow(pG, G) / spow(pG, F)))


def n_eff(pw: np.ndarray) -> float:
    q = pw / pw.sum()
    return float(np.exp(-(q * np.log(q + 1e-300)).sum()))


def load(s: int, d: int, arm: str) -> tuple[dict, np.ndarray] | str:
    stem = f"split_add113_seed{s}_eps2.0_{arm}"
    hits = sorted((HERE / "raw").glob(f"EXP-049_d{d}_seed{s}_{stem}_devcuda"))
    if len(hits) != 1 or not (hits[0] / "result.json").exists():
        return "missing run dir / result.json"
    res = json.loads((hits[0] / "result.json").read_text(encoding="utf-8"))
    if (res["status"] != "completed" or res["steps_completed"] < STEP or res["seed"] != s or res.get("device") != "cuda"
            or res["d_model"] != d or res["config"]["d_model"] != d):
        return "status/steps/seed/device/width"
    if res["split_hash"] != split_hash(np.load(HERE / f"splits/{stem}.npy")):
        return "split content hash mismatch"
    steps = np.load(hits[0] / "spectra_steps.npy").tolist()
    if STEP not in steps:
        return f"no spectrum at {STEP}"
    return res, np.load(hits[0] / "spectra.npy")[steps.index(STEP)]


def row(s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    meta = json.loads((HERE / f"splits/split_add113_seed{s}_eps2.0_F.json").read_text(encoding="utf-8"))
    T = {"F": meta["targets_F"], "G": meta["targets_G"]}
    r.update(T)
    for d in WIDTHS:
        pw, info = {}, {}
        for arm in "FG":
            got = load(s, d, arm)
            if isinstance(got, str):
                r["reason"] = f"d{d} {arm}: {got}"
                return r
            res, pw[arm] = got
            info[arm] = {"gen": res.get("generalization_step"), "test_acc": res["final_acc"]["test"],
                         "train_acc": res["final_acc"]["train"], "top5": sorted(top(pw[arm])), "n_eff": n_eff(pw[arm])}
        K = {a: top(pw[a]) for a in "FG"}
        r[f"d{d}"] = {"arms": info, "Delta_pow": delta_pow(pw["F"], pw["G"], T["F"], T["G"]),
                      "Delta_top5": (len(K["F"] & set(T["F"])) + len(K["G"] & set(T["G"]))
                                     - len(K["F"] & set(T["G"])) - len(K["G"] & set(T["F"])))}
    r["valid"] = True
    return r


def one_sided_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def selftest() -> None:
    pF, pG = np.ones(56), np.ones(56)
    pF[[0, 1]] = 10.0
    pG[[20, 21]] = 10.0
    assert delta_pow(pF, pG, [1, 2], [21, 22]) > 0 and delta_pow(pG, pF, [1, 2], [21, 22]) < 0
    assert abs(n_eff(np.ones(56)) - 56) < 1e-9
    assert one_sided_p(np.ones(10)) == 1 / 1024 and one_sided_p(np.array([1.0, -1.0])) == 0.75
    print("[exp049] selftest ok", flush=True)


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
        D = np.array([r["d512"]["Delta_pow"] for r in valid])
        p = one_sided_p(D)
        D128 = np.array([r["d128"]["Delta_pow"] for r in valid])
        diff = D - D128
        out.update({"Delta_pow_512_mean": float(D.mean()), "p": p, "n_positive": int((D > 0).sum()),
                    "Delta_pow_128_mean": float(D128.mean()), "p_128_secondary": one_sided_p(D128),
                    "diff_512_minus_128_mean": float(diff.mean()),
                    "p_diff_less_secondary": one_sided_p(-diff),
                    **{f"Delta_top5_{d}_mean": float(np.mean([r[f"d{d}"]["Delta_top5"] for r in valid])) for d in WIDTHS},
                    **{f"n_eff_{d}_mean": float(np.mean([r[f"d{d}"]["arms"][a]["n_eff"] for r in valid for a in "FG"]))
                       for d in WIDTHS},
                    **{f"test_acc_{d}_mean": float(np.mean([r[f"d{d}"]["arms"][a]["test_acc"] for r in valid for a in "FG"]))
                       for d in WIDTHS}})
        out["verdict"] = ("steuerbar" if D.mean() > 0 and p < ALPHA else
                          "richtungsgleich, n. s." if D.mean() > 0 else "widerspricht")
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
