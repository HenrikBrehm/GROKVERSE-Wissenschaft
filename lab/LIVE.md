---
tags: [lab/live]
---
# LIVE: Laborsitzung 46

- **Sitzungsstart:** 2026-09-29 00:49 Berlin (22:49Z, vom Runner)
- **Deadline:** 2026-09-29 03:49 Berlin (01:49Z)
- **Zuletzt aktualisiert:** 01:23 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.).

## Gerade

GPU: **L0-Pilot** läuft (Menge gegen Reihenfolge unter Minibatch; Teil 1: 64 Läufe) und die B = 16-Sonde (Variante 1 lernt nicht; 2 und 3 laufen). Teil 2 des Piloten startet automatisch. Ein Agent prüft die neuen Paper-Abschnitte (R10, R11) gegen die Quellen.

## Als Nächstes

Pilot beobachten (≈ 1 h) → `analyze.py` → Nachrechnung → Wechsel-Läufe (`switch.txt`).

## Verlauf dieser Sitzung

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
