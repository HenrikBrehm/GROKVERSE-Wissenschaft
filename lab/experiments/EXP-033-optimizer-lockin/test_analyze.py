"""Synthetic checks of EXP-033 analyze.py: verdict branches, overshoot gate, missing GD run. Run via guarded_run.py."""
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as A  # noqa: E402

T = [16, 20, 25, 47, 49]
LR = 3.0


def spec(ds_target: float) -> list[float]:
    """Spectrum with share(F) - share(H) = ds_target (H = folded 57k, other mass uniform)."""
    H = {A.fold(57 * t) for t in T}
    s = [0.0] * 56
    rest = [k for k in range(1, 57) if k not in set(T) | H]
    base = 0.5
    for k in T:
        s[k - 1] = (base + ds_target) / 5
    for k in H:
        s[k - 1] = base / 5
    for k in rest:
        s[k - 1] = (1 - 2 * base - ds_target) / len(rest)
    return s


def write(p: Path, r: dict) -> None:
    p.mkdir(parents=True, exist_ok=True)
    (p / "result.json").write_text(json.dumps(r))


def sigma_run(s, ts, alpha, ds):
    return {"complete": True, "targets": T, "final_test_acc": 1.0,
            "args": {"steps": 5000, "alpha": alpha, "switch_step": ts, "alpha_after": 0.0, "seed": s, "arm": "F",
                     "width": 512, "init_seed": None}, "spectra": {"5000": {"weighted": spec(ds)}}}


def opt_run(ds, r_switch, reached=True, test=1.0):
    return {"complete": reached, "reached": reached, "targets": T, "final_test_acc": test, "r_switch": r_switch,
            "wout_norm_switch": 0.1, "r_quantiles_switch": [0.01] * 5, "gen_step_test95": 1000, "phase1_steps": 10,
            "spectra": {"p2_5000": {"weighted": spec(ds)}, "switch": {"weighted": spec(ds / 3)}}}


def build(tmp: Path, ds_ar: float, ds_gd: float, overshoot: float = 0.0, drop_gd=None) -> None:
    lab = tmp / "lab"
    here = lab / "EXP-033-optimizer-lockin"
    (here).mkdir(parents=True)
    (here / "lr.json").write_text(json.dumps({"lr": LR}))
    for s in A.SEEDS:
        rt = 0.0167 + s * 1e-5
        if s < 15:
            write(lab / "EXP-026-parity-crossover" / "raw" / f"EXP-026_a3_sw0to0_seed{s}_F", sigma_run(s, 0, 3.0, 0.0))
        else:
            write(lab / "EXP-027-width-selection" / "raw_b" / f"EXP-026_a0_seed{s}_F", sigma_run(s, -1, 0.0, 0.0))
        write(here / "raw" / f"EXP-033_adamw_t10_seed{s}", opt_run(ds_ar, rt))
        if drop_gd != s:
            write(here / "raw" / f"EXP-033_gd_r{rt:g}_lr{LR:g}_seed{s}_bt", opt_run(ds_gd, rt * (1 + overshoot)))
        write(here / "raw" / f"EXP-033_sign_r{rt:g}_seed{s}_bt", opt_run(ds_ar, rt))
    A.HERE, A.LAB = here, lab


def verdict(**kw) -> str:
    with tempfile.TemporaryDirectory() as d:
        build(Path(d), **kw)
        with contextlib.redirect_stdout(io.StringIO()):
            A.main()
        return json.loads((A.HERE / "summary.json").read_text())["verdict"]


def main() -> None:
    assert abs(A.share_diff(spec(0.1), set(T), {A.fold(57 * t) for t in T}) - 0.1) < 1e-9
    cases = [
        (dict(ds_ar=0.12, ds_gd=0.12), "zustandsbestimmt"),
        (dict(ds_ar=0.12, ds_gd=0.0), "AdamW-gebunden"),       # d_gd = 0 everywhere: k = 0, ratio 0
        (dict(ds_ar=0.02, ds_gd=0.12), "GD stärker"),
        (dict(ds_ar=0.12, ds_gd=0.03), "AdamW verstärkt, Festlegung schwach vorhanden"),
        (dict(ds_ar=0.0, ds_gd=0.12), "nicht auswertbar (Kontrolle AdamW-reset repliziert die Festlegung nicht)"),
        (dict(ds_ar=0.12, ds_gd=0.12, overshoot=0.05), "nicht auswertbar"),
        (dict(ds_ar=0.12, ds_gd=0.12, drop_gd=13), "nicht auswertbar"),
    ]
    for kw, want in cases:
        got = verdict(**kw)
        assert got == want, (kw, got, want)
        print("ok", kw, "->", got)
    print("all ok")


if __name__ == "__main__":
    main()
