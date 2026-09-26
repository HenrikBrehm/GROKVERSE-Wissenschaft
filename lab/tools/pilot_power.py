"""Pilot spread of Delta_pow and sample-size planning for P1 (FINDINGS "Programm"). Written session 14, UNTESTED. Read-only.

P1 is stated on the continuous Delta_pow = log[P_F(F)/P_F(G)] + log[P_G(G)/P_G(F)] (W_E power at step 2000), but the night
analyses of EXP-043/046/047 decide on the top-5 overlap Delta. This script computes Delta_pow for every valid F/G seed pair of
the pilot night from the stored runs (shared result loader, same validity rules), takes EXP-048/049 from their summary.json,
and plans n for the confirmation block (seeds 1000-1099):
  true mean = MIN_EFFECT (1.0, FINDINGS) with the pilot SD (conservative when the pilot mean is larger),
  one-sided sign-flip test at alpha / FAMILY (Holm worst case over P1-P3), power by simulation (normal and pilot bootstrap).
Exploration only: it does not change any preregistered verdict; writes tools/pilot_power_summary.json. Run under guarded_run.py (EXP-043 import pulls torch).

  python lab/tools/pilot_power.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
EXP = LAB / "experiments"
sys.path.insert(0, str(LAB / "tools"))
from result_loader import Expect, find_run, load_run  # noqa: E402

STEP, MIN_EFFECT, ALPHA, FAMILY, POWER_GOAL = 2000, 1.0, 0.05, 3, 0.8
N_SIM, N_FLIP, N_MAX, RNG_SEED = 1000, 2000, 60, 1


def delta_pow(pF: np.ndarray, pG: np.ndarray, F: list[int], G: list[int]) -> float:
    s = lambda pw, S: float(pw[[k - 1 for k in S]].sum())   # noqa: E731
    return float(np.log(s(pF, F) / s(pF, G)) + np.log(s(pG, G) / s(pG, F)))


def exp043(task: str, p: int) -> list[float]:
    d = EXP / "EXP-043-generalize-steering"
    sys.path.insert(0, str(d))
    from analyze import group_power                          # EXP-043's own K measurement
    out = []
    for s in range(70, 80):
        pw, T = {}, {}
        for arm in "FG":
            stem = f"split_{task}{p}_seed{s}_eps2.0_{arm}"
            T[arm] = json.loads((d / f"splits/{stem}.json").read_text(encoding="utf-8"))["targets"]
            L = load_run(find_run(d / "raw", f"EXP-043_baseline_seed{s}_thr*_{stem}_{task}{p}_devcuda"),
                         Expect(seed=s, device="cuda", max_steps=STEP, split_file=d / f"splits/{stem}.npy",
                                config={"p": p, "task": task}, snapshots_at=(STEP,)))
            if L.status != "ok":
                break
            pw[arm] = group_power(L.snapshot(STEP), task, p)[0]
        if len(pw) == 2:
            out.append(delta_pow(pw["F"], pw["G"], T["F"], T["G"]))
    return out


def spectra_pairs(d: Path, seeds: range, stem_of, pattern_of, config: dict) -> list[float]:
    out = []
    for s in seeds:
        pw, T = {}, {}
        for arm in "FG":
            stem = stem_of(s, arm)
            T[arm] = json.loads((d / f"splits/{stem}.json").read_text(encoding="utf-8"))["targets"]
            L = load_run(find_run(d / "raw", pattern_of(s, stem)),
                         Expect(seed=s, device="cuda", max_steps=STEP, split_file=d / f"splits/{stem}.npy", config=config,
                                at=(STEP,)))
            if L.status != "ok":
                break
            pw[arm] = L.spectrum(STEP)
        if len(pw) == 2:
            out.append(delta_pow(pw["F"], pw["G"], T["F"], T["G"]))
    return out


def from_summary(d: Path, get) -> list[float]:
    f = d / "summary.json"
    if not f.exists():
        return []
    return [float(get(r)) for r in json.loads(f.read_text(encoding="utf-8"))["rows"] if r.get("valid")]


def sign_flip_p(d: np.ndarray, rng: np.random.Generator) -> float:
    flips = rng.choice((1.0, -1.0), size=(N_FLIP, len(d)))
    return float((np.sum((flips * d).mean(axis=1) >= d.mean() - 1e-12) + 1) / (N_FLIP + 1))


def power(n: int, draw, rng: np.random.Generator) -> float:
    a = ALPHA / FAMILY
    return float(np.mean([sign_flip_p(draw(n), rng) < a for _ in range(N_SIM)]))


def first_n(draw, rng: np.random.Generator) -> int | None:
    """Smallest n with estimated power >= goal at n AND n + 1 (review s14: first noisy crossing biases n down)."""
    ok_prev = False
    for n in range(6, N_MAX + 2):
        ok = power(n, draw, rng) >= POWER_GOAL
        if ok and ok_prev:
            return n - 1
        ok_prev = ok
    return None


def sd_upper80(sd: float, n: int) -> float:
    """Upper 80 % bound of the SD from n pilot values (chi-square, Wilson-Hilferty approximation of the 20 % quantile)."""
    k, z = n - 1, -0.8416
    q = k * (1 - 2 / (9 * k) + z * np.sqrt(2 / (9 * k))) ** 3
    return float(sd * np.sqrt(k / q))


def plan(D: list[float], rng: np.random.Generator) -> dict:
    x = np.asarray(D)
    sd = float(x.std(ddof=1))
    boot = np.array([rng.choice(x, len(x)).mean() for _ in range(5000)])
    res = {"n_pilot": len(x), "mean": float(x.mean()), "sd": sd, "n_positive": int((x > 0).sum()),
           "ci95_mean": [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))]}
    centered = x - x.mean() + MIN_EFFECT
    sd_up = sd_upper80(sd, len(x))
    res["sd_upper80"] = sd_up
    for name, draw in (("normal", lambda n: rng.normal(MIN_EFFECT, sd, n)), ("bootstrap", lambda n: rng.choice(centered, n)),
                       ("normal_sd_upper80", lambda n: rng.normal(MIN_EFFECT, sd_up, n))):
        res[f"n_needed_{name}"] = first_n(draw, rng)
    if x.mean() < MIN_EFFECT:
        res["warning"] = "pilot mean below the minimum effect: power at mean 1 is optimistic"
    return res


def selftest() -> None:
    rng = np.random.default_rng(0)
    assert abs(delta_pow(np.array([4.0, 1.0]), np.array([1.0, 4.0]), [1], [2]) - 2 * np.log(4)) < 1e-12
    big = plan(list(rng.normal(8.4, 1.2, 10)), rng)          # EXP-016-like pilot: SD 1.2 -> small n for mean >= 1
    assert big["n_needed_normal"] is not None and big["n_needed_normal"] <= 20, big
    tiny = plan(list(rng.normal(0.2, 6.0, 10)), rng)           # very noisy pilot -> more seeds than the cap
    assert tiny["n_needed_normal"] is None and "warning" in tiny, tiny
    import itertools                                           # Monte Carlo sign flip vs the exact test
    d = np.array([0.9, -0.2, 1.3, 0.4, 0.7, -0.5, 1.1, 0.2])
    flips = np.array(list(itertools.product((1, -1), repeat=len(d))))
    exact = float(((flips * d).mean(axis=1) >= d.mean() - 1e-12).mean())
    assert abs(sign_flip_p(d, rng) - exact) < 0.03, (sign_flip_p(d, rng), exact)
    assert abs(delta_pow(np.array([2.0, 1, 1, 4]), np.array([1.0, 2, 3, 1]), [1, 4], [2, 3]) - (np.log(6 / 2) + np.log(5 / 2))) < 1e-12
    assert 1.1 < sd_upper80(1.0, 10) < 1.4
    print("[pilot_power] selftest ok", big["n_needed_normal"], tiny["n_needed_normal"])


def main() -> None:
    rng = np.random.default_rng(RNG_SEED)
    e46, e47 = EXP / "EXP-046-dihedral-steering", EXP / "EXP-047-marginal-control"
    cases = {
        "add97 (EXP-043)": exp043("add", 97),
        "mul113 (EXP-043)": exp043("mul", 113),
        "D59 (EXP-046)": spectra_pairs(e46, range(140, 150), lambda s, a: f"split_D59_seed{s}_eps2.0_{a}",
                                       lambda s, st: f"EXP-046_seed{s}_{st}_devcuda", {"p": 118, "group": "D59"}),
        "add113 GPU eng (EXP-047)": spectra_pairs(e47, range(150, 160), lambda s, a: f"split_add113_seed{s}_eng_{a}",
                                                  lambda s, st: f"*_seed{s}_thr*_{st}_devcuda", {"p": 113, "task": "add"}),
        "intadd detrended (EXP-048)": from_summary(EXP / "EXP-048-intadd-steering", lambda r: r["Delta_pow"]),
        "add113 d512 (EXP-049)": from_summary(EXP / "EXP-049-width-steering", lambda r: r["d512"]["Delta_pow"]),
    }
    out = {"min_effect": MIN_EFFECT, "alpha_per_test": ALPHA / FAMILY, "power_goal": POWER_GOAL, "cases": {}}
    for name, D in cases.items():
        out["cases"][name] = plan(D, rng) if len(D) >= 5 else {"n_pilot": len(D), "note": "zu wenige gültige Paare"}
        print(name, json.dumps(out["cases"][name]), flush=True)
    (LAB / "tools" / "pilot_power_summary.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    selftest() if sys.argv[1:] == ["--selftest"] else main()
