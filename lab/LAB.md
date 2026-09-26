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
| [[experiments/EXP-015-mask-spectrum/README\|EXP-015]] Masken-Spektrum des Splits als Prädiktor | **abgeschlossen, bestätigt** | Nur aus dem Split: frische Seeds r̄ 0.277 (p < 1e-5), fremde Masken 0.499 (p 5e-5). Post hoc auch in allen MLPs ||| [[experiments/EXP-015-mask-spectrum/README\|EXP-015]] Masken-Spektrum des Splits als Prädiktor | **abgeschlossen, bestätigt** | Nur aus dem Split: frische Seeds r̄ 0.277 (p < 1e-5), fremde Masken 0.499 (p 5e-5). Post hoc auch in allen MLPs |
| [[experiments/EXP-016-engineered-split/README\|EXP-016]] Frequenzen per Datenauswahl steuern | vorbereitet (Nachtrag a: zwei Arme, fester Schritt) | noch kein Lauf |
| [[experiments/EXP-017-rfm-split/README\|EXP-017]] Frequenzwahl ohne Zufalls-Init (RFM) | vorbereitet | noch kein Lauf |
