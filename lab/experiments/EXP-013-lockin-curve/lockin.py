"""EXP-013: dense lock-in curve of the frequency choice over the first 300 steps (exploratory).

Mirrors the training loop of freq_ban.py / grokverse.train (arch25k, full-batch AdamW), no intervention.
Run only through lab/tools/guarded_run.py. Definition: README.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
ROOT = LAB.parent
sys.path.insert(0, str(ROOT / "training"))
sys.path.insert(0, str(LAB / "experiments/EXP-012-init-gradient"))
sys.path.insert(0, str(LAB / "experiments/EXP-001-freq-ban"))

import freq_ban as fb  # noqa: E402
import predict as p12  # noqa: E402
from grokverse.config import get_config  # noqa: E402
from grokverse.data import make_dataset  # noqa: E402
from grokverse.models import build_model  # noqa: E402
from grokverse.seed import set_seed  # noqa: E402

STEPS = (0, 1, 2, 3, 5, 10, 15, 25, 50, 75, 100, 150, 200, 250, 300)
M = 5


def overlap(power: np.ndarray, K: list[int]) -> int:
    return len(set(fb.top_frequencies(power, M)) & set(K))


def curve(seed: int, K: list[int]) -> dict:
    cfg = get_config("arch25k", seed=seed, threads=4)
    torch.set_num_threads(cfg.threads)
    set_seed(cfg.seed)
    data = make_dataset(cfg)
    model = build_model(cfg)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay,
                            betas=(cfg.beta1, cfg.beta2))
    p, basis = cfg.p, fb.fourier_basis(cfg.p)
    trx, try_ = data["train_x"], data["train_y"]
    stored = ROOT / f"training/runs/txf_add_p113_wd1.0_frac0.3_seed{seed}_arch25k/ckpt_step000000.pt"
    check = None
    if stored.exists():
        ck = torch.load(stored, map_location="cpu", weights_only=True)
        check = all(torch.equal(ck[n], getattr(model, n).detach()) for n in ck)
    rows, e250 = [], None
    for step in range(0, max(STEPS) + 1):
        model.train()
        loss = F.cross_entropy(model.logits_last(trx)[:, :p], try_)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        if step in STEPS:           # W_E after `step` optimizer steps; gradient at that point
            pe = fb.freq_power(model.W_E.detach().numpy().astype(np.float64)[:p], basis)
            pg = fb.freq_power(model.W_E.grad.numpy().astype(np.float64)[:p], basis)
            rows.append({"t": step, "rbar_E": p12.rbar(pe, K), "rbar_G": p12.rbar(pg, K),
                         "ov_E": overlap(pe, K), "ov_G": overlap(pg, K)})
            if step == 250:
                e250 = pe
        if step < max(STEPS):
            opt.step()
    return {"seed": seed, "K": K, "init_matches_stored": check, "rows": rows,
            "power_E250": e250.tolist()}


def main() -> None:
    k009 = {}
    for r in json.loads(p12.EXP009.read_text(encoding="utf-8"))["runs"]:
        if r["run"].startswith("txf_add_p113_wd1.0_frac0.3_seed"):
            k009[int(r["run"].split("seed")[1].split("_")[0])] = r["k_final"]
    out = []
    for s in range(0, 10):
        out.append(curve(s, k009[s]))
        print(s, out[-1]["init_matches_stored"], [(r["t"], r["ov_E"], r["ov_G"]) for r in out[-1]["rows"]],
              flush=True)
    d10 = Path(str(p12.BASE_D).format(s=10))
    res10 = json.loads((d10 / "result.json").read_text(encoding="utf-8"))
    c10 = curve(10, res10["final_top_m_freqs"])
    spec, steps = np.load(d10 / "spectra.npy"), np.load(d10 / "spectra_steps.npy").tolist()
    c10["matches_exp003d_at_250"] = bool(np.allclose(spec[steps.index(250)], c10["power_E250"], rtol=1e-4))
    out.append(c10)
    summary = {"curves": out, "mean": {
        t: {k: float(np.mean([c["rows"][i][k] for c in out[:10]])) for k in ("rbar_E", "rbar_G", "ov_E", "ov_G")}
        for i, t in enumerate(STEPS)}}
    (HERE / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print("seed10 matches EXP-003d spectrum at 250:", c10["matches_exp003d_at_250"])
    for t, v in summary["mean"].items():
        print(t, {k: round(x, 3) for k, x in v.items()})


if __name__ == "__main__":
    main()
