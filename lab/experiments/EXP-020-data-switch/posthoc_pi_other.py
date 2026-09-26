"""Post hoc (session 14, exploratory): the persistence measure pi of posthoc_beta_persistence.py for the stored EXP-035 (warmup)
and EXP-037 (alternation) runs, so the numbers in their READMEs are reproducible. Normalisation per seed with the pure EXP-018
runs at step 2000 (F with warmup where it exists, EXP-035 seed 30; otherwise F without warmup). Pure numpy, no training.
"""
import json
from pathlib import Path

from posthoc_beta_persistence import D

HERE = Path(__file__).resolve().parent
E35, E37 = HERE.parent / "EXP-035-warmup-lockin", HERE.parent / "EXP-037-alternation-conflict"


def main() -> None:
    base = json.loads((HERE / "posthoc_beta_persistence.json").read_text(encoding="utf-8"))
    out: dict = {"EXP-035": {}, "EXP-037": {}}
    for s in (30, 31):
        fw = E35 / "raw" / f"EXP-018_baseline_seed{s}_thr4_seed{s}_train_F_wu200"
        dF = D(fw, s, 2000) if fw.exists() else base["D_onlyF"][str(s)]
        dG = base["D_onlyG"][str(s)]
        for t in (10, 25, 50, 100, 150, 250):
            r = E35 / "raw" / f"EXP-020_baseline_seed{s}_thr4_seed{s}_train_F_to_seed{s}_train_G_at{t}_wu200"
            if r.exists():
                out["EXP-035"][f"seed{s}_t{t}"] = {"pi": (D(r, s, None) - dG) / (dF - dG), "F_norm_with_warmup": fw.exists()}
    for s in (30, 31, 32):
        dF, dG = base["D_onlyF"][str(s)], base["D_onlyG"][str(s)]
        for arm in ("at100", "at200_alt25", "at200_alt5"):
            r = E37 / "raw" / f"EXP-020_baseline_seed{s}_thr4_seed{s}_train_F_to_seed{s}_train_G_{arm}"
            out["EXP-037"][f"seed{s}_{arm}"] = (D(r, s, None) - dG) / (dF - dG)
    (HERE / "posthoc_pi_other.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
