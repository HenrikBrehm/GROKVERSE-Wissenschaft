---
tags: [lab/live]
---
# LIVE: Laborsitzung 44

- **Sitzungsstart:** 2026-09-28 20:19 Berlin (18:19Z, vom Runner)
- **Deadline:** 2026-09-28 23:19 Berlin (21:19Z)
- **Zuletzt aktualisiert:** 20:31 Berlin
- **Run-Fenster:** zu (Wächter: outside_window); öffnet 23:59, also nach dieser Sitzung. Diese Sitzung trainiert und testet nicht.

## Gerade

Zwei unabhängige Prüfungen laufen (nur lesend): `rfm_k2.py` (EXP-101) und `lm_ladder.py` (EXP-102). Danach Befunde einarbeiten, JOURNAL/STATE, Commit.

## Als Nächstes

Nächste Sitzung 23:54 Berlin; ab 23:59 R10 fertig, dann L0. EXP-101 (CPU) kann parallel zu R10 laufen: Selbsttest → Nachbau p 61 → 30 Läufe.

## Verlauf dieser Sitzung

- 20:30 EXP-102: Trainer `lm_ladder.py` für die Sprachmodell-Leiter geschrieben (ungetestet); Designpunkt: Verlust auf allen Positionen macht p(b|a) des Splits zum Ziel → Kontrollarm „alle außer b“.
- 20:27 Zenodo: absoluter Benutzerpfad in 6 von 7 Repro-Dateien ersetzt (k2.py bleibt, R7 bindet den Hash).
- 20:26 EXP-101: `rfm_k2.py` (eigene Gauß-RFM, schnelle AGOP, Lesarten vorab), keine Installation nötig.
- 20:20 Stand gelesen: keine Prozesse, kein STOP, R10 bei 268/480 (ungesehen). RFM-Code braucht für den Gauß-Pfad nur torch/numpy + `scipy.linalg.sqrtm` → keine Installation nötig.
