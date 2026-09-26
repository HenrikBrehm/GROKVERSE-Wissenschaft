"""EXP-023: transformer variant in which position 1 (operand b) has its OWN attention value matrix W_V1.

Lab-local (the study code in training/ is not modified). `convert(model, seed, variant)` turns an already initialised
OneLayerTransformer into this variant IN PLACE; all existing parameters keep their values (bitwise identical init to the
baseline of the same seed):
  variant "rand": W_V1 drawn from a SEPARATE torch.Generator (seed + SALT), same distribution as W_V
                  (changes the initial function: breaks the left/right interference of the first gradient)
  variant "copy": W_V1 = copy of W_V (same initial function and first gradient as the baseline, untied afterwards)
Positions 0 and 2 keep using W_V. Saved models must be reloaded with `load_variant` (Codex review 2026-09-26): the
recorded Config builds a plain OneLayerTransformer, and loading W_V1 into it without the override would be wrong.
"""
from __future__ import annotations

import hashlib
import math

import numpy as np
import torch
import torch.nn as nn

SALT = 70_001
VARIANTS = ("rand", "copy")


def _forward(self, tokens: torch.Tensor) -> torch.Tensor:
    cfg = self.cfg
    T = tokens.shape[1]
    x = self.W_E[tokens] + self.W_pos[None, :T, :]
    q = torch.einsum("btd,hde->bhte", x, self.W_Q)
    k = torch.einsum("btd,hde->bhte", x, self.W_K)
    v = torch.einsum("btd,hde->bhte", x, self.W_V)
    v1 = torch.einsum("bd,hde->bhe", x[:, 1], self.W_V1)
    v = torch.cat([v[:, :, :1], v1[:, :, None], v[:, :, 2:]], dim=2)
    scores = torch.einsum("bhte,bhse->bhts", q, k) / math.sqrt(cfg.d_head)
    mask = torch.triu(torch.ones(T, T, dtype=torch.bool, device=x.device), diagonal=1)
    attn = scores.masked_fill(mask, float("-inf")).softmax(dim=-1)
    z = torch.einsum("bhts,bhse->bhte", attn, v)
    x = x + torch.einsum("bhte,hed->btd", z, self.W_O)
    hmlp = torch.relu(torch.einsum("btd,df->btf", x, self.W_in))
    x = x + torch.einsum("btf,fd->btd", hmlp, self.W_out)
    return torch.einsum("btd,dv->btv", x, self.W_U)


def shared_checksum(model: nn.Module) -> str:
    """SHA-256 over all parameters except W_V1 (name-sorted), to prove the init equals the baseline's."""
    h = hashlib.sha256()
    for name, prm in sorted(model.named_parameters()):
        if name != "W_V1":
            h.update(name.encode())
            h.update(np.ascontiguousarray(prm.detach().cpu().numpy()).tobytes())
    return h.hexdigest()


def convert(model: nn.Module, seed: int, variant: str = "rand") -> nn.Module:
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    if variant == "rand":
        g = torch.Generator().manual_seed(seed + SALT)
        std = model.cfg.init_scale / math.sqrt(model.cfg.d_model)   # as W_V in OneLayerTransformer._init_weights
        w = torch.randn(model.W_V.shape, generator=g) * std
    else:
        w = model.W_V.detach().clone()
    model.W_V1 = nn.Parameter(w.to(model.W_V.dtype))
    model.forward = _forward.__get__(model)              # bound override; logits_last calls self.forward
    model.split_value_variant = variant
    return model


def load_variant(cfg, state: dict, seed: int, variant: str) -> nn.Module:
    """Rebuild a saved split-value model: plain model + convert + strict state_dict load."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "training"))
    from grokverse.models import build_model
    model = convert(build_model(cfg), seed, variant)
    model.load_state_dict(state, strict=True)
    return model
