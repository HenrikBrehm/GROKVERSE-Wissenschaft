---
tags: [lab/live]
---
# LIVE: Laborsitzung 37

- **Sitzungsstart:** 2026-09-28 02:29 Berlin (00:29Z, vom Runner)
- **Deadline:** 2026-09-28 05:29 Berlin (03:29Z)
- **Zuletzt aktualisiert:** 02:53 Berlin
- **Run-Fenster:** heute bis 18:00.

## Gerade

R1-Block läuft (Robustheit K2 gegen Lernrate/Weight Decay/Trainingsanteil, 180 GPU-Läufe, 7 parallel, ≈ 45/180). CPU: EXP-040 Wechselstufe (32 Läufe, ≈ 3 h, läuft über die Deadline hinaus weiter in Sitzung 38).

## Als Nächstes

R1 auswerten (+ C1), dann R6-Block (480 Läufe), R5-Block (140 × 8000), EXP-085, EXP-078 → R7.

## Verlauf dieser Sitzung

- 02:50 **R5 eingefroren** (n = 20; Codex ohne Guthaben, Ersatzprüfung ohne Blocker), Smoke grün.
- 02:46 **EXP-086: Frequenzkonflikt** – ein früher Wechsel kostet nur bei anderen Zielfrequenzen Zeit (D = +0.82 log2, 9/10, p = 0.011; Pilot).
- 02:46 R1-Block gestartet.
- 02:40 **R1 und R6 eingefroren** (6298e67, 5b2bca6), Smokes grün.
- 02:39 Paper §3.6: P2f/S1/C4 eingearbeitet, unabhängig geprüft (keine Zahlenfehler).
- 02:34 Repro-Gleichwertigkeit bestanden (bitgleich).
- 02:31 EXP-086 gestartet (Smoke grün).
- 02:30 **EXP-074 Zeitkosten:** VO-Reset kostet mehr Zeit als QK-Reset (18/18, p = 3.8e-6).
- 02:30 CPU-Programm EXP-040/014 neu gestartet.
