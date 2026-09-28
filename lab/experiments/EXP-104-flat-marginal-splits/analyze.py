"""EXP-104 analysis (exploration, N53; 2 seeds, no test statistics). Read-only; run through the guard like every analysis.

Per seed and move count m: Delta_pow at step 2000 (P1 definition, natural log, spectra.npy = additive DFT for add 113),
generalization step (trainer event: first test accuracy >= 0.95 ... as logged by freq_ban), final test accuracy.
Readings fixed before any run (session 45; revised after the pre-run review, still before any run):
  generalization per arm: trainer event "generalization_step" (None = no event by 8000). A cell (seed, m) "generalizes" if both
    arms do, "fails" if neither does, "mixed" otherwise; per-arm steps are always reported. Test set = one common held-out set
    per seed (pairs outside all six train splits). A pattern is read only if both seeds show it at every m; any mixed cell or
    seed disagreement -> "no reading", and m = 0 generalizing while m = 10 fails -> "no reading" (not anticipated).
    m = 0 fails and m = 10 generalizes in both seeds -> "exact translation invariance blocks generalization" (candidate finding,
      compare Tomas Bernal et al. 2026, RFM); m = 10 fails and m = 500 generalizes -> "near-invariance blocks";
      all generalize -> "the symmetry does not block a transformer"; m = 500 fails too -> "flat splits do not generalize here"
      (then not usable as an LM control without further work).
  steering: Delta_pow > 1 (P1 minimum effect) in both seeds at a given m -> "steers with flat marginals" at that m. The mask
    concentration (0.65-0.74 at m <= 10) is far above P1 (0.17-0.19): Delta_pow is reported per m and never compared with P1,
    and Delta_pow <= 1 is NOT read as evidence about the count signal (no matched non-flat arm; symmetry and generalization
    would confound it). Per-target mask shares are reported (uneven targets, e.g. s3850 G). 2 seeds: pilot, no confirmation.
  python lab/experiments/EXP-104-flat-marginal-splits/analyze.py            # also: --selftest
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(HERE))
from design import ARMS, MOVES, SEEDS, SPL, STEPS, RAW, TF, mask_power  # noqa: E402
from result_loader import Expect, find_run, load_run  # noqa: E402

STEP = 2000


def delta_pow(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float:
    s = lambda pw, S: float(pw[[k - 1 for k in S]].sum())   # noqa: E731
    return float(np.log(s(pF, F) / s(pF, G)) + np.log(s(pG, G) / s(pG, F)))


def one(seed: int, m: int) -> dict:
    row: dict = {"seed": seed, "moves": m}
    pw, T = {}, {}
    for arm in ARMS:
        f = SPL / f"s{seed}_{arm}_m{m}.npy"
        T[arm] = json.loads(f.with_suffix(".json").read_text(encoding="utf-8"))["targets"]
        m0 = mask_power(np.load(f), "add", 113)
        row.setdefault("mask_share_per_target", {})[arm] = {t: round(float(m0[t - 1] / m0.sum()), 4) for t in T[arm]}
        r = load_run(find_run(RAW, f"EXP-018_baseline_seed{seed}_thr1_{f.stem}_tf{TF!r}_devcuda"),
                     Expect(seed=seed, device="cuda", max_steps=STEPS, min_steps_completed=STEP, split_file=f,
                            test_file=SPL / f"s{seed}_test.npy", at=(STEP,)))
        if r.status != "ok":
            row[arm] = {"status": r.status, "reason": r.reason}
            continue
        pw[arm] = r.spectrum(STEP)
        row[arm] = {"status": "ok", "gen_step": (r.res.get("events") or {}).get("generalization_step"),
                    "final_test": (r.res.get("final_acc") or {}).get("test")}
    if len(pw) == 2:
        row["delta_pow"] = delta_pow(pw["F"], pw["G"], T["F"], T["G"])
    if len(pw) == 2:
        g = [row[a]["gen_step"] is not None for a in ARMS]
        row["cell"] = "generalizes" if all(g) else "fails" if not any(g) else "mixed"
    return row


def selftest() -> None:
    assert abs(delta_pow(np.array([4.0, 1.0]), np.array([1.0, 4.0]), [1], [2]) - 2 * np.log(4)) < 1e-12
    assert delta_pow(np.ones(56), np.ones(56), [1, 2], [3, 4]) == 0.0
    for seed in SEEDS:
        for arm in ARMS:
            for m in MOVES:
                idx = np.load(SPL / f"s{seed}_{arm}_m{m}.npy")
                a, b = idx // 113, idx % 113
                assert all(np.ptp(np.bincount(v, minlength=113)) == 0 for v in (a, b, (a + b) % 113)), (seed, arm, m)
                assert len(idx) == round(TF * 113 * 113), (seed, arm, m, len(idx))     # freq_ban split-size check
                assert not np.intersect1d(idx, np.load(SPL / f"s{seed}_test.npy")).size
    print("selftest ok")


def main() -> None:
    if "--selftest" in sys.argv:
        selftest()
        return
    rows = [one(s, m) for s in SEEDS for m in MOVES]
    for r in rows:
        print(json.dumps(r))
    (HERE / "summary.json").write_text(json.dumps({"note": "exploration, 2 seeds", "rows": rows}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
