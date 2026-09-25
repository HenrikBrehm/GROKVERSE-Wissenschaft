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
| [[experiments/EXP-003-early-prediction/CONFIRM_d\|EXP-003d]] frische Seeds 10–19 | vorbereitet | noch kein Lauf |
| [[experiments/EXP-009-freq-commitment/SUMMARY\|EXP-009]] Frequenz-Lotterie / Lock-in (Auswertung) | abgeschlossen | Init-Spektrum von W_E trägt Information über die finalen Top-5 (r̄ = 0.386 vs. 0.5, p < 1e-5, seed-spezifisch). Bei der Two-hot-MLP nur pro Neuron |
| [[experiments/EXP-010-init-swap/README\|EXP-010]] Init-Tausch (kausal) | vorbereitet | noch kein Lauf |
