---
tags: [lab/live]
---
# LIVE: Laborsitzung 42

- **Sitzungsstart:** 2026-09-28 16:00 Berlin (14:00Z, vom Runner)
- **Deadline:** 2026-09-28 18:59 Berlin (16:59Z)
- **Zuletzt aktualisiert:** 16:56 Berlin
- **Run-Fenster:** heute bis 18:00 (Wächter), ab 29.09. wieder 00:00–13:00.

## Gerade

**EXP-095 fertig: Die frühe Festlegung braucht frische Gradienten unterwegs.** Wird der Gradient in den ersten 24 Schritten nur 3-mal neu berechnet, legt das Modell genauso schwach fest wie mit 3 großen Schritten (Unterschied 0.000). Nur mit dem Anfangsgradienten bewegt es sich sogar weiter, aber ungezielt. Jetzt: FINDINGS, Paper §4, LAB nachführen. Repro läuft weiter (k2 mul 113).

## Als Nächstes

Paper-Absatz unabhängig prüfen lassen; Repro-Rest eintragen; Nachtplanung (Bestätigung EXP-092–095-Linie?).

## Verlauf dieser Sitzung

- 16:54 **EXP-095: „Auswertungen zählen“** (e8 = +0.14, g8 = c8b genau; nur Anfangsgradient: π 0.10 statt 0.28).
- 16:32 Repro **K4b bitgenau** (N28, 30 Seeds).

- 16:25 EXP-095: ≈ 60/192 Läufe fertig, keine Fehler; Repro k4b läuft (langsamer, GPU geteilt). Literatur zu N48 dokumentiert.
- 16:13 EXP-095-Block gestartet (Smoke 3/3 ok vorher).
- 16:12 Unabhängige Prüfung der Trainer-Option: keine Blocker, zwei kleine Hinweise ohne Handlungsbedarf.
- 16:10 EXP-095 festgelegt (README, design, analyze; Selbsttest grün).
- 16:06 Trainer-Option `--pre-switch-grad-every` gebaut, Test zuerst geschrieben, alle 8 Trainer-Tests grün.
- 16:02 Repro-Kette (Rest) gestartet.
- 16:00 Start: kein STOP, keine Prozesse, Fenster bis 18:00.
