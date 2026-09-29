---
tags: [lab/live]
---
# LIVE: Laborsitzung 49

- **Sitzungsstart:** 2026-09-29 08:49 Berlin (06:49Z, vom Runner, nach Absturz von Sitzung 48 um 08:24)
- **Deadline:** 2026-09-29 11:49 Berlin (09:49Z)
- **Zuletzt aktualisiert:** 09:51 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe laufen jetzt über den GPU-Dienst (Regel 21).

## Gerade

- GPU-Dienst rechnet das Repro-Paket (R5 läuft, danach R6, R8, R4; ≈ bis 11:20). Zenodo-Paket ergänzt und aus frisch entpackten Dateien getestet.
- Zwei hängende EXP-105-Prozesse bis ≈ 10:20; Pilot-Fortsetzung (`11_`) läuft mit altem Dienstcode erst nach den Repro-Läufen.

## Als Nächstes

R5-Repro auswerten (≈ 10:20); danach R6/R8/R4; Pilot, sobald er gelaufen ist.

## Verlauf dieser Sitzung

- 09:51 Zenodo-Paket: fehlende Module ergänzt, Import-Test bestanden.
- 09:47 Anhang K geprüft und korrigiert; FINDINGS-Nachtrag.

- 09:36 Repro L0 verglichen (H1 exakt, H2 spät abweichend); Anhang K ergänzt.
- 09:34 Nachrechnung EXP-102/112 bestätigt (mit Vorbehalt „gleiche Schritte ≠ gleiches Stadium“).
- 09:26 EXP-102 „r0 lang“: Abstand bleibt; EXP-112 „10k“: „nur verzögert“.
- 09:25 R8- und R4-Repro fertig, eingereiht.

- 09:12 R6-Repro fertig (Smoke ok); L0/R5/R6-Volläufe (660) beim Dienst eingereiht.
- 09:05 R5-Repro fertig (Smoke ok, Splits bitgleich).
- 08:58 L0-Repro fertig (Smoke ok, Splits bitgleich).

- 08:53 queue_s48c über die Inbox eingereiht (läuft, 8 Worker).
- 08:51 Pilot-Fortsetzung über die Inbox: RNG-Fehler beim Laden entdeckt, Wrapper geschrieben.
