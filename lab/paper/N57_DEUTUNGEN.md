---
id: N57_DEUTUNGEN
status: vorab
datum: 2026-09-30
tags: [paper, neu/kandidat]
---
# N57 / EXP-123: Deutungssätze VOR dem Ergebnis (Sitzung 55, ≈ 01:08 Berlin, vor dem Ergebnis)

Zurück: [[LAB]] · [[experiments/EXP-123-commutativity-stages/README|EXP-123]] · [[NOVEL_DIRECTIONS]] N57 · [[paper/STATUS]]

Zweck: Der Anhangstext zu EXP-122/123 wird aus genau einem dieser Sätze gebaut, je nach vorab festgelegtem Ausgang. Keine Kernaussage (Regel 20a); höchstens ein Anhangsabsatz („exploration, pre-set readings, R5 units whose generalization times were known“). Pflichtzitat: He et al. 2026a (arXiv 2602.16849; im Paper schon zitiert, bisher nur zur Init-Lotterie), weil dort dasselbe Muster in einem Netz mit eingebauter Kommutativität (Eingabe h_x + h_y) beschrieben ist.

**H1 gestützt:** "On the random splits of the R5 units, held-out pairs whose mirrored pair (b, a) was trained reached accuracy 0.5 before the other held-out pairs in k of n units (pre-set: at least 100 steps earlier), so in this transformer, whose input does not build commutativity in, the test accuracy before grokking is first carried by the learned symmetry a + b = b + a; He et al. (2026a) describe the same pattern in a network whose input sum makes it commutative by construction."

**H1 nicht gestützt:** "Unlike in the four pilot runs (EXP-122), the mirrored pairs did not reliably lead (k of n units), so a commutativity stage is not a general feature of grokking on random splits in this setup."

**H2 gestützt:** "When the mirrored held-out pairs first reached 0.5, the other held-out pairs were at accuracy m = … on engineered splits against … on random splits of the same units (mean difference d = … [CI], k of n units positive; pre-set minimum 0.05), so the engineered choice of pairs mainly shortens the second stage, the generalization to pairs without a trained mirror; how the frequency concentration does this is not tested here."

**H2 Richtung ja, unter Mindesteffekt:** "The other pairs were ahead on engineered splits in k of n units, but by less than the pre-set minimum of 0.05 (d = …), so the engineered splits shorten both stages about proportionally rather than mainly the second."

**H2 nicht gestützt:** "At the time the mirrored pairs reached 0.5, the other pairs were not further on engineered splits than on random ones (d = …), so the engineered choice speeds up grokking as a whole, including the commutativity stage, not a specific second stage."

**D_0 (beschreibend, immer als solches):** "The count-matched control D_0 (same number of pairs per antidiagonal as the engineered split, positions random) behaved like [the random / the engineered] split in this respect (median m …)", mit dem Zusatz, dass D in R5 selbst langsam war (H-ED).

**Nicht auswertbar:** Kein Anhangstext; nur JOURNAL.
