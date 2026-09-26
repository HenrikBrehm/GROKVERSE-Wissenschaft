---
tags: [lab/einstieg]
---
# GROKVERSE-Labor: Einstieg

Das autonome Forschungslabor zu GROKVERSE: Grokking bei modularer Addition (p = 113), Transformer
und MLPs. Die Studie (`RESULTS.md`) ist historisch, neue Befunde stehen nur hier unter `lab/`.

- [[LIVE]]: was gerade passiert (Sitzungsstatus)
- [[STATE]]: aktueller Stand, nächste Aktion, Wiederaufnahme
- [[JOURNAL]]: Protokoll aller Sitzungen
- [[BACKLOG]]: priorisierte Forschungsfragen
- [[NOVEL_DIRECTIONS]]: Kandidaten, die für die Forschung neu sein könnten, mit Literaturprüfung
- [[BEFUND-split-mechanismus]]: Wie der Trainingssplit die Frequenzen auswählt (Stand Sitzung 5, überwiegend explorativ)

**Lage (2026-09-26, Sitzung 5):** Nach der Freigabe des Nutzers lief ab 07:30 wieder Training. **EXP-016 ist abgeschlossen: Konstruierte Splits geben die gelernten Frequenzen vor** (10/10 Seeds, Δ̄ +7.7 von 10, p ≈ 0.001; alle Abweichungen sind 2k-Harmonische). Bestätigt ist außerdem: Das Masken-Spektrum des Trainingssplits sagt die gelernten Frequenzen voraus (EXP-015). Neu, post hoc: Mechanismus über Positions-Interferenz im ersten Gradienten (M0c) und 2k-Harmonische als „Fehlgriffe“, siehe [[BEFUND-split-mechanismus]]. Vorbereitet: EXP-018 bis EXP-022, Warteschlange `queue_s5.sh`.

**Lage (2026-09-25, Sitzung 3):** Alle Trainingsversuche sind vorbereitet, aber noch nicht
gelaufen, weil alle bisherigen Sitzungen außerhalb des Fensters 00:00–13:00 Berlin lagen. Die
Auswertungen gespeicherter Läufe (EXP-003, EXP-009) sind abgeschlossen. Wichtigster Befund bisher:
Das zufällige Init-Spektrum des Embeddings sagt mit voraus, welche Frequenzen das Netz am Ende
nutzt ([[experiments/EXP-009-freq-commitment/SUMMARY|EXP-009]]).

## Versuche

| Versuch | Status | Ergebnis in einer Zeile |
|---|---|---|
| [[experiments/EXP-001-freq-ban/README\|EXP-001]] Frequenzverbot ab t0 | vorbereitet (Nachtrag b nach Codex-Review) | noch kein Lauf |
| [[experiments/EXP-002-destined-ban/README\|EXP-002]] Verbot der Zielfrequenzen ab Schritt 1 | vorbereitet | noch kein Lauf |
| [[experiments/EXP-003-early-prediction/SUMMARY\|EXP-003]] Frühvorhersage (Auswertung) | abgeschlossen | F6 (W_E-Fourier-Konzentration) teilweise bestätigt, ein Fortschrittsmaß ohne feste Vorlaufzeit |
| [[experiments/EXP-003-early-prediction/CONFIRM_b\|EXP-003b]] Two-hot-MLP | abgeschlossen | richtungsgleich, nicht signifikant |
| [[experiments/EXP-003-early-prediction/CONFIRM_d\|EXP-003d]] frische Seeds 10–19 | **läuft** (Sitzung 4) | noch kein Ergebnis |
| [[experiments/EXP-009-freq-commitment/SUMMARY\|EXP-009]] Frequenz-Lotterie / Lock-in (Auswertung) | abgeschlossen | Init-Spektrum von W_E trägt Information über die finalen Top-5 (r̄ = 0.386 vs. 0.5, p < 1e-5, seed-spezifisch). Bei der Two-hot-MLP nur pro Neuron |
| [[experiments/EXP-010-init-swap/README\|EXP-010]] Init-Tausch (kausal) | **läuft** (Sitzung 4, Paare mit EXP-003d) | noch kein Ergebnis |
| [[experiments/EXP-011-init-magswap/README\|EXP-011]] Betrag oder Richtung? (nur Normen tauschen) | vorbereitet | noch kein Lauf |
| [[experiments/EXP-012-init-gradient/README\|EXP-012]] Init-Gradient als Frequenz-Prädiktor | **abgeschlossen, bestätigt** | Erster Gradient sagt K besser voraus als die Init: frische Seeds r̄ 0.254 vs. 0.369, p = 0.031 ||| [[experiments/EXP-012-init-gradient/README\|EXP-012]] Init-Gradient als Frequenz-Prädiktor | **abgeschlossen, bestätigt** | Erster Gradient sagt K besser voraus als die Init: frische Seeds r̄ 0.254 vs. 0.369, p = 0.031 |
| [[experiments/EXP-013-lockin-curve/README\|EXP-013]] Lock-in-Kurve Schritt 0–300 | vorbereitet | noch kein Lauf |
| [[experiments/EXP-014-split-vs-init/README\|EXP-014]] Split oder Init? | vorbereitet (Nachtrag a: disjunkte Paare) | Gradient-Vorschau: erster Gradient folgt dem Split (ρ 0.34 vs. −0.01); Kreuzläufe offen |
| [[experiments/EXP-015-mask-spectrum/README\|EXP-015]] Masken-Spektrum des Splits als Prädiktor | **abgeschlossen, bestätigt** | Nur aus dem Split vorhergesagt (Assoziation): frische Seeds r̄ 0.277, fremde Masken 0.499, exaktes p 2.5e-5; hält auch gegen die funktionalen Schlüsselfrequenzen. Post hoc auch in allen MLPs. Kausal: EXP-016 |
| [[experiments/EXP-016-engineered-split/README\|EXP-016]] Frequenzen per Datenauswahl steuern | **abgeschlossen, steuerbar** | 10/10 Seeds, Δ̄ = +7.7 von 10, p ≈ 0.001: Konstruierte Splits geben die gelernten Frequenzen vor; alle Abweichungen sind 2k-Harmonische der Ziele |
| [[experiments/EXP-017-rfm-split/README\|EXP-017]] Frequenzwahl ohne Zufalls-Init (RFM) | vorbereitet | noch kein Lauf |
| [[experiments/EXP-018-split-speed/README\|EXP-018]] Beschleunigt ein spektral konzentrierter Split das Grokking? | vorbereitet | Feste gemeinsame Testmenge, Kontrolle D = gleiche Gewichte ohne Fourier-Anordnung; Seeds 20–29; nach Codex-Review nachgeschärft; noch kein Lauf |
| [[experiments/EXP-019-coherent-mask/README\|EXP-019]] Kohärentes Masken-Spektrum M0c gegen M0 | vorbereitet | Post hoc richtungsgleich (0.280 vs. 0.307; 0.222 vs. 0.277), n. s.; Bestätigung an 12 frischen Seeds ohne eigene Läufe |
| [[experiments/EXP-020-data-switch/README\|EXP-020]] Datenwechsel F → G: kausale Festlegungszeit der Frequenzwahl | vorbereitet | Seeds 30–34, gleiches G-Budget, Intervallzensur; nach Codex-Review umgebaut; noch kein Lauf |
| [[experiments/EXP-021-harmonic-misses/README\|EXP-021]] Fehlgriffe = zweite Harmonische der Ziele? (Bestätigung) | vorbereitet | Post hoc 14/14 in EXP-016 Seeds 10–15; Bestätigung an 18 frischen Läufen ohne eigenes Training |
| [[experiments/EXP-022-single-frequency/README\|EXP-022]] Erzwingt ein Ein-Frequenz-Split eine Ein-Frequenz-Lösung? | vorbereitet | Seeds 40–44, Arme S1/S5/R, feste Testmenge; drei konkurrierende Vorhersagen; noch kein Lauf |
| [[experiments/EXP-023-split-value/README\|EXP-023]] Getrennte Wertepfade je Position: folgt die Frequenzwahl dann M0 statt M0c? | vorbereitet | Seeds 50–59, Arme Baseline/rand/copy, 3000 Schritte; nach Codex-Review umgebaut; noch kein Lauf |
| [[experiments/EXP-024-quadratic-agf-mask/README\|EXP-024]] Gleicher Split, andere Aktivierung: lernt ein x²-Netz die *halben* Ziele? | **läuft** (Sitzung 6) | AGF-Nutzenrechnung: x² → halbe Ziele (3.3/5), ReLU → Ziele (4.7/5); Test an trainierten Zwei-Hot-Netzen, vorab festgelegt, Codex-geprüft |
| [[experiments/EXP-025-utility-random-split/README\|EXP-025]] Sagt der architekturspezifische Nutzen K auch unter Zufallssplits voraus? | vorbereitet | 20 Läufe à ~80 s, nach EXP-024 |
