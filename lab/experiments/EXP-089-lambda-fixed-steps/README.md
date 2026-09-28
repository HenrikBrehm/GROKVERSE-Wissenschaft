---
id: EXP-089
status: abgeschlossen
datum: 2026-09-28
tags: [exp/abgeschlossen, befund/positiv, neu/kandidat]
---
# EXP-089: Wächst die Festlegung bei fester Lernratensumme Λ mit der Schrittzahl? (Pilot, „Teil C“ von EXP-081)

Zurück: [[LAB]] · [[FINDINGS]] (größte offene Frage: Was macht die frühe Wahl fest?) · Vorläufer [[confirm/R3_REGISTRATION_DRAFT|R3]] (Λ gegen Schritte), [[experiments/EXP-081-optimizer-clock/README|EXP-081]] Nachtrag b Punkt 3 · [[experiments/EXP-059-momentum-exposure/README|EXP-059]] (π-Kurve) · [[JOURNAL]] Sitzung 40.

**Festgelegt:** Sitzung 40, 2026-09-28, vor jedem EXP-089-Lauf und **vor dem Lesen eines EXP-081-Ergebnisses**. Pilot/Exploration (10 frische Seeds, kein eingefrorenes Manifest).

## Warum

R3 (20 frische Seeds): Die reine Schrittuhr passt nicht; doppelte Lernrate für 25 Schritte hält fest wie 50 Standardschritte (bestätigt), halbe Lernrate für 50 Schritte steigt überwiegend um, aber nur ≈ 81 % des Weges zur Λ-Erwartung (beschreibend). Offen ist, ob die Festlegung bei gleichem Λ mit der Schrittzahl leicht wächst (Mischuhr τ ≈ Λ^a · t^(1−a), grob a ≈ 0.8) oder ob die R3-Lücke Rauschen/Messgröße war (reine Λ-Uhr). Hier ist Λ fest und t variiert über den Faktor 4; gemessen wird mit π (EXP-056/059), nicht mit der Genauigkeitsgröße von R3.

## Konkurrenzmodelle und Vorhersagen (π, Referenzkurve EXP-059: π(25) ≈ 0.30, π(30) ≈ 0.39, π(35) ≈ 0.56; Steigung ≈ 0.02–0.03 je Schritt)

| Zelle (c, t), Λ = c·t | reine Λ-Uhr | Mischuhr a = 0.8 (τ = 25 · (t/25)^0.2) | Schrittuhr |
|---|---|---|---|
| (1, 25) Referenz | 0.30 | 0.30 | 0.30 |
| (0.5, 50) | wie Referenz | τ ≈ 28.7 → π ≈ 0.36 | ≈ 1.05 |
| (0.25, 100) | wie Referenz | τ ≈ 33 → π ≈ 0.49 | > 1 |

Weight Decay folgt Λ (AdamW-Zerfall lr·wd je Schritt; wie in R3 gerechnet). Der Momentum-Schwanz nach dem Wechsel läuft bei Standard-Lernrate und ist in m̂/√v̂ lernratenfrei, also in allen Zellen gleich groß (EXP-081 Nachtrag d). Das Training ist Vollbatch: Mehr Schritte bei kleinerer Lernrate heißt feinere Diskretisierung derselben Bahn, nicht mehr Rauschen. Eine Mischuhr wäre hier also ein Diskretisierungseffekt (oder ein Effekt von Adams schrittweiser Normierung), keine Minibatch-Statistik.

## Versuch

| Punkt | Festlegung |
|---|---|
| **Frage** | Ist π bei Λ = 25 nach 100 Schritten (lr × 0.25) größer als nach 25 Standardschritten? |
| **Protokoll** | wie EXP-081/059: add 113, ω = 0-Splits (EXP-053-Bau), Wechsel A → B und B → A bei t, danach 2000 Schritte Standard-Lernrate; `--lr-scale c` wirkt in den Schritten 1 … t (EXP-039/R3-Option, unverändert); GPU, 1 Thread |
| **Zellen** | Standardkurve c = 1 bei t = 25, 33, 45; Λ-Zellen (0.5, 50), (0.25, 100); reine A/B-Läufe (Standard, 2000 Schritte) |
| **Seeds** | 3260–3269 (frisch, Dateisuche 28.09.; vorher nirgends genutzt) |
| **Umfang** | 10 × (2 + 5 × 2) = 120 GPU-Läufe à 2000–2100 Schritte, ≈ 25 min bei 8 Workern |
| **Primär** | d100 = π(0.25, 100) − π(1, 25) je Seed, gepaart; 95-%-Perzentil-Bootstrap (10 000, rng 89) |
| **Lesart vorab** | KI ganz in [−0.1, +0.1] → ***Λ-Uhr gestützt***; KI-Untergrenze > 0 und Mittel < 0.5 → ***Mischuhr gestützt***; KI-Untergrenze > 0 und Mittel ≥ 0.5 → ***nahe Schrittuhr***; sonst ***unklar***. < 8 gültige Seeds → *nicht auswertbar* |
| **Sekundär (beschreibend)** | d50 = π(0.5, 50) − π(1, 25) mit KI; gleichwertiger Standardschritt t_eq der Zellmittel auf der Kurve 25/33/45 (linear, außerhalb nan); Exponent 1 − a = log(t_eq/25) / log(t/25) |
| **Gültigkeit je Seed** | alle 12 Läufe über den gemeinsamen Lader ok (inkl. `lr_scale` in der Konfiguration), L(A) − L(B) ≥ 2 |
| **Was dagegen spräche** | Λ-Uhr: d100 ≈ 0 trotz Faktor 4 in t. Gegen beide einfachen Uhren: d100 < 0 (weniger Festlegung bei mehr Schritten) |
| **Grenzen** | Pilot, 10 Seeds; eine Aufgabe (add 113), eine Architektur; ein Λ; sehr kleine Lernrate kann den Vorlauf qualitativ anders formen (Adams ε, Bias-Korrektur in den ersten Schritten); π ist nichtlinear in t (Umrechnung über t_eq nur grob) |
| **Budget / Abbruch** | ≈ 25 min GPU. NaN/Divergenz → *nicht auswertbar*. Start erst nach EXP-081 (GPU frei), frühestens in dieser Sitzung |
| **Bereits gesehene Daten** | R3 (Seeds aus dem R3-Block: Richtung und ≈ 81 %), EXP-039 (Pilot), EXP-059 (π-Kurve an 400–409). Beeinflusst: Wahl von Λ = 25, von t bis 100 und der Mischuhr-Vorhersage (a ≈ 0.8 aus R3). EXP-081 ist bei der Festlegung nicht ausgewertet |

## Ziel in FINDINGS

Größte offene Frage („Was macht die frühe Wahl fest?“) und die beschreibende R3-Lücke (Paper §3.10). Entscheidet zwischen reiner Λ-Uhr und Mischuhr (Regel 18c).

## Befehle

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-089-lambda-fixed-steps/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-089-lambda-fixed-steps/smoke.txt --workers 3
python lab/tools/parallel_queue.py lab/experiments/EXP-089-lambda-fixed-steps/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-089-lambda-fixed-steps/analyze.py
```
Selbsttest grün (Sitzung 40). Splits in `splits/`, Jobs in `jobs.txt` (`design.py --jobs`).

## Literatur zur Deutung (Sitzung 40, 10:48, nach der Registrierung, vor jedem Ergebnis; ändert keine Lesart)

Suche 2026-09-28 (WebSearch: „implicit bias of Adam backward error analysis“, „implicit gradient regularization“). Dass endliche Schritte die Bahn gegenüber dem Gradientenfluss systematisch verändern, ist bekannt: Bei GD bestraft die Rückwärtsfehleranalyse die Gradientennorm mit Gewicht ∝ Schrittweite (Barrett & Dherin, *Implicit Gradient Regularization*, [arXiv 2009.11162](https://arxiv.org/abs/2009.11162)); bei Adam/RMSProp hängt der Korrekturterm von Hyperparametern und Trainingsphase ab und wirkt auf eine (gestörte) 1-Norm der Gradienten, meist hemmend (Cattaneo, Klusowski & Shigida, ICML 2024, [arXiv 2309.00079](https://arxiv.org/abs/2309.00079)). Bei festem Λ unterscheiden sich unsere Zellen genau in diesem Korrekturterm (Schrittweite 4× kleiner bei t = 100). Eine Abweichung von der Λ-Uhr wäre damit **erwartbar in der Art, nicht in Richtung und Größe**; welche Richtung die Festlegung nimmt, sagt keine der beiden Arbeiten für unsere Größe π voraus. Die Einordnung „Mischuhr“ wäre deshalb als Diskretisierungseffekt zu lesen, nicht als eigene Uhr.

## Ergebnis (Sitzung 40, 2026-09-28; 120/120 GPU-Läufe 10:43–11:04 Berlin laut Queue-Log, parallel zu EXP-081; `analyze.py` über den Wächter; Pilot)

10/10 Seeds gültig, keine technischen Ausfälle.
- **Primär:** d100 = π(0.25, 100) − π(1, 25) = **+0.24**, SD 0.15, 95-%-KI **[0.17, 0.34]**, 10/10 Seeds > 0 → ***Mischuhr gestützt*** (registriert).
- **Sekundär:** d50 = +0.09 [0.04, 0.15]. Zellmittel π: Standard t = 25 / 33 / 45: 0.32 / 0.56 / 0.84; Λ = 25 bei t = 50: 0.40, bei t = 100: 0.56. Gleichwertiger Standardschritt t_eq = **27.8** (t = 50) und **32.8** (t = 100); Exponent 1 − a = 0.15 bzw. 0.19.
- **Gegen die vorab genannte Vorhersage der Mischuhr mit a = 0.8** (τ ≈ 28.7 bzw. 33): getroffen, bei t = 100 fast genau. In π lag die Vorhersage (0.36 / 0.49 aus der EXP-059-Kurve) etwas niedriger als beobachtet, weil die Standardkurve dieser Seeds steiler ist (π(33) 0.56 statt ≈ 0.45); über t_eq, auf der eigenen Kurve der Seeds, passt sie.

**Lesart (Interpretation, Pilot):** Bei gleicher Lernratensumme legt sich das Modell mit mehr, kleineren Schritten stärker fest; ein Faktor 4 in der Schrittzahl wirkt wie ≈ 30 % mehr Λ. Weder die reine Λ-Uhr (d = 0) noch die Schrittuhr (π nach 100 Schritten ≫ 1) beschreibt das. Die Mischuhr τ ≈ Λ^0.8 · t^0.2 aus der R3-Lücke sagt die Größe richtig voraus, an unabhängigen Seeds und mit einer anderen Messgröße (π statt Genauigkeit). Das spricht dafür, dass die R3-Lücke echt ist und nicht an der Messgröße lag.
**Mechanismus offen:** Vollbatch-Training, gleicher Weight-Decay-Faktor und gleicher Momentum-Schwanz (in allen Zellen gleich) schließen Minibatch-Rauschen, Decay und den Schwanz als einfache Erklärung aus. Übrig bleiben Diskretisierungseffekte (Rückwärtsfehler-Terme ∝ Schrittweite, Literatur oben: größere Schritte weichen stärker vom Fluss ab) und Adams schrittweise Normierung/Bias-Korrektur. Die Richtung heißt: Der feinere Pfad (näher am Fluss) legt sich *stärker* fest; größere Schritte „verschwenden“ einen Teil von Λ.
**Grenzen:** Pilot, 10 Seeds, ein Λ, eine Aufgabe (add 113), eine Architektur; t_eq aus Zellmitteln und linearer Interpolation; π-Kurve nichtlinear. Eine Bestätigung bräuchte frische Seeds, eingefrorenes Manifest und eine zweite Λ-Stufe (z. B. Λ = 12.5 mit t = 12/25/50 oder ×8 in t), damit die Potenzform geprüft und nicht nur ein Punkt getroffen wird.
