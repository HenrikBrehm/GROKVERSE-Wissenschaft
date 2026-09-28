---
id: EXP-094
status: abgeschlossen
datum: 2026-09-28
tags: [exp/abgeschlossen, befund/unklar, neu/kandidat]
---
# EXP-094: Zählen bei großen Schritten die Gradientenauswertungen oder nur Adams Fenster? (Pilot, Exploration)

Zurück: [[LAB]] · [[FINDINGS]] (offene Frage nach EXP-093) · [[NOVEL_DIRECTIONS]] N48 · Vorgänger [[experiments/EXP-093-lag-clock-range/README|EXP-093]], [[experiments/EXP-092-momentum-lag-clock/README|EXP-092]] · [[confirm/R9_REGISTRATION_DRAFT|R9]]

**Festgelegt vor jedem EXP-094-Lauf** (Sitzung 41, 2026-09-28, 15:35 Berlin gemessen; `design.py`, `analyze.py`, Selbsttest grün über den Wächter).

## Bezug und Frage

EXP-093: Bei festem Λ = 24 legen größere, seltenere Schritte zunehmend schwächer fest (π 0.27 bei c = 2 → 0.09 bei c = 8), mit gleich großer, aber weniger zielgenauer früher Bewegung. Zwei Erklärungen: **(W) Fenster:** Adams β-Fenster sind in Schritten fest, bei großem c also in Λ lang. Das R9-Gesetz sagt: Mit β′ = 1 − c(1 − β) (in Λ angeglichen) sollte der Rückstand verschwinden (gleiche Adam-ODE in Λ). **(A) Auswertungen:** Die Zielgenauigkeit wächst mit der Zahl der Gradientenauswertungen (Diskretisierung, frühe breite Gradienten werden lange angewandt). Dann bleibt ein Rückstand auch mit angeglichenen Fenstern und wächst mit c. R9 prüfte die Angleichung nur bis c = 2 (t = 15), EXP-093 zeigte schon bei c = 2 −0.04.

## Aufbau

Wie EXP-092/093 (add 113, ω = 0-Splitpaare, Wechsel A → B und B → A, danach 2000 Standardschritte mit β 0.9/0.98, π gegen reine Läufe; GPU). **Seeds 3440–3455** (frisch: Dateisuche 28.09. ohne Treffer). Alle Zellen Λ = 24: n24 (Standard), c4 (c = 4, t = 6, Standard-β; Replikation), **c2b** (2, 12, β′ 0.8/0.96), **c4b** (4, 6, β′ 0.6/0.92), **c8b** (8, 3, β′ 0.2/0.84). 12 Läufe je Seed, **192 GPU-Läufe**.

## Vorhersagen und Lesarten (verbindlich, im Code)

d_c = π(n24) − π(c b) (Rückstand nach Angleichung), m4 = π(c4b) − π(c4); Bootstrap-KIs über Seeds.
- **„Auswertungen zählen“** (A): d4 und d8 mit KI-Untergrenze > 0.03 und mittleres d8 > d4.
- **„Fenster erklären“** (W): d4 und d8 mit KI innerhalb ±0.05.
- sonst **„teilweise“**; < 10 gültige Seeds → *nicht auswertbar*.
- **Beschreibend:** d2, m4, Zellmittel von π, Zielanteil f und Norm N beim Wechsel; **prospektive Prüfung** der Post-hoc-Geraden π = −1.389 + 9.428·f aus EXP-092/093 (`posthoc_state_s41.json`, vor diesem Lauf committet): MAE über die fünf Zellmittel.
- **Erwartung:** eher (A) oder „teilweise“: EXP-093 zeigte, dass die Lag-Korrektur (erste Ordnung) bei großem c nicht reicht; R9 H3 (c = 2, t = 15) lag aber mit β′ auf der Λ-Erwartung. Bei c = 8 ist β₁′ = 0.2 fast kein Momentum mehr; auch das Verhalten von Adam mit β₂′ 0.84 über 3 Schritte ist ungewohnt (Grenze des Aufbaus).

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-093 (Frage, Λ = 24, c-Stufen, Schwelle 0.03), EXP-092 (c4-Fehlschlag), R9 (β′-Regel, ±-Grenze 0.1 → hier enger 0.05), Post-hoc-Gerade π(f). Keine Seeds aus diesen Blöcken.

## Befehle

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-094-evaluations-vs-window/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-094-evaluations-vs-window/smoke.txt --workers 3
python lab/tools/parallel_queue.py lab/experiments/EXP-094-evaluations-vs-window/jobs.txt --workers 8
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-094-evaluations-vs-window/analyze.py
```

## Ergebnis

Sitzung 41, 2026-09-28; Block 15:36–15:53 Berlin, 192/192 ok; `analyze.py` über den Wächter; `summary.json`. 16/16 Seeds gültig.
**Registrierte Lesart: „teilweise“** (d4-KI-Untergrenze 0.023 knapp unter 0.03).
- Rückstand nach Angleichung der Fenster gegen n24 (π 0.329): **d2 +0.032** [0.015, 0.053] (15/16), **d4 +0.051** [0.023, 0.079] (15/16), **d8 +0.174** [0.127, 0.219] (16/16). Wächst mit c.
- Was die Angleichung bei c = 4 bringt: **m4 = π(c4b) − π(c4) = +0.049** [0.019, 0.082] (12/16); ohne Angleichung Rückstand c4 ≈ 0.10 (π 0.229), mit ≈ 0.05 (π 0.277).
- Zellmittel π: n24 0.329, c2b 0.296, c4 0.229, c4b 0.277, c8b 0.155. Zielanteil f: 0.178 / 0.176 / 0.163 / 0.171 / 0.161; Norm fast gleich (c8b etwas kleiner, 2.18).
- **Prospektive Prüfung der Post-hoc-Geraden π(f):** MAE 0.045; Rangfolge der Zellen getroffen, aber alle Vorhersagen zu niedrig (n24: 0.287 gegen 0.329). Die Gerade überträgt die Ordnung, nicht das Niveau (anderer Seed-Block).
**Einordnung:** Adams in Schritten feste Fenster erklären bei großen Schritten einen Teil des Rückstands (bei c = 4 etwa die Hälfte, wie in R9 bei c = 2 der größte Teil). Ein zweiter Anteil bleibt, wächst mit c und dominiert bei c = 8 (3 Schritte, β₁′ 0.2): Bei gleichem Λ und in Λ angeglichenen Fenstern legen wenige große Schritte schwächer fest und bewegen W_E weniger zielgenau. Passend zu „Zielgenauigkeit wächst mit der Zahl der Gradientenauswertungen“, aber nicht getrennt von Diskretisierung/Überschießen. **Grenzen:** Pilot, eine Aufgabe, W_E-Energiemaß; bei c = 8 ist die β′-Angleichung extrem (β₁′ 0.2, β₂′ 0.84 über 3 Schritte).
