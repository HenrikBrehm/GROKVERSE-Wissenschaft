"""Post hoc (session 14, exploratory, already analysed seeds 30-34): a continuous persistence measure for the data switch.

beta_X = slope of log W_E power on log M0 of split X (k = 1..56), at the end of each run (t + 2000 steps after a switch F -> G at
step t; step 2000 for the pure runs). D = beta_F - beta_G. Normalised persistence pi(t) = (D(t) - D_onlyG) / (D_onlyF - D_onlyG):
0 = like a pure G run, 1 = like a pure F run. Pure numpy on stored spectra and split files; no training.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-043-generalize-steering"))
from make_split import mask_power  # noqa: E402

SEEDS, TS = range(30, 35), (10, 25, 50, 150, 400, 1000)


def beta(m0: np.ndarray, pw: np.ndarray) -> float:
    return float(np.polyfit(np.log(m0), np.log(pw), 1)[0])


def D(run: Path, s: int, step: int | None) -> float:
    st = list(np.load(run / "spectra_steps.npy"))
    pw = np.load(run / "spectra.npy")[-1 if step is None else st.index(step)]
    m = {a: mask_power(np.load(HERE / f"splits/seed{s}_train_{a}.npy"), "add", 113) for a in "FG"}
    return beta(m["F"], pw) - beta(m["G"], pw)


def main() -> None:
    raw = HERE / "raw"
    pure = {a: {s: D(raw / f"EXP-018_baseline_seed{s}_thr4_seed{s}_train_{a}", s, 2000) for s in SEEDS} for a in "FG"}
    out = {"D_onlyF": pure["F"], "D_onlyG": pure["G"], "switch": {}}
    for t in TS:
        d = {s: D(raw / f"EXP-020_baseline_seed{s}_thr4_seed{s}_train_F_to_seed{s}_train_G_at{t}", s, None) for s in SEEDS}
        pi = {s: (d[s] - pure["G"][s]) / (pure["F"][s] - pure["G"][s]) for s in SEEDS}   # per seed normalisation
        out["switch"][t] = {"D": d, "pi": pi, "pi_mean": float(np.mean(list(pi.values()))),
                            "pi_min": float(min(pi.values())), "pi_max": float(max(pi.values()))}
        print(t, f"pi mean {out['switch'][t]['pi_mean']:.2f} [{out['switch'][t]['pi_min']:.2f}, {out['switch'][t]['pi_max']:.2f}]")
    (HERE / "posthoc_beta_persistence.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
