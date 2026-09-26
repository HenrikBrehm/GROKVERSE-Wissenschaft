"""EXP-046: does data-split steering (EXP-016) carry over to composition in the non-abelian group D_59? UNTESTED.

Per init seed i (140-149): arms F and G (disjoint sets of 5 target irreps out of 29 two-dim irreps), 2000 steps, GPU.
K = top-5 two-dim irreps by W_E power at step 2000 (spectra.npy of the run).
Validity (preregistered, README): both runs completed on cuda, split hash matches. Structure check: the top-5 hold
>= 2x their uniform share of the non-trivial W_E power (0.342) in >= 8 of the 20 steered runs, else the whole
experiment is 'nicht auswertbar (keine Irrep-Struktur)'.
Primary: Delta_i = ov(K_F, F) + ov(K_G, G) - ov(K_F, G) - ov(K_G, F); one-sided sign-flip test over valid seeds.
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
from paket_a_device import DEV, FB_SUFFIX, TR_SUFFIX  # noqa: E402  (session 15: CPU fallback for programme A)

from dihedral import irrep_basis, irrep_power, n_irrep2, rho  # noqa: E402

N = 59
SEEDS = range(140, 150)
M, STEP, ALPHA, MIN_VALID = 5, 2000, 0.05, 8
SHARE_MIN, MIN_STRUCTURED = 2 * (M * 4) / (2 * N - 1), 8


def run_dir(s: int, arm: str, eps: str = "2.0") -> Path | None:
    hits = sorted((HERE / "raw").glob(f"EXP-046_seed{s}_split_D{N}_seed{s}_eps{eps}_{arm}{TR_SUFFIX}"))
    return hits[0] if len(hits) == 1 else None


def top(pw: np.ndarray) -> set[int]:
    return {int(k) + 1 for k in np.lexsort((np.arange(len(pw)), -pw))[:M]}


def load(d: Path | None, s: int, stem: str) -> tuple[dict, np.ndarray] | str:
    r = load_run(d, Expect(seed=s, device=DEV, max_steps=STEP, split_file=HERE / f"splits/{stem}.npy",
                           config={"p": 2 * N}, at=(STEP,)))
    return (r.res, r.spectrum(STEP)) if r.status == "ok" else f"{r.status}: {r.reason}"


def row(s: int) -> dict:
    r: dict = {"seed": s, "valid": False}
    T, K, extra = {}, {}, {}
    for arm in "FG":
        stem = f"split_D{N}_seed{s}_eps2.0_{arm}"
        T[arm] = set(json.loads((HERE / f"splits/{stem}.json").read_text(encoding="utf-8"))["targets"])
        d = run_dir(s, arm)
        if d is None:
            r["reason"] = f"arm {arm}: missing run dir"
            return r
        got = load(d, s, stem)
        if isinstance(got, str):
            r["reason"] = f"arm {arm}: {got}"
            return r
        res, pw = got
        K[arm] = top(pw)
        extra[arm] = {"gen": res.get("generalization_step"), "test_acc": res["final_acc"]["test"],
                      "train_acc": res["final_acc"]["train"], "top5_share": res["final_top_m_share"]}
    ov = {f"{x}{y}": len(K[x] & T[y]) for x in "FG" for y in "FG"}
    r.update({"valid": True, "F": sorted(T["F"]), "G": sorted(T["G"]), "K_F": sorted(K["F"]), "K_G": sorted(K["G"]),
              **{f"ov_{k}": v for k, v in ov.items()}, "Delta": ov["FF"] + ov["GG"] - ov["FG"] - ov["GF"], "arms": extra})
    d = run_dir(s, "R", eps="0.0")                        # secondary: random split against both target sets
    if d is not None:
        got = load(d, s, f"split_D{N}_seed{s}_eps0.0_R")
        if not isinstance(got, str):
            kr = top(got[1])
            r.update({"ov_random_F": len(kr & T["F"]), "ov_random_G": len(kr & T["G"]),
                      "random_top5_share": got[0]["final_top_m_share"], "random_test_acc": got[0]["final_acc"]["test"]})
    return r


def one_sided_p(d: np.ndarray) -> float:
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    return float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())


def selftest() -> None:
    """Fail closed: a W_E built from irrep k0 has k0 on top; Parseval over the full basis."""
    B, labels = irrep_basis(N)
    rng = np.random.default_rng(0)
    for k0 in (1, 7, n_irrep2(N)):
        W = 0.05 * rng.normal(size=(2 * N, 8))
        W[:, 0] += 3 * rho(N, k0)[:, 0, 1]
        pw = irrep_power(W, B, labels, N)
        assert int(np.argmax(pw)) + 1 == k0 and k0 in top(pw), k0
    W = rng.normal(size=(2 * N, 8))
    C = B.T @ W
    assert abs((C ** 2).sum() - (W ** 2).sum()) < 1e-8, "Parseval"
    assert abs(irrep_power(W, B, labels, N).sum() + (C[:2] ** 2).sum() - (W ** 2).sum()) < 1e-8, "irrep split"
    assert one_sided_p(np.ones(10)) == 1 / 1024
    print("[exp046] selftest ok", flush=True)


def main() -> None:
    if sys.argv[1:] == ["--selftest"]:
        selftest()
        return
    rows = [row(s) for s in SEEDS]
    valid = [r for r in rows if r["valid"]]
    out: dict = {"rows": rows, "n_valid": len(valid)}
    shares = [r["arms"][a]["top5_share"] for r in valid for a in "FG"]
    out["n_structured"] = int(sum(x >= SHARE_MIN for x in shares))
    out["share_min"] = SHARE_MIN
    if len(valid) < MIN_VALID:
        out["verdict"] = "nicht auswertbar"
    elif out["n_structured"] < MIN_STRUCTURED:
        out["verdict"] = "nicht auswertbar (keine Irrep-Struktur)"
    else:
        D = np.array([r["Delta"] for r in valid], dtype=float)
        p = one_sided_p(D)
        out.update({"Delta_mean": float(D.mean()), "p": p, "n_positive": int((D > 0).sum()),
                    "ov_matched_mean": float(np.mean([(r["ov_FF"] + r["ov_GG"]) / 2 for r in valid])),
                    "ov_crossed_mean": float(np.mean([(r["ov_FG"] + r["ov_GF"]) / 2 for r in valid]))})
        out["verdict"] = ("steuerbar" if D.mean() > 0 and p < ALPHA else
                          "richtungsgleich, n. s." if D.mean() > 0 else "widerspricht")
    rr = [r for r in valid if "ov_random_F" in r]
    if rr:
        out["ov_random_mean"] = float(np.mean([(r["ov_random_F"] + r["ov_random_G"]) / 2 for r in rr]))
        out["n_random"] = len(rr)
    (HERE / "summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
