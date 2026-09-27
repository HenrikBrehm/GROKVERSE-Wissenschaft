"""C2 analysis (registration lab/confirm/C2_REGISTRATION.md, session 28). Written BEFORE any R2 run; must not change measure,
unit, test or thresholds of the registration.

Per R2 run: Spearman over the five OLD targets (first split's targets) between the W_E group power at the switch step t and at
t + budget, from the bound W_E snapshots (R2 binding: hash -> load -> hash; split bytes pinned). Unit = seed: mean over its valid
t = 50 runs (two cells x two directions). Primary: one-sided sign-flip test mean > 0 (200 000 draws), 95 % bootstrap CI over
seeds (10 000); confirmed = p < 0.05 and CI lower bound >= 0.10; not evaluable if < 20 seeds have a valid t = 50 run.

  python lab/confirm/C2_analyze.py --selftest              (window only: reproduces the N29 exploration, t = 50, 0.580)
  python lab/confirm/C2_analyze.py lab/confirm/R2_manifest.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "confirm"))
sys.path.insert(0, str(LAB / "experiments/EXP-043-generalize-steering"))
from analyze import group_power  # noqa: E402
from C1_analyze import primary as _primary, spearman5  # noqa: E402
from P1_posthoc_within import m0c_add  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

P, T_PRIMARY, MIN_SEEDS = 113, 50, 20
OUT = LAB / "confirm" / "C2_summary.json"


def primary(d: np.ndarray, rng: np.random.Generator) -> dict:
    """C1's test with C2's minimum number of seeds (C1: 60)."""
    import C1_analyze
    old, C1_analyze.MIN_SEEDS = C1_analyze.MIN_SEEDS, MIN_SEEDS
    try:
        return _primary(d, rng)
    finally:
        C1_analyze.MIN_SEEDS = old


def run_values(W_t: np.ndarray, W_end: np.ndarray, old: list[int], new: list[int], sp_first: np.ndarray, sp_second: np.ndarray) -> dict:
    pt, pe = group_power(W_t, "add", P)[0], group_power(W_end, "add", P)[0]
    mf, ms = m0c_add(sp_first, P), m0c_add(sp_second, P)
    o, n = [k - 1 for k in old], [k - 1 for k in new]
    return {"rho_old_switch": spearman5(pt[o], pe[o]), "rho_old_M0c_first": spearman5(mf[o], pe[o]), "rho_old_M0c_second": spearman5(ms[o], pe[o]),
            "rho_new_switch": spearman5(pt[n], pe[n]), "rho_new_M0c_second": spearman5(ms[n], pe[n])}


def load_snaps(r2, man: dict, c: str, s: int, t: int, first: str, second: str) -> tuple[np.ndarray, np.ndarray] | str:
    cell = man["cells"][c]
    sp, sw, te = r2.SPL / f"{r2.stem(s, first)}.npy", r2.SPL / f"{r2.stem(s, second)}.npy", r2.SPL / f"r2_seed{s}_test.npy"
    cmd = ["x", r2.FB, "--seed", str(s), "--threads", str(man["threads"]), "--device", man["device"], "--split-file", str(sp),
           "--switch-split-file", str(sw), "--switch-step", str(t)]
    for k, v in cell["hp"].items():
        cmd += [r2.FLAG[k], repr(v)]
    d, steps = r2.run_dir(cmd), t + man["budget"]
    if not d.exists():
        return "fehlt"
    if (why := r2.BLOCK.unbound(man, d)):
        return f"defekt: {why}"
    hp = {"lr": r2.LR0, "weight_decay": r2.WD0, "train_frac": r2.FRAC0, **cell["hp"]}
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=steps, split_file=sp, test_file=te, switch_file=sw,
                           config={"p": P, "task": "add", "arch": "transformer", **hp}, snapshots_at=(t, steps)))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    if (why := r2.BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != r2.sha(sp):
        return f"defekt after load: {why or 'split bytes differ'}"
    return L.snapshot(t).astype(np.float64), L.snapshot(steps).astype(np.float64)


def analyze(manifest: Path) -> None:
    import confirm_r2 as r2
    man = json.loads(manifest.read_text(encoding="utf-8"))
    r2.BLOCK.check_manifest(manifest, man)
    rows, bad = [], []
    for s in man["seeds"]:
        if (m := r2.split_mismatch(man, s)):
            bad.append(f"{s}: {m}")
            continue
        T = json.loads((r2.SPL / f"r2_seed{s}_w0.json").read_text(encoding="utf-8"))["targets"]
        for c, cell in man["cells"].items():
            for t in cell["ts"]:
                for first, second in (("A", "B"), ("B", "A")):
                    snaps = load_snaps(r2, man, c, s, t, first, second)
                    if isinstance(snaps, str):
                        bad.append(f"{s} {c} {first}{second}@{t}: {snaps}")
                        continue
                    sp1, sp2 = (np.load(r2.SPL / f"{r2.stem(s, a)}.npy") for a in (first, second))
                    rows.append({"seed": s, "cell": c, "t": t, "dir": first + second,
                                 **run_values(*snaps, T[first], T[second], sp1, sp2)})
    by: dict[int, list[float]] = {}
    for r in rows:
        if r["t"] == T_PRIMARY:
            by.setdefault(r["seed"], []).append(r["rho_old_switch"])
    d = np.array([np.mean(v) for v in by.values()])
    desc = {}
    for c, cell in man["cells"].items():
        for t in cell["ts"]:
            sel = [r for r in rows if r["cell"] == c and r["t"] == t]
            desc[f"{c}@{t}"] = {k: float(np.mean([r[k] for r in sel])) for k in sel[0] if k.startswith("rho_")} if sel else None
    out = {"registration": "lab/confirm/C2_REGISTRATION.md", "manifest_commit": man["commit"],
           "primary": primary(d, np.random.default_rng(2026_09_28_4)), "descriptive_per_run_means": desc, "bad": bad, "rows": rows}
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    """(1) primary() uses MIN_SEEDS = 20 here and restores C1's value; (2) the N29 exploration value at t = 50 (0.580) is
    reproduced through run_values on the stored N29 snapshots."""
    import C1_analyze
    rng = np.random.default_rng(0)
    assert primary(rng.normal(0.5, 0.3, 20), rng)["verdict"] == "bestätigt" and C1_analyze.MIN_SEEDS == 60
    assert primary(rng.normal(0.5, 0.3, 19), rng)["verdict"] == "nicht auswertbar"
    raw, spl = LAB / "confirm/n29_raw", LAB / "confirm/n29_splits"
    by: dict[int, list[float]] = {}
    for d in sorted(raw.glob("*_at50_devcuda")):
        s = int(d.name.split("_seed")[1].split("_")[0])
        first, second = ("A", "B") if f"w0_A_to_n29_seed{s}_w0_B" in d.name else ("B", "A")
        T = json.loads((spl / f"n29_seed{s}_w0.json").read_text(encoding="utf-8"))["targets"]
        st, W = list(np.load(d / "we_snapshot_steps.npy")), np.load(d / "we_snapshots.npy").astype(np.float64)
        v = run_values(W[st.index(50)], W[st.index(4050)], T[first], T[second],
                       *(np.load(spl / f"n29_seed{s}_w0_{a}.npy") for a in (first, second)))
        by.setdefault(s, []).append(v["rho_old_switch"])
    u = float(np.mean([np.mean(v) for v in by.values()]))
    assert len(by) == 20 and abs(u - 0.580) < 0.0015, u
    print("C2 selftest ok", round(u, 4))


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif len(sys.argv) == 2:
        analyze(Path(sys.argv[1]))
    else:
        raise SystemExit(__doc__)
