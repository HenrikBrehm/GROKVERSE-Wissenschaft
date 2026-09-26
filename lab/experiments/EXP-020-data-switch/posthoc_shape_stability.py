"""Post hoc (session 15, exploratory, seen seeds 30-34): is the whole W_E log-spectrum shape preserved over the G phase, or only pi?

For every EXP-020 switch run and the pure EXP-018 runs: Pearson r between the log power at global step 250 and at the final step (all 56
frequencies, centred), top-5 overlap between the two, and as reference the same r between the step-250 spectrum of the run and the final
spectrum of the pure G run (where would pure G training lead). Pure numpy on stored spectra; no training.
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
SEEDS, TS = range(30, 35), (10, 25, 50, 150)


def spec(run: Path) -> dict[int, np.ndarray]:
    return {int(a): np.log(b) for a, b in zip(np.load(run / "spectra_steps.npy"), np.load(run / "spectra.npy"))}


def top5(x: np.ndarray) -> set[int]:
    return set((np.argsort(-x)[:5] + 1).tolist())


def main() -> None:
    out = {}
    for s in SEEDS:
        pure = {a: spec(RAW / f"EXP-018_baseline_seed{s}_thr4_seed{s}_train_{a}") for a in "FG"}
        runs = {f"at{t}": spec(RAW / f"EXP-020_baseline_seed{s}_thr4_seed{s}_train_F_to_seed{s}_train_G_at{t}") for t in TS}
        runs.update({"onlyF": pure["F"], "onlyG": pure["G"]})
        for name, sp in runs.items():
            end = max(sp) if name.startswith("at") else 2000
            a, b = sp[250], sp[end]
            out[f"seed{s}_{name}"] = {"r_250_end": float(np.corrcoef(a, b)[0, 1]),
                                      "top5_overlap_250_end": len(top5(a) & top5(b)),
                                      "r_250_vs_onlyG_end": float(np.corrcoef(a, pure["G"][2000])[0, 1]),
                                      "r_end_vs_onlyG_end": float(np.corrcoef(b, pure["G"][2000])[0, 1])}
    (HERE / "posthoc_shape_stability.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    for name in ["onlyF", "onlyG"] + [f"at{t}" for t in TS]:
        v = [out[f"seed{s}_{name}"] for s in SEEDS]
        f = lambda k: f"{np.mean([x[k] for x in v]):.2f}[{min(x[k] for x in v):.2f},{max(x[k] for x in v):.2f}]"  # noqa: E731
        print(f"{name:6} r(250,end) {f('r_250_end')}  top5 kept {f('top5_overlap_250_end')}  "
              f"r(250,G_end) {f('r_250_vs_onlyG_end')} -> r(end,G_end) {f('r_end_vs_onlyG_end')}")


if __name__ == "__main__":
    main()
