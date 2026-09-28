---
tags: [lab/live]
---
# LIVE: Laborsitzung 40

- **Sitzungsstart:** 2026-09-28 10:29 Berlin (08:29Z, vom Runner)
- **Deadline:** 2026-09-28 13:29 Berlin (11:29Z)
- **Zuletzt aktualisiert:** 10:45 Berlin
- **Run-Fenster:** heute bis 18:00.

## Gerade

**EXP-081 läuft** (500 GPU-Läufe, 8 Worker; ≈ 13 Läufe/min → fertig ≈ 11:20). Frage: Legt β₁ über den Momentum-Schwanz fest, wie stark die frühe Frequenzwahl nach einem Datenwechsel hält (N38)? Skaliert das Fenster mit β₂ (N37)?
**EXP-089 läuft daneben** (120 Läufe, 4 Worker): Hält die Festlegung bei gleicher Lernratensumme Λ nach 100 kleinen Schritten stärker als nach 25 normalen?

## Als Nächstes

Fortschritt alle ~10 min prüfen; nach dem Block `analyze.py`, Ergebnis dokumentieren.

## Verlauf dieser Sitzung

- 10:45 EXP-089 registriert (vor jedem Ergebnis), Smoke ok, Block gestartet.
- 10:41 Paper §4: EXP-087/088 eingearbeitet, unabhängig geprüft (keine Zahlenfehler; 6 Formulierungen korrigiert).
- 10:37 EXP-081-Block gestartet (Smoke ok: alle vier β-Zellen stabil, generalisiert).
- 10:35 EXP-081 Endfassung registriert (Nachtrag d, Splits Seeds 830–839, Jobs, Auswertung mit Selbsttest; 05157f0c).
- 10:30 Start: kein STOP, Fenster offen, keine Python-Prozesse, Stand gelesen.
