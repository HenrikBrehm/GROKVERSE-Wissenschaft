---
id: paper-draft
status: entwurf
datum: 2026-09-27
tags: [lab/paper]
verwandt: ["[[paper/STATUS]]", "[[FINDINGS]]", "[[FINDINGS_DETAILS]]", "[[paper/related_work]]"]
---
# DRAFT — Training-set composition steers the Fourier features of grokking transformers, and a 25–50-step history persists under a data switch

*Working draft (session 24, 2026-09-27). Not for circulation. All numbers are copied from the frozen confirmation blocks listed in [[FINDINGS_DETAILS]]; every result section names its registration.
Explorations are marked as such and are not results. Authorship, venue and submission are open decisions of the user ([[paper/STATUS]]).*

## Abstract (draft)

Networks that grok modular arithmetic implement it with a sparse set of Fourier features, and which frequencies a given network uses is usually treated as an arbitrary outcome of initialization.
We show that, with fixed one-hot tokens, the *composition of the training set* — which input pairs are shown — causally steers which frequencies (for the dihedral group D59: which irreducible
representations) the embedding of a one-layer transformer learns. In pre-registered, held-out replications with fresh seeds (50 per task), engineered training splits enrich five prescribed
frequencies in addition mod 113 and 97, multiplication mod 113, and composition in D59. For add 113, add 97 and mul 113 (D59 pending), equal-norm embedding perturbations along the steered
frequencies reduce the logit margin more than along control frequencies. The choice starts to persist early (addition mod 113): 25 training steps on a first split measurably shape the embedding after 2000 further steps on a pair-disjoint second split, and the sign of an ablation contrast
(old vs new target frequencies removed) reverses between a switch after 25 and after 50 steps. Resetting the attention (weights and optimizer state) at a switch after 50 steps reverses the sign of this contrast, whereas the tested
MLP reset barely changes it, and resetting its value path lowers it more than an equal-size reset of its query/key weights — a reset sensitivity, not a storage location. We report effect sizes with confidence intervals, the limits of each measurement (notably that functional sensitivity follows spectral energy), and negative results.

## 1 Introduction (draft prose, session 26; checked against the sources by an independent agent, 13 points corrected)

Small networks trained on modular arithmetic first memorize their training pairs and only much later generalize ("grokking"; Power et al. 2022). Mechanistic analyses showed that the generalizing
solution computes with a handful of Fourier frequencies of the group (Nanda et al. 2023) and, for other finite groups, with a few irreducible representations (Chughtai et al. 2023). *Which*
frequencies a particular network ends up using has been described as arbitrary across runs (Chughtai et al. 2023). Recent theory attributes the competition between frequencies to the initialization
(He et al. 2026a) and, for uniform data over all input sequences, derives the order in which irreducible representations are learned from the Fourier statistics of the input encoding
(Marchetti et al. 2026). With one-hot tokens that encoding favours no frequency in cyclic groups and ties irreducible representations of equal dimension, and the role of the train–test split has
been named as open (He et al. 2026b).

We ask whether the training set itself can decide this choice. In the one-layer transformer of a previous grokking study we construct training splits whose pair mask carries power at five
prescribed frequencies, and we train with full-batch AdamW and fixed one-hot tokens. The lever differs from the order of examples within an epoch, which LeDoux (2026) showed to set the fundamental
frequency, from the encoding statistics of Marchetti et al. (2026), and from deliberately symmetric training sets, which in feature-learning kernels select the symmetry subgroup the features encode (Tomàs Bernal et al. 2026): here only *which* pairs are shown changes, the split has no built-in symmetry, and the targets are prescribed Fourier frequencies. In pre-registered replications with fresh seeds, the embedding enriches the
prescribed frequencies over disjoint comparison frequencies at step 2000 in every one of 50 seeds per task, for addition mod 113 and mod 97, multiplication mod 113 and composition in the dihedral
group D59 (for D59 this is before grokking; §3.1, §3.6). For the three cyclic tasks (D59 pending), the network is also more sensitive to perturbations along the steered frequencies than along
control frequencies (§3.2). Where we examined it (add-113 switch models, exploratory), this sensitivity follows the embedding energy, so we do not claim use beyond energy.

The choice starts to persist early; the persistence and reset results are for addition mod 113 only. After as few as 25 full-batch steps on a first split, a switch to a pair-disjoint second split
leaves a measurable trace in the embedding 2000 steps later (§3.3). Between a switch after 25 and after 50 steps, the sign of an ablation contrast reverses on average: after 25 steps the final model
loses more accuracy when the new target frequencies are removed, after 50 steps when the old ones are removed (§3.4; post hoc, the embedding energy points the same way, so this contrast does not
separate reliance from energy). Early training that later data cannot fully undo is familiar from critical learning periods (Achille et al. 2019), the primacy bias (Nikishin et al. 2022) and warm
starting (Ash & Adams 2020); Lyle et al. (2025) relate grokking to the overwriting of early features and explain recovery by the effective learning rate (their data-switch experiments use CIFAR,
not modular arithmetic), and LeDoux (2026) conjectures a critical period for the frequency choice. Our contribution here is a measured time scale of tens of steps for a specific, prescribed
feature choice against a controlled data switch.

Finally, we ask which part of the network this persistence is sensitive to. Resetting the attention weights together with their optimizer state at the switch after 50 steps reverses the sign of
the ablation contrast (mean 0.86 → −0.63), whereas the tested MLP reset barely changes it (0.79); resetting only the value/output path brings the contrast to about zero, an equal-size reset of the
query/key weights does not (§3.5). Because weights and optimizer state are reset together, the value/output and query/key resets are matched only in parameter count, and the MLP control resets
twice as many parameters, we read this as reset sensitivity, not as the place where the choice is stored. In language models, the ordering within attention is reversed for restoring the ability
to learn a withheld capability (Dong 2026); we discuss this contrast rather than generalize either ordering.

**Contributions.** (i) Causal steering of the learned frequencies (irreps) by the composition of the training set, replicated on held-out seeds across four tasks including a non-abelian group;
(ii) a functional validation on three cyclic tasks, with its limit (where examined, sensitivity follows energy); (iii) an early, time-dependent persistence of the choice under a data switch, with
a reversal of an ablation contrast between 25 and 50 steps; (iv) reset interventions showing that this persistence is more sensitive to resetting attention than to the tested MLP reset, and within
attention to the value/output path than to an equal-size query/key reset. A first-order account of the steering (§5) and all explorations and negative results (§4) are reported separately from
the confirmed results. All claims hold for one model family, one optimizer setting and constructed splits, and the persistence and reset results (§3.3–3.5) for addition mod 113 only (§6).

## 1 Introduction (outline)

- Grokking and Fourier circuits (Power et al. 2022; Nanda et al. 2023); which frequencies/irreps are learned is "arbitrary" per network (Chughtai et al. 2023) and has been linked to initialization
  (He et al. 2026) and, for uniform data, to the Fourier statistics of the input encoding (Marchetti et al. 2026, AGF).
- Closest work (see [[paper/related_work]], to be checked by a human): LeDoux (2026, arXiv 2603.25047) shows that the *order* of training examples sets the fundamental frequency in modular
  arithmetic; Marchetti et al. (ICML 2026) derive the irrep order from the Fourier statistics of the input *encoding* under uniform data; He et al. (2026) attribute the competition to initialization.
  Our lever is the complementary one: the *set* of training pairs, full batch, one-hot tokens, predicted in advance by the mask spectrum M0 (we found no AGF-utility bridge for M0, EXP-076).
- Lock-in: critical periods (Achille et al. 2019; Kleinman et al.), primacy bias (Nikishin et al. 2022), warm starting (Ash & Adams 2020) and, closest, grokking under non-stationarity with the
  effective learning rate as explanation (Lyle et al. 2025). Our contribution is a measured lock-in time of the frequency choice (≈ 25–50 steps) against a pair-disjoint switch and the reversal of an ablation contrast.
  Also to cite (full-text check, session 25, [[paper/fulltext_check_2026-09-27]]): LeDoux (2026) *conjectures* a critical learning period within the first few dozen epochs (fundamental frequency
  identifiable by epoch 3, significant by epoch 14; their §3.4/§6.2) without a switch experiment; Khanh (2026, arXiv 2607.06628) uses the same kind of model (1-layer transformer, full-batch AdamW, embedding power spectrum as circuit identity) and shows that transplanting
  another run's weight *direction* overwrites a run's frequency identity — a weight-space intervention rather than a data switch; Lyle et al. (2025) run warm-start experiments only on
  CIFAR and treat modular arithmetic as stationary (their §4.2), with no frequency analysis. He et al. (2026b, arXiv 2606.02993, §6) name the analysis of the train–test split as open.
- The functional measure (K2-function) is a validation of K2 rather than a separate contribution (frequency ablations go back to Nanda et al. 2023), and we state its limit (function follows energy).
- Partial resets (full-text check, session 25): Dong (2026, arXiv 2607.27281) reports for language models (Pythia up to 1.4B) that after "aging" on base data re-initializing only the
  query–key slices restores learnability (6/6) while the value slices do nothing (0/6). "An attention reset beats an MLP reset" is therefore not new for transformers; our contrast is the
  opposite ordering within attention (value path > query/key) in the grokking/frequency setting, which must be discussed as such (different tasks, scales, measures and reset protocols;
  no claim which is general).
- Contributions: (i) causal steering via split construction, held-out across four tasks incl. a non-abelian group; (ii) a functional validation (margin sensitivity) with its limits; (iii) an early, time-dependent
  lock-in under a data switch; (iv) reset interventions that localize *sensitivity* (not storage) in the attention value path.


## 1b Related work (draft prose, session 25; every entry to be checked by a human against [[paper/related_work]] and [[paper/fulltext_check_2026-09-27]])

**Fourier and irrep circuits.** Networks that grok modular addition compute it with a few Fourier frequencies (Power et al. 2022; Nanda et al. 2023); for finite groups they use irreducible
representations (Chughtai et al. 2023; coset circuits in S₅/S₆: Stander et al. 2024), and which ones a network uses has been described as arbitrary (Chughtai et al. 2023). Recent theory explains the competition between frequencies by
the initialization (He et al. 2026a), analyses irrep selection with the full group table as data and names the role of the train–test split as open (He et al. 2026b, §6), and, within
alternating gradient flow (Kunin et al. 2025), derives the order in which irreps are learned from the Fourier statistics of the input encoding under uniform data (Marchetti et al. 2026;
with one-hot tokens, irreps of equal dimension tie). LeDoux (2026) shows that the *order* of training examples (minibatches) sets the fundamental frequency, while, under a fixed stride ordering,
different random subsets of training pairs gave the same frequency (their §4.2.3, §5.3). Zhou, Zhang and Xu (2024) show outside modular arithmetic that an insufficient, non-uniform sample makes networks learn spurious (aliased) frequencies first; there the sample adds artefacts next to a fixed correct solution, here it selects among equally correct ones. Salah and Yevick (2024, §3.5) restrict the training set of modular addition by symmetry (only a ≥ b; additionally excluding some differences a − b, which mattered only together with a > b) and find that this changes whether and how well an MLP generalizes; which frequencies it learns is not examined. Our lever is the *set* of training pairs under full-batch training with one-hot tokens, with the targets prescribed in advance through the pair mask. On the kernel side, Tomàs Bernal et al. (2026) show for recursive feature machines on modular arithmetic that a deliberately symmetric (H-invariant) training set makes the learned features encode only the invariance subgroup H, and that generalization then requires breaking this symmetry: the structure of the training set selects the group structure the features encode. This is the closest conceptual precedent for our result; it concerns kernels and symmetry subgroups, whereas we select prescribed Fourier frequencies (irreps) in transformers through the spectrum of a non-symmetric pair mask.
More generally, data statistics select among redundant features (Hermann & Lampinen 2020), stage-wise learning follows data spectra in linear networks (Saxe et al. 2014), and neural
networks fit low frequencies first in continuous input spaces (spectral bias / frequency principle; Rahaman et al. 2019; Xu et al. 2019). These do not address which discrete group
frequencies a grokking network adopts.

**Early commitment and lock-in.** Critical learning periods (Achille et al. 2019; Kleinman et al. 2023, 2024), the importance of the early phase of training (Frankle et al. 2020), the
lasting cost of warm starting (Ash & Adams 2020) and the primacy bias (Nikishin et al. 2022) all describe early training that later data cannot fully undo. Closest to our setting,
Lyle et al. (2025) relate grokking to the overwriting of early features and explain recovery by the effective learning rate; their warm-start experiments use CIFAR and treat modular
arithmetic as stationary, without frequency analysis, so the effective learning rate is an alternative we must address for K4. LeDoux (2026, §3.4) conjectures a critical period in
modular arithmetic without a switch experiment; Howe (2026a) reports that an auxiliary representational (contrastive) prior applied only during the first 2000 epochs (4 % of training) gives most of its benefit (a loss intervention, not a data switch). Khanh (2026) uses the same model class and embedding power spectrum as a circuit identity and shows that transplanting another run's
weight direction overwrites it — a weight-space intervention, whereas we switch the data and measure when the frequency choice becomes persistent.

**Partial resets.** Resetting layers or parameter groups is an established tool to restore plasticity or to probe module criticality (Nikishin et al. 2022; Zhou et al. 2022; Zhang et al.
2022; Chatterji et al. 2020; Asadi et al. 2023 for optimizer resets). For transformers, Dong (2026) reports in language models up to 1.4B parameters that re-initializing only the
query–key slices of attention restores the ability to learn a withheld capability, while value slices do nothing. Our reset results (K4d, K4e) concern a different quantity (persistence
of an early frequency choice) and show the opposite ordering within attention (value path more than query/key); we report this as a contrast, not as a general statement about attention. In our model family, Jia (2026) transfers embeddings, readout and internal blocks between modular tasks and freezes embeddings and readout (query, key and value in one fused matrix), without resets at a data switch and without frequency analysis.

## 2 Setup (draft prose, session 27; to be checked against the code by an independent agent)

**Model and training.** We use the one-layer transformer of the original GROKVERSE study (preset arch25k, following the recipe of Nanda et al. 2023; our implementation has no bias terms): token embedding W_E and learned positional
embedding W_pos (d_model = 128), one causal attention layer with four heads of width 32, a ReLU MLP of width 512, residual connections, no layer normalization and no biases, and an untied
readout W_U. Inputs are the three tokens (a, b, =) with a, b ∈ {0, …, p−1}; the loss is the cross-entropy of the logits at the last position over the p output classes. All weights are
zero-mean Gaussians at initialization, with standard deviation 1/√d_model for W_E, W_pos, W_Q, W_K, W_V, W_in and W_U, 1/√(4·32) for W_O and 1/√512 for W_out. Training is full-batch AdamW (learning rate 10⁻³, weight decay 1.0, β = (0.9, 0.98)) on 30 % of all pairs; K2 runs train for 2000 steps. The two arms
of a seed share the initialization; only the training set differs. Confirmation blocks ran on one GPU (PyTorch 2.9.1 with ROCm, one thread per run) after a statistical (not bitwise) equivalence check against the CPU path on add 113;
all arms and seeds compared within a block ran on the same device.

**Tasks.** Addition modulo 113 (primary) and 97, multiplication modulo 113, and composition in the dihedral group D59 (order 118). For multiplication, pairs with a zero operand are not in
the group; frequencies refer to the discrete-logarithm coordinate (the cyclic group Z_112), and pairs with a zero keep uniform weight in the split construction below. For a cyclic group of
order n, the candidate frequencies are k = 1, …, ⌊(n−1)/2⌋; for D59 they are the 29 two-dimensional irreducible representations, computed from an explicit real basis.

**Engineered splits (K2).** For each seed, a random permutation of the candidate frequencies gives two disjoint target sets T_F and T_G of five frequencies each. Arm F draws its training set
(30 % of all pairs) without replacement with weights q(a, b) = max(0.05, 1 + ε·w(a, b)), where for a cyclic task w(a, b) = (1/5) Σ_{k∈T_F} cos(2πk·u(a)/n + φ_k(c)), u(a) is the group
coordinate of the left operand, c the output and φ_k(c) a random phase per target and output; arm G does the same with T_G. For D59 the cosine is replaced by tr(A_k(c) ρ_k(a)) with random
unit-norm 2×2 matrices A_k(c) and the irrep matrices ρ_k. We use ε = 2. Weighted sampling uses exponential keys (key = U^{1/q}, the largest 30 % are kept). The construction arranges the
target frequencies along the output classes; the token frequencies are no more unequal than in a random split (coefficient of variation 0.14 for the pilot construction), although their spectrum is target-enriched (§5).

**Switch protocol (K4–K4e).** For the persistence experiments (addition mod 113), a common held-out test set of 20 % of all pairs is removed first; from the remaining pool two training sets
A and B of 3831 pairs each (30 % of all pairs) are drawn with target sets T_A, T_B as above. A and B pick their pairs in alternation from their own weighted key orders, so at overlap ω = 0 (all primary analyses) they share no pair
(a sequential draw would give B the negative image of A's pattern). The steering strength ε is calibrated on separate calibration seeds so that the mask-spectrum target share of A and B matches
the pilot level (0.185; ε ≈ 2.23 at ω = 0). P3 additionally ran ω = 0.4 (40 % uniformly drawn shared pairs, ε ≈ 5.93) as a descriptive secondary level. A run trains t steps on A, then switches to B (optimizer state kept unless stated) and trains a fixed further budget (2000 steps in P3/N28, 4000
steps in N29–N29c); each seed is run in both directions (A→B, B→A). Reset arms re-initialize the named parameter tensors to their values at initialization and clear their AdamW state at the switch.

**Measures.** All spectral measures use the n group-element rows X of W_E in group order (for mul 113: W_E[g^i], g = 3, i = 0, …, 111). P_k(X) is the power of X in the real two-dimensional Fourier subspace of k (for D59: the four-dimensional span of the matrix coefficients of irrep k),
and P(S) = Σ_{k∈S} P_k for a set S. The definitions of Δ_pow (K2), the margin sensitivity D (K2-function), the persistence index π (K4) and the ablation contrast R (K4c–e) are given in the
outline below and in the frozen registrations.

**Protocol.** Each confirmation block was registered before any of its runs: hypotheses, primary measure, minimum effect, family and Holm correction, sample size (from pilot variance), a
reserved block of fresh seeds, and a list of previously seen data and the decisions they influenced. The manifest was committed and names its commit; it stores SHA-256 hashes of the analysis, split and training code;
every run was started through a wrapper that checks the code hashes before, during (every 2 s) and after training and binds each output file to the manifest, and the analysis accepts only bound runs. In P1 (two jobs), N28, N29–N29c, P2d and P2e,
one job of the frozen list was first run as a smoke test and counted as a regular run (from N28 on also through the frozen loader); P2c and P3 had none. Confidence intervals are percentile bootstrap intervals over seeds. Pilots on other seeds are reported
separately as explorations (§4).

## 2 Setup (outline)

- Model: the one-layer transformer of the original GROKVERSE study (preset arch25k, d_model 128, 4 heads, MLP 512), full-batch AdamW (lr 1e-3, wd 1.0, β as in the study), train fraction 0.3,
  inputs (a, b, =). Tasks: add mod 113 / 97, mul mod 113 (frequencies over the discrete-log order, Z_112), D59 (group order 118, irreps from an explicit real basis).
- Engineered splits: pairs are sampled with weights 1 + ε·wave, where the wave carries five target frequencies with random phases per output (for D59: random 2×2 coefficient matrices per output); F and G splits of a seed use disjoint target sets.
  Separate random streams (SeedSequence over experiment, task, seed, arm, purpose).
- Measures (all computed on the number rows X = W_E[:n] in group order; P_k(X) = power of X in the real Fourier (or irrep) subspace of k; for a set S, P(S) = Σ_{k∈S} P_k):
  - **Δ_pow** (K2): for a seed with arms F and G (same init, disjoint target sets T_F, T_G), Δ_pow = log[P_F(T_F)/P_F(T_G)] + log[P_G(T_G)/P_G(T_F)] at step 2000; 0 = no steering.
  - **Margin sensitivity D** (K2-function): u_S = P_S X / ‖P_S X‖, X' = X − δ u_S with δ = 0.02 ‖X‖; drop_S = mean correct-class logit margin on pairs outside both splits, before minus after;
    D = drop_own − mean over four control sets of five frequencies (drawn from a restricted pool excluding own, other targets and their 2k harmonics), averaged over the two arms.
  - **Persistence index π** (K4, K4b): L = log[P(T_A)/P(T_B)] of the final W_E; π = (L_switch − L_pureB)/(L_pureA − L_pureB), averaged over both switch directions; an affine,
    unbounded index (0 = pure second-split endpoint, 1 = pure first-split endpoint), not a probability.
  - **Ablation contrast R** (K4c–e): accuracy on a held-out test set after projecting W_E onto the complement of the five NEW target subspaces minus after removing the five OLD ones; R > 0 means the
    final model relies on the old frequencies. Averaged over both switch directions per seed.
- Protocol: every confirmation was registered before its runs, analysis code and manifest frozen by commit hash, fresh seeds from a reserved block, (from N28 on) a smoke job run through the frozen loader, Holm
  within a family, bootstrap CIs over seeds. Runs are bound to the manifest by content hashes. Table of all confirmation blocks (manifest commit, fresh seed range, n, runs), generated from the frozen manifests: `lab/paper/figures/table_registrations.py` → `table_registrations.md`.

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

A one-sided step of norm 0.02·‖X‖_F (X = number rows of W_E) along the steered frequencies reduced the mean correct-class logit margin on pairs outside both splits more than the mean of four pre-specified control sets:
add 113 (4000 steps) 0.250 [0.229, 0.270], 20/20 seeds; mul 113 (8000 steps) 0.291 [0.268, 0.308]; add 97 (8000 steps) 0.294 [0.275, 0.312], each 20/20 (Holm over the two tasks).
**Limit:** in the add-113 switch models examined (EXP-064 post hoc, EXP-068; 80 N29 models), sensitivity follows the energy distribution in W_E; at equal removed energy the dominant set has no
advantage (exploration). P2d/P2e models were not tested with the equal-energy measure. We therefore do not claim use
beyond energy. Earlier registered functional variants were not evaluable (P2), aborted for a design error (P2b), or not confirmed with the sign reversed (P2c, loss after removing half the control energy); we report all three.

### 3.3 Early lock-in under a data switch (K4, K4b; P3 f8adf45, N28 fa154bd)

After 25 steps on a first engineered split and 2000 steps on a pair-disjoint second split, final models sat at 0.351 of the normalized log-energy distance between the two pure endpoints; the excess over
any tested static additive W_E trace was 0.293 [0.263, 0.322] (30 fresh seeds, 30/30). Zeroing Adam's first moment at the switch lowered the persistence index π by 0.151 (0.340 → 0.189); ten extra
pre-switch steps with the same reset compensated this (non-inferiority, margin 0.05). This is compatible with an "exposure" reading, not a proof of it. *Size, post hoc:* in a scalar
model of bias-corrected Adam (β = 0.9/0.98), the first moment at the switch still carries 6.5–10.8 update-equivalents (at t = 25–35) of displacement along the old direction (≈ 8.7–8.9 if later gradients on the
same coordinate keep their magnitude); in the pilot π curve (EXP-059, 10 known seeds, sampled every 5 steps up to t = 35), zeroing m shifted π by 8.1, 9.6 and 6.5 steps at t = 25, 30, 35, (at t = 40 and 50 the interpolated shifts, 3.8 and 2.4, are not interpretable: the curve was not sampled between 35 and 50 and approaches its natural ceiling π ≈ 1).
That the first moment carries a source signal past the removal of the source data has been shown by state surgery in a different setting (Xu 2026); that fixed-clock first-moment memory makes data-order effects first order in the learning rate has been shown for fine-tuning (Sweeney 2026); a measure of training memory that grows with momentum collapses when the optimizer state is reset (Sevetlidis and Pavlidis 2026). What we add is only the size estimate in our setting.

### 3.4 An ablation contrast reverses between a switch at 25 and at 50 steps (K4c; N29 087e042)

Removing all five target frequencies from W_E after a switch and 4000 further steps: after a switch at t = 50, removing the **old** targets cost 0.903 more test accuracy than removing the new ones
(95 % CI 0.846–0.953; 20/20 seeds > 0.3); after a switch at t = 25, removing the **new** targets cost 0.603 more (0.498–0.700; 17/20 > 0.3). Two time points bracket a reversal of this ablation contrast;
a network-wide or irreversible functional commitment is not shown. Post hoc, the W_E energy points in the same direction (38/40 and 40/40 directions), so this contrast does not separate reliance
from energy. 19/20 seeds generalized.

### 3.5 Reset sensitivity: attention more than the tested MLP reset, value path more than query/key (K4d N29b db31564, K4e N29c 3c9cb63)

At a switch after 50 steps, resetting W_Q, W_K, W_V, W_O to initialization together with their AdamW state lowered the ablation contrast by 1.49 [1.36, 1.61] vs no reset and by 1.42 [1.28, 1.56] vs the
tested MLP reset (20 paired seeds, Holm-p 4.7·10⁻¹²). Resetting only W_V, W_O lowered it by 0.850 [0.685, 0.998] vs no reset and by 0.752 [0.596, 0.897] vs an equal-size reset of W_Q, W_K
(Holm-p 2.1·10⁻⁴ and 1.9·10⁻⁵). These show *reset sensitivity*, not a storage location: weights and optimizer state were reset together, the VO and QK resets are matched only in parameter count, and the MLP control resets twice as many parameters and is not matched in displacement or dynamics. Generalized seeds: 19/20 (N29b),
17/20 (N29c). *Relation to prior work:* in language models the ordering is reversed (query–key reset restores, value reset does not; Dong 2026); we report our ordering for this
setting only. A possible reading (untested): our switch keeps the task and hence the routing requirement (attend to both operands) and changes only which frequencies the
content carries, which passes through the value/output path; a withheld capability in a language model plausibly requires new routing (query–key).

### 3.6 Pending: D59 function (P2f, prepared) and generalization of the lock-in

D59 models generalize after a median of ≈ 4600 steps (pilot EXP-072: range 2875–8150; 9/10 runs by 20 000 steps), so K2 for D59 (3.1) concerns the pre-grokking choice. In the pilot the steered irreps carry 0.90–0.99 of the
embedding energy after grokking (exploration). Confirmation P2f (20 fresh seeds, 12 000 steps) is prepared (registration drafted and Codex-reviewed) but not yet frozen; results will replace this paragraph.

### 3.7 Pending robustness blocks (registered drafts, not run; session 26)

- **R1** (K2 vs learning rate 0.5e-3 / 2e-3, weight decay 0.3 / 3, train fraction 0.2 / 0.5; 15 fresh seeds per cell, Holm over 6; [[confirm/R1_REGISTRATION_DRAFT|R1]]).
- **R2** (K4c at lr 2e-3 and at wd 0.3; 30 fresh seeds, Holm over 4; [[confirm/R2_REGISTRATION_DRAFT|R2]]).
- **R3** (does the lock-in follow summed learning rate or step count? lr × 2 for 25 steps vs × 0.5 for 50 steps before the switch only; 20 fresh seeds, Holm over 2; [[confirm/R3_REGISTRATION_DRAFT|R3]]).
- **P4** (K2 in a shared-embedding MLP, at 4× width, and for non-modular integer addition; [[confirm/P4_REGISTRATION_DRAFT|P4]]).
- Pilot **EXP-078** (K2 in a two-layer transformer; exploration, known seeds).
Whatever these show, including "holds only in a range", replaces this list; nothing here is a result.

## 4 Explorations and negative results (not claims)

- Lock-in is smooth in the number of pre-switch steps (π ≈ 0.01, 0.19, 0.30, 0.56, 1.05 at t = 10, 20, 25, 35, 50; pilot, 10 known seeds); neither the W_E lead nor OV alignment at the switch predicts
  it better than the step count (EXP-060, EXP-070, EXP-071).
- The mask spectrum M0 predicts the learned frequencies (EXP-015) and is closely related, at first order, to the power of the first W_E gradient (coherent variant M0c for the transformer;
EXP-050: first order explains only part; [[BEFUND-split-mechanismus]]); it is *not* the first-stage utility of
  the simplest AGF model (EXP-076, negative).
- Post hoc on the 50 confirmed add-113 seeds of P1: the M0 target contrast of a seed's split pair correlates with the size of its Δ_pow (Spearman 0.39, permutation p 0.006; centred M0c
  0.26, p 0.07; two measures, not pre-registered); split contrasts vary little, so most of the seed-to-seed spread comes from elsewhere. In the shuffled control of EXP-047, Δ_pow is also
  ≈ 0 on the continuous measure (0.02 ± 0.65, post hoc).
- Further pilots: steering also in a shared-embedding MLP, at 4× width and for non-modular integer addition (EXP-045, 049, 048) — to be confirmed or reported as pilots (rule 19b).

## 5 Theory (first order, outline)

Under near-uniform initial outputs, the first gradient on embedding row t is a sum over the training pairs containing t, mapped through the initial Jacobian; its Fourier power at k is the coherent
mask spectrum M0c for the transformer (shared path for both positions) and M0 for the MLP (independent halves). A row's own occurrence count cancels exactly; the other operand's token frequencies do not (corrected in session 25, see 5.2), so the prediction for a frequency-matched
control with shuffled pairs (no steering) rests on the weak marginals of the engineered splits (consistent with pilot EXP-047, not a confirmation). Derivation and its limits: [[BEFUND-split-mechanismus]].

**5.1 Setting (draft text, session 25; post hoc explanation, not an independent test).** Let m(a, b) ∈ {0, 1} mark the training pairs, N = Σ m, and c = a + b mod p. At
initialization the logits are small, so the softmax output is close to uniform, s ≈ 𝟙/p, and the cross-entropy gradient with respect to the logits of pair (a, b) is
s − e_c ≈ −P⊥ e_c with P⊥ = I − 𝟙𝟙ᵀ/p. Write J_L, J_R for the Jacobians of the logits with respect to the embedding of the left and right operand, assumed at first order to be
the same for all pairs. The gradient on embedding row t is then

  g_t ≈ −(1/N) [ J_Lᵀ P⊥ ℓ_t + J_Rᵀ P⊥ r_t ],  ℓ_t(c) = m(t, c − t),  r_t(c) = m(c − t, t).

**5.2 Frequency content.** Taking the DFT over the token index t (ℓ̂_k(c) = Σ_t ℓ_t(c) ω^{−kt}, ω = e^{2πi/p}) and assuming isotropic random Jacobians at initialization,

- *shared path* (transformer: at initialization the nearly uniform attention mixes both positions into the same value/output path, J_L ≈ J_R):
  E‖ĝ_k‖² ∝ ‖P⊥(ℓ̂_k + r̂_k)‖² = Σ_c |ℓ̂_k(c) + r̂_k(c)|² − |n̂_L(k) + n̂_R(k)|²/p, the *coherent mask spectrum* M0c minus a marginal term;
- *separate paths* (shared-embedding MLP: a and b enter different halves of W_in, J_L and J_R independent): the cross term averages out,
  E‖ĝ_k‖² ∝ ‖P⊥ℓ̂_k‖² + ‖P⊥r̂_k‖², the *mask spectrum* M0 minus marginal terms.

Here n̂_L(k) = Σ_c ℓ̂_k(c) is the DFT of how often each token occurs as a left operand (likewise n̂_R). The subtracted term is the power (p·|mean|²) of the c-mean component of ℓ̂_k(c) + r̂_k(c): P⊥ removes
every component that does not vary along the output c. What cancels exactly is therefore a row's *own* occurrence count (its n_t u term). Token frequencies still enter through the
*other* operand: for m(a, b) = ρ(a), ℓ̂_k(c) = ρ̂(k) is constant in c and vanishes, but r̂_k(c) = ω^{−kc} ρ̂(k)* is not, and the shared-path power is p |ρ̂(k)|² (checked numerically,
session 25). **Prediction 1 (quantitative, not "marginals never steer"):** a control that keeps the a/b token frequencies of an engineered split but shuffles its pairs keeps only the
marginal contribution (plus random pair noise); for the EXP-016 construction the marginals are no more unequal than in a random split (coefficient of variation 0.14), although their spectrum is target-enriched
(mean target rank 11.6 vs 27.5 by chance); after centring, the first-order spectrum of the shuffled splits is at chance (shared path, recomputed in session 25: mean 0-based target rank
26.2 vs 27.5, share 0.090 vs 0.191 for the engineered splits), so such a control is predicted to steer at most weakly. A split with strongly structured token frequencies would be predicted to steer towards the frequencies of ρ.
**Prediction 2 (architecture contrast):** the first gradient of the transformer should follow M0c, that of the shared-embedding MLP M0.

**5.3 Status of the predictions (all exploratory, known seeds).** Prediction 2 matches the measured first gradients (Spearman ρ 0.77 for M0c vs 0.57 for M0 in the transformer; 0.24 vs 0.37 in
the MLP, 9/10 seeds), measured before the derivation was written, so it is an explanation rather than a test. The expected outcome for pilot EXP-047 (no steering by the shuffled control) was noted before its runs, but derived
from the uncorrected argument that all token frequencies cancel; the corrected quantitative form (§5.2) was written after the result. A control with exactly matched a/b token frequencies
but random pair structure showed no detectable steering (Δ̄ 0.3 on the top-5 overlap score, p = 0.33), while the pair structure did (D̄ 6.8, 10/10 seeds, p = 0.001); a pilot on 10 seeds,
not a confirmation. For the *final* frequencies M0c is only descriptively better than M0 in the MLP (r̄ 0.351 vs 0.323, 6/10 seeds, p ≈ 0.21).

**5.4 Limits of the first-order argument.** (i) It describes the gradient at initialization. With AdamW the first update is approximately lr · sign(g) coordinate-wise (bias-corrected
moments give m̂/√v̂ = g/|g| at step 1), which keeps the dominant frequencies but can spread some power to other frequencies; the spectrum of the *update* is therefore not exactly the one derived above. In a simulation of the first-order model (isotropic random Jacobian, d = 128, P1 construction on 10 calibration
seeds × 2 arms, session 25, numpy only) the coordinate-wise sign of the gradient kept all five targets in its top five in every case (target share of the power 0.152 vs 0.191 for
the gradient itself); this checks only the model, not the network. In a
two-hot quadratic pilot network with an activation switch (EXP-033, exploratory), replacing AdamW by plain gradient descent in the first phase only (to matched amplitude; the second phase
was always AdamW; one stage tested) still gave a persistent bias towards the split's targets, slightly stronger (ratio 1.26 [1.10, 1.46]); sign-GD reproduced AdamW. Whether this holds for
the transformer is untested. (ii) It predicts which frequencies the network starts to grow, not which survive: in the engineered splits some early-weak
targets were displaced by step 2000 by second harmonics fold(2k) of targets of the same arm (EXP-016, post hoc, 14/14 in seeds 10–15; the registered check EXP-021 has not been run). (iii) The isotropy assumption on the Jacobians is not checked beyond the first-gradient
correlations. (iv) It says nothing about why the early choice persists after a data switch (K4); the lab's amplitude model for that (H40) is prepared as EXP-040, not yet run. A drafted registration (R3, not yet frozen or run) separates summed learning rate from step count; a drafted pilot (EXP-081) varies β₁ (momentum tail) and β₂ (a proposed second-moment horizon, for which our scalar model gives no mechanism).
The derivation in the simplest alternating-gradient-flow model (AGF) does *not* reduce to M0 (EXP-076, negative), so the link to AGF-type theories remains open.

## 5b Discussion (draft, session 25)

**What the data choose.** Which Fourier features a grokking network uses is not only a matter of initialization: a training set with a prescribed pair structure moves the choice
towards prescribed frequencies across three cyclic tasks and a non-abelian group. A first-order argument (§5, post hoc) accounts for part of this through how the training pairs enter the first gradient on the embedding;
the derivation also says what should *not* matter (a row's own occurrence count) and what should (the arrangement of pairs along the output classes, including the token frequencies of
the other operand). The last point is a prediction we have not yet tested (pilot EXP-077 prepared); it would test whether marginals alone can steer (against the reading that only
non-marginal pair structure steers), without by itself isolating the first-order route.

**How early and where.** The choice becomes persistent within tens of optimizer steps: after a switch at 50 steps, removing the old frequencies from the final network costs more than removing
the new ones, after a switch at 25 steps the reverse (an ablation contrast that does not separate reliance from energy). Resetting the attention, and within it the value/output path, at
the switch reverses much of this contrast; the tested MLP reset does little.
Two cautions frame this. First, the resets show where the persistence is *sensitive*, not where it is stored: weights and optimizer state were reset together, and in the same model class
transplanting MLP weight directions alone appears to move frequency identity (Khanh 2026, suggestive, three pairs per task). Second, in language models the ordering within attention is reversed for restoring the ability to learn a new capability
(query–key rather than value; Dong 2026). One reading, untested, is that the relevant path is the one the new data require to change: our switch keeps the task and the routing and changes
only the content.

**Open questions.** (i) Which state variable makes the early choice persistent? No measured quantity we tried (W_E lead, OV alignment) explains the time course better than the step count
(EXP-060, 070, 071); an amplitude-race account is prepared (EXP-040, not yet run). (ii) Do the persistence results hold beyond add 113 and this architecture (EXP-074, EXP-075 pilots, prepared, not yet run)? (iii) Is the
steering robust to learning rate, weight decay and training fraction (registration R1)? (iv) Can the first-order account be connected to theories of the learning order under uniform data
(AGF; the simplest bridge failed, EXP-076)?

## 6 Limitations

One architecture family and optimizer for all persistence claims (add 113 only, generalization pending: EXP-074, EXP-075); engineered splits; functional measures do not separate identity from energy;
resets localize sensitivity, not mechanism; in the same model class (one-layer transformer, d = 128, full-batch AdamW lr 1e-3, wd 1; p = 59) Khanh (2026, §7, App. A) reports suggestive
evidence (three pairs per task) that transplanting the weight direction of attention, MLP or unembedding alone each pulls the frequency identity towards the donor, so our weak MLP *reset*
effect at a 50-step switch must not be read as "the MLP carries no frequency identity"; many design decisions were informed by pilots on known seeds (each registration lists them). Final models are measured 2000–4000 steps after the switch; whether the persistence survives much longer training is untested (post-grokking loss of generalization has been reported for add 113, 2608.07436). All persistence results use AdamW with β = (0.9, 0.98); part of the persistence is carried by the first moment (K4b), so its size is expected to depend on the optimizer and β₁ (untested; a β₁/β₂ pilot is drafted, EXP-081).

## AI use disclosure (draft wording, to be confirmed by the user)

Experiment planning, code, analyses and text of this work were produced to a substantial degree by AI agents (Anthropic Claude as the lab agent; OpenAI Codex as an independent reviewer of designs and
code), operating under written rules set by the human author, who bears responsibility for the content. All numerical results come from logged runs bound to frozen manifests; no number was written by hand.

## Figures (scripts under `lab/paper/figures/`, rendered from stored runs / frozen summaries)

1. **done:** `figures/fig1_mask_vs_learned.py` — mask spectrum M0 vs learned W_E power at step 2000 for EXP-016 seed 10 F (pilot data). Caption must say: four of five targets dominate;
   target 25 is replaced by 32 = 2·16 (a harmonic of a target, as seen throughout EXP-016).
2. Δ_pow per task with CIs (P1 summary) — **done:** `figures/fig2_p1_delta_pow.py` → `fig2_p1_delta_pow.png/.svg` (reads `lab/confirm/P1_summary.json`).
3. **done:** `figures/fig3_ablation_contrast.py` — ablation contrast R per seed for N29 (switch at 25 vs 50) and N29b/N29c (switch at 50, reset arms); blocks use different seeds.
4. **done:** `figures/fig4_pi_curve.py` — π(t) pilot curve (EXP-059, 10 known seeds, mean ± SD) with the N28 confirmed points at t = 25 (0.340 [0.302, 0.377]) and 50 (0.998 [0.965, 1.032]),
   30 fresh seeds (CIs recomputed from the frozen per-seed values; confirmed points offset by 1.2 steps for visibility).
5. **done:** `figures/fig5_margin_sensitivity.py` — K2-function D per seed with CI (P2d add 113; P2e mul 113, add 97); different step budgets, compare qualitatively.

## Reproduction (draft, session 27; scripts exist, none has been run end to end yet)

Every confirmed number can be regenerated in two ways. (i) From the frozen blocks: each block's job list, bound runs and frozen analysis (`lab/confirm/<BLOCK>_jobs.txt`, `confirm_<block>.py --analyze`; code hashes are checked against the manifest, so a re-analysis after later code changes needs a checkout of the manifest commit). (ii) From scratch with a lean trainer (`lab/paper/repro/train.py`, same model, data order, optimizer and switch/reset semantics as the lab trainer; equivalence against stored runs is checked first) and one script per claim, each with a smoke mode and a comparison gate against the frozen summary:

| Claim | Block | Script | Gate |
|---|---|---|---|
| K2 (add 113, mul 113, add 97) | P1 | `repro/k2.py --task add|mul --p 113|97 --compare-p1` | every seed's Δ_pow within 10⁻³ (strict; may need loosening if GPU runs are not deterministic) |
| K2-function (add 113) | P2d | `repro/k2_function.py --compare-p2d` | mean D within 0.02 |
| K2-function (mul 113, add 97) | P2e | `repro/k2_function_p2e.py --compare-p2e` | mean D per task within 0.02, all seeds |
| K4 (π arms), K4b | N28 | `repro/k4b.py --compare-n28` | mean π per arm within 0.05, all seeds |
| K4c | N29 | `repro/k4c.py --compare-n29` | mean accuracies within 0.02 |
| K4d / K4e | N29b / N29c | `repro/k4_resets.py --block n29b|n29c --compare` | mean R per arm and contrasts within 0.05, all seeds |

Not yet covered by a lean script: K2 for D59 (other trainer) and the static-trace decomposition of P3. Run times and the outcome of the full runs will be added here; until then, this section describes tooling, not results.

## Verification (session 24)

All numbers in §3 were checked against the frozen summaries by an independent verification agent (≈ 85 claims OK); 15 wording/scope issues were corrected.
