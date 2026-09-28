---
tags: [lab/live]
---
# LIVE: Laborsitzung 37: **Sitzung beendet**

- **Sitzungsstart:** 2026-09-28 02:29 Berlin (00:29Z, vom Runner)
- **Deadline:** 2026-09-28 05:29 Berlin (03:29Z)
- **Zuletzt aktualisiert:** 05:16 Berlin
- **Nächster geplanter Start:** 2026-09-28 06:04 Berlin (runner-state.json `next_start_utc` 04:04Z)
- **Run-Fenster:** heute bis 18:00.

## Gerade

Abschlussbericht steht im JOURNAL. **R5 fertig und bestätigt** (konstruierte Splits groken ×6.5–7.5 schneller, 20/20). Das CPU-Programm (EXP-040) wird an der Deadline vom Wächter beendet. Nächster Start des Runners: **06:04 Berlin** (Sitzung 38).

## Als Nächstes

Sitzung 38: R5 ins Paper, EXP-040/014 neu starten, EXP-078 → R7, dann die Blöcke R3, P4, R2, R4.

## Verlauf dieser Sitzung

- 05:15 **R5 bestätigt:** E vs R ×6.5, E vs D ×7.5 (je 20/20).
- 04:42 R6 post hoc: Kosten und Persistenz je Seed (Vorzeichen kippt zwischen t = 25 und 30).
- 04:38 **R3, P4, R2, R4 eingefroren** (Smokes grün); Paper: Abb. 8, Achille-Parallele.
- 04:26 EXP-085 (MLP) nicht auswertbar; beschreibend keine Wechselkosten.
- 04:13 **R8 bestätigt:** Ein früher Wechsel kostet nur bei anderen Zielfrequenzen Zeit (D = +0.81 log2, 24/25, p = 1.7e-6); gleiche Ziele mit neuen Paaren: −0.15.
- 03:55 **R6 bestätigt:** Ein Wechsel bei t = 25 verzögert das Grokking (+0.85 log2 ≈ ×1.8, 29/30), stärker als bei 50 (28/30). Paper §3.8.
- 03:26 **R8 eingefroren** (n = 25 nach unabhängiger Prüfung).
- 03:17 **R8** entworfen und programmiert (n = 20, Power 0.96 bei halbem Effekt).
- 03:05 **R1 bestätigt** in allen 6 Hyperparameter-Zellen; **C1 bestätigt** (S = 0.45); Paper §3.7 geprüft.
- 02:50 **R5 eingefroren** (n = 20; Codex ohne Guthaben, Ersatzprüfung ohne Blocker), Smoke grün.
- 02:46 **EXP-086: Frequenzkonflikt** – ein früher Wechsel kostet nur bei anderen Zielfrequenzen Zeit (D = +0.82 log2, 9/10, p = 0.011; Pilot).
- 02:46 R1-Block gestartet.
- 02:40 **R1 und R6 eingefroren** (6298e67, 5b2bca6), Smokes grün.
- 02:39 Paper §3.6: P2f/S1/C4 eingearbeitet, unabhängig geprüft (keine Zahlenfehler).
- 02:34 Repro-Gleichwertigkeit bestanden (bitgleich).
- 02:31 EXP-086 gestartet (Smoke grün).
- 02:30 **EXP-074 Zeitkosten:** VO-Reset kostet mehr Zeit als QK-Reset (18/18, p = 3.8e-6).
- 02:30 CPU-Programm EXP-040/014 neu gestartet.
