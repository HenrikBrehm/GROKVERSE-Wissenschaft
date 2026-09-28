---
tags: [lab/live]
---
# LIVE: Laborsitzung 40

- **Sitzungsstart:** 2026-09-28 10:29 Berlin (08:29Z, vom Runner)
- **Deadline:** 2026-09-28 13:29 Berlin (11:29Z)
- **Zuletzt aktualisiert:** 11:32 Berlin
- **Run-Fenster:** heute bis 18:00.

## Gerade

Beide Blöcke ausgewertet. Ich baue jetzt eine Trainer-Option für den entscheidenden Test: Liegt die stärkere Festlegung nach vielen kleinen Schritten an Adams Mittelungsfenstern (β), die in Schritten zählen?

## Als Nächstes

Option `--pre-switch-betas` + Tests + unabhängige Prüfung, dann Pilot EXP-090 (≈ 20 min GPU).

## Verlauf dieser Sitzung

- 11:28 **EXP-081 fertig:** Teil A *N38 gestützt* (Momentum-Schwanz trägt zur Festlegung bei, wächst mit β₁; 9/10); Teil B *N37 verworfen* (β₂ skaliert das Fenster nicht). Post hoc: längeres β₁-Fenster → deutlich weniger Festlegung beim Wechsel (9/10).
- 11:22 EXP-089 gegengeprüft: Effekt hält; Deutung korrigiert (führend: Adams β-Fenster zählen in Schritten).
- 11:05 **EXP-089 fertig: Mischuhr gestützt** (Pilot): bei gleicher Lernratensumme hält die Wahl nach 100 kleinen Schritten stärker fest als nach 25 normalen (+0.24, 10/10); Größe wie vorhergesagt (τ ≈ Λ^0.8·t^0.2). Unabhängige Gegenprüfung läuft.
- 10:45 EXP-089 registriert (vor jedem Ergebnis), Smoke ok, Block gestartet.
- 10:41 Paper §4: EXP-087/088 eingearbeitet, unabhängig geprüft (keine Zahlenfehler; 6 Formulierungen korrigiert).
- 10:37 EXP-081-Block gestartet (Smoke ok: alle vier β-Zellen stabil, generalisiert).
- 10:35 EXP-081 Endfassung registriert (Nachtrag d, Splits Seeds 830–839, Jobs, Auswertung mit Selbsttest; 05157f0c).
- 10:30 Start: kein STOP, Fenster offen, keine Python-Prozesse, Stand gelesen.
