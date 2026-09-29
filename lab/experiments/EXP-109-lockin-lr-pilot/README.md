---
id: EXP-109
status: laufend
datum: 2026-09-29
tags: [exp/laufend]
---
# EXP-109 (Pilot zu N54b): Festlegungsfenster gegen Batchgröße bei Lernrate 2e-3

Zurück: [[LAB]] · [[FINDINGS]] (Result 3 / L0) · [[NOVEL_DIRECTIONS]] N54 · Vorgänger [[experiments/EXP-108-lockin-batch-series/README|EXP-108]] · Registrierung [[confirm/N54B_REGISTRATION_DRAFT|N54b]]

**Stand:** festgelegt Sitzung 47 (2026-09-29, 03:33 Berlin gemessen, Commit 9804ce01) vor jedem Lauf; `analyze.py` geschrieben, während die Läufe liefen, vor jedem Ergebnis.

**Frage:** Ist lr 2e-3 unter Minibatch (bis B 64) stabil genug für die Bestätigung, und wo liegt t½ je Batchgröße (Raster für die Registrierung)?
**Aufbau:** EXP-100-Splits, Seeds 3700–3701 (gesehen), lr 2e-3, wd 1, B ∈ {Full, 1024, 256, 64}, reine Läufe F/G + Wechsel F→G, G→F bei Raster GRID[B] (Full 8–75, 1024 15–150, 256 30–300, 64 75–700), je 5000 Schritte, 112 Läufe, GPU.
**Regeln (vorab):** Raster je B geeignet, wenn in beiden Seeds π(erstes t) < 0.5 ≤ π(letztes t). lr 2e-3 brauchbar, wenn jedes reine Paar getrennt ist (L_F − L_G ≥ 0.5). α beschreibend (2 Seeds, kein Urteil).
**Erwartung (vor dem Lauf):** Wenn früh die Lernrate zählt (EXP-103), sollte t½ bei 2e-3 kürzer sein (≈ ×0.5–0.7), α ähnlich 0.5.

```
python lab/tools/parallel_queue.py lab/experiments/EXP-109-lockin-lr-pilot/jobs.txt --workers 10 --min-minutes 3
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-109-lockin-lr-pilot/analyze.py
```
