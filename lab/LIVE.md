---
tags: [lab/live]
---
# LIVE: Laborsitzung 24

- **Sitzungsstart:** 2026-09-27 12:29 Berlin (10:29Z, vom Runner)
- **Deadline:** 2026-09-27 15:29 Berlin (13:29Z)
- **Zuletzt aktualisiert:** 12:40 Berlin (gemessen)
- **Run-Fenster:** offen bis 13:00, danach nur Denk- und Vorbereitungsarbeit.

## Gerade

Drei Dinge laufen bis zum Fensterende (~12:57): CPU-Programm (EXP-042); **EXP-071** (110 kurze GPU-Laeufe: sagt die Ausrichtung des Attention-Wertepfads beim Datenwechsel voraus, wie fest ein Seed an seiner ersten Wahl haengt?); **EXP-072** (10 lange D59-Laeufe: generalisiert die nicht-abelsche Gruppe ueberhaupt? In P1 nach 2000 Schritten 0/100).

## Als Naechstes

EXP-071 auswerten; EXP-072-Verlauf lesen (auch wenn der Waechter die Laeufe um 12:57 beendet); danach D59-Plan (P2f) je nach Ergebnis.

## Verlauf dieser Sitzung

- 12:40 EXP-072 Zwischenstand: D59 generalisiert doch, meist zwischen 3000 und 7000 Schritten (5 von 10 Laeufen bei Schritt 6000 schon ueber 0.99).
- 12:39 **EXP-071 (Exploration): unklar, schwacher Hinweis.** Seeds mit staerker ausgerichtetem Wertepfad beim Wechsel haengen etwas fester an der ersten Wahl (r = 0.45, p = 0.09, n = 10); den zeitlichen Verlauf erklaert das Mass nicht besser als die Schrittzahl.
- 12:37 EXP-072 festgelegt und gestartet (D59 generalisiert in P1 nie: 0/100 nach 2000 Schritten).
- 12:33 EXP-071 festgelegt und gestartet.
- 12:30 Stand gelesen, kein STOP, keine laufenden Prozesse; CPU-Programm gestartet.
