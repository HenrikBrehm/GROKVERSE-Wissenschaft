"""Session 49: readings pre-stated in JOURNAL (09:39) for the late L0 divergence; bitwise comparison at all spectrum steps."""
import json
from pathlib import Path

import numpy as np

runs = {"frozen": Path("lab/confirm/l0_raw/EXP-018_baseline_seed3728_thr1_l0_seed3728_F_bs64_devcuda"),
        "repro1": Path("lab/paper/repro/out/l0/add113_steps30000_cuda/runs/seed3728_F_bs64"),
        "rep1": Path("lab/paper/repro/out/l0_nondet/seed3728_F_bs64_rep1"),
        "rep2": Path("lab/paper/repro/out/l0_nondet/seed3728_F_bs64_rep2")}
sp = {k: (np.load(d / "spectra.npy"), np.load(d / "spectra_steps.npy").tolist()) for k, d in runs.items()}
common = sorted(set.intersection(*(set(v[1]) for v in sp.values())))


def first_diff(a: str, b: str):
    (sa, ta), (sb, tb) = sp[a], sp[b]
    return next((t for t in common if not np.array_equal(sa[ta.index(t)], sb[tb.index(t)])), None)


pairs = {f"{a}~{b}": first_diff(a, b) for a, b in [("repro1", "rep1"), ("repro1", "rep2"), ("rep1", "rep2"),
                                                    ("frozen", "rep1"), ("frozen", "rep2"), ("frozen", "repro1")]}
same = lambda a, b: pairs.get(f"{a}~{b}", pairs.get(f"{b}~{a}")) is None   # noqa: E731
if same("rep1", "rep2") and same("repro1", "rep1") and not same("frozen", "repro1"):
    reading = "(a) deterministische Abweichung train.py gegen freq_ban.py"
elif not (same("rep1", "rep2") and same("repro1", "rep1")):
    reading = "(b) nicht-deterministische GPU-Rechnung belegt"
else:
    reading = "sonst"
out = {"common_steps": [common[0], common[-1], len(common)], "first_diff_step": pairs, "reading": reading}
print(json.dumps(out, indent=1, ensure_ascii=False))
Path("lab/paper/repro/nondet_l0_s49.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
