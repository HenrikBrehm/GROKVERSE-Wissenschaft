"""C4 analysis (registration lab/confirm/C4_REGISTRATION.md, session 28). Written BEFORE any P2f run; must not change measure,
unit, test or thresholds of the registration. Same statistics as C1 (C1_analyze.aggregate) with one cell.

Per arm (P2f run, D59, group_train.py, 12 000 steps): rho = Spearman over the arm's 5 target irreps between the split's D59 mask
spectrum (confirm_splits.m0 'D') and the irrep power of W_E at step 12 000 (spectra.npy); step-0 power from the same file.
Loaded through the P2f binding (hash -> load -> hash, split bytes pinned). Unit = seed (mean F/G, both valid). Confirmed =
sign-flip p < 0.05 and bootstrap CI lower bound >= 0.10 and CI lower bound of the adjusted coefficient (mask | irrep index,
step 0) > 0; not evaluable with fewer than 10 of 20 seeds. Code gate C4_manifest.json (as C1).

  python lab/confirm/C4_analyze.py --selftest              (window only)
  python lab/confirm/C4_analyze.py lab/confirm/P2f_manifest.json
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
import confirm_splits as cs  # noqa: E402
import rank_tools as rt  # noqa: E402
from C1_analyze import aggregate, gate_commit  # noqa: E402
from result_loader import Expect, load_run  # noqa: E402

N, STEP = 59, 12000
OUT = LAB / "confirm" / "C4_summary.json"
GATE = LAB / "confirm" / "C4_manifest.json"
CODE = ("lab/confirm/C4_analyze.py", "lab/confirm/C1_analyze.py", "lab/confirm/rank_tools.py", "lab/confirm/P1_posthoc_within.py")


def code_hashes() -> dict[str, str]:
    return {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in CODE}


def check_gate(block_commit: str) -> dict:
    g = json.loads(GATE.read_text(encoding="utf-8"))
    if g.get("code_sha256") != code_hashes():
        raise SystemExit("C4: code differs from C4_manifest.json, analysis refused")
    return {**g, "gate_commit": gate_commit([GATE, LAB / "confirm" / "C4_REGISTRATION.md"], block_commit)}


def arm_block(idx: np.ndarray, T: list[int], sp: np.ndarray, st: list[int]) -> dict:
    sel = [k - 1 for k in T]
    return {"y": sp[st.index(STEP)][sel], "m0c": cs.m0(idx, "D", N)[sel], "k": np.array(T, dtype=np.float64), "init": sp[st.index(0)][sel]}


def load_arm(p2f, man: dict, s: int, a: str) -> dict | str:
    split = p2f.SPL / f"{p2f.stem(s, a)}.npy"
    d = p2f.run_dir(["x", p2f.GT, "--seed", str(s), "--device", man["device"], "--split-file", str(split)])
    if not d.exists():
        return "fehlt"
    if (why := p2f.BLOCK.unbound(man, d)):
        return f"defekt: {why}"
    L = load_run(d, Expect(seed=s, device=man["device"], max_steps=man["steps"], split_file=split, config={"p": 2 * N}, at=(0, STEP)))
    if L.status != "ok":
        return f"{L.status}: {L.reason}"
    if (why := p2f.BLOCK.unbound(man, d)) or L.res.get("fingerprint_fields", {}).get("split_file_sha256") != p2f.sha(split):
        return f"defekt after load: {why or 'split bytes differ'}"
    sp = np.vstack([np.asarray(L.spectrum(0), dtype=np.float64), np.asarray(L.spectrum(STEP), dtype=np.float64)])
    if sp.shape[1] != cs.n_targets_pool("D", N) or not np.all(np.isfinite(sp)):
        return "defekt: spectrum shape or values"
    T = json.loads((p2f.SPL / f"{p2f.stem(s, a)}.json").read_text(encoding="utf-8"))["targets"]
    gen = L.res.get("generalization_step")                 # Codex s28: reported (descriptive), never a condition
    return {**arm_block(np.load(split), T, sp, [0, STEP]), "generalized": gen is not None and int(gen) <= STEP}


def analyze(manifest: Path) -> None:
    import confirm_p2f as p2f
    if OUT.exists():
        raise SystemExit(f"{OUT.name} exists: never overwritten (move it away deliberately)")
    man = json.loads(manifest.read_text(encoding="utf-8"))
    gate = check_gate(man["commit"])
    p2f.BLOCK.check_manifest(manifest, man)
    units, rows, dropped = {"all": []}, [], []
    for s in man["seeds"]:
        if (m := p2f.split_mismatch(man, s)):
            dropped.append({"seed": s, "reason": m})
            continue
        got, notes = {}, []
        for a in "FG":
            b = load_arm(p2f, man, s, a)
            if isinstance(b, str):
                notes.append(f"{a}: {b}")
                continue
            try:
                got[a] = (b, rt.spearman(b["m0c"], b["y"]), rt.spearman(b["init"], b["y"]))
            except rt.TieError as ex:
                notes.append(f"{a}: {ex}")
        if len(got) != 2:
            dropped.append({"seed": s, "reason": "; ".join(notes)})
            continue
        rho = (got["F"][1] + got["G"][1]) / 2
        units["all"].append({"rho": rho, "blocks": [got[a][0] for a in "FG"]})
        rows.append({"seed": s, "unit_rho": rho, "rho_init_F": got["F"][2], "rho_init_G": got["G"][2],
                     "generalized_arms": int(got["F"][0]["generalized"]) + int(got["G"][0]["generalized"])})
    res = aggregate(units, {"all": len(man["seeds"])}, np.random.default_rng(2026_09_28_6))
    out = {"registration": "lab/confirm/C4_REGISTRATION.md", "gate": gate, "p2f_manifest_commit": man["commit"], "code_sha256": code_hashes(),
           "primary": res, "descriptive_generalized_arms": sum(r["generalized_arms"] for r in rows), "descriptive_counted_arms": 2 * len(rows),
           "dropped": dropped, "rows": rows}
    with open(OUT, "x", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    """arm_block on the EXP-072 pilot reproduces its stored late-step value (mean rho over 10 arms at step 10 000: 0.58, the
    pilot ran 20 000 steps; this checks the D59 mask spectrum, target indexing and the rank code, NOT load_arm / the P2f binding
    (Codex s28 MINOR: that path is exercised only by the mandatory P2f smoke and a technical failure there is counted, not hidden))."""
    e72 = next((LAB / "experiments").glob("EXP-072*"))
    ref = json.loads((LAB / "confirm/EXP072_posthoc_time.json").read_text(encoding="utf-8"))["mean_rho_M0"]["10000"]
    r = []
    for d in sorted((e72 / "raw").glob("*_devcuda")):
        stem = d.name.split("_", 2)[2].rsplit("_devcuda", 1)[0]
        T = json.loads((LAB / "confirm/splits" / f"{stem}.json").read_text(encoding="utf-8"))["targets"]
        sp, st = np.load(d / "spectra.npy"), [int(x) for x in np.load(d / "spectra_steps.npy")]
        b = arm_block(np.load(LAB / "confirm/splits" / f"{stem}.npy"), T, np.vstack([sp[st.index(0)], sp[st.index(10000)]]), [0, STEP])
        r.append(rt.spearman(b["m0c"], b["y"]))
    assert len(r) == 10 and abs(np.mean(r) - ref) < 1e-3, (np.mean(r), ref)
    print("C4 selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif len(sys.argv) == 2:
        analyze(Path(sys.argv[1]))
    else:
        raise SystemExit(__doc__)
