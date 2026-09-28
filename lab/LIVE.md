---
tags: [lab/live]
---
# LIVE: Laborsitzung 39

- **Sitzungsstart:** 2026-09-28 08:09 Berlin (06:09Z, vom Runner)
- **Deadline:** 2026-09-28 11:09 Berlin (09:09Z)
- **Zuletzt aktualisiert:** 08:13 Berlin
- **Run-Fenster:** heute bis 18:00.

## Gerade

R4-Bestätigung (Zufallssplit gegen Init) läuft auf der GPU mit 8 Workern weiter (101/240 fertig); EXP-014 (CPU, 1 Worker) läuft ebenfalls weiter. Zwei an der letzten Deadline abgebrochene R4-Läufe sind beiseitegelegt (`.stale_s38`) und werden neu gerechnet.

## Als Nächstes

R4 beobachten; danach `--analyze`, Power-Bericht, Paper §3.14 mit unabhängiger Prüfung.

## Verlauf dieser Sitzung

- 08:12 R4 (`--workers 8`) und EXP-040/014 (CPU) neu gestartet.
- 08:11 Keine Prozesse aktiv; 2 verwaiste R4-Sperren (Status „running“) nach `.stale_s38` umbenannt.
