---
tags: [lab/live]
---
# LIVE: Laborsitzung 40

- **Sitzungsstart:** 2026-09-28 10:29 Berlin (08:29Z, vom Runner)
- **Deadline:** 2026-09-28 13:29 Berlin (11:29Z)
- **Zuletzt aktualisiert:** 10:39 Berlin
- **Run-Fenster:** heute bis 18:00.

## Gerade

**EXP-081 läuft** (500 GPU-Läufe, 8 Worker; ≈ 5 Läufe/min → fertig ≈ 12:15). Frage: Legt β₁ über den Momentum-Schwanz fest, wie stark die frühe Frequenzwahl nach einem Datenwechsel hält (N38)? Skaliert das Fenster mit β₂ (N37)?
Daneben: EXP-087/088 in Paper §4 eingearbeitet, unabhängige Prüfung läuft.

## Als Nächstes

Fortschritt alle ~10 min prüfen; nach dem Block `analyze.py`, Ergebnis dokumentieren.

## Verlauf dieser Sitzung

- 10:37 EXP-081-Block gestartet (Smoke ok: alle vier β-Zellen stabil, generalisiert).
- 10:35 EXP-081 Endfassung registriert (Nachtrag d, Splits Seeds 830–839, Jobs, Auswertung mit Selbsttest; 05157f0c).
- 10:30 Start: kein STOP, Fenster offen, keine Python-Prozesse, Stand gelesen.
