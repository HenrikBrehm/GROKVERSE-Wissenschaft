---
tags: [lab/live]
---
# LIVE: Laborsitzung 46

- **Sitzungsstart:** 2026-09-29 00:49 Berlin (22:49Z, vom Runner)
- **Deadline:** 2026-09-29 03:49 Berlin (01:49Z)
- **Zuletzt aktualisiert:** 02:12 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.).

## Gerade

GPU: EXP-106 (lange Epochen, 64 Läufe) und L0-Wechselläufe (64) laufen. Ein Agent rechnet den L0-Piloten unabhängig nach.

## Als Nächstes

Nachrechnung prüfen → Ergebnis ins Paper (§6 Kurzfassung) → `switch_analyze.py` → EXP-106 auswerten → L0-Registrierung (H3?) einfrieren.

## Verlauf dieser Sitzung

- 02:07 **L0-Pilot fertig: Die Menge steuert auch unter Päckchen-Training** (B 256 und 64, so stark wie Full-Batch); eine feste Reihenfolge wirkt dort gar nicht (0/16). L0-Bestätigung braucht nur n = 10.
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
