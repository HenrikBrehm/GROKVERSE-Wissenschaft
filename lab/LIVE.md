---
tags: [lab/live]
---
# LIVE: Laborsitzung 42

- **Sitzungsstart:** 2026-09-28 16:00 Berlin (14:00Z, vom Runner)
- **Deadline:** 2026-09-28 18:59 Berlin (16:59Z)
- **Zuletzt aktualisiert:** 17:01 Berlin
- **Run-Fenster:** heute bis 18:00 (Wächter), ab 29.09. wieder 00:00–13:00.

## Gerade

Die Bestätigung **R10** für den EXP-095-Befund ist vorbereitet (48 frische Seeds, Code-Selbsttest grün). Ein unabhängiger Agent prüft sie vor dem Einfrieren. Gerechnet wird in der Nacht. Die Repro-Kette rechnet P2e, danach mul 113 neu.

## Als Nächstes

Prüfbefunde zu R10 einarbeiten; Repro-Ergebnisse eintragen; Sitzungsabschluss vor 18:50.

## Verlauf dieser Sitzung

- 17:00 R10-Registrierung und Code (n = 48; Power 0.92/1.00/0.99 bei halbem Effekt).
- 16:58 Paper-Absatz zu EXP-095 geprüft: Zahlen stimmen; drei Formulierungen vorsichtiger („Rückkopplung“ war nur vermutet).
- 16:49 Repro **k2 add 97 bitgenau**; k2 mul 113 technisch gescheitert (GPU unter Last), wird neu gerechnet.
- 16:54 **EXP-095: „Auswertungen zählen“** (e8 = +0.14, g8 = c8b genau; nur Anfangsgradient: π 0.10 statt 0.28).
- 16:32 Repro **K4b bitgenau** (N28, 30 Seeds).

- 16:25 EXP-095: ≈ 60/192 Läufe fertig, keine Fehler; Repro k4b läuft (langsamer, GPU geteilt). Literatur zu N48 dokumentiert.
- 16:13 EXP-095-Block gestartet (Smoke 3/3 ok vorher).
- 16:12 Unabhängige Prüfung der Trainer-Option: keine Blocker, zwei kleine Hinweise ohne Handlungsbedarf.
- 16:10 EXP-095 festgelegt (README, design, analyze; Selbsttest grün).
- 16:06 Trainer-Option `--pre-switch-grad-every` gebaut, Test zuerst geschrieben, alle 8 Trainer-Tests grün.
- 16:02 Repro-Kette (Rest) gestartet.
- 16:00 Start: kein STOP, keine Prozesse, Fenster bis 18:00.
