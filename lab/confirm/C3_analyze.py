"""C3 analysis (registration lab/confirm/C3_REGISTRATION.md, session 28). Written BEFORE any P4 run; must not change measure,
unit, test or thresholds of the registration. Same statistics as C1 (C1_analyze.aggregate), cells = the three P4 conditions.

Per arm (P4 run, step 2000, through the frozen P4 loader confirm_p4.spectra: 'secondary' for mlp, 'primary' for d512 and intadd):
  rho = Spearman over the 5 targets between the split's mask spectrum and the W_E power; mask spectrum = M0c (m0c_add) for
  mlp and d512 (add 113), EXP-048 mask_power for intadd. Step-0 power from a second full load of the same run (spectra.npy);
  missing step 0 or ties -> arm technical. intadd: the step-0 control is the RAW spectrum (the trainer stores no step-0 W_E),
  while the outcome is detrended: a deliberately different control (registration, Codex s28 MAJOR). Unit = seed (mean F/G, both valid). Confirmed = sign-flip p < 0.05 and stratified
  bootstrap CI lower bound of the equal-weight condition mean >= 0.10 and CI lower bound of the adjusted coefficient
  (mask | k, step 0) > 0. Not evaluable if a condition has fewer than 10 of 15 seeds. Code gate C3_manifest.json.

  python lab/confirm/C3_analyze.py --selftest              (window only)
  python lab/confirm/C3_analyze.py lab/confirm/P4_manifest.json
"""
from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import json
import shlex
import sys
from pathlib import Path

import numpy as np

LAB = Path(__file__).resolve().parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(LAB / "tools"))
sys.path.insert(0, str(LAB / "confirm"))
import rank_tools as rt  # noqa: E402
from C1_analyze import aggregate, gate_commit  # noqa: E402
from P1_posthoc_within import m0c_add  # noqa: E402
from result_loader import load_run  # noqa: E402

P, STEP = 113, 2000
OUT = LAB / "confirm" / "C3_summary.json"
GATE = LAB / "confirm" / "C3_manifest.json"
CODE = ("lab/confirm/C3_analyze.py", "lab/confirm/C1_analyze.py", "lab/confirm/rank_tools.py", "lab/confirm/P1_posthoc_within.py")
MS48 = LAB / "experiments/EXP-048-intadd-steering/make_split.py"


def code_hashes() -> dict[str, str]:
    return {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in CODE}


def check_gate(block_commit: str) -> dict:
    g = json.loads(GATE.read_text(encoding="utf-8"))
    if g.get("code_sha256") != code_hashes():
        raise SystemExit("C3: code differs from C3_manifest.json, analysis refused")
    return {**g, "gate_commit": gate_commit([GATE, LAB / "confirm" / "C3_REGISTRATION.md"], block_commit)}


_MS48 = None


def mask_spectrum(cond: str, idx: np.ndarray) -> np.ndarray:
    global _MS48
    if cond != "intadd":
        return m0c_add(idx, P)
    if _MS48 is None:
        spec = importlib.util.spec_from_file_location("c3_ms48", MS48)
        _MS48 = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(MS48.parent))
        spec.loader.exec_module(_MS48)
    return _MS48.mask_power(idx)


def step0(p4, man: dict, c: str, s: int, a: str) -> np.ndarray | str:
    split = p4.SPL / f"{p4.stem(c, s, a)}.npy"
    d = p4.run_dir(shlex.split(p4.job(man, c, s, a)))
    e = p4.expect(man, c, s, split)
    L = load_run(d, dataclasses.replace(e, at=tuple(sorted({*e.at, 0}))))
    if L.status != "ok" or p4.BLOCK.unbound(man, d) is not None:
        return f"step 0: {L.status} {L.reason}"
    pw = np.asarray(L.spectrum(0), dtype=np.float64)
    return pw if pw.shape == (56,) and np.all(np.isfinite(pw)) else "step 0: shape or values"


def analyze(manifest: Path) -> None:
    import confirm_p4 as p4
    if OUT.exists():
        raise SystemExit(f"{OUT.name} exists: never overwritten (move it away deliberately)")
    man = json.loads(manifest.read_text(encoding="utf-8"))
    gate = check_gate(man["commit"])
    p4.BLOCK.check_manifest(manifest, man)
    p4.check_design(man)
    units: dict[str, list[dict]] = {c: [] for c in p4.CONDS}
    rows, dropped = [], []
    for c in p4.CONDS:
        for s in man["seeds"][c]:
            if (m := p4.split_mismatch(c, s)):
                dropped.append({"cond": c, "seed": s, "reason": m})
                continue
            got, notes = {}, []
            for a in "FG":
                run = p4.spectra(man, c, s, a)
                pw0 = step0(p4, man, c, s, a) if not isinstance(run, str) else None
                if isinstance(run, str) or isinstance(pw0, str):
                    notes.append(f"{a}: {run if isinstance(run, str) else pw0}")
                    continue
                y = run["secondary"] if c == "mlp" else run["primary"]      # step 2000 in every condition
                T = json.loads((p4.SPL / f"{p4.stem(c, s, a)}.json").read_text(encoding="utf-8"))["targets"]
                sel = [k - 1 for k in T]
                b = {"y": y[sel], "m0c": mask_spectrum(c, np.load(p4.SPL / f"{p4.stem(c, s, a)}.npy"))[sel],
                     "k": np.array(T, dtype=np.float64), "init": pw0[sel]}
                try:
                    got[a] = (b, rt.spearman(b["m0c"], b["y"]), rt.spearman(b["init"], b["y"]))
                except rt.TieError as ex:
                    notes.append(f"{a}: {ex}")
            if len(got) != 2:
                dropped.append({"cond": c, "seed": s, "reason": "; ".join(notes)})
                continue
            rho = (got["F"][1] + got["G"][1]) / 2
            units[c].append({"rho": rho, "blocks": [got[a][0] for a in "FG"]})
            rows.append({"cond": c, "seed": s, "unit_rho": rho, "rho_init_F": got["F"][2], "rho_init_G": got["G"][2]})
    res = aggregate(units, {c: len(man["seeds"][c]) for c in p4.CONDS}, np.random.default_rng(2026_09_28_5))
    out = {"registration": "lab/confirm/C3_REGISTRATION.md", "gate": gate, "p4_manifest_commit": man["commit"], "code_sha256": code_hashes(),
           "primary": res, "descriptive_mean_rho_init": float(np.mean([r[f"rho_init_{a}"] for r in rows for a in "FG"])) if rows else None,
           "dropped": dropped, "rows": rows}
    with open(OUT, "x", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1, ensure_ascii=False))


def selftest() -> None:
    """mask_spectrum: add 113 -> m0c_add; intadd -> EXP-048 mask_power (same values as a direct call); aggregate() is C1's
    (tested there); the pilot values of A_posthoc_within.py are reproduced for EXP-048 through mask_spectrum."""
    rng = np.random.default_rng(3)
    idx = np.sort(rng.choice(P * P, 3831, replace=False))
    assert np.array_equal(mask_spectrum("mlp", idx), m0c_add(idx, P)) and np.array_equal(mask_spectrum("d512", idx), m0c_add(idx, P))
    mi = mask_spectrum("intadd", idx)
    assert mi.shape == (56,) and np.all(np.isfinite(mi)) and np.array_equal(mi, _MS48.mask_power(idx))
    ref = json.loads((LAB / "confirm/A_posthoc_within.json").read_text(encoding="utf-8"))["EXP-048"]["raw"]["M0"]["mean_rho"]
    e48 = LAB / "experiments/EXP-048-intadd-steering"
    r = []
    for d in sorted((e48 / "raw").glob("EXP-048_*_eps2.0_*_devcuda")):
        stem = d.name.split("_", 2)[2].rsplit("_devcuda", 1)[0]
        T = json.loads((e48 / f"splits/{stem}.json").read_text(encoding="utf-8"))["targets"]
        sel = [k - 1 for k in T]
        sp, st = np.load(d / "spectra.npy"), list(np.load(d / "spectra_steps.npy"))
        r.append(rt.spearman(mask_spectrum("intadd", np.load(e48 / f"splits/{stem}.npy"))[sel], sp[st.index(2000)][sel]))
    assert len(r) == 20 and abs(np.mean(r) - ref) < 1e-3, (np.mean(r), ref)
    # Codex s28 (MINOR): also the detrended primary of the pilot (0.285), rebuilt as confirm_p4.spectra does it
    spec = importlib.util.spec_from_file_location("c3_a48", e48 / "analyze.py")
    a48 = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(e48))
    spec.loader.exec_module(a48)
    from intadd_train import dft_power
    ref_d = json.loads((LAB / "confirm/A_posthoc_within.json").read_text(encoding="utf-8"))["EXP-048"]["detrended"]["M0"]["mean_rho"]
    rd = []
    for d in sorted((e48 / "raw").glob("EXP-048_*_eps2.0_*_devcuda")):
        stem = d.name.split("_", 2)[2].rsplit("_devcuda", 1)[0]
        T = json.loads((e48 / f"splits/{stem}.json").read_text(encoding="utf-8"))["targets"]
        sel = [k - 1 for k in T]
        y = dft_power(a48.detrend(np.load(d / "we_final.npy").astype(np.float64)))
        rd.append(rt.spearman(mask_spectrum("intadd", np.load(e48 / f"splits/{stem}.npy"))[sel], y[sel]))
    assert len(rd) == 20 and abs(np.mean(rd) - ref_d) < 1e-3, (np.mean(rd), ref_d)
    print("C3 selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif len(sys.argv) == 2:
        analyze(Path(sys.argv[1]))
    else:
        raise SystemExit(__doc__)
