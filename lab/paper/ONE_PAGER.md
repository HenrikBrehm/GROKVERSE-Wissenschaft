---
id: ONE_PAGER
status: entwurf
datum: 2026-09-28
tags: [paper, onepager]
---
# Which training pairs a network sees decides which Fourier features it learns — and the choice sets in within the first ~25 steps

*One-page summary for enquiries (supervision, novelty check, compute). Draft, session 41; numbers from [[FINDINGS]] and [[paper/draft]]. Not for publication as is.*

**Core finding.** In small networks that grok modular arithmetic, the *composition of the training set* (which input pairs are shown) causally steers which of the equally valid Fourier features the embedding learns; this choice starts to persist after only ~25 full-batch steps, and its clock is the summed learning rate once Adam's momentum window is measured in the same unit.

**Strongest confirmed results** (each pre-registered, frozen analysis manifest, fresh seeds; 95 % bootstrap CIs):
1. **Steering (K2).** Engineered splits enrich five prescribed frequencies in the embedding at step 2000: add 113 Δ_pow = 8.24 [7.92, 8.54], mul 113 8.09, add 97 6.11, dihedral group D₅₉ 2.64 (50/50 seeds each). It holds at ½× and 2× learning rate, 0.3× and 3× weight decay, train fractions 0.2 and 0.5 (6 cells × 15 seeds, 15/15 each), in a shared-embedding MLP (8.89), a 4×-wide transformer (7.84), for non-modular integer addition (2.35; representation only, no generalization) (15 seeds each), and in a two-layer transformer (6.15, 10/10).
2. **Faster grokking.** Engineered splits generalize ≈ 6.5× faster than a uniform random split and ≈ 7.5× faster than a control with the same number of pairs per output (add 113, 20/20 units each). A dose curve over concentration (pilot, prediction fixed before the runs) saturates as predicted (Fig. 7).
3. **Early lock-in and switch cost.** After a data switch at step 25 the final model relies on the new targets, after a switch at 50 on the old ones (ablation contrast 0.60 and 0.90 accuracy, 20 seeds). A switch at step 25 delays grokking ≈ 1.8× (29/30 seeds), but only if the new split carries *different* target frequencies (difference +0.81 log2 [0.57, 1.04], 24/25).
4. **Clock of the lock-in.** At equal summed learning rate, persistence depends on step count only through Adam's momentum window: rescaling the betas so that the windows are equal in summed learning rate shifts persistence as predicted (+0.161 [0.132, 0.192], 36/36 seeds at ¼× learning rate; +0.057, 34/36 at 2×) and makes 100 steps at ¼× equivalent within ±0.1 to 25 default steps.

**Method.** Every claim above comes from a registration written before its block ran, a frozen analysis manifest (commit ID, code hashes), reserved fresh seeds never used in exploration, Holm correction within each family, and minimum effects or equivalence margins fixed in advance. Explorations, negative and unclear results (≈ 90 pilots) are kept and reported separately.

**What is known, what we did not find.** Fourier circuits and seed-dependent key frequencies in grokking (Nanda et al. 2023; Zhong et al. 2023); competing frequencies decided by an initial advantage (He et al. 2026); sampling that determines which frequencies are learned first (Zhou et al. 2024); data *order* as a channel that sets the learned frequency (LeDoux 2026); input statistics setting the order of irreps (Marchetti, Kunin et al. 2026); critical learning periods (Achille et al. 2019). For result 4, summed learning rate as the natural time axis (e.g. Tissue et al. 2024) and scaling 1 − β with the step size (Barakat & Bianchi 2021) are known; result 4 is an application of these principles to a new quantity. *Not found in our searches (Sept. 2026; preliminary, needs expert review):* steering by pair composition at fixed one-hot tokens across tasks and architectures, the 25–50-step lock-in window with its switch cost, and its momentum-window clock.

**Limits.** Toy tasks (modular and integer addition, D₅₉), small one- and two-layer models, full-batch AdamW; the functional measure follows embedding energy (no use beyond energy shown); many mechanistic questions are open.

**Next question (needs compute and supervision).** Does data composition steer features — and lock them in early — in a small language model that learns arithmetic from text? Can pair selection become a practical method to speed up or shape feature learning?

**Figure.** Dose curve, time to generalization against the split's target share (`lab/paper/figures/fig7_dose_curve.png`); alternatively K2 steering across tasks (`fig2_p1_delta_pow.png`).

**Disclosure.** Planning, code, experiments and text were carried out largely by AI agents (Claude, with Codex as a second reviewer) in an autonomous lab set-up; the human author, a secondary-school student, is responsible for the work and its use.
