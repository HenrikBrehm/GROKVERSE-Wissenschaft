---
tags: [lab/live]
---
# LIVE: Laborsitzung 44

- **Sitzungsstart:** 2026-09-28 20:19 Berlin (18:19Z, vom Runner)
- **Deadline:** 2026-09-28 23:19 Berlin (21:19Z)
- **Zuletzt aktualisiert:** 20:43 Berlin
- **Run-Fenster:** zu (Wächter: outside_window); öffnet 23:59, also nach dieser Sitzung. Diese Sitzung trainiert und testet nicht.

## Gerade

Nächste Denkarbeit wählen (Fenster zu). Vorbereitet sind jetzt EXP-101 (RFM), EXP-102 (Sprachmodell-Leiter), EXP-103 (lr·wd-Zeit, frühe Kurve + gekreuzte Zellen).

## Als Nächstes

Nächste Sitzung 23:54 Berlin; ab 23:59 R10 fertig → L0. Füllarbeit: EXP-101 (CPU), EXP-103 (GPU, 140 kurze Läufe, ≤ 4 Worker).

## Verlauf dieser Sitzung

- 20:43 EXP-103 vorbereitet: dichte frühe P1-Kurve + gekreuzte Zellen lr 2e-3/wd 0.5 und lr 5e-4/wd 2 (gepaart mit P1).
- 20:42 Nachrechnung R1: Zahlen stimmen; Deutung eingeschränkt (4 Zellen, kleine Reste, Produktform ungeprüft).
- 20:39 **R1 post hoc:** Δ_pow-Größen der lr/wd-Zellen liegen ab τ = t·lr·wd ≥ 250 auf der P1-Kurve (±4 %); vorab-Lesart nur „teilweise“ (Abweichung bei τ < 250).
- 20:37 N50 (braucht K2 Auswahldruck?) mit Literatursuche; neue Arbeit Pracher et al. 2026 (Zeitskala ∝ lr·wd).
- 20:35 EXP-102: Prüfung (1 Blocker: Split-Reihenfolge) behoben; Splits 3800–3809, 140 Jobs, Auswertung.
- 20:30 EXP-102: Trainer `lm_ladder.py` für die Sprachmodell-Leiter geschrieben (ungetestet); Designpunkt: Verlust auf allen Positionen macht p(b|a) des Splits zum Ziel → Kontrollarm „alle außer b“.
- 20:27 Zenodo: absoluter Benutzerpfad in 6 von 7 Repro-Dateien ersetzt (k2.py bleibt, R7 bindet den Hash).
- 20:26 EXP-101: `rfm_k2.py` (eigene Gauß-RFM, schnelle AGOP, Lesarten vorab), keine Installation nötig.
- 20:20 Stand gelesen: keine Prozesse, kein STOP, R10 bei 268/480 (ungesehen). RFM-Code braucht für den Gauß-Pfad nur torch/numpy + `scipy.linalg.sqrtm` → keine Installation nötig.
