"""EXP-023: transformer variant in which position 1 (operand b) has its OWN attention value matrix W_V1.

Lab-local (the study code in training/ is not modified). `convert(model, seed)` turns an already initialised
OneLayerTransformer into this variant IN PLACE: all existing parameters keep their values (so the init is bitwise identical
to the baseline of the same seed), and W_V1 is drawn from a SEPARATE torch.Generator (seed + SALT) with the same
distribution as W_V. Positions 0 and 2 keep using W_V.
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn

SALT = 70_001


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


def convert(model: nn.Module, seed: int) -> nn.Module:
    g = torch.Generator().manual_seed(seed + SALT)
    d = model.cfg.d_model
    std = model.cfg.init_scale / math.sqrt(d)            # same as W_V in OneLayerTransformer._init_weights
    model.W_V1 = nn.Parameter(torch.randn(model.W_V.shape, generator=g) * std)
    model.forward = _forward.__get__(model)              # bound override; logits_last calls self.forward
    return model
