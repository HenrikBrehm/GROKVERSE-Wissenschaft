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

## Gliederung (nach dem Schnittplan in [[paper/STATUS]])

1. Introduction and related work (LeDoux 2026: order; Tomàs Bernal, Mallinar, Belkin 2026: kernels; Fu et al. 2026; Karkada et al. 2026; He et al. 2026a; Sweeney 2026)
2. Setup (full batch; for L0: minibatch protocol)
3. Result 1: composition steers the frequencies (K2 + function + R4; robustness R1/P4/R7 in one sentence)
4. Result 2: engineered splits speed up generalization (R5)
5. Result 3: lock-in within 25–50 steps (K4/K4b, K4c, R6/R8)
6. L0: set composition vs data order under minibatch
7. Discussion and limitations
Appendix: resets (K4d/e), D59 details, R1–R3, P4, R7, R2/C2, K5/R9/R10, explorations, first-order theory, reproduction.
