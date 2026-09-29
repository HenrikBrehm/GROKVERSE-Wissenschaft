---
id: EXP-110
status: laufend
datum: 2026-09-29
tags: [exp/laufend]
---
# EXP-110 (Pilot zu N54c): Festlegungsfenster gegen Batchgröße bei Lernrate 4e-3

Zurück: [[LAB]] · [[FINDINGS]] (N54b) · Registrierung [[confirm/N54B_REGISTRATION_DRAFT|N54b]] · Vorgänger [[experiments/EXP-109-lockin-lr-pilot/README|EXP-109]]

**Stand:** festgelegt Sitzung 47 (2026-09-29, ≈ 05:33 Berlin) vor jedem Lauf. Auswertung mit `EXP-109/analyze.py`-Logik (Kopie folgt vor dem Lesen).
**Frage:** Ist lr 4e-3 unter Minibatch (B 1024/256/64) stabil und wo liegt t½ (Raster für eine N54c-Registrierung)? Welches Modell aus dem N54b-Vergleich trifft die Werte (Vorhersagen im JOURNAL, 05:00: M_i 18/36/72, M_add 20/56/177, M_pow 23/57/141)?
**Aufbau:** EXP-100-Splits, Seeds 3700–3701 (gesehen), lr 4e-3, wd 1, reine Läufe F/G + Wechsel bei 1024: 8–40, 256: 20–120, 64: 50–300; 5000 Schritte; 84 Läufe, GPU, 6 Worker.
**Regeln (vorab):** brauchbar, wenn alle reinen Paare getrennt (L_F − L_G ≥ 0.5); Raster geeignet, wenn π(erstes t) < 0.5 ≤ π(letztes t). Modellnähe beschreibend (2 Seeds): |log(t½/Vorhersage)| je B.
