"""C1 analysis, version 2 (registration lab/confirm/C1_REGISTRATION.md, "Fassung 2", session 28, after the Codex review).
Written BEFORE any R1 run; must not change measure, unit, test or thresholds of the registration.

Per arm (R1 run, add 113, step 2000, through the frozen R1 loader; step-0 snapshot through a full load of the same run):
  rho = Spearman over the 5 targets between M0c(target) of the split and the W_E power; exact ties -> arm technical.
Unit = seed (mean of F and G; both arms valid). Statistic S = equal-weight mean over the six cells of the cell means.
Confirmed = (i) sign-flip p < 0.05 and (ii) stratified-bootstrap CI lower bound of S >= 0.10 and (iii) stratified-bootstrap
CI lower bound of the adjusted coefficient (M0c ranks | k ranks, step-0 ranks; all arms with step 0 stacked) > 0.
Not evaluable if any cell has fewer than 10 of 15 seeds with two valid arms. The code gate (C1_manifest.json: sha256 of the
code files) must match; an existing summary is never overwritten.

  python lab/confirm/C1_analyze.py --selftest              (window only)
  python lab/confirm/C1_analyze.py lab/confirm/R1_manifest.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "confirm"))
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
import confirm_splits as cs  # noqa: E402
import rank_tools as rt  # noqa: E402
from analyze import group_power  # noqa: E402
from P1_posthoc_within import m0c_add  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

P, ALPHA, MIN_EFFECT, MIN_PER_CELL = 113, 0.05, 0.10, 10
OUT = LAB / "confirm" / "C1_summary.json"
GATE = LAB / "confirm" / "C1_manifest.json"
CODE = ("lab/confirm/C1_analyze.py", "lab/confirm/rank_tools.py", "lab/confirm/P1_posthoc_within.py")


def code_hashes() -> dict[str, str]:
    return {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in CODE}


def check_gate() -> dict:
    g = json.loads(GATE.read_text(encoding="utf-8"))
    if g.get("code_sha256") != code_hashes():
        raise SystemExit("C1: code differs from C1_manifest.json, analysis refused")
    return g


def arm_block(idx: np.ndarray, T: list[int], pw: np.ndarray, pw0: np.ndarray | None) -> dict:
    sel = [k - 1 for k in T]
    return {"y": pw[sel], "m0c": m0c_add(idx, P)[sel], "m0": cs.m0(idx, "add", P)[sel], "k": np.array(T, dtype=np.float64),
            "init": None if pw0 is None else pw0[sel]}


def arm_stats(b: dict) -> dict:
    """Raises rt.TieError on ties in y or M0c (arm technical)."""
    return {"rho_M0c": rt.spearman(b["m0c"], b["y"]), "rho_M0": rt.spearman(b["m0"], b["y"]),
            "rho_init": None if b["init"] is None else rt.spearman(b["init"], b["y"]),
            "weakest_is_lowest_M0c": bool(np.argmin(b["m0c"]) == np.argmin(b["y"]))}


def aggregate(units: dict[str, list[dict]], n_planned: dict[str, int], rng: np.random.Generator,
              n_flip: int = 200_000, n_boot: int = 10_000) -> dict:
    """units: cell -> list of seed units {"rho": float, "blocks": [arm blocks with init or None]}."""
    counts = {c: len(u) for c, u in units.items()}
    if any(counts.get(c, 0) < MIN_PER_CELL for c in n_planned):
        return {"counts": counts, "verdict": "nicht auswertbar"}
    vals = {c: np.array([u["rho"] for u in us]) for c, us in units.items()}
    S = rt.cell_mean(vals)
    p = rt.sign_flip_p(vals, rng, n_flip)
    ci = rt.strat_boot(units, lambda u: rt.cell_mean({c: np.array([x["rho"] for x in xs]) for c, xs in u.items()}), rng, n_boot)

    def adj(u: dict[str, list[dict]]) -> float:
        return rt.adjusted_coef([b for xs in u.values() for x in xs for b in x["blocks"] if b["init"] is not None], "m0c", ["k", "init"])

    a_units = {c: [x for x in xs if all(b["init"] is not None for b in x["blocks"])] for c, xs in units.items()}
    a = adj(a_units)
    a_ci = rt.strat_boot(a_units, adj, rng, n_boot)
    missing = sum(n_planned.values()) - sum(counts.values())
    worst = rt.cell_mean({c: np.concatenate([vals[c], -np.ones(n_planned[c] - counts[c])]) for c in n_planned})
    ok = p < ALPHA and ci[0] >= MIN_EFFECT and a_ci[0] > 0
    return {"counts": counts, "S": S, "p": p, "ci95": ci, "adjusted_coef": a, "adjusted_ci95": a_ci,
            "adjusted_seeds": {c: len(x) for c, x in a_units.items()}, "cell_means": {c: float(v.mean()) for c, v in vals.items()},
            "missing_seeds": missing, "S_if_missing_were_minus_1": worst, "verdict": "bestätigt" if ok else "nicht bestätigt"}


def load_arm(r1, man: dict, c: str, s: int, a: str) -> tuple[dict, str | None] | str:
    run = r1.power(man, c, s, a)                        # frozen R1 loader: binding, split bytes, hp, finite step-2000 spectrum
    if isinstance(run, str):
        return run
    split = r1.SPL / f"{r1.stem(c, s, a)}.npy"
    T = json.loads((r1.SPL / f"{r1.stem(c, s, a)}.json").read_text(encoding="utf-8"))["targets"]
    cmd = ["x", r1.FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--split-file", str(split)]
    for k, v in r1.CELLS[c].items():
        cmd += [r1.FLAG[k], repr(v)]
    d = r1.run_dir(cmd)
    hp = {"lr": 1e-3, "weight_decay": 1.0, "train_frac": r1.FRAC0, **r1.CELLS[c]}
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=man["steps"], split_file=split,
                           config={"p": P, "task": "add", "arch": "transformer", **hp}, at=(man["steps"],), snapshots_at=(0,)))
    why0 = None if L.status == "ok" and r1.BLOCK.unbound(man, d) is None else f"step 0: {L.status} {L.reason}"
    pw0 = None if why0 else group_power(L.snapshot(0).astype(np.float64), "add", P)[0]
    return arm_block(np.load(split), T, run["pw"], pw0), why0


def analyze(manifest: Path) -> None:
    import confirm_r1 as r1
    gate = check_gate()
    if OUT.exists():
        raise SystemExit(f"{OUT.name} exists: never overwritten (move it away deliberately)")
    man = json.loads(manifest.read_text(encoding="utf-8"))
    r1.BLOCK.check_manifest(manifest, man)
    r1.check_design(man)
    units: dict[str, list[dict]] = {c: [] for c in r1.CELLS}
    rows, dropped = [], []
    for c in r1.CELLS:
        for s in man["seeds"][c]:
            if (m := r1.split_mismatch(man, c, s)):
                dropped.append({"cell": c, "seed": s, "reason": m})
                continue
            got, notes = {}, []
            for a in "FG":
                res = load_arm(r1, man, c, s, a)
                if isinstance(res, str):
                    notes.append(f"{a}: {res}")
                    continue
                b, why0 = res
                try:
                    got[a] = (b, arm_stats(b))
                except rt.TieError as ex:
                    notes.append(f"{a}: {ex}")
                    continue
                if why0:
                    notes.append(f"{a}: {why0}")
            if len(got) != 2:
                dropped.append({"cell": c, "seed": s, "reason": "; ".join(notes)})
                continue
            rho = (got["F"][1]["rho_M0c"] + got["G"][1]["rho_M0c"]) / 2
            units[c].append({"rho": rho, "blocks": [got[a][0] for a in "FG"]})
            rows.append({"cell": c, "seed": s, "unit_rho": rho, "notes": notes, **{f"{k}_{a}": v for a in "FG" for k, v in got[a][1].items()}})
    res = aggregate(units, {c: len(man["seeds"][c]) for c in r1.CELLS}, np.random.default_rng(2026_09_28_1))
    desc = {k: float(np.mean([r[f"{k}_{a}"] for r in rows for a in "FG" if r[f"{k}_{a}"] is not None])) if rows else None
            for k in ("rho_M0", "rho_init", "weakest_is_lowest_M0c")}
    out = {"registration": "lab/confirm/C1_REGISTRATION.md (Fassung 2)", "gate": gate, "r1_manifest_commit": man["commit"],
           "code_sha256": code_hashes(), "primary": res, "descriptive": desc, "dropped": dropped, "rows": rows}
    with open(OUT, "x", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    """rank_tools hand values; aggregate() on synthetic units (confirms / rejects / not evaluable / missing bound / adjusted
    coefficient ~0 when y follows k only); M0c against an independent brute-force computation on a small split."""
    rt.selftest()
    rng = np.random.default_rng(0)
    cells = {f"c{i}": 15 for i in range(6)}

    def synth(shift: float, follow: str, n: int = 15) -> dict[str, list[dict]]:
        out = {}
        for c in cells:
            us = []
            for _ in range(n):
                bl = []
                for _a in "FG":
                    m, k, i0 = rng.permutation(5.0), rng.permutation(5.0), rng.permutation(5.0)
                    y = {"m0c": m, "k": k}[follow] + shift * rng.standard_normal(5)
                    bl.append({"y": y, "m0c": m + 1e-3 * rng.random(5), "k": k, "init": i0})
                us.append({"rho": float(np.mean([rt.spearman(b["m0c"], b["y"]) for b in bl])), "blocks": bl})
            out[c] = us
        return out

    assert aggregate(synth(1.0, "m0c"), cells, rng, 5000, 500)["verdict"] == "bestätigt"
    r = aggregate(synth(1.0, "k"), cells, rng, 5000, 500)
    assert r["verdict"] == "nicht bestätigt" and abs(r["adjusted_coef"]) < 0.15, r
    assert aggregate(synth(1.0, "m0c", 9), cells, rng, 5000, 500)["verdict"] == "nicht auswertbar"
    u = synth(1.0, "m0c")
    u["c0"] = u["c0"][:12]
    r = aggregate(u, cells, rng, 5000, 500)
    assert r["missing_seeds"] == 3 and r["S_if_missing_were_minus_1"] < r["S"]
    # M0c brute force: coherent shared-path signal f_t(c) = m(t, c - t) + m(c - t, t), DFT over t, centred over c, folded k/p-k
    p = 13
    idx = np.sort(rng.choice(p * p, 50, replace=False))
    m = np.zeros((p, p))
    m[idx // p, idx % p] = 1
    f = np.array([[m[t, (c - t) % p] + m[(c - t) % p, t] for c in range(p)] for t in range(p)])
    X = np.array([[sum(f[t, c] * np.exp(-2j * np.pi * k * t / p) for t in range(p)) for c in range(p)] for k in range(p)])
    X = X - X.mean(1, keepdims=True)
    s = (np.abs(X) ** 2).sum(1)
    brute = np.array([s[k] + s[p - k] for k in range(1, (p - 1) // 2 + 1)])
    assert np.allclose(m0c_add(idx, p), brute), (m0c_add(idx, p), brute)
    print("C1 selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif len(sys.argv) == 2:
        analyze(Path(sys.argv[1]))
    else:
        raise SystemExit(__doc__)
