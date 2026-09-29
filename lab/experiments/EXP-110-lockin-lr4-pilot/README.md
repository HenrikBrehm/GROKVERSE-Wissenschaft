---
id: EXP-110
status: abgeschlossen
datum: 2026-09-29
tags: [exp/abgeschlossen, befund/unklar, neu/kandidat]
---
# EXP-110 (Pilot zu N54c): Festlegungsfenster gegen Batchgröße bei Lernrate 4e-3

Zurück: [[LAB]] · [[FINDINGS]] (N54b) · Registrierung [[confirm/N54B_REGISTRATION_DRAFT|N54b]] · Vorgänger [[experiments/EXP-109-lockin-lr-pilot/README|EXP-109]]

**Stand:** festgelegt Sitzung 47 (2026-09-29, ≈ 05:33 Berlin) vor jedem Lauf. Auswertung mit `EXP-109/analyze.py`-Logik (Kopie folgt vor dem Lesen).
**Frage:** Ist lr 4e-3 unter Minibatch (B 1024/256/64) stabil und wo liegt t½ (Raster für eine N54c-Registrierung)? Welches Modell aus dem N54b-Vergleich trifft die Werte (Vorhersagen im JOURNAL, 05:00: M_i 18/36/72, M_add 20/56/177, M_pow 23/57/141)?
**Aufbau:** EXP-100-Splits, Seeds 3700–3701 (gesehen), lr 4e-3, wd 1, reine Läufe F/G + Wechsel bei 1024: 8–40, 256: 20–120, 64: 50–300; 5000 Schritte; 84 Läufe, GPU, 6 Worker.
**Regeln (vorab):** brauchbar, wenn alle reinen Paare getrennt (L_F − L_G ≥ 0.5); Raster geeignet, wenn π(erstes t) < 0.5 ≤ π(letztes t). Modellnähe beschreibend (2 Seeds): |log(t½/Vorhersage)| je B.

## Ergebnis erstes Raster (Sitzung 47, 05:43; 2 gesehene Seeds, beschreibend)

84/84 fehlerfrei; alle reinen Paare getrennt (L_F − L_G 8.2–11.2) → lr 4e-3 brauchbar. t½: B 1024 20.3 / 26.5 (Vorhersagen M_i 18, M_add 20, M_pow 23), B 256 69.5 / 57.4 (M_i 36, M_add 56, M_pow 57), **B 64: kein Durchgang bis 300** (π 0.48 / 0.03 bei 300; Raster ungeeignet). lr 1e-3 auf denselben Seeds: B 64 244 / 326 (EXP-108), lr 2e-3: 205 / 225 (EXP-109).
**Erweiterung (vor jedem Lauf festgelegt, 05:44):** B 64 zusätzlich t = 400, 600, 900, 1400 (16 Läufe, `design.py --ext`). Lesart je Seed: t½(4e-3, 64) aus dem vereinigten Raster; „Umkehr“, wenn in beiden Seeds t½(4e-3) > t½(1e-3) derselben Seeds (244 / 326), „keine Beschleunigung“, wenn zwischen t½(2e-3) und t½(1e-3), sonst beschreiben.

**Ergebnis Erweiterung (05:45; `ext_summary.json`; 2 gesehene Seeds, nicht nachgerechnet):** Lesart **„Umkehr“**: t½(4e-3, B 64) = 305 / 355 Schritte (π 0.48/0.03 bei 300, 0.89/0.88 bei 400) gegen 244 / 326 bei lr 1e-3 und 205 / 225 bei lr 2e-3. Bei B 64 ist die Abhängigkeit von der Lernrate damit **nicht monoton** (1e-3 → 2e-3 schneller, 2e-3 → 4e-3 langsamer), bei B 1024/256 beschleunigt lr 4e-3 weiter (≈ 20–27 bzw. 57–70). Keines der Modelle (M_i, M_add, M_pow) sagt die B-64-Zelle vorher (M_add 177, M_pow 141). **Vorsicht:** 2 Seeds, dieselben wie EXP-108/109; π bei B 64/lr 4e-3 schwankt früh (0.28/0.31 bei 50/75, dann ≈ 0).
**Folge:** Kandidat für N54c: „Bei kleinem Batch hat die Festlegungszeit ein Minimum in der Lernrate“ (lr 1e-3/2e-3/4e-3 bei B 64, frische Seeds, vorab registriert).

**Nachrechnung (05:47; unabhängiger Agent, eigener Code, `recheck_s47.py`):** alle Werte gleich (π bis auf Rundung, t½ exakt), 100/100 Läufe integer. Robust: t½(4e-3) > t½(2e-3) bei B 64 in beiden Seeds; t½(4e-3) > t½(1e-3) nur in Seed 3700 robust (3701: Durchgang 4e-3 zwischen 300 und 400, 1e-3 zwischen 300 und 450). Frühe π-Beule in Seed 3700 (0.28/0.31 bei 50/75) ohne Einfluss auf t½.
