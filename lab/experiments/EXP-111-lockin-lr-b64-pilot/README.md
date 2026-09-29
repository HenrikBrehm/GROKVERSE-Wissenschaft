---
id: EXP-111
status: laufend
datum: 2026-09-29
tags: [exp/laufend]
---
# EXP-111 (Power-Pilot zu N54c): Ist die Festlegung bei B 64 mit lr 4e-3 langsamer als mit 2e-3?

Zurück: [[LAB]] · [[FINDINGS]] (N54b) · Vorgänger [[experiments/EXP-110-lockin-lr4-pilot/README|EXP-110]]

**Stand:** festgelegt Sitzung 47 (2026-09-29, ≈ 05:49 Berlin) vor jedem Lauf. Exploration, 2 Seeds (3702–3703; bei lr 1e-3 in EXP-100/107/108 gesehen, nie bei 2e-3/4e-3).
**Aufbau:** B 64, lr 2e-3 und 4e-3, EXP-100-Splits, reine Läufe F/G + Wechsel bei 100, 150, 200, 250, 300, 350, 400, 500; 5000 Schritte; 72 Läufe, GPU.
**Lesart (vorab, beschreibend):** je Seed d = log t½(4e-3) − log t½(2e-3); „gleiche Richtung wie EXP-110“, wenn d > 0 in beiden Seeds. Zweck: Effektgröße und Streuung für die Power von N54c (zusammen mit EXP-110).
