# THIRD_PARTY.md — dependencies, datasets, and adapted code

All third-party software, data, and any adapted reference code are listed here with their licenses. Exact pinned versions are recorded in `training/requirements.txt`; this file records the license and role of each.

## Datasets

- **None external.** The only dataset is a *synthetically generated* modular-arithmetic table (`(a + b) mod p`), produced deterministically in `training/grokverse/data.py`. No third-party data is used.

## Python dependencies (training/)

| Package | Version | Role | License |
|---|---|---|---|
| PyTorch (`torch`) | 2.12.1+cpu | model definition, training, autograd | BSD-3-Clause |
| NumPy | 2.4.6 | numerics, Fourier/PCA analysis | BSD-3-Clause |
| matplotlib | 3.11.0 | publication figures | Matplotlib License (BSD-style, PSF-based) |

(Exact versions pinned in `training/requirements.txt`.)

## Adapted reference code

- **Method/recipe** for the grokking reproduction follows **Nanda et al. 2023** (arXiv:2301.05217) and **Power et al. 2022** (arXiv:2201.02177). Any code adapted from their public repositories will be attributed here with the specific file and commit; as of Phase 0, the implementation is written from the papers' descriptions rather than copied.

- **Grokfast** — **Lee, Kang, Kim & Lee 2024**, *Grokfast: Accelerated Grokking by Amplifying Slow Gradients* (arXiv:2405.20233). `training/grokverse/train.py::apply_grokfast` implements the paper's EMA gradient filter (Algorithm 2, lines 7–8; the official `gradfilter_ema` initialisation μ₁ = g₁) with the README defaults `alpha = 0.98`, `lambda = 2.0`. Written from the paper's description; no code copied from the official repository. Used only for the accelerated corroboration runs, never for the un-accelerated reference results (`RESULTS.md`).

_Last updated: 2026-09-20 (Grokfast attribution added; see `docs/sources/power2022_and_grokfast2024.md` item 9)._
