---
tags: [lab/live]
---
# LIVE: Laborsitzung 49

- **Sitzungsstart:** 2026-09-29 08:49 Berlin (06:49Z, vom Runner, nach Absturz von Sitzung 48 um 08:24)
- **Deadline:** 2026-09-29 11:49 Berlin (09:49Z)
- **Zuletzt aktualisiert:** 09:13 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe laufen jetzt über den GPU-Dienst (Regel 21).

## Gerade

- **Reproduktionspaket für die Hauptaussagen** (Regel 19c): Skripte für L0, R5, R6 fertig (Smokes ok, Splits bitgleich zu den eingefrorenen); 660 Läufe beim GPU-Dienst eingereiht (laufen nach der Nebenwarteschlange). Jetzt: R8.
- GPU-Dienst: `20_s48c_r0long_10k` läuft (8 Worker). Zwei abgestürzte EXP-105-Prozesse hängen bis ≈ 10:20 (Beenden nicht freigegeben – Entscheidung beim Nutzer).

## Als Nächstes

R8-Repro-Skript; ab ≈ 10:20 EXP-105-Pilot mit `resume_wrapper.py` fortsetzen; Auswertungen, sobald Läufe fertig sind.

## Verlauf dieser Sitzung

- 09:12 R6-Repro fertig (Smoke ok); L0/R5/R6-Volläufe (660) beim Dienst eingereiht.
- 09:05 R5-Repro fertig (Smoke ok, Splits bitgleich).
- 08:58 L0-Repro fertig (Smoke ok, Splits bitgleich).

- 08:53 queue_s48c über die Inbox eingereiht (läuft, 8 Worker).
- 08:51 Pilot-Fortsetzung über die Inbox: RNG-Fehler beim Laden entdeckt, Wrapper geschrieben.
