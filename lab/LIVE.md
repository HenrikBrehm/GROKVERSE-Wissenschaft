---
tags: [lab/live]
---
# LIVE: Laborsitzung 49

- **Sitzungsstart:** 2026-09-29 08:49 Berlin (06:49Z, vom Runner, nach Absturz von Sitzung 48 um 08:24)
- **Deadline:** 2026-09-29 11:49 Berlin (09:49Z)
- **Zuletzt aktualisiert:** 11:20 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe laufen jetzt über den GPU-Dienst (Regel 21).

## Gerade

- **Sitzung beendet.** Nächster geplanter Start laut Runner: 12:24 Berlin (10:24Z). Der GPU-Dienst rechnet weiter: Repro R4, dann EXP-113 (Sprachmodell Stufe 2b, mehrere Stunden).

## Als Nächstes

Nächste Sitzung: R4-Vergleich; EXP-113 beobachten und am Budgetende auswerten.

## Verlauf dieser Sitzung

- 11:20 Sitzungsende; R6 und R8 exakt reproduziert (11:14 / 11:20).
- 10:45 Anhang R (Reproduktion) geprüft und korrigiert.

- 10:33 EXP-113 vorab festgelegt, GPU-Selbsttest ok, eingereiht.
- 10:32 R5 exakt reproduziert; L0-Abweichung = GPU-Nichtdeterminismus.
- 10:27 EXP-105-Pilot ausgewertet: „unklar“.

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
