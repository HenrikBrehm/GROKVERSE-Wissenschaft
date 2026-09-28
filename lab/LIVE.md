---
tags: [lab/live]
---
# LIVE: Laborsitzung 46

- **Sitzungsstart:** 2026-09-29 00:49 Berlin (22:49Z, vom Runner)
- **Deadline:** 2026-09-29 03:49 Berlin (01:49Z)
- **Zuletzt aktualisiert:** 00:54 Berlin
- **Run-Fenster:** offen (durchgehend bis 06.10.).

## Gerade

R11 (Festlegung bei add 97 / mul 113, 240 GPU-Läufe) eingefroren und gestartet (5 Worker). Daneben L0-Machbarkeit (18 Läufe × 30 000 Schritte, 5 Worker). Ich suche derweil den Fehler im Selbsttest von `EXP-100/analyze.py`.

## Als Nächstes

`feas_read.py` → Vorhersage-Test `mask_prediction_s45.py` → Kalibrierung SGD. EXP-101 (RFM) ins README eintragen.

## Verlauf dieser Sitzung

- 00:53 L0-Machbarkeit gestartet (18 Läufe).
- 00:52 R11 eingefroren (Manifest-Commit), Smoke 3/3 geladen, Block gestartet.
- 00:51 L0-Smoke 3/3 ok (0.011 s/Schritt bei 3 GPU-Prozessen; Minibatch-Reihenfolge wird protokolliert).
- 00:50 EXP-101 (RFM) ausgewertet: **Tor nicht bestanden** — RFM generalisiert auf dem Zufallssplit 30 % bei p = 113 nicht → keine K2-Lesart in RFM. `analyze.py --selftest` (L0) scheitert, `switch_analyze.py --selftest` ok, R11-Selbsttest ok.
