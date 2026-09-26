"""Synthetic checks of EXP-034 analyze.py (verdict branches A5/A10/B, P34c). Run via guarded_run.py."""
import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze as A  # noqa: E402

T = [16, 20, 25, 47, 49]


def spec(ds: float) -> list[float]:
    H = {A.fold(57 * t) for t in T}
    rest = [k for k in range(1, 57) if k not in set(T) | H]
    s = [0.0] * 56
    for k in T:
        s[k - 1] = (0.5 + ds) / 5
    for k in H:
        s[k - 1] = 0.1
    for k in rest:
        s[k - 1] = (0.5 - ds) / len(rest)
    return s


def run(ds_end, ds_sw, r, end_key, test=1.0):
    return {"complete": True, "targets": T, "final_test_acc": test, "r_switch": r, "gen_step_test95": 2000,
            "spectra": {end_key: {"weighted": spec(ds_end)}, "switch": {"weighted": spec(ds_sw)}}}


def build(root: Path, d_ar5, d_gd5, d_ar10, d_gd10, d_b, lr2=3.0, drop=None):
    raw = root / "raw"
    for s in A.SEEDS:
        for suf, end, dd in (("", "p2_5000", None), ("" if lr2 is None else f"_p2gd{lr2:g}_n10000", "p2_10000", d_b)):
            if end == "p2_10000" and lr2 is None:
                continue
            vals = {0: 0.0, 5: d_ar5, 10: d_ar10} if not suf else {0: 0.0, 10: dd}
            for ts, v in vals.items():
                r = 0.01 + ts * 1e-3
                (raw / f"EXP-033_adamw_t{ts}_seed{s}{suf}").mkdir(parents=True, exist_ok=True)
                (raw / f"EXP-033_adamw_t{ts}_seed{s}{suf}" / "result.json").write_text(json.dumps(run(v, 0.05, r, end)))
                if ts == 0 or (drop == (s, ts, suf)):
                    continue
                g = {5: d_gd5, 10: d_gd10}[ts] if not suf else dd
                d = raw / f"EXP-033_gd_r{r:g}_lr3_seed{s}_bt{suf}"
                d.mkdir(parents=True, exist_ok=True)
                d.joinpath("result.json").write_text(json.dumps(run(g, 0.05 + (s - 60) * 0.01, r, end)))
    (root / "lr2.json").write_text(json.dumps({"lr2": lr2}))
    shutil.copy(HERE / "linear_modes.json", root / "linear_modes.json")
    A.HERE = root


def verdicts(**kw):
    with tempfile.TemporaryDirectory() as d:
        build(Path(d), **kw)
        with contextlib.redirect_stdout(io.StringIO()):
            A.main()
        res = json.loads((Path(d) / "summary.json").read_text())
    return res["A5"]["verdict"], res["A10"]["verdict"], res["B"]["verdict"], res.get("P34c", {}).get("verdict")


def main() -> None:
    cases = [
        (dict(d_ar5=.1, d_gd5=.1, d_ar10=.12, d_gd10=.15, d_b=.1),
         ("Festlegung bei 1.25 × Init ohne AdamW in Phase 1", "EXP-033 an frischen Splits bestätigt", "Erhalt ohne AdamW")),
        (dict(d_ar5=.1, d_gd5=-.01, d_ar10=.12, d_gd10=.15, d_b=0.0),
         ("bei der 5-Schritte-Stufe nicht ohne AdamW gezeigt", "EXP-033 an frischen Splits bestätigt",
          "Erhalt unter GD-Phase-2 deutlich schwächer (ar, gd)")),
        (dict(d_ar5=.1, d_gd5=.1, d_ar10=.12, d_gd10=.15, d_b=.1, lr2=None),
         ("Festlegung bei 1.25 × Init ohne AdamW in Phase 1", "EXP-033 an frischen Splits bestätigt",
          "nicht durchführbar (keine zulässige lr2)")),
        (dict(d_ar5=.1, d_gd5=.1, d_ar10=.12, d_gd10=.15, d_b=.1, drop=(63, 10, "_p2gd3_n10000")),
         ("Festlegung bei 1.25 × Init ohne AdamW in Phase 1", "EXP-033 an frischen Splits bestätigt",
          "nicht auswertbar (unvollständig oder ungültig)")),
        (dict(d_ar5=0.0, d_gd5=.1, d_ar10=.12, d_gd10=-.01, d_b=.1),
         ("nicht auswertbar (Tor: AR5 repliziert EXP-032/033 nicht)", "EXP-033 an frischen Splits nicht bestätigt",
          "nicht auswertbar (Tor: Stufe 10 mit AdamW-Phase-2 nicht repliziert)")),
    ]
    for kw, want in cases:
        got = verdicts(**kw)
        assert got[:3] == want, (kw, got)
        print("ok", got)
    print("all ok")


if __name__ == "__main__":
    main()
