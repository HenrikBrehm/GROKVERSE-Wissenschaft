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

## Gliederung (nach dem Schnittplan in [[paper/STATUS]])

1. Introduction and related work (LeDoux 2026: order; Tomàs Bernal, Mallinar, Belkin 2026: kernels; Fu et al. 2026; Karkada et al. 2026; He et al. 2026a; Sweeney 2026)
2. Setup (full batch; for L0: minibatch protocol)
3. Result 1: composition steers the frequencies (K2 + function + R4; robustness R1/P4/R7 in one sentence)
4. Result 2: engineered splits speed up generalization (R5)
5. Result 3: lock-in within 25–50 steps (K4/K4b, K4c, R6/R8)
6. L0: set composition vs data order under minibatch
7. Discussion and limitations
Appendix: resets (K4d/e), D59 details, R1–R3, P4, R7, R2/C2, K5/R9/R10, explorations, first-order theory, reproduction.
