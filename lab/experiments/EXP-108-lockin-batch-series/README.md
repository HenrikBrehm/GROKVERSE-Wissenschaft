---
id: EXP-108
status: laufend
datum: 2026-09-29
tags: [exp/laufend, neu/kandidat]
---
# EXP-108 (N54b, Exploration): Wie verschiebt sich das Festlegungsfenster mit der Batchgröße?

Zurück: [[LAB]] · [[FINDINGS]] (K4 / Result 3; L0) · [[NOVEL_DIRECTIONS]] N54 · Vorgänger [[experiments/EXP-107-lockin-epochs/README|EXP-107]], [[experiments/EXP-100-set-vs-order/README|EXP-100]]

**Stand:** festgelegt Sitzung 46 (2026-09-29, ≈ 03:10 Berlin), **vor jedem EXP-108-Lauf**; Läufe gestartet direkt danach. **Auswertungscode folgt in der nächsten Sitzung** (die Lesarten unten sind jetzt fest; der Code darf sie nur umsetzen).

**Gesehen:** Full-Batch t½ ≈ 31 Schritte (EXP-100-Referenz, π(25) 0.38, π(50) 0.87, lineare Interpolation), B = 256 t½ ≈ 133 Schritte (EXP-107, gleiche Seeds). Daraus die post-hoc Vermutung N54b: Uhr ∝ √(N/B) (Exponent aus den zwei Punkten: log(133/31)/log(15) = 0.54).

**Aufbau:** EXP-100-Splits, Seeds 3700–3707, i.i.d.-Minibatch AdamW (lr 1e-3, wd 1), Wechsel F → G und G → F; B = 64 bei t = 100, 200, 300, 450, 700; B = 1024 bei t = 25, 50, 75, 100, 150; jeder Lauf 5000 Schritte; reine Läufe: B 64 aus dem EXP-100-Piloten (iid64, Schnappschuss 5000), B 1024 neu hier (16 Läufe). 176 Läufe, GPU. π wie EXP-107 (W_E-Gruppenleistung bei Schritt 5000; Seed gültig, wenn alle Läufe laden und L_F − L_G ≥ 0.5).

**Vorhersagen (vor dem Lauf):**
| B | N/B | Schritt-Uhr | Wurzel-Uhr (∝ √(N/B), verankert an Full-Batch 31) | Epochen-Uhr (∝ N/B) |
|---|---|---|---|---|
| 1024 | 3.7 | ≈ 31 | **≈ 60** (an B 256 verankert: 67) | ≈ 116 |
| 256 | 15 | ≈ 31 | 120 (beobachtet 133) | 465 |
| 64 | 60 | ≈ 31 | **≈ 240** (an B 256 verankert: 266) | ≈ 1856 (> Raster, π(700) < 0.5) |

**Lesarten (fest):** t½ je Seed und B durch lineare Interpolation von π zwischen den Rasterpunkten (π(0) = 0); liegt π am größten t noch < 0.5, gilt t½ > t_max (zensiert). Exponent α = Steigung von log t½ gegen log(N/B) über B ∈ {64, 256 (EXP-107), 1024} je Seed, Full-Batch-Punkt (N/B = 1, 31 Schritte) fest; Mittel über Seeds mit Bootstrap-95-%-KI.
- „**Wurzel-Uhr gestützt**“: KI von α ganz in [0.3, 0.7].
- „**Epochen-Uhr**“: KI ganz in [0.8, 1.2]. „**Schritt-Uhr**“: KI ganz in [−0.2, 0.2].
- Sonst „**gemischt/andere**“ (α und KI berichten). Zensierte Seeds (B 64 mit π(700) < 0.5) gehen mit t½ = 700 als untere Schranke ein und werden gezählt; mehr als 2 zensierte Seeds bei B 64 → Lesart nur „t½(64) > 700, gegen Wurzel-Uhr“.
- Beschreibend: π je B und t mit KI; Punktvergleich t½(64) und t½(1024) mit den Vorhersagen.
**Dagegen spräche die Wurzel-Uhr:** t½(64) ≫ 340 oder t½(1024) ≳ 100.
**Grenzen:** 8 Seeds (gleiche wie EXP-100/107), Energiemaß, eine Aufgabe, Full-Batch-Punkt interpoliert und bei anderem Horizont gelesen; B 64 ist am Ende oft nicht eingeschwungen (EXP-100/L0).

```
python lab/tools/parallel_queue.py lab/experiments/EXP-108-lockin-batch-series/jobs.txt --workers 10 --min-minutes 3
```
