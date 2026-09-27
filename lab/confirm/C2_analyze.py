"""C2 analysis, version 2 (registration lab/confirm/C2_REGISTRATION.md, "Fassung 2", session 28, Codex points of C1 applied).
Written BEFORE any R2 run; must not change measure, unit, test or thresholds of the registration.

Per R2 run with switch at t = 50: Spearman over the five OLD targets (first split's targets) between the W_E group power at
step t and at t + budget, from bound W_E snapshots (R2 binding: hash -> load -> hash; split bytes pinned); ties -> run technical.
Unit = seed: mean over its four t = 50 runs (two cells x two directions); a seed counts only with all four valid. Confirmed = (i) sign-flip p < 0.05 and
(ii) bootstrap CI (seeds) lower bound of the mean >= 0.10 and (iii) bootstrap CI lower bound of the adjusted coefficient
(switch ranks | k ranks, second-split M0c ranks; all valid t = 50 runs stacked) > 0. Not evaluable if < 20 seeds have a valid
t = 50 run set. Code gate C2_manifest.json; an existing summary is never overwritten.

  python lab/confirm/C2_analyze.py --selftest              (window only)
  python lab/confirm/C2_analyze.py lab/confirm/R2_manifest.json
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
import rank_tools as rt  # noqa: E402
from analyze import group_power  # noqa: E402
from P1_posthoc_within import m0c_add  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

P, T_PRIMARY, ALPHA, MIN_EFFECT, MIN_SEEDS, N_PRIMARY_RUNS = 113, 50, 0.05, 0.10, 20, 4
OUT = LAB / "confirm" / "C2_summary.json"
GATE = LAB / "confirm" / "C2_manifest.json"
CODE = ("lab/confirm/C2_analyze.py", "lab/confirm/rank_tools.py", "lab/confirm/P1_posthoc_within.py")


def code_hashes() -> dict[str, str]:
    return {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in CODE}


def check_gate(block_commit: str) -> dict:
    """As C1 (Codex recheck s28): hashes match and the gate + registration were committed before the R2 manifest commit."""
    from C1_analyze import gate_commit
    g = json.loads(GATE.read_text(encoding="utf-8"))
    if g.get("code_sha256") != code_hashes():
        raise SystemExit("C2: code differs from C2_manifest.json, analysis refused")
    return {**g, "gate_commit": gate_commit([GATE, LAB / "confirm" / "C2_REGISTRATION.md"], block_commit)}


def run_block(W_t: np.ndarray, W_end: np.ndarray, old: list[int], new: list[int], sp_first: np.ndarray, sp_second: np.ndarray) -> dict:
    pt, pe = group_power(W_t, "add", P)[0], group_power(W_end, "add", P)[0]
    mf, ms = m0c_add(sp_first, P), m0c_add(sp_second, P)
    o, n = [k - 1 for k in old], [k - 1 for k in new]
    return {"y": pe[o], "switch": pt[o], "k": np.array(old, dtype=np.float64), "m0c_first": mf[o], "m0c_second": ms[o],
            "new_y": pe[n], "new_switch": pt[n], "new_m0c_second": ms[n]}


def run_stats(b: dict) -> dict:
    """Primary rho first (raises rt.TieError -> run technical); descriptive ones may be None on ties."""
    out = {"rho_old_switch": rt.spearman(b["switch"], b["y"])}
    rt.cranks(b["k"]), rt.cranks(b["m0c_second"])            # Codex recheck s28: controls must rank too, else run technical
    for name, x, y in (("rho_old_M0c_first", "m0c_first", "y"), ("rho_old_M0c_second", "m0c_second", "y"),
                       ("rho_new_switch", "new_switch", "new_y"), ("rho_new_M0c_second", "new_m0c_second", "new_y")):
        try:
            out[name] = rt.spearman(b[x], b[y])
        except rt.TieError:
            out[name] = None
    return out


def aggregate(units: list[dict], n_planned: int, rng: np.random.Generator, n_flip: int = 200_000, n_boot: int = 10_000) -> dict:
    """units: one per seed {"rho": mean over its valid t = 50 runs, "blocks": [run blocks]}; single stratum."""
    if len(units) < MIN_SEEDS:
        return {"n": len(units), "verdict": "nicht auswertbar"}
    vals = {"all": np.array([u["rho"] for u in units])}
    m = rt.cell_mean(vals)
    p = rt.sign_flip_p(vals, rng, n_flip)
    ci = rt.strat_boot({"all": units}, lambda u: float(np.mean([x["rho"] for x in u["all"]])), rng, n_boot)

    def adj(u: dict[str, list[dict]]) -> float:
        return rt.adjusted_coef([b for x in u["all"] for b in x["blocks"]], "switch", ["k", "m0c_second"])

    a = adj({"all": units})
    a_ci = rt.strat_boot({"all": units}, adj, rng, n_boot)
    ok = p < ALPHA and ci[0] >= MIN_EFFECT and a_ci[0] > 0
    return {"n": len(units), "n_planned": n_planned, "mean": m, "sd": float(vals["all"].std(ddof=1)), "n_positive": int((vals["all"] > 0).sum()),
            "p": p, "ci95": ci, "adjusted_coef": a, "adjusted_ci95": a_ci,
            "mean_if_missing_were_minus_1": float((vals["all"].sum() - (n_planned - len(units))) / n_planned),
            "verdict": "bestätigt" if ok else "nicht bestätigt"}


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
    if OUT.exists():
        raise SystemExit(f"{OUT.name} exists: never overwritten (move it away deliberately)")
    man = json.loads(manifest.read_text(encoding="utf-8"))
    gate = check_gate(man["commit"])
    r2.BLOCK.check_manifest(manifest, man)
    rows, bad, units = [], [], []
    for s in man["seeds"]:
        if (m := r2.split_mismatch(man, s)):
            bad.append(f"{s}: {m}")
            continue
        T = json.loads((r2.SPL / f"r2_seed{s}_w0.json").read_text(encoding="utf-8"))["targets"]
        prim = []
        for c, cell in man["cells"].items():
            for t in cell["ts"]:
                for first, second in (("A", "B"), ("B", "A")):
                    snaps = load_snaps(r2, man, c, s, t, first, second)
                    if isinstance(snaps, str):
                        bad.append(f"{s} {c} {first}{second}@{t}: {snaps}")
                        continue
                    sp1, sp2 = (np.load(r2.SPL / f"{r2.stem(s, a)}.npy") for a in (first, second))
                    b = run_block(*snaps, T[first], T[second], sp1, sp2)
                    try:
                        st = run_stats(b)
                    except rt.TieError as ex:
                        bad.append(f"{s} {c} {first}{second}@{t}: {ex}")
                        continue
                    rows.append({"seed": s, "cell": c, "t": t, "dir": first + second, **st})
                    if t == T_PRIMARY:
                        prim.append((st["rho_old_switch"], b))
        if len(prim) == N_PRIMARY_RUNS:                   # Codex recheck s28: both cells x both directions, else seed technical
            units.append({"rho": float(np.mean([r for r, _ in prim])), "blocks": [b for _, b in prim]})
    desc = {}
    for c, cell in man["cells"].items():
        for t in cell["ts"]:
            sel = [r for r in rows if r["cell"] == c and r["t"] == t]
            desc[f"{c}@{t}"] = {k: float(np.mean([r[k] for r in sel if r[k] is not None])) for k in sel[0] if k.startswith("rho_")} if sel else None
    out = {"registration": "lab/confirm/C2_REGISTRATION.md (Fassung 2)", "gate": gate, "r2_manifest_commit": man["commit"],
           "code_sha256": code_hashes(), "primary": aggregate(units, len(man["seeds"]), np.random.default_rng(2026_09_28_4)),
           "descriptive_per_run_means": desc, "bad": bad, "rows": rows}
    with open(OUT, "x", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    """rank_tools hand values; aggregate() on synthetic seeds (confirms when y follows the switch ranks, not when it follows k,
    not evaluable below 20 seeds); the N29 exploration value at t = 50 (0.580) through run_block/run_stats."""
    rt.selftest()
    rng = np.random.default_rng(0)

    def synth(follow: str, n: int = 30) -> list[dict]:
        us = []
        for _ in range(n):
            bl = []
            for _r in range(4):
                sw, k, m2 = rng.permutation(5.0), rng.permutation(5.0), rng.permutation(5.0)
                bl.append({"y": {"switch": sw, "k": k}[follow] + rng.standard_normal(5), "switch": sw, "k": k, "m0c_second": m2})
            us.append({"rho": float(np.mean([rt.spearman(b["switch"], b["y"]) for b in bl])), "blocks": bl})
        return us

    assert aggregate(synth("switch"), 30, rng, 5000, 500)["verdict"] == "bestätigt"
    r = aggregate(synth("k"), 30, rng, 5000, 500)
    assert r["verdict"] == "nicht bestätigt" and abs(r["adjusted_coef"]) < 0.15, r
    assert aggregate(synth("switch", 19), 30, rng, 5000, 500)["verdict"] == "nicht auswertbar"
    raw, spl = LAB / "confirm/n29_raw", LAB / "confirm/n29_splits"
    by: dict[int, list[float]] = {}
    for d in sorted(raw.glob("*_at50_devcuda")):
        s = int(d.name.split("_seed")[1].split("_")[0])
        first, second = ("A", "B") if f"w0_A_to_n29_seed{s}_w0_B" in d.name else ("B", "A")
        T = json.loads((spl / f"n29_seed{s}_w0.json").read_text(encoding="utf-8"))["targets"]
        st, W = list(np.load(d / "we_snapshot_steps.npy")), np.load(d / "we_snapshots.npy").astype(np.float64)
        b = run_block(W[st.index(50)], W[st.index(4050)], T[first], T[second],
                      *(np.load(spl / f"n29_seed{s}_w0_{a}.npy") for a in (first, second)))
        by.setdefault(s, []).append(run_stats(b)["rho_old_switch"])
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
