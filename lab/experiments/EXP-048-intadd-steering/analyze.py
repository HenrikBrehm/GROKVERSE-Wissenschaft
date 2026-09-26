"""EXP-048: does data-split steering (EXP-016, K2) carry over to NON-modular integer addition? UNTESTED.

Per init seed i (160-169): arms F and G (disjoint sets of 5 target frequencies from k = 6..56), 2000 steps, GPU.
Primary (preregistered, README Nachtrag a, before any run): Delta_pow_i = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)],
P_arm(S) = DFT power of the DETRENDED final W_E (step 2000, we_final.npy; per column the least-squares line in a removed)
summed over the frequencies S. One-sided sign-flip test over the valid seeds (exact).
Secondary (reported): the same Delta on the raw spectrum at 2000 (original primary), top-5 overlap Delta as in EXP-016,
linear R^2 (number line), random arm R, accuracies.
Validity: both runs completed, 2000 steps, cuda, split hash = content of the .npy; < 8 valid seeds -> 'nicht auswertbar'.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "training"))
sys.path.insert(0, str(HERE))
from grokverse.data import split_hash  # noqa: E402
sys.path.insert(0, str(HERE.parents[1] / "tools"))
from result_loader import Expect, find_run, load_run  # noqa: E402  (Astra 16: shared loader)

SEEDS = range(160, 170)
M, STEP, ALPHA, MIN_VALID, P = 5, 2000, 0.05, 8, 113


def run_dir(s: int, arm: str) -> Path | None:
    eps = "0.0" if arm == "R" else "2.0"
    hits = sorted((HERE / "raw").glob(f"EXP-048_seed{s}_split_intadd113_seed{s}_eps{eps}_{arm}_devcuda"))
    return hits[0] if len(hits) == 1 and (hits[0] / "result.json").exists() else None


def top(pw: np.ndarray) -> set[int]:
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:M]}


def spow(pw: np.ndarray, S) -> float:
    return float(pw[[k - 1 for k in S]].sum())


def load(s: int, arm: str) -> tuple[dict, np.ndarray, np.ndarray] | str:
    eps = "0.0" if arm == "R" else "2.0"
    stem = f"split_intadd113_seed{s}_eps{eps}_{arm}"
    r = load_run(find_run(HERE / "raw", f"EXP-048_seed{s}_{stem}_devcuda"),
                 Expect(seed=s, device="cuda", max_steps=STEP, split_file=HERE / f"splits/{stem}.npy",
                        config={"p": 225}, at=(STEP,), files=("we_final.npy",)))
    if r.status != "ok":
        return f"{r.status}: {r.reason}"
    from intadd_train import dft_power
    W = np.load(r.path / "we_final.npy").astype(float)
    return r.res, r.spectrum(STEP), dft_power(detrend(W))


def detrend(W: np.ndarray) -> np.ndarray:
    """Remove, per column, the least-squares line alpha + beta * a (a = 0..112): a number line leaks power into k >= 6."""
    X = np.stack([np.ones(P), np.arange(P, dtype=float)], 1)
    return W - X @ np.linalg.lstsq(X, W, rcond=None)[0]


def delta_pow(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float:
    return float(np.log(spow(pF, F) / spow(pF, G)) + np.log(spow(pG, G) / spow(pG, F)))


def row(s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    meta = json.loads((HERE / f"splits/split_intadd113_seed{s}_eps2.0_F.json").read_text(encoding="utf-8"))
    T = {"F": meta["targets_F"], "G": meta["targets_G"]}
    pw, pd, info = {}, {}, {}
    for arm in "FG":
        got = load(s, arm)
        if isinstance(got, str):
            r["reason"] = f"arm {arm}: {got}"
            return r
        res, pw[arm], pd[arm] = got
        info[arm] = {"gen": res.get("generalization_step"), "test_acc": res["final_acc"]["test"],
                     "train_acc": res["final_acc"]["train"], "top5": sorted(top(pw[arm])),
                     "top5_share": res["final_top_m_share"], "linear_r2_2000": res["linear_r2"][-1]}
    K = {a: top(pw[a]) for a in "FG"}
    ov = {f"{x}{y}": len(K[x] & set(T[y])) for x in "FG" for y in "FG"}
    r.update({"valid": True, "F": T["F"], "G": T["G"], "arms": info, **{f"ov_{k}": v for k, v in ov.items()},
              "Delta_top5": ov["FF"] + ov["GG"] - ov["FG"] - ov["GF"],
              "Delta_pow": delta_pow(pd["F"], pd["G"], T["F"], T["G"]),
              "Delta_pow_raw": delta_pow(pw["F"], pw["G"], T["F"], T["G"])})
    got = load(s, "R")                                   # secondary: unsteered split, both target sets
    if not isinstance(got, str):
        res, pr, prd = got
        r["R"] = {"logratio_F_over_G": float(np.log(spow(prd, T["F"]) / spow(prd, T["G"]))), "top5": sorted(top(pr)),
                  "test_acc": res["final_acc"]["test"], "gen": res.get("generalization_step"),
                  "linear_r2_2000": res["linear_r2"][-1]}
    return r


def one_sided_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def selftest() -> None:
    from intadd_train import dft_power, linear_r2
    a = np.arange(P)
    rng = np.random.default_rng(0)
    for k0 in (6, 23, 56):
        W = 0.05 * rng.normal(size=(P, 8))
        W[:, 3] += np.cos(2 * np.pi * k0 * a / P + 0.4)
        assert int(np.argmax(dft_power(W))) + 1 == k0, k0
    ramp = np.outer(a, rng.normal(size=4))
    assert abs(linear_r2(ramp) - 1) < 1e-9 and linear_r2(np.cos(2 * np.pi * 7 * a / P)[:, None]) < 0.01
    pF, pG = np.ones(56), np.ones(56)
    pF[[5, 6]] = 10.0
    pG[[20, 21]] = 10.0
    assert delta_pow(pF, pG, [6, 7], [21, 22]) > 0 and delta_pow(pG, pF, [6, 7], [21, 22]) < 0
    assert abs(delta_pow(np.ones(56), np.ones(56), [6, 7], [21, 22])) < 1e-12
    ramp = np.outer(a, rng.normal(size=8))           # detrending: a ramp vanishes, a target wave survives
    w9 = np.outer(np.cos(2 * np.pi * 9 * a / P), rng.normal(size=8))
    w40 = np.outer(np.cos(2 * np.pi * 40 * a / P + 1.0), rng.normal(size=8))
    base = 0.05 * rng.normal(size=(P, 8))
    assert np.abs(detrend(3 * ramp)).max() < 1e-9
    d1 = delta_pow(dft_power(detrend(3 * ramp + w9 + base)), dft_power(detrend(ramp + w40 + base)), [9], [40])
    d0 = delta_pow(dft_power(detrend(ramp + w9 + base)), dft_power(detrend(ramp + w40 + base)), [9], [40])
    assert d1 > 1 and abs(d1 - d0) < 1e-6, (d1, d0)
    assert one_sided_p(np.ones(10)) == 1 / 1024
    print("[exp048] selftest ok", flush=True)


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
        D = np.array([r["Delta_pow"] for r in valid])
        p = one_sided_p(D)
        Dt = np.array([r["Delta_top5"] for r in valid], dtype=float)
        Dr = np.array([r["Delta_pow_raw"] for r in valid])
        out.update({"Delta_pow_raw_mean": float(Dr.mean()), "p_raw_secondary": one_sided_p(Dr)})
        out.update({"Delta_pow_mean": float(D.mean()), "p": p, "n_positive": int((D > 0).sum()),
                    "Delta_top5_mean": float(Dt.mean()), "p_top5_secondary": one_sided_p(Dt),
                    "linear_r2_mean": float(np.mean([r["arms"][a]["linear_r2_2000"] for r in valid for a in "FG"])),
                    "test_acc_mean": float(np.mean([r["arms"][a]["test_acc"] for r in valid for a in "FG"]))})
        out["verdict"] = ("steuerbar" if D.mean() > 0 and p < ALPHA else
                          "richtungsgleich, n. s." if D.mean() > 0 else "widerspricht")
    rr = [r["R"] for r in valid if "R" in r]
    if rr:
        out["R_n"] = len(rr)
        out["R_logratio_mean"] = float(np.mean([x["logratio_F_over_G"] for x in rr]))
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
