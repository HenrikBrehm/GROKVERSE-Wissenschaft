"""Post hoc (session 5, exploratory): are the EXP-016 'misses' (learned non-target frequencies) favoured by the init?
H (stated before computing): the missed frequencies have a mean normalized rank < 0.5 in the init W_E spectrum E0
and/or in the first gradient G0 computed on the engineered split. Init + one backward pass per run, no training.
Null: rank of a random non-target frequency (mean 0.5 over non-targets; MC over the same number of draws)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB.parent / "training"))
sys.path.insert(0, str(LAB / "experiments/EXP-001-freq-ban"))
import freq_ban as fb  # noqa: E402
from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402

rows = json.loads((HERE / "posthoc_m0c.json").read_text(encoding="utf-8"))


def spectra(seed: int, split_file: Path) -> tuple[np.ndarray, np.ndarray]:
    cfg = get_config("arch25k", seed=seed, threads=4)
    torch.set_num_threads(cfg.threads)
    set_seed(cfg.seed)                         # same order as freq_ban.run: seed, data, model
    data = make_dataset(cfg)
    model = build_model(cfg)
    tr = torch.from_numpy(np.load(split_file).astype(np.int64))
    p = cfg.p
    loss = F.cross_entropy(model.logits_last(data["all_x"][tr])[:, :p], data["all_y"][tr])
    loss.backward()
    basis = fb.fourier_basis(p)
    E0 = fb.freq_power(model.W_E.detach().numpy().astype(np.float64)[:p], basis)
    G0 = fb.freq_power(model.W_E.grad.numpy().astype(np.float64)[:p], basis)
    return E0, G0


def nonrank(power: np.ndarray, k: int, exclude: set[int]) -> float:
    """normalized rank of k among the non-target frequencies (0 = strongest)."""
    cand = [j for j in range(1, len(power) + 1) if j not in exclude]
    order = sorted(cand, key=lambda j: -power[j - 1])
    return order.index(k) / (len(cand) - 1)


out, rE, rG = [], [], []
for r in rows:
    suf = "" if r["arm"] == "F" else "_G"
    E0, G0 = spectra(r["seed"], HERE / f"splits/split_seed{r['seed']}_eps2.0{suf}.npy")
    tg = set(r["targets"])
    e = [nonrank(E0, k, tg) for k in r["missed"]]
    g = [nonrank(G0, k, tg) for k in r["missed"]]
    rE += e
    rG += g
    out.append({**{k: r[k] for k in ("seed", "arm", "missed")}, "E0_nonrank": e, "G0_nonrank": g})
rng = np.random.default_rng(0)
n = len(rE)
null = rng.random((200_000, n)).mean(axis=1)       # uniform ranks in [0, 1] as the null for a random non-target
summ = {"n_missed": n, "mean_E0_nonrank": float(np.mean(rE)), "mean_G0_nonrank": float(np.mean(rG)),
        "p_E0": float((null <= np.mean(rE)).mean()), "p_G0": float((null <= np.mean(rG)).mean()),
        "E0_top10_of_51": int(sum(x < 10 / 50 for x in rE)), "G0_top10_of_51": int(sum(x < 10 / 50 for x in rG))}
(HERE / "posthoc_init_misses.json").write_text(json.dumps({"summary": summ, "rows": out}, indent=1), encoding="utf-8")
for o in out:
    print(o)
print(json.dumps(summ, indent=1))
