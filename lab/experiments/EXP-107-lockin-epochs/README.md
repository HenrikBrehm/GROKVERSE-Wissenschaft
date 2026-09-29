---
id: EXP-107
status: abgeschlossen
datum: 2026-09-29
tags: [exp/abgeschlossen, befund/positiv, neu/kandidat]
---
# EXP-107 (N54, Exploration): Zählt die frühe Festlegung in Epochen statt in Schritten?

Zurück: [[LAB]] · [[FINDINGS]] (Kernaussage K4 / Result 3 des Papers: Festlegung 25–50 Schritte, Full-Batch) · [[NOVEL_DIRECTIONS]] N54 · Anlass [[experiments/EXP-100-set-vs-order/README|EXP-100]] (Wechselläufe)

**Stand:** festgelegt Sitzung 46 (2026-09-29, ≈ 02:36 Berlin), vor jedem EXP-107-Lauf. `design.py` (80 Jobzeilen), `analyze.py` (Lader an vorhandenen EXP-100-Läufen geprüft, Lesart-Logik an synthetischen Werten).

**Frage:** Full-Batch legt sich zwischen 25 und 50 Schritten (= Epochen) fest. Unter i.i.d.-Minibatch B = 256 (15 Schritte je Epoche) war bei 25 und 50 Schritten nichts festgelegt (π ≈ 0, 8 Seeds, auch bei gleichem Horizont). Liegt das Fenster unter Minibatch bei 25–50 **Epochen** (375–750 Schritte)?
**Aufbau:** EXP-100-Splits und Seeds 3700–3707, iid256 (AdamW lr 1e-3, wd 1), Wechsel F → G und G → F bei t = 100, 200, 375, 750, 1500 Schritten (6.7 / 13.4 / 25 / 50 / 100 Epochen), jeder Lauf 5000 Schritte insgesamt; π aus der W_E-Gruppenleistung bei Schritt 5000 gegen die reinen iid256-Pilotläufe (Schnappschuss 5000). 80 Läufe à 5000 Schritte (≈ 40 s), GPU.
**Lesarten (vorab, Docstring maßgeblich):** „Epochen-Uhr gestützt“, wenn π(375) < 0.5 < π(750) (Mittel) und KI von π(750) − π(375) > 0; „früher als in Epochen“ (π(375) ≥ 0.5); „später als in Epochen“ (π(750) < 0.5 ≤ π(1500)); „keine Festlegung bis 100 Epochen“ (π(1500) < 0.5); sonst „gemischt“. Beschreibend: π je t mit KI, Schnittpunkt π = 0.5 in Schritten und Epochen.
**Dagegen spräche:** Fenster deutlich früher als 375 Schritte (dann eher eine Schrittuhr mit Rauschen) oder gar keine Festlegung.
**Grenzen/bekannt:** Horizont nach dem Wechsel verschieden (4900 bis 3500 Schritte); im EXP-100-Nachtrag änderte der Horizont π unter Minibatch nicht. Gesehene Daten: EXP-100-Wechselläufe (t = 25/50) und deren Post-hoc-Horizontanalyse; die Pilot-Endpunkte. Literatur zur Frage noch nicht geprüft (N54).

```
python lab/tools/parallel_queue.py lab/experiments/EXP-107-lockin-epochs/jobs.txt --workers 5 --min-minutes 5
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-107-lockin-epochs/analyze.py
```

## Ergebnis (Sitzung 46, 2026-09-29, 03:00 Berlin; Exploration, 8 Seeds, nicht unabhängig nachgerechnet)

80/80 Läufe fehlerfrei, 8/8 Seeds gültig. **Lesart (vorab): „früher als in Epochen“.**

| t (Schritte) | Epochen | π (Mittel, 95-%-KI) |
|---|---|---|
| 25 / 50 (EXP-100, gesehen) | 1.7 / 3.3 | ≈ 0 |
| 100 | 6.7 | 0.33 [0.24, 0.42] |
| 200 | 13.4 | 0.85 [0.78, 0.92] |
| 375 | 25 | 1.00 [0.95, 1.06] |
| 750 | 50 | 1.00 [0.98, 1.02] |
| 1500 | 100 | 1.00 [0.99, 1.00] |

Halber Wert (π = 0.5, linear interpoliert) bei ≈ **133 Schritten = 8.9 Epochen**; Full-Batch (EXP-100-Referenz, π(25) 0.38, π(50) 0.87) bei ≈ 30 Schritten = 30 Epochen. **Deutung (vorsichtig):** Unter Minibatch B = 256 gibt es das Festlegungsfenster, nur später in Schritten (≈ ×4.4) und früher in Epochen (≈ ×1/3.4). Weder eine reine Schritt- noch eine reine Epochen-Uhr. **Post hoc (Vermutung, ungeprüft):** ×4.4 liegt nahe √(N/B) = √15 ≈ 3.9, wie es eine rauschbestimmte Uhr (Wurzelregel) nahelegen würde; ein Test bräuchte eine B-Reihe (z. B. B = 64, 1024) mit vorab festgelegter Vorhersage t½ ∝ √(N/B). Grenzen: 8 Seeds, eine Aufgabe, Horizont nach dem Wechsel je t verschieden, π Energiemaß.
