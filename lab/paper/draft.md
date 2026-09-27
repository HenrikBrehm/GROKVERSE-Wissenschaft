---
id: paper-draft
status: entwurf
datum: 2026-09-27
tags: [lab/paper]
verwandt: ["[[paper/STATUS]]", "[[FINDINGS]]", "[[FINDINGS_DETAILS]]", "[[paper/related_work]]"]
---
# DRAFT — Training-set composition steers and locks in the Fourier features of grokking transformers

*Working draft (session 24, 2026-09-27). Not for circulation. All numbers are copied from the frozen confirmation blocks listed in [[FINDINGS_DETAILS]]; every result section names its registration.
Explorations are marked as such and are not results. Authorship, venue and submission are open decisions of the user ([[paper/STATUS]]).*

## Abstract (draft)

Networks that grok modular arithmetic implement it with a sparse set of Fourier features, and which frequencies a given network uses is usually treated as an arbitrary outcome of initialization.
We show that, with fixed one-hot tokens, the *composition of the training set* — which input pairs are shown — causally steers which frequencies (for the dihedral group D59: which irreducible
representations) the embedding of a one-layer transformer learns. In pre-registered, held-out replications with fresh seeds (50 per task), engineered training splits enrich five prescribed
frequencies in addition mod 113 and 97, multiplication mod 113, and composition in D59. Equal-norm embedding perturbations along the steered frequencies reduce the logit margin more than along control
frequencies. The choice is made early: 25 training steps on a first split measurably shape the embedding after 2000 further steps on a pair-disjoint second split, and whether the final network relies on
the old or the new frequencies flips between a switch after 25 and after 50 steps. Resetting the attention's value path at the switch removes this persistence far more than resetting the MLP or the
attention pattern. We report effect sizes with confidence intervals, the limits of each measurement (notably that functional sensitivity follows spectral energy), and negative results.

## 1 Introduction (outline)

- Grokking and Fourier circuits (Power et al. 2022; Nanda et al. 2023); which frequencies/irreps are learned is "arbitrary" per network (Chughtai et al. 2023) and has been linked to initialization
  (He et al. 2026) and, for uniform data, to the Fourier statistics of the input encoding (Marchetti et al. 2026, AGF).
- Gap (to be confirmed by the human literature review, [[paper/related_work]]): with one-hot tokens, the encoding prefers no frequency; we ask whether the *training pairs* break the tie, and when the
  choice becomes fixed.
- Contributions: (i) causal steering via split construction, held-out across four tasks incl. a non-abelian group; (ii) a functional sensitivity measure and its limits; (iii) an early, time-dependent
  lock-in under a data switch; (iv) reset interventions that localize *sensitivity* (not storage) in the attention value path.

## 2 Setup

- Model: the one-layer transformer of the original GROKVERSE study (preset arch25k, d_model 128, 4 heads, MLP 512), full-batch AdamW (lr 1e-3, wd 1.0, β as in the study), train fraction 0.3,
  inputs (a, b, =). Tasks: add mod 113 / 97, mul mod 113 (frequencies over the discrete-log order, Z_112), D59 (group order 118, irreps from an explicit real basis).
- Engineered splits: pairs are sampled with weights 1 + ε·wave, where the wave carries five target frequencies with random phases per output; F and G splits of a seed use disjoint target sets.
  Separate random streams (SeedSequence over experiment, task, seed, arm, purpose).
- Protocol: every confirmation was registered before its runs, analysis code and manifest frozen by commit hash, a smoke job run through the frozen loader, fresh seeds from a reserved block, Holm
  within a family, bootstrap CIs over seeds. Runs are bound to the manifest by content hashes.

## 3 Results (confirmed)

### 3.1 Split composition steers the learned frequencies (K2; registration P1, manifest 733e829)

At step 2000, the relative W_E energy of the five prescribed targets vs five disjoint comparison components (Δ_pow) was:

| Task | Δ_pow (95 % CI) | positive | Holm-p (worst case) |
|---|---|---|---|
| add 113 (primary) | 8.24 [7.92, 8.54] | 50/50 | 1.5·10⁻⁵ |
| mul 113 | 8.09 [7.75, 8.43] | 50/50 | 1.5·10⁻⁵ |
| add 97 | 6.11 [5.79, 6.43] | 50/50 | 1.5·10⁻⁵ |
| D59 | 2.64 [2.55, 2.73] | 50/50 | 1.5·10⁻⁵ |

Limits: engineered (not natural) splits; one architecture family; one time point (step 2000, before grokking for D59 — see 3.6). Δ_pow is relative enrichment, not concentration vs initialization.

### 3.2 Functional sensitivity along the steered frequencies (K2-function; P2d c0cd65f, P2e 3c484ef)

A one-sided W_E step of norm 0.02·‖W_E‖ along the steered frequencies reduced the mean correct-class logit margin on pairs outside both splits more than the mean of four pre-specified control sets:
add 113 (4000 steps) 0.250 [0.229, 0.270], 20/20 seeds; mul 113 (8000 steps) 0.291 [0.268, 0.308]; add 97 0.294 [0.275, 0.312], each 20/20 (Holm over the two tasks).
**Limit:** in all models examined, sensitivity follows the energy distribution in W_E; at equal removed energy the dominant set has no advantage (exploration EXP-068). We therefore do not claim use
beyond energy. The earlier registered variant P2c (loss after removing half the control energy) was *not* confirmed (sign reversed); we report it.

### 3.3 Early lock-in under a data switch (K4, K4b; P3 f8adf45, N28 fa154bd)

After 25 steps on a first engineered split and 2000 steps on a pair-disjoint second split, final models sat at 0.351 of the normalized log-energy distance between the two pure endpoints; the excess over
any tested static additive W_E trace was 0.293 [0.263, 0.322] (30 fresh seeds, 30/30). Zeroing Adam's first moment at the switch lowered the persistence index π by 0.151 (0.340 → 0.189); ten extra
pre-switch steps with the same reset compensated this (non-inferiority, margin 0.05). This is compatible with an "exposure" reading, not a proof of it.

### 3.4 The reliance flips between a switch at 25 and at 50 steps (K4c; N29 087e042)

Removing all five target frequencies from W_E after a switch and 4000 further steps: after a switch at t = 50, removing the **old** targets cost 0.903 more test accuracy than removing the new ones
(95 % CI 0.846–0.953; 20/20 seeds > 0.3); after a switch at t = 25, removing the **new** targets cost 0.603 more (0.498–0.700; 17/20 > 0.3). Two time points bracket a reversal of this ablation contrast;
a network-wide or irreversible functional commitment is not shown.

### 3.5 Reset sensitivity is concentrated in the attention value path (K4d N29b db31564, K4e N29c 3c9cb63)

At a switch after 50 steps, resetting W_Q, W_K, W_V, W_O to initialization together with their AdamW state lowered the ablation contrast by 1.49 [1.36, 1.61] vs no reset and by 1.42 [1.28, 1.56] vs the
tested MLP reset (20 paired seeds, Holm-p 4.7·10⁻¹²). Resetting only W_V, W_O lowered it by 0.850 [0.685, 0.998] vs no reset and by 0.752 [0.596, 0.897] vs an equal-size reset of W_Q, W_K
(Holm-p 2.1·10⁻⁴ and 1.9·10⁻⁵). These show *reset sensitivity*, not a storage location: weights and optimizer state were reset together, and the interventions are matched only in parameter count.

### 3.6 Pending: D59 function (P2f, registered) and generalization of the lock-in

D59 models generalize only after ≈ 4600 steps (pilot EXP-072, 9/10 runs by 20 000 steps), so K2 for D59 (3.1) concerns the pre-grokking choice. In the pilot the steered irreps carry 0.90–0.99 of the
embedding energy after grokking (exploration). Confirmation P2f (20 fresh seeds, 12 000 steps) is registered; results will replace this paragraph.

## 4 Explorations and negative results (not claims)

- Lock-in is smooth in the number of pre-switch steps (π ≈ 0.01, 0.19, 0.30, 0.56, 1.05 at t = 10, 20, 25, 35, 50; pilot, 10 known seeds); neither the W_E lead nor OV alignment at the switch predicts
  it better than the step count (EXP-060, EXP-070, EXP-071).
- The mask spectrum M0 predicts the learned frequencies (EXP-015) and equals, to first order, the power of the first W_E gradient ([[BEFUND-split-mechanismus]]); it is *not* the first-stage utility of
  the simplest AGF model (EXP-076, negative).
- Further pilots: steering also in a shared-embedding MLP, at 4× width and for non-modular integer addition (EXP-045, 049, 048) — to be confirmed or reported as pilots (rule 19b).

## 5 Theory (first order, outline)

Under near-uniform initial outputs, the first gradient on embedding row t is a sum over the training pairs containing t, mapped through the initial Jacobian; its Fourier power at k is the coherent
mask spectrum M0c for the transformer (shared path for both positions) and M0 for the MLP (independent halves). Token-frequency (marginal) contributions cancel exactly, predicting that frequency-matched
controls do not steer (consistent with pilot EXP-047, not a confirmation). Derivation and its limits: [[BEFUND-split-mechanismus]].

## 6 Limitations

One architecture family and optimizer for all persistence claims (add 113 only, generalization pending: EXP-074, EXP-075); engineered splits; functional measures do not separate identity from energy;
resets localize sensitivity, not mechanism; many design decisions were informed by pilots on known seeds (each registration lists them).

## AI use disclosure (draft wording, to be confirmed by the user)

Experiment planning, code, analyses and text of this work were produced to a substantial degree by AI agents (Anthropic Claude as the lab agent; OpenAI Codex as an independent reviewer of designs and
code), operating under written rules set by the human author, who bears responsibility for the content. All numerical results come from logged runs bound to frozen manifests; no number was written by hand.

## Figures (to be produced by scripts under `lab/paper/figures/`, none yet)

1. **done:** `figures/fig1_mask_vs_learned.py` — mask spectrum M0 vs learned W_E power at step 2000 for EXP-016 seed 10 F (pilot data). Caption must say: four of five targets dominate;
   target 25 is replaced by 32 = 2·16 (a harmonic of a target, as seen throughout EXP-016).
2. Δ_pow per task with CIs (P1 summary) — **done:** `figures/fig2_p1_delta_pow.py` → `fig2_p1_delta_pow.png/.svg` (reads `lab/confirm/P1_summary.json`).
3. **done:** `figures/fig3_ablation_contrast.py` — ablation contrast R per seed for N29 (switch at 25 vs 50) and N29b/N29c (switch at 50, reset arms); blocks use different seeds.
4. π(t) pilot curve (EXP-059, clearly marked as pilot) — open.
