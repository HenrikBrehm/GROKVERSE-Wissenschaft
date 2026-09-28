---
id: paper-draft-short
status: entwurf
datum: 2026-09-28
tags: [lab/paper]
verwandt: ["[[paper/STATUS]]", "[[paper/draft]]", "[[FINDINGS]]"]
---
# Kurzfassung (Regel 20d): ≤ 8 Seiten, 3 Kernaussagen + L0

Zurück zu [[paper/STATUS]] (Schnittplan) · Langfassung [[paper/draft]] (bleibt als Quelle und Anhang). Angelegt Sitzung 43 (2026-09-28). **Stand: nur Abstract-Entwurf; jede Zahl ist aus dem geprüften Abstract der Langfassung übernommen und muss vor der Freigabe unabhängig gegen die Summaries geprüft werden.** Der L0-Satz ist ein Platzhalter, bis EXP-100 und die L0-Bestätigung ausgewertet sind.

## Abstract (Entwurf, Sitzung 43; Fassung 2 nach unabhängiger Prüfung)

Networks that grok modular arithmetic use a sparse set of Fourier features, and which frequencies a network uses is usually treated as an outcome of its initialization. We show that the composition of the training set steers this choice. In pre-registered replications on fresh seeds, engineered training splits enrich five prescribed frequencies in the embedding of a one-layer transformer for addition mod 113 and 97, multiplication mod 113 and the dihedral group D59 (50 seeds per task), and equal-norm embedding perturbations along the steered frequencies reduce the logit margin more than along controls (20 seeds per task; D59 after grokking). In addition mod 113, even an ordinary uniform 30 % split biases the learned frequencies, though far from determining them, and engineered splits generalize in about 6.5× fewer steps than uniform random splits and 7.5× fewer than a control with the same number of pairs per output (geometric means, times bounded at 8000 steps; all 20 units in the same direction). The choice starts to persist within 25 to 50 steps (addition mod 113): the sign of an ablation contrast between old and new target frequencies reverses between a data switch after 25 and after 50 steps (it tracks embedding energy), and a switch after 25 steps delays grokking by a factor of about 1.8, whereas a switch to new pairs with the same target frequencies costs no time on average. All of these results use full-batch training. [L0: result of the minibatch and data-order test, pending.] We report effect sizes with confidence intervals, the limits of each measure (functional sensitivity follows spectral energy), and negative results.

*Prüfung (Sitzung 43, Claude-Agent, nur lesend):* alle Zahlen stimmen (P1 50/50 je Aufgabe; P2d/e/f je 20/20; R5 ×6.53/×7.47; N29 0.903/0.603; R6 ×1.80; R8 −0.15). Übernommen: Geltungsbereich add 113 für R4/R5/K4/R6/R8, 20 Seeds für die Funktion, „starts to persist“ statt „locks in“ mit dem Energie-Vorbehalt, genaues Zeitmaß für R5, R8 nicht als „only if“.

## 3 Result 1: the composition of the training set steers the learned frequencies (Kurzfassung, Sitzung 43, ungeprüft)

**Steering (P1, pre-registered, 50 fresh seeds per task).** For each seed we built two engineered splits F and G of the same size whose pair masks concentrate their spectrum on five disjoint target frequencies (irreducible representations for D59), and trained the same initialization on each. At step 2000 the relative W_E energy of the own against the other targets, Δ_pow, was 8.24 [7.92, 8.54] for addition mod 113, 8.09 [7.75, 8.43] for multiplication mod 113, 6.11 [5.79, 6.43] for addition mod 97 and 2.64 [2.55, 2.73] for D59, positive in 50/50 seeds in every task (Holm-p 1.5·10⁻⁵, worst case). Descriptively, the five own targets carried on average 0.80 of the embedding's group power in addition mod 113 (chance 0.089), 0.79 in multiplication mod 113, 0.69 in addition mod 97 and 0.44 in D59 (chance 0.17). The steering held when one hyperparameter deviated (learning rate ×0.5/×2, weight decay ×0.3/×3, train fraction 0.2/0.5; R1), in a shared-embedding MLP, at 4× width and for non-modular integer addition (P4), and in a two-layer transformer (R7); details in Appendix A.

**Functional sensitivity (P2d, P2e, P2f).** A step of norm 0.02·‖X‖ (X = number rows of W_E) along the steered frequencies reduced the mean correct-class logit margin on pairs outside both splits more than steps along four pre-specified control sets: 0.250 [0.229, 0.270] (addition mod 113), 0.291 [0.268, 0.308] (multiplication mod 113), 0.294 [0.275, 0.312] (addition mod 97), each 20/20 seeds, and D = 0.233 [0.214, 0.253] for D59 after grokking (12 000 steps, 20/20). In the models where we could test it, this sensitivity follows the energy distribution: at equal removed energy the dominant set had no advantage. We therefore claim sensitivity, not use beyond energy.

**An ordinary random split also shapes the choice (R4, addition mod 113, 60 fresh units).** Each unit crossed two initializations with two uniform 30 % splits (8000 steps). Networks sharing a split had more similar embedding spectra than networks sharing nothing: after 8000 steps, Δ_split = 0.118 [0.079, 0.157] in an energy-weighted cosine (48/60 units positive), and before grokking the rank signature was also shared (Spearman at step 2000, 0.33 [0.30, 0.36]). Descriptively the shared split raised similarity more than a shared initialization, but it is far from determining the choice: networks with the same split share on average about one of their five strongest frequencies, against about one half without a shared split.

**What this shows and what it does not.** The prescribed frequencies are enriched causally by the choice of training pairs, in four tasks, with fixed one-hot tokens and full-batch training. Whether the steering survives minibatch training and competing order signals is tested in Section 6 (L0). LeDoux (2026) reports the same frequency across random training subsets under a structured example order at p = 9973. That is plausibly a different regime, dominated by the order signal, with ≈ 80× more pairs, whose random mask fluctuations are correspondingly smaller.

## 4 Result 2: engineered splits generalize earlier (R5; Kurzfassung, Sitzung 43, ungeprüft)

**Design (pre-registered, 20 fresh units, addition mod 113, 8000 steps).** Per unit, seven training sets of 3831 pairs share one held-out test set and one initialization: a uniform random split R, engineered splits (ε = 1, 2, 8), and for each primary engineered split a control D with exactly the same number of training pairs per output value (per anti-diagonal), but with positions drawn uniformly within each anti-diagonal. The event is a stable rise of test accuracy to ≥ 0.95 after train accuracy ≥ 0.99; times are bounded at 8000 steps.

**Result.** The engineered split generalized in ×6.5 [5.3, 7.9] fewer steps than the random split and ×7.5 [6.5, 8.6] fewer than the matched control (geometric means of bounded time ratios; 20/20 units in the same direction for both; Holm-p 2·10⁻⁵). A stronger concentration of the mask spectrum was faster (ε = 1 took ×14.4 [12.4, 16.6] as long as ε = 8; secondary). Median bounded times were 775–813 steps (ε = 2), 6163 (R) and 6850–7513 (D). By step 8000, 16/20 random-split units and 14/20 and 11/20 control units had generalized.

**What this shows and what it does not.** At matched per-output counts the arrangement of the pairs, which carries the spectral concentration of the mask, produces the speed-up; the output marginals alone do not. "Earlier" means an earlier stable rise within 8000 steps, not a higher final accuracy. That early task-aligned embedding structure shortens the grokking delay is known from other interventions (Howe 2026b; GrokTransfer). The contribution here is that the choice of training pairs alone produces it, at matched size, initialization and test set. Post hoc, a higher early target share goes with earlier generalization; whether the speed-up runs entirely through this early signal is open.

## 5 Result 3: the choice starts to persist within 25–50 steps (K4, K4c, R6, R8; addition mod 113; Kurzfassung, Sitzung 43, ungeprüft)

**Persistence after a switch (P3, N28; pre-registered, 30 fresh seeds each).** After 25 steps on a first engineered split and 2000 steps on a pair-disjoint second split, final models sat at 0.351 of the normalized log-energy distance between the two pure endpoints (persistence π), 0.293 [0.263, 0.322] above any tested static additive trace (30/30). Zeroing Adam's first moment at the switch lowered π from 0.340 to 0.189, and ten extra pre-switch steps compensated this (N28). This is compatible with an "exposure" reading, not a proof of it. That the first moment carries such a signal is known from other settings (Sweeney 2026; Xu 2026). What we add is the size in ours.

**An ablation contrast reverses (N29, 20 fresh seeds).** Removing all five target frequencies from W_E after a switch and 4000 further steps: after a switch at step 50, removing the old targets cost 0.903 [0.846, 0.953] more test accuracy than removing the new ones (20/20 seeds above 0.3); after a switch at step 25, removing the new targets cost 0.603 [0.498, 0.700] more (17/20). The embedding energy points the same way (post hoc), so the contrast does not separate reliance from energy. The two time points bracket a reversal; a network-wide or irreversible commitment is not shown.

**A switch inside this window costs time (R6, 30 fresh seeds).** With b the first step with test accuracy ≥ 0.95 (bounded at 2000) and C(t) the log2 time ratio against training on the destination split only, a switch at step 25 delayed grokking by C(25) = +0.85 [0.73, 0.96] (a factor ≈ 1.8; 29/30 seeds) and more than a switch at step 50 (C(25) − C(50) = +1.25 [0.97, 1.50]; 28/30). Across the grid the cost was positive from t = 10 to 40 and negative from t = 50 on.

**Only a change of targets costs (R8, 25 fresh seeds).** A switch at step 25 to a pair-disjoint split with the same five targets and matched steering strength did not delay grokking on average (−0.15 log2; 8/25 seeds slower), whereas the switch to other targets did (+0.66; 24/25); difference +0.81 [0.57, 1.04]. The delay is therefore not a generic cost of an early change of training pairs, nor of fewer destination updates alone. Because the same-target split has partly reversed wave phases, a pure phase conflict is not excluded.

## Gliederung (nach dem Schnittplan in [[paper/STATUS]])

1. Introduction and related work (LeDoux 2026: order; Tomàs Bernal, Mallinar, Belkin 2026: kernels; Fu et al. 2026; Karkada et al. 2026; He et al. 2026a; Sweeney 2026)
2. Setup (full batch; for L0: minibatch protocol)
3. Result 1: composition steers the frequencies (K2 + function + R4; robustness R1/P4/R7 in one sentence)
4. Result 2: engineered splits speed up generalization (R5)
5. Result 3: lock-in within 25–50 steps (K4/K4b, K4c, R6/R8)
6. L0: set composition vs data order under minibatch
7. Discussion and limitations
Appendix: resets (K4d/e), D59 details, R1–R3, P4, R7, R2/C2, K5/R9/R10, explorations, first-order theory, reproduction.
