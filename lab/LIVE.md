---
tags: [lab/live]
---
# LIVE: Laborsitzung 46: **Sitzung beendet**

- **Sitzungsstart:** 2026-09-29 00:49 Berlin (22:49Z, vom Runner)
- **Deadline:** 2026-09-29 03:49 Berlin (01:49Z)
- **Zuletzt aktualisiert:** 03:21 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.).

## Gerade

**Sitzung beendet** (03:21). Keine laufenden Prozesse. Abschlussbericht im JOURNAL.

## Als Nächstes

Nächster Runner-Start laut runner-state.json **29.09. 04:24 Berlin**: Literatur und Registrierung zu N54b (Wurzel-Uhr), L0b (Reihenfolge bei langen Epochen), Paper-Langfassung ergänzen.

## Verlauf dieser Sitzung

- 03:21 Sitzung beendet (Bericht im JOURNAL).
- 03:22 **EXP-108: Die Festlegung wandert mit der Wurzel der Schritte pro Durchgang** (Vorhersage für B 1024: 60–67, gemessen 62); nachgerechnet.
- 03:07 EXP-108 festgelegt und gestartet (Vorhersage Wurzel-Uhr: B 64 ≈ 240, B 1024 ≈ 60 Schritte).
- 03:05 Paper: §6 und Abstract nach unabhängiger Textprüfung korrigiert (Abstract 1875 Zeichen).
- 03:04 EXP-103 (Füllarbeit): lr·wd-Uhr ab ≈ 250 Schritten, davor zählt die Lernrate allein.
- 03:00 **EXP-107: Unter Päckchen (B 256) legt sich die Wahl bei 100–200 Schritten fest** (Full-Batch ≈ 30); nachgerechnet.
- 02:56 **L0 BESTÄTIGT:** Steuerung durch die Menge hält unter Päckchen-Training (10/10 frische Netze bei B 256 und 64); nachgerechnet.
- 02:51 **EXP-106:** bei langen Epochen steuert die Menge; feste Reihenfolge verschiebt nur Zufallssplits, kostet bei konstruierten Splits Zeit.
- 02:37 L0-Bestätigung: Smoke ok, Block gestartet. EXP-107 festgelegt.
- 02:33 **Unter Päckchen-Training (B = 256) keine Festlegung bis 50 Schritte** (Full-Batch-Fenster repliziert). Kein Horizont-Artefakt. Vermutung: zählt in Epochen.
- 02:25 **L0-Bestätigung eingefroren** (H1/H2, n = 10; Prüfung: kein Blocker, Text nachgeschärft).
- 02:12 L0-Pilot unabhängig nachgerechnet; Paper §6 mit Ergebnis gefüllt; Abb. 4 gezeichnet.
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
