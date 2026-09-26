---
id: LESART-nacht-2026-09-27
status: vorab
datum: 2026-09-26
tags: [lab/synthese]
verwandt: ["[[FINDINGS]]", "[[STATE]]", "[[JOURNAL]]"]
---
# Vorab-Lesart der GPU-Nacht 26./27.09.2026 (vor jedem Lauf festgelegt)

Zurück zu [[FINDINGS]] · [[LAB]]. Geschrieben in Sitzung 13 (2026-09-26, 20:22 Berlin, gemessen), **bevor** ein einziger Lauf von
EXP-043 bis EXP-049 existierte. Die Einzelurteile regeln die READMEs; hier steht nur, was die **Kombination** für [[FINDINGS]] heißt.

## Einzelne Bausteine → Aussage in FINDINGS

| Versuch (Frage) | *steuerbar* bzw. vorhergesagtes Urteil | *widerspricht* | *n. s.* / *nicht auswertbar* |
|---|---|---|---|
| [[experiments/EXP-047-marginal-control/README\|EXP-047]] (Paarstruktur oder Häufigkeiten?) | H47b ja, H47a nein (Vorhersage erster Ordnung): Wirkweg über die Paarstruktur, K1/K2 wie formuliert | H47a ja: Häufigkeiten steuern mit. K2 umformulieren, und die Theorie erster Ordnung reicht nicht (Weg über spätere Schritte/Adam/MLP) | Mechanismus bleibt offen; Grenze 4 in FINDINGS bleibt stehen |
| [[experiments/EXP-043-generalize-steering/README\|EXP-043]] (add 97, mul 113) | K2 nicht an p = 113 gebunden; mul: auch bei zusammengesetztem Modulus (Z₁₁₂) | K2 hängt am Modulus (nur bei der betroffenen Aufgabe) | keine Aussage über diese Aufgabe |
| [[experiments/EXP-046-dihedral-steering/README\|EXP-046]] (D₅₉) | „Der Split steuert“ auch bei nicht-kommutativer Verknüpfung (Mechanismus nur über EXP-047) | Steuerung ist Eigenheit zyklischer Gruppen | *keine Irrep-Struktur*: keine Aussage, **nicht** als Gegenbeleg lesen |
| [[experiments/EXP-048-intadd-steering/README\|EXP-048]] (a + b ohne mod) | Steuerung auch ohne Gruppenstruktur (als Fourier-Leistung in W_E, nicht als Funktion) | K2 an Gruppenaufgaben gebunden: wichtige Grenze | keine Aussage |
| [[experiments/EXP-049-width-steering/README\|EXP-049]] (d = 512) | K2 hält bei 4× Breite | K2 ist Knappheitseffekt kleiner Modelle | keine Aussage |
| [[experiments/EXP-052-oos-mask-prediction/README\|EXP-052]] (K1 an unberührten Fällen, eingefroren; Ergänzung Sitzung 14) | je Fall *K1 gilt hier*: Der Split allein sagt das W_E-Spektrum der Zufallssplit-Läufe voraus (Assoziation, keine Steuerung). Stützt die Deutung, dass EXP-043/046/048 über denselben Weg wirken | *nicht bestätigt* bei einem Fall mit *steuerbar* im Schwesterversuch: Steuerung ohne Abdruck im Zufallssplit, Mechanismus dort anders als M0 | *nicht auswertbar*: keine Aussage |

## Regeln für die Zusammenschau

1. **Keine Familienkorrektur über Versuche**, weil jeder Versuch eine eigene Frage beantwortet. Deshalb gilt: Bei fünf unabhängigen Tests
   mit α = 0.05 ist bei überall wahrer Nullhypothese mit ≈ 23 % mindestens ein falsch positives Ergebnis zu erwarten. **Ein einzelnes
   knappes *steuerbar* (0.01 < p < 0.05) unter vielen *n. s.* wird in FINDINGS nur als „Hinweis“ geführt**, nicht als Kernaussage.
2. K2 wird in FINDINGS nur dann auf „über Aufgaben hinweg“ erweitert, wenn **mindestens zwei der drei echt anderen Aufgaben**
   (EXP-046, EXP-048, eine der EXP-043-Aufgaben) *steuerbar* sind. Sonst bleibt K2 auf die gezeigten Aufgaben beschränkt, mit Liste.
3. *widerspricht* in einem Versuch mit bestandener Manipulations-/Strukturprüfung ist ein **Befund** (Grenze von K2) und kommt mit
   gleichem Gewicht in FINDINGS wie ein positives Ergebnis.
4. Ein technisch gescheiterter oder vom Wächter abgebrochener Versuch ist *nicht ausgeführt*, nicht negativ (§5, §8).
5. Effektgrößen immer mitberichten (Δ̄, n positiv/n gültig), nicht nur das Urteil. Δ_pow-Werte aus EXP-048/049 sind wegen anderer
   Aufgabe bzw. Breite nicht direkt mit der EXP-016-Kalibrierung (8.4) vergleichbar.
6. Befunde zu K4 (EXP-044) nur, wenn EXP-043 für die Aufgabe *steuerbar* war (so in der Queue festgelegt).
7. **Ergänzung (20:54, Regel 18c):** Alle Versuche dieser Nacht sind **Pilot/Exploration** für das Programm A/B/C in [[FINDINGS]]. Ein *steuerbar* hier ist keine Bestätigung von P1–P3; es liefert die Streuung für die Stichprobenplanung und entscheidet, welche Aufgaben in den reservierten Bestätigungsblock (Seeds 1000–1099) kommen. Technische Ausfälle (Lader: „fehlt“/„defekt“) werden getrennt von wissenschaftlich negativen Ergebnissen berichtet.
8. **Ergänzung (Sitzung 14):** EXP-052 ist der einzige Versuch dieser Nacht, dessen Vorhersagen nachweislich (Commit 7c6492a/1d71c5d/354e3dc) vor den Daten lagen. Seine Sekundärfragen (M0c > M0, M0 > E0, M0 > CNT) entscheiden zwischen den Mechanismus-Modellen; S1 (M0c) hat wegen ρ(M0, M0c) ≈ 0.7 wenig Trennschärfe, ein *n. s.* dort ist kein Beleg gegen die Rechnung erster Ordnung.
   *Korrektur (Sitzung 14, vor jedem Lauf, EXP-052 Nachtrag e):* Die Aussage „S1 hat wenig Trennschärfe“ in Regel 8 war falsch. Simuliert: Ist M0 oder M0c der Treiber, liegt ρ(M0c) − ρ(M0) bei ±0.16–0.24 mit Power ≈ 1. Ein S1 nahe 0 ist deshalb ein Befund (Mischung oder dritter Treiber).
9. **Ergänzung (Sitzung 14, beschreibend): Beschleunigung.** Gesteuerte Splits generalisierten bei add 113 früh (EXP-018/020 „nur F/G“: gen 625–1325),
   Zufallssplits der Studie spät (≈ 6000–10 000). In EXP-043/046/048 haben F/G und R je 2000 Schritte: berichtet wird der Anteil generalisierter
   Läufe bei 2000 je Arm (gesteuert gegen R). Erwartung bei gleicher Wirkung: gesteuert großteils generalisiert, R kaum. Das ist **kein Test von
   H18** ([[experiments/EXP-018-split-speed/README|EXP-018]]: dort gegen eine strukturierte Kontrolle D und mit gemeinsamer Testmenge); R nutzt
   hier das eigene Komplement als Testmenge. Nur als Hinweis, ob EXP-018 für die neuen Aufgaben lohnt.
