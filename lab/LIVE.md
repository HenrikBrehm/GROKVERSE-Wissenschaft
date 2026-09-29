---
tags: [lab/live]
---
# LIVE: Laborsitzung 49

- **Sitzungsstart:** 2026-09-29 08:49 Berlin (06:49Z, vom Runner, nach Absturz von Sitzung 48 um 08:24)
- **Deadline:** 2026-09-29 11:49 Berlin (09:49Z)
- **Zuletzt aktualisiert:** 09:38 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.). Lange Läufe laufen jetzt über den GPU-Dienst (Regel 21).

## Gerade

- Repro-Paket: **L0 nachgerechnet** – B 256 exakt gleich (20/20 Läufe bitgleich), B 64 gleiches Urteil, aber 3/20 Läufe laufen spät auseinander (vermutlich GPU-Rauschen) → formal „nicht numerisch reproduziert“. R5/R6/R8/R4 rechnen beim GPU-Dienst.
- Paper-Anhang K mit den neuen Ergebnissen ergänzt; unabhängige Textprüfung läuft.
- Zwei hängende EXP-105-Prozesse bis ≈ 10:20; Pilot-Fortsetzung liegt als `11_` in der Inbox (läuft mit altem Dienstcode erst nach den Repro-Läufen).

## Als Nächstes

Textprüfung einarbeiten; R5-Repro auswerten, sobald fertig; Tageserklärung ergänzen.

## Verlauf dieser Sitzung

- 09:36 Repro L0 verglichen (H1 exakt, H2 spät abweichend); Anhang K ergänzt.
- 09:34 Nachrechnung EXP-102/112 bestätigt (mit Vorbehalt „gleiche Schritte ≠ gleiches Stadium“).
- 09:26 EXP-102 „r0 lang“: Abstand bleibt; EXP-112 „10k“: „nur verzögert“.
- 09:25 R8- und R4-Repro fertig, eingereiht.

- 09:12 R6-Repro fertig (Smoke ok); L0/R5/R6-Volläufe (660) beim Dienst eingereiht.
- 09:05 R5-Repro fertig (Smoke ok, Splits bitgleich).
- 08:58 L0-Repro fertig (Smoke ok, Splits bitgleich).

- 08:53 queue_s48c über die Inbox eingereiht (läuft, 8 Worker).
- 08:51 Pilot-Fortsetzung über die Inbox: RNG-Fehler beim Laden entdeckt, Wrapper geschrieben.
