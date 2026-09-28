---
tags: [lab/live]
---
# LIVE: Laborsitzung 37

- **Sitzungsstart:** 2026-09-28 02:29 Berlin (00:29Z, vom Runner)
- **Deadline:** 2026-09-28 05:29 Berlin (03:29Z)
- **Zuletzt aktualisiert:** 03:18 Berlin
- **Run-Fenster:** heute bis 18:00.

## Gerade

R6-Block läuft (480 GPU-Läufe, ≈ 110/480, voraussichtlich fertig ≈ 04:40). R8 (Bestätigung Frequenzkonflikt) ist geschrieben, der Selbsttest ist grün, eine unabhängige Prüfung läuft. CPU: EXP-040.

## Als Nächstes

R8 einfrieren, danach R6 auswerten, dann R8-Block (≈ 20 min). R5 folgt in Sitzung 38.

## Verlauf dieser Sitzung

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
