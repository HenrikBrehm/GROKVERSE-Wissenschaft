---
id: EXP136_DEUTUNGEN
datum: 2026-10-01
tags: [lab/paper]
---
# EXP-136 (K2 bei größerem Modulus und wenig Daten): Paper-Sätze je Ausgang, vorab

Zurück zu [[paper/STATUS]] · [[LAB]] · [[experiments/EXP-136-large-modulus/README|EXP-136]] · [[paper/L0b_DEUTUNGEN]]

**Geschrieben in Sitzung 65 (01.10.2026, ≈ 01:00 Berlin), bevor ein Blocklauf von EXP-136 existierte.** Bekannt: zwei Smokes (p = 307, 30 %: Generalisierung nach 175 Schritten; p = 307, 4 %: nur Tempo) und ein Lader-Test (Seed 13600, p = 211, 3831 Paare: Δ_pow 1.24 bei Schritt 2000, noch nicht generalisiert), siehe README. EXP-136 ist eine **Exploration mit 3 Seeds je Zelle**: höchstens ein Satz im Anhang (neben EXP-043 / Anhang A, „other moduli“) und ein Halbsatz in Grenze (ii) der Kurzfassung. **Kein Abstract, keine neue Kernaussage.** Zahlen nach `analyze.py`, unabhängige Textprüfung wie immer.

## Satz im Anhang, je Gesamtlesart

- **alle vier Zellen „steuert“:** *In a pilot at larger moduli (addition mod 211 and mod 307, three seeds per cell, exploration), the engineered splits again steered the embedding frequencies at step 2000, both at 30 % data (Δ_pow …–…) and with the same number of training pairs as addition mod 113 (3831 pairs, 8.6 % and 4.1 % of all pairs; Δ_pow …–…).* (+ Zweitlesart am Ende, falls anders: *… at the end of training …*)
- **„hi“ steuert, „lo“ bricht (und „verdict_end“ bei „lo“ nicht „steuert“):** *… the engineered splits steered the embedding frequencies at 30 % data (Δ_pow …–…) but not with 3831 pairs (8.6 % / 4.1 %; Δ_pow …–…, threshold 1), also at the end of training. In this pilot the steering needed a denser training set, which is consistent with LeDoux's (2026) report that composition did not matter at p = 9973 and 0.3 % data.*
- **„lo“ bricht bei 2000, aber „verdict_end“ „steuert“:** *… with 3831 pairs the steering was not visible at step 2000 (memorization phase, Δ_pow …) but at the end of training (Δ_pow …, … of 6 runs generalized).* Keine Aussage „braucht Datendichte“.
- **„hi“ bricht:** *… the engineered splits did not steer the embedding frequencies at addition mod 211/307 even at 30 % data (Δ_pow …–…), so the steering of Section 3.1 is limited to small moduli in this pilot.* → Grenze (ii) ausdrücklich, FINDINGS-Grenze.
- **gemischt / „unklar“ / „nicht auswertbar“:** *A pilot at larger moduli (…) was inconclusive (…).*

## Grenze (ii), Halbsatz (nach „steering holds in four tasks“)

- steuert überall: *; a three-seed pilot at moduli 211 and 307, also with only 4–9 % data, pointed the same way (Appendix A).*
- braucht Datendichte: *; in a three-seed pilot at moduli 211 and 307 it held at 30 % but not at 4–9 % data (Appendix A).*
- sonst: *; a pilot at moduli 211 and 307 was inconclusive (Appendix A).*

## Was ausdrücklich nicht gesagt wird

- nichts über p = 9973 oder 0.3 % Daten (LeDoux' Regime) – wir sind bei p ≤ 307 und ≥ 4 %;
- „Datendichte“ und „Paarzahl“ sind hier nicht getrennt (lo hält die Paarzahl fest, nicht den Anteil);
- keine Skalierungsaussage über p (zwei Werte, drei Seeds); kein Vergleich der Δ_pow-Beträge mit add 113 als Effekt von p (andere Zahl von Frequenzen, andere Seeds);
- Einbettungsenergie, keine Ablation (Funktion nicht geprüft).
