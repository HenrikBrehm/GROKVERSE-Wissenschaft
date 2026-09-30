"""EXP-133 (session 62, N61): fine-tune Pythia-160M on addition mod 113 exactly as EXP-127, but with the INPUT and OUTPUT
embedding rows of the number tokens 0..112 re-initialised at random before training (rest of the model pretrained).
Separates "the pretrained number rows are reused" from "the pretrained body imposes its features" (EXP-127 "bricht").

Wrapper around EXP-127's ft_pythia.py (imported unchanged); only ft.load_model is replaced:
  - after loading, the number rows of embed_in and embed_out keep their MEAN row (constant over the numbers, so it carries
    no Fourier power at k >= 1, but it holds the shared "is a number" component: pretrained number logits share an offset
    of ~835 at the answer position) and their deviations from it are replaced by Gaussian directions scaled (one common factor) to the
    mean norm of the pretrained deviations of that matrix. (First version replaced the whole rows: initial answer loss 840
    instead of 5.8, logit_scale_check.py; changed before any EXP-133 run.)
  - the random rows come from torch.Generator seeded with SeedSequence([133, seed, 5]) -> F and G of one seed start from
    the same reset rows (paired, like EXP-127), different seeds from different rows.
Snapshot 0 is taken after the reset, so the residual change U = E(T) - c E(0) is measured against the reset rows.
Run ids: ft_pythia's config does not know about the reset -> --out-root must lie inside this folder; a sidecar
reset_meta_<hash>.json records the reset (norms, wrapper hash).
Written in session 62 before any EXP-133 run; UNTESTED until --selftest-reset and a smoke run have passed.

  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-133-pythia-reset-numbers/ft_reset.py --selftest-reset
  python lab/tools/guarded_run.py -- .venv-gpu/Scripts/python.exe lab/experiments/EXP-133-pythia-reset-numbers/ft_reset.py \
      --seed S --split-file <F|G.npy> --test-file <test.npy> --targets-file <seedS.json> --steps N --out-root <dir>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
LAB = HERE.parents[1]
sys.path.insert(0, str(LAB / "experiments/EXP-127-pretrained-lm"))
import ft_pythia as ft  # noqa: E402

_orig_load = ft.load_model
META: dict = {}


def reset_rows(model, num: list[int], seed: int) -> dict:
    """Keep the mean number row, replace the deviations (in place, both embeddings); return norms for the sidecar."""
    g = torch.Generator().manual_seed(int(np.random.SeedSequence([133, seed, 5]).generate_state(1)[0]))
    idx = torch.tensor(num)
    info = {}
    with torch.no_grad():
        for side, E in (("in", model.get_input_embeddings().weight), ("out", model.get_output_embeddings().weight)):
            rows = E[idx.to(E.device)].float().cpu()
            mu = rows.mean(0, keepdim=True)
            dev = rows - mu
            target = float(dev.norm(dim=1).mean())
            R = torch.randn(rows.shape, generator=g)
            R = R - R.mean(0, keepdim=True)                 # keep the mean row exactly ...
            R = R * (target / float(R.norm(dim=1).mean()))  # ... so one common scale (row norms vary ~2-3 %)
            E[idx.to(E.device)] = (mu + R).to(E.device, E.dtype)
            info[side] = {"pretrained_mean_dev_norm": target, "pretrained_dev_norm_sd": float(dev.norm(dim=1).std()),
                          "mean_row_norm": float(mu.norm()), "pretrained_mean_row_norm": float(rows.norm(dim=1).mean())}
    return info


def make_loader(seed: int):
    def load_model_reset(device: str):
        tok, model = _orig_load(device)
        META["reset"] = reset_rows(model, ft.token_ids(tok)["num"], seed)
        return tok, model
    return load_model_reset


def selftest_reset() -> None:
    """Pretrained model on CPU: only the number rows change, mean row kept, deviation norms match, same seed -> same
    rows, other seed -> other."""
    tok, m1 = _orig_load("cpu")
    num = ft.token_ids(tok)["num"]
    E0_in = m1.get_input_embeddings().weight.detach().clone()
    E0_out = m1.get_output_embeddings().weight.detach().clone()
    assert E0_in.data_ptr() != E0_out.data_ptr()
    info = reset_rows(m1, num, 4000)
    Ei, Eo = m1.get_input_embeddings().weight.detach(), m1.get_output_embeddings().weight.detach()
    mask = torch.ones(Ei.shape[0], dtype=torch.bool)
    mask[num] = False
    assert torch.equal(Ei[mask], E0_in[mask]) and torch.equal(Eo[mask], E0_out[mask]), "non-number rows changed"
    for side, E, E0 in (("in", Ei, E0_in), ("out", Eo, E0_out)):
        assert torch.allclose(E[num].mean(0), E0[num].mean(0), atol=1e-4 * float(E0[num].mean(0).norm()) + 1e-6), side
        dv, dv0 = E[num] - E[num].mean(0), E0[num] - E0[num].mean(0)
        n, t = dv.norm(dim=1), info[side]["pretrained_mean_dev_norm"]
        assert abs(float(n.mean()) / t - 1) < 1e-3 and float((n / t - 1).abs().max()) < 0.15, side
        cos = torch.nn.functional.cosine_similarity(dv, dv0, dim=1).abs().max()
        assert float(cos) < 0.25, (side, float(cos))                      # random direction, not the old row
    _, m2 = _orig_load("cpu")
    reset_rows(m2, num, 4000)
    assert torch.equal(m2.get_input_embeddings().weight[num], Ei[num]), "same seed must give the same rows"
    _, m3 = _orig_load("cpu")
    reset_rows(m3, num, 4001)
    assert not torch.equal(m3.get_input_embeddings().weight[num], Ei[num]), "other seed must give other rows"
    pw = ft.power(Ei[num].numpy())
    top = float(np.sort(pw)[-5:].sum() / pw.sum())
    print(f"selftest-reset ok; info {info}; top-5 power share of reset input rows {top:.3f} (uniform 0.089)")


def main() -> None:
    args = sys.argv[1:]
    if "--selftest-reset" in args:
        torch.set_num_threads(2)
        selftest_reset()
        sys.stdout.flush()
        os._exit(0)
    if "--selftest" in args:
        raise SystemExit("use --selftest-reset (ft_pythia's --selftest does not know the reset)")
    if "--out-root" not in args or HERE.resolve() not in Path(args[args.index("--out-root") + 1]).resolve().parents:
        raise SystemExit("--out-root must lie inside lab/experiments/EXP-133-pythia-reset-numbers (run ids do not know the reset)")
    seed = int(args[args.index("--seed") + 1])
    ft.load_model = make_loader(seed)
    root = Path(args[args.index("--out-root") + 1])
    root.mkdir(parents=True, exist_ok=True)
    tag = hashlib.sha256(json.dumps(args).encode()).hexdigest()[:12]
    meta = {"intervention": "number rows of embed_in and embed_out: mean row kept, deviations re-initialised (Gaussian, mean pretrained deviation norm)",
            "wrapper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "ft_pythia_sha256": ft.sha(ft.__file__), "argv": args, "rng": [133, seed, 5]}
    side = root / f"reset_meta_{tag}.json"
    if not side.exists():                             # a relaunched finished run must not erase the recorded norms
        side.write_text(json.dumps(meta, indent=1), encoding="utf-8")
    _exit = os._exit

    def exit_with_meta(code: int) -> None:            # ft.main ends with os._exit(0): add the norms to the sidecar first
        if META:                                      # empty when ft skipped a completed run
            meta.update(META)
            side.write_text(json.dumps(meta, indent=1), encoding="utf-8")
        _exit(code)
    ft.os._exit = exit_with_meta
    sys.argv = [sys.argv[0]] + args
    ft.main()


if __name__ == "__main__":
    main()
