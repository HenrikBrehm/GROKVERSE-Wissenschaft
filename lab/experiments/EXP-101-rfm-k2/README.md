---
id: EXP-101
status: entwurf
datum: 2026-09-28
tags: [exp/vorbereitet]
---
# EXP-101 (Regel 20c): Steuert die Datenauswahl auch die Merkmale einer Recursive Feature Machine (RFM)? (Entwurf)

Zurück: [[LAB]] · [[FINDINGS]] (K2) · Regel 20c · Brücke zu Tomàs Bernal, Mallinar, Belkin 2026 (arXiv 2604.00316) · Code: `lab/external/rfm-grokking` (Mallinar et al., arXiv 2407.20199; GPL-3.0, Commit 73181df8, nicht im Repo)

**Stand:** Entwurf (Sitzung 43, 2026-09-28). Noch kein Code, keine Installation. Die Abhängigkeiten (jax, neural-tangents, wandb, scipy, einops) kommen erst **nach R10** in `.venv-gpu`, mit festgehaltenen Versionen (Regel 20f).

## Frage

Wird K2 (konstruierte Trainingssplits steuern die gelernten Frequenzen) auch in einem nicht-neuronalen Lerner sichtbar, der Grokking zeigt? Tomàs Bernal et al. zeigen für RFM, dass die Symmetrie der Trainingsmenge bestimmt, was gelernt wird. Unser Hebel ist ein anderer: eine Paarmaske ohne eingebaute Symmetrie mit vorgegebenen Frequenzen. Hält K2 in RFM, spricht das dafür, dass die Steuerung eine Eigenschaft der Daten ist und nicht des Transformers.

## Plan

- **Daten:** RFM baut die Eingaben wie wir (`operation_mod_p_data`: `cartesian_prod(x, y)`, flacher Index a·p + b, one-hot, 2p Dimensionen). Unsere Split-Dateien (flache Indizes) lassen sich deshalb direkt einspeisen: `data.make_data_splits` wird in einem eigenen Wrapper ersetzt (externer Code bleibt unverändert). Aufgabe add 113, Splits F/G wie P1 (Trainingsanteil 30 %) an 10 Seeds, gleiche Testmenge.
- **Modell:** Gauß-Kern-RFM wie im Original (`--kernel_type gaussian`, Bandbreite, `agop_power` 0.5, Iterationen wie in ihrer README/ihren Skripten; vorher an einem Zufallssplit reproduzieren, dass Grokking auftritt).
- **Messgröße:** Die AGOP-Matrix M (2p × 2p) wird in die a- und b-Blöcke zerlegt und je Block in die reelle DFT-Basis gedreht. Gemessen wird die Leistung je Frequenz auf der Diagonale bzw. im Frequenzblock. Δ_pow_RFM = log[P_F(T_F)/P_F(T_G)] + log[P_G(T_G)/P_G(T_F)] wie P1.
- **Lesarten (vor dem Lauf einfrieren):** „K2 in RFM“, wenn Δ_pow_RFM-KI > 0 über Seeds; „nicht“, wenn KI ⊂ [−0.5, 0.5]. Beschreibend: Testgenauigkeit, Iteration bis zur Generalisierung.
- **Aufwand:** Kern 3831 × 3831, wenige Iterationen; CPU reicht vermutlich. Laufzeit im Smoke messen.

## Offen

Wrapper `run_rfm.py` (nach der Installation), Nachbau eines Originalergebnisses als Gleichwertigkeitsprüfung, statische Prüfung, dann Pilot.
