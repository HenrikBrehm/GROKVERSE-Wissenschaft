"""Two-layer version of the study's transformer (EXP-078, session 26, UNTESTED).

Same recipe as training/grokverse/models/transformer.py (no LayerNorm, ReLU MLP, causal attention, prediction at the '=' position,
same init scales), with TWO attention+MLP blocks. Layer-1 weights keep the one-layer names (W_Q, W_K, W_V, W_O, W_in, W_out) so that
W_E, W_U and layer 1 are initialised in the same order and with the same shapes as in the one-layer model; layer-2 weights carry a
suffix 2 and are initialised after all one-layer parameters. Lab-owned: the study's model code is not changed.
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn

BLOCK = ("W_Q", "W_K", "W_V", "W_O", "W_in", "W_out")


class TwoLayerTransformer(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        assert cfg.n_heads * cfg.d_head == cfg.d_model, "n_heads * d_head must equal d_model"
        self.cfg = cfg
        d, v, h, dh = cfg.d_model, cfg.vocab_size, cfg.n_heads, cfg.d_head
        self.W_E = nn.Parameter(torch.empty(v, d))
        self.W_pos = nn.Parameter(torch.empty(cfg.n_ctx, d))
        for sfx in ("", "2"):
            setattr(self, f"W_Q{sfx}", nn.Parameter(torch.empty(h, d, dh)))
            setattr(self, f"W_K{sfx}", nn.Parameter(torch.empty(h, d, dh)))
            setattr(self, f"W_V{sfx}", nn.Parameter(torch.empty(h, d, dh)))
            setattr(self, f"W_O{sfx}", nn.Parameter(torch.empty(h, dh, d)))
            setattr(self, f"W_in{sfx}", nn.Parameter(torch.empty(d, cfg.d_mlp)))
            setattr(self, f"W_out{sfx}", nn.Parameter(torch.empty(cfg.d_mlp, d)))
            if sfx == "":
                self.W_U = nn.Parameter(torch.empty(d, v))
        self._init_weights()

    def _init_block(self, sfx: str) -> None:
        s, d, dh, h = self.cfg.init_scale, self.cfg.d_model, self.cfg.d_head, self.cfg.n_heads
        for nm in ("W_Q", "W_K", "W_V"):
            nn.init.normal_(getattr(self, nm + sfx), std=s / math.sqrt(d))
        nn.init.normal_(getattr(self, "W_O" + sfx), std=s / math.sqrt(dh * h))
        nn.init.normal_(getattr(self, "W_in" + sfx), std=s / math.sqrt(d))
        nn.init.normal_(getattr(self, "W_out" + sfx), std=s / math.sqrt(self.cfg.d_mlp))

    def _init_weights(self) -> None:
        s, d = self.cfg.init_scale, self.cfg.d_model
        nn.init.normal_(self.W_E, std=s / math.sqrt(d))                  # same order as the one-layer model ...
        nn.init.normal_(self.W_pos, std=s / math.sqrt(d))
        self._init_block("")
        nn.init.normal_(self.W_U, std=s / math.sqrt(d))                  # ... up to here
        self._init_block("2")                                            # then layer 2

    def _block(self, x: torch.Tensor, sfx: str) -> torch.Tensor:
        cfg, T = self.cfg, x.shape[1]
        q = torch.einsum("btd,hde->bhte", x, getattr(self, "W_Q" + sfx))
        k = torch.einsum("btd,hde->bhte", x, getattr(self, "W_K" + sfx))
        v = torch.einsum("btd,hde->bhte", x, getattr(self, "W_V" + sfx))
        scores = torch.einsum("bhte,bhse->bhts", q, k) / math.sqrt(cfg.d_head)
        mask = torch.triu(torch.ones(T, T, dtype=torch.bool, device=x.device), diagonal=1)
        attn = scores.masked_fill(mask, float("-inf")).softmax(dim=-1)
        x = x + torch.einsum("bhte,hed->btd", torch.einsum("bhts,bhse->bhte", attn, v), getattr(self, "W_O" + sfx))
        hmlp = torch.relu(torch.einsum("btd,df->btf", x, getattr(self, "W_in" + sfx)))
        return x + torch.einsum("btf,fd->btd", hmlp, getattr(self, "W_out" + sfx))

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        x = self.W_E[tokens] + self.W_pos[None, :tokens.shape[1], :]
        return torch.einsum("btd,dv->btv", self._block(self._block(x, ""), "2"), self.W_U)

    def logits_last(self, tokens: torch.Tensor) -> torch.Tensor:
        return self.forward(tokens)[:, -1, :]
