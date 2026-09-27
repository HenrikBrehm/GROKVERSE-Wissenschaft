---
id: EXP-060
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/negativ]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-059-momentum-exposure/README|EXP-059]]", "[[experiments/EXP-061-grad-alignment/README|EXP-061]]", "[[JOURNAL]]"]
---
# EXP-060: Sagt der W_E-Vorsprung beim Wechsel die Persistenz voraus? (EXPLORATION, post hoc)

Zurück zu [[LAB]] · [[FINDINGS]] (Programm B) · Daten aus [[experiments/EXP-059-momentum-exposure/README|EXP-059]] (keine neuen Läufe). **Exploration**: Maß nach dem Ansehen der π-Werte gewählt, kein Urteil.

- **Frage:** Ist die Festlegung bei t eine sichtbare Zustandsgröße von W_E? Maß: Vorsprung x = log[P_eigen / P_fremd] der gelernten Änderung ΔW = W_E(t) − W_E(0) (Mittel beider Richtungen),
  dazu die relative Größe ‖ΔW‖/‖W_E(0)‖.
- **Ergebnis (Sitzung 22, 07:37 gemessen; `summary.json`, 70 Punkte, Seeds 400–409 × t = 10…50):** Gepoolt Spearman(x, π) = 0.67, aber das ist der gemeinsame Anstieg mit t.
  Innerhalb von t: ρ = 0.02 / 0.21 / 0.27 / 0.21 / 0.36 / 0.19 / 0.04 (t = 10 … 50); Residuen-r nach Abzug der t-Mittel 0.26 (Seeds wiederholt, nicht unabhängig).
  x wächst nur langsam (0.55 → 0.89, d. h. Energieverhältnis 1.7 → 2.4), während π von 0.01 auf 1.05 steigt. Schon bei t = 10 hat ΔW einen klaren Vorsprung, und trotzdem ist π ≈ 0.
  ‖ΔW‖/‖W_E(0)‖ steigt von 0.10 auf 0.42, ist aber bei gegebenem t fast konstant (SD 0.001–0.004) und damit nur eine Uhr.
- **Lesart:** Die Festlegung lässt sich nicht aus dem W_E-Spektrum ablesen. Das passt zu EXP-038 (auch der Rest des Netzes trägt die Wahl). Folgeversuch: [[experiments/EXP-061-grad-alignment/README|EXP-061]].
