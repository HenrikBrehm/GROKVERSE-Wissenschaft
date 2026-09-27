---
tags: [lab/live]
---
# LIVE: Laborsitzung 36

- **Sitzungsstart:** 2026-09-27 23:39 Berlin (21:39Z, vom Runner)
- **Deadline:** 2026-09-28 02:39 Berlin (00:39Z)
- **Zuletzt aktualisiert:** 23:45 Berlin
- **Run-Fenster:** gesperrt bis Mo 28.09. 01:30 (Nutzer), dann bis 18:00.

## Gerade

Sitzung 35 endete um 23:34 nach 15 min, weil sie auf einen Hintergrund-Wecker gesetzt und die Antwort beendet hat. In einer Runner-Sitzung beendet das die Sitzung. Diese Sitzung bleibt deshalb aktiv bis 01:30 und startet dann selbst.

## Als Nächstes (Plan ab 01:30, unverändert aus Sitzung 35)

1. `--check`, offene Selbsttests (C1/C2-Wrapper, `confirm_r4/r7`, EXP-078/073/075 analyze), dann die Auswertungen EXP-021, EXP-019 (`--device cuda`) und N45.
2. CPU: `night_program.py --cpu --cpu-workers 1 --experiments EXP-040,EXP-014`, daneben 8 GPU-Prozesse.
3. GPU: P2f-Smoke → `--analyze` als Ladertest → `P2f_jobs.txt --workers 8`.

## Verlauf dieser Sitzung

- 23:40 Start: kein STOP, keine Python-Prozesse, Wächter Exit 3 (bis 01:30).
