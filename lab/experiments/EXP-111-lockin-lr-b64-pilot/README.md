---
id: EXP-111
status: abgeschlossen
datum: 2026-09-29
tags: [exp/abgeschlossen, befund/negativ]
---
# EXP-111 (Power-Pilot zu N54c): Ist die Festlegung bei B 64 mit lr 4e-3 langsamer als mit 2e-3?

Zurück: [[LAB]] · [[FINDINGS]] (N54b) · Vorgänger [[experiments/EXP-110-lockin-lr4-pilot/README|EXP-110]]

**Stand:** festgelegt Sitzung 47 (2026-09-29, ≈ 05:49 Berlin) vor jedem Lauf. Exploration, 2 Seeds (3702–3703; bei lr 1e-3 in EXP-100/107/108 gesehen, nie bei 2e-3/4e-3).
**Aufbau:** B 64, lr 2e-3 und 4e-3, EXP-100-Splits, reine Läufe F/G + Wechsel bei 100, 150, 200, 250, 300, 350, 400, 500; 5000 Schritte; 72 Läufe, GPU.
**Lesart (vorab, beschreibend):** je Seed d = log t½(4e-3) − log t½(2e-3); „gleiche Richtung wie EXP-110“, wenn d > 0 in beiden Seeds. Zweck: Effektgröße und Streuung für die Power von N54c (zusammen mit EXP-110).

## Ergebnis (Sitzung 47, 05:51 Berlin; 2 Seeds, beschreibend, nicht nachgerechnet)

72/72 fehlerfrei, alle reinen Paare getrennt. t½ bei B 64: Seed 3702 lr 2e-3 **223**, lr 4e-3 **198**; Seed 3703 **216** bzw. **199** → d = log t½(4e-3) − log t½(2e-3) = −0.12 / −0.08. Lesart (vorab): **„nicht gleiche Richtung“** wie EXP-110. Über vier Seeds (EXP-110 + EXP-111): d = +0.40, +0.46, −0.12, −0.08 → **gemischt**; die „Umkehr“ aus EXP-110 ist nicht belastbar (seedabhängig oder Rauschen; π bei lr 4e-3 teils nicht monoton, z. B. 3703: 0.51 bei 200, 0.47 bei 250). Die Registrierung N54c in der geplanten Form wird **nicht** vorbereitet; wenn überhaupt, erst mit mehr Seeds als Exploration.
