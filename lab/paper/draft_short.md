---
id: paper-draft-short
status: entwurf
datum: 2026-09-28
tags: [lab/paper]
verwandt: ["[[paper/STATUS]]", "[[paper/draft]]", "[[FINDINGS]]"]
---
# Kurzfassung (Regel 20d): ≤ 8 Seiten, 3 Kernaussagen + L0

Zurück zu [[paper/STATUS]] (Schnittplan) · Langfassung [[paper/draft]] (bleibt als Quelle und Anhang). Angelegt Sitzung 43 (2026-09-28). **Stand: nur Abstract-Entwurf; jede Zahl ist aus dem geprüften Abstract der Langfassung übernommen und muss vor der Freigabe unabhängig gegen die Summaries geprüft werden.** Der L0-Satz ist ein Platzhalter, bis EXP-100 und die L0-Bestätigung ausgewertet sind.

## Abstract (Entwurf, Sitzung 43)

Networks that grok modular arithmetic use a sparse set of Fourier features, and which frequencies a network uses is usually treated as an outcome of its initialization. We show that the composition of the training set steers this choice. In pre-registered replications on fresh seeds, engineered training splits enrich five prescribed frequencies in the embedding of a one-layer transformer for addition mod 113 and 97, multiplication mod 113 and the dihedral group D59 (50 seeds per task), and the networks are more sensitive to perturbations along the steered frequencies than along controls. Even an ordinary uniform 30 % split biases the learned frequencies, though far from determining them. Engineered splits also generalize earlier: about 6.5× faster than uniform random splits and 7.5× faster than a control with the same number of pairs per output (20/20 units each). The choice locks in within 25 to 50 steps: after a data switch at 50 steps an ablation contrast points to the old target frequencies, after 25 steps to the new ones, and a switch at 25 steps delays grokking by a factor of about 1.8, but only if the new split carries different target frequencies. All of these results use full-batch training. [L0: result of the minibatch and data-order test, pending.] We report effect sizes with confidence intervals, the limits of each measure (functional sensitivity follows spectral energy), and negative results.

## Gliederung (nach dem Schnittplan in [[paper/STATUS]])

1. Introduction and related work (LeDoux 2026: order; Tomàs Bernal, Mallinar, Belkin 2026: kernels; Fu et al. 2026; Karkada et al. 2026; He et al. 2026a; Sweeney 2026)
2. Setup (full batch; for L0: minibatch protocol)
3. Result 1: composition steers the frequencies (K2 + function + R4; robustness R1/P4/R7 in one sentence)
4. Result 2: engineered splits speed up generalization (R5)
5. Result 3: lock-in within 25–50 steps (K4/K4b, K4c, R6/R8)
6. L0: set composition vs data order under minibatch
7. Discussion and limitations
Appendix: resets (K4d/e), D59 details, R1–R3, P4, R7, R2/C2, K5/R9/R10, explorations, first-order theory, reproduction.
