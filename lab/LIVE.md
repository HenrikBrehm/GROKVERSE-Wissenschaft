---
tags: [lab/live]
---
# LIVE: Laborsitzung 46

- **Sitzungsstart:** 2026-09-29 00:49 Berlin (22:49Z, vom Runner)
- **Deadline:** 2026-09-29 03:49 Berlin (01:49Z)
- **Zuletzt aktualisiert:** 01:34 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.).

## Gerade

GPU (10 Prozesse): **L0-Pilot** Teil 1 und Teil 2 laufen (bisher 22 fertig, 0 Fehler). Danach automatisch: EXP-106 (lange Epochen, B = 16) und die Wechsel-Läufe von L0.

## Als Nächstes

Pilot fertig (≈ 02:20) → `analyze.py` → Nachrechnung; Power für die L0-Registrierung.

## Verlauf dieser Sitzung

- 01:33 **EXP-106 festgelegt:** Menge gegen Reihenfolge bei langen Epochen (B = 16, weight decay 0.1), 64 Läufe, startet nach Pilot-Teil 1.
- 01:30 **B = 16 lernt mit weight decay 0.1** (3/3, auch mit fester Reihenfolge); dort wirkt die Reihenfolge (verschiebt Energie, verzögert ≈ 2000 Schritte), bestimmt aber nicht die stärkste Frequenz (n = 3).
- 01:30 Paper-Textprüfung: 3 Fehler + Präzisierungen in den R10/R11-Abschnitten behoben.
- 01:22 Paper: R11 in Lang- und Kurzfassung, Grenzen angepasst.
- 01:21 **L0-Pilot gestartet** (128 Läufe; Prüfung der Jobliste: kein Blocker).
- 01:21 **R11 unabhängig nachgerechnet:** alle Zahlen gleich.
- 01:19 **R11 bestätigt (alle 6):** Die Festlegung in den ersten 25–50 Schritten gilt auch für add 97 und mul 113.
- 01:18 SGD lässt sich nicht einstellen (lernt nicht oder divergiert) → SGD-Arm „nicht auswertbar“.
- 01:17 Nanda-Messung unabhängig nachgerechnet: alle vier Aufgaben gleich, 20/20.
- 01:13 RFM endgültig: lernt die Aufgabe bei 30 % Daten nicht → keine Aussage zu K2 in RFM.
- 01:06 L0-Machbarkeit: B = 256 keine Reihenfolge-Wirkung, B = 64 knapp, B = 16 Netz lernt nicht.
- 00:52 R11 eingefroren und gestartet.
- 00:50 Selbsttests; RFM-Tor bei 30 Iterationen nicht bestanden.
