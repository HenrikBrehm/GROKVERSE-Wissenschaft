---
tags: [lab/live]
---
# LIVE: Laborsitzung 37

- **Sitzungsstart:** 2026-09-28 02:29 Berlin (00:29Z, vom Runner)
- **Deadline:** 2026-09-28 05:29 Berlin (03:29Z)
- **Zuletzt aktualisiert:** 04:00 Berlin
- **Run-Fenster:** heute bis 18:00.

## Gerade

R8-Block läuft (Frequenzkonflikt, 175 Läufe, gestartet 03:55). Danach startet automatisch EXP-085. Ein Prüfagent kontrolliert Paper §3.8 (R6). CPU: EXP-040.

## Als Nächstes

R8 auswerten (≈ 04:25), Sitzungsende 05:29 → Abschlussbericht. Sitzung 38: R5-Block, EXP-078 → R7, R3, P4, R2, R4.

## Verlauf dieser Sitzung

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
