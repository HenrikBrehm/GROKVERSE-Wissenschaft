"""Post hoc (session 15, exploratory): where does the top-5 crossover d(t) = |K ∩ F| - |K ∩ G| fall under a PURE CLOCK?

Model (integration window, posthoc_window_model.py): each of the first T* = 69 steps adds the first-order pull of its split; the final
W_E log-spectrum is a monotone function of the accumulated pull, so K = top-5 of u(t) = t * m_F + (T* - t) * m_G. Two variants for the
pull m: centred M0 ("lin") and log M0 ("log"). The clock (T*) does not depend on G. Question: does this pure clock already predict a later
crossover for a more concentrated G (EXP-042 eps 8) and an earlier one for eps 1? Pure numpy on split files; no training.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "EXP-043-generalize-steering"))
from make_split import mask_power  # noqa: E402

T_STAR = 69
E42 = HERE.parent / "EXP-042-bias-strength"
SEEDS = (30, 31, 32, 34)


def split_dir(eps: int) -> Path:
    return HERE / "splits" if eps == 2 else E42 / f"eps{eps}" / "splits"


def targets(eps: int, s: int) -> dict[str, set[int]]:
    meta = json.loads((split_dir(eps) / f"seed{s}.json").read_text(encoding="utf-8"))
    return {a: set(int(k) for k in meta["targets"][a]) for a in "FG"}


def crossover(mF: np.ndarray, mG: np.ndarray, tg: dict[str, set[int]]) -> tuple[int | None, dict[int, int]]:
    ds = {}
    for t in range(0, T_STAR + 1):
        u = t * mF + (T_STAR - t) * mG
        K = set((np.argsort(-u)[:5] + 1).tolist())
        ds[t] = len(K & tg["F"]) - len(K & tg["G"])
    first = next((t for t in range(T_STAR + 1) if ds[t] > 0), None)
    return first, ds


def main() -> None:
    out: dict = {}
    for eps in (2, 8, 1):
        for s in SEEDS:
            tgF = targets(2, s)["F"]
            tg = {"F": tgF, "G": targets(eps, s)["G"]}
            M = {a: mask_power(np.load(split_dir(2 if a == "F" else eps) / f"seed{s}_train_{a}.npy"), "add", 113) for a in "FG"}
            row = {}
            for var in ("lin", "log"):
                f = (lambda x: x - x.mean()) if var == "lin" else (lambda x: np.log(x) - np.log(x).mean())
                first, ds = crossover(f(M["F"]), f(M["G"]), tg)
                row[var] = {"first_t_d_pos": first, "d_at": {t: ds[t] for t in (10, 25, 50) if t in ds}}
            share = {a: float(sum(M[a][k - 1] for k in tg[a]) / M[a].sum()) for a in "FG"}
            row["target_share"] = share
            out.setdefault(f"eps{eps}", {})[str(s)] = row
            print(f"eps{eps} seed{s} share F {share['F']:.3f} G {share['G']:.3f} | crossover lin {row['lin']['first_t_d_pos']}"
                  f" log {row['log']['first_t_d_pos']} | d(10,25,50) lin {list(row['lin']['d_at'].values())}"
                  f" log {list(row['log']['d_at'].values())}")
    (HERE / "posthoc_clock_crossover.json").write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
