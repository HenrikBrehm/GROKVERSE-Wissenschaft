---
id: EXP-084
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet, programm/A, paper, neu/kandidat]
---
# EXP-084: Dosis-Kurve der Grokking-Beschleunigung: sättigt sie oder kehrt sie bei extremer Konzentration um? (Exploration, frische Seeds)

Zurück: [[LAB]] · [[FINDINGS]] (Beobachtung „konstruierte Splits groken früher“, Ergänzung Sitzung 31: Dosis-Wirkung) · Bestätigung: [[confirm/R5_REGISTRATION_DRAFT|R5]] · Anlass: `EXP-042-bias-strength/posthoc_speed_dose.py` ([[JOURNAL]] Sitzung 31, Zyklus 2) · [[NOVEL_DIRECTIONS]] N6.

**Status:** vorbereitet, Sitzung 31 (2026-09-27, 20:14 Berlin, gemessen), vor jedem Lauf. Splits erzeugt (reine Rechnung). Jobliste, Smoke und `analyze.py` fertig, **ungetestet**. **Exploration, kein Urteil für FINDINGS**; frische Seeds, damit die Form der Kurve nicht an gesehenen Seeds bestimmt wird.

## Frage und Bezug

Post hoc (Seeds 30, 31, 32, 34) generalisieren Splits umso früher, je konzentrierter ihr Paarspektrum ist (ε 1 / 2 / 8). Offen ist die **Form** der Kurve: Wird es mit weiter steigender Konzentration immer schneller, sättigt es, oder kehrt es sich bei extremer Konzentration um (zu wenige „Nicht-Ziel“-Paare, extreme Ziehgewichte)? Das betrifft die Paper-Beobachtung (§4) und die Frage, wie man Trainingsdaten für schnelles Grokking wählt. R5 prüft nur ε 1 gegen 8 (sekundär).

## Aufbau (vorab festgelegt)

| Punkt | Festlegung |
|---|---|
| Einheiten | 10, Init-Seeds **2780–2789** (reserviert), eigene Split-Ströme `SeedSequence([20261002, u, …])`, keiner aus dem Init-Seed |
| Arme je Einheit | R (gleichverteilt) und ε ∈ {0.5, 1, 2, 4, 8, 16, 32} (Konstruktion EXP-016/018, Untergrenze 0.05), **gleiche** Testmenge (20 %), Schlüssel, Wellenphasen und Ziele A; Arme unterscheiden sich nur in ε |
| Realisierter M0-Zielanteil (Rechnung vor dem Lauf) | R 0.08–0.10, ε 0.5 0.09–0.10, 1 0.11–0.12, 2 0.17–0.18, 4 0.27–0.28, 8 0.35–0.36, 16 0.39–0.41, **32 0.42–0.44**. Die Konstruktion sättigt: ε 16/32 prüfen vor allem extremere Ziehgewichte, kaum mehr Konzentration |
| Training | freq_ban, GPU, `--threads 1`, 4000 Schritte, `--stop-after-gen 100`, Spektrum bei 250; Reihenfolge der 80 Läufe fest gemischt |
| Ereignis | erste Kreuzung des Trainers (Test ≥ 0.95); zensiert bei 4000. Exploration: die erste Kreuzung reicht (R5 verlangt 3 Auswertungen) |
| Lesarten (beschreibend, je Einheit; mehrere können zugleich gelten) | **monoton:** Spearman(Konzentrationsrang, log2 b) ≤ −0.8 in ≥ 8/10 Einheiten. **Umkehr:** b(ε 32) > b(ε 8) in ≥ 7/10 Einheiten und Median log2(b32/b8) ≥ 0.25. **Sättigung:** \|Median log2(b32/b8)\| ≤ 0.25 |
| Beschreibend | Median b je Arm, beobachtete Ereignisse, W_E-Zielanteil bei 250, M0-Zielanteil, Endgenauigkeit |
| Was gegen die Beobachtung spräche | ε 2 < ε 8 nicht in der Mehrheit der Einheiten (dann trägt schon der Befund aus Sitzung 31 nicht) |
| Budget | 80 Läufe; konstruierte Arme ≈ 500–1000 Schritte, R und kleine ε bis 4000; GPU bei 8–10 parallel ≈ 15 min |
| Bereits gesehen | EXP-020/042 (Seeds 30, 31, 32, 34) für ε 1/2/8; daraus die Wahl des Bereichs. Keine Läufe mit 2780–2789 |

**Neuheit:** Die Suche vom 2026-09-27 ([[paper/lit_grokking_speed_2026-09-27]]) fand keine Beschleunigung über die Konzentration des Paarspektrums; eine Dosis-Kurve wurde dort ebenfalls nicht gefunden (vorläufig, keine neue Suche).

## Vorhersage vor dem Lauf (Sitzung 32, 2026-09-27, 20:32 Berlin gemessen; kein EXP-084-Lauf existiert; mit Commit festgehalten)

**Frage:** Wirkt die Konzentration nur über das Paarspektrum der Maske (realisierter M0-Zielanteil s), oder wirken die immer extremeren Ziehgewichte selbst? EXP-084 trennt das, weil s ab ε 16 sättigt (0.40/0.43), die Gewichte aber weiter extremer werden. Bezug: Arbeitspaket C in [[FINDINGS]] (mechanistische Vorhersage an unberührten Fällen) und die Beobachtung „Beschleunigung“ (R5).

**Zwei Konkurrenzmodelle, nur an gesehenen Läufen kalibriert** (`prediction_s32.py`, Ausgabe `prediction_s32.json`): Kalibriert wird an EXP-020/042 (Seeds 30/31/32/34, **CPU**). Die Mediane sind ε 2 → s 0.18, b 775 und ε 8 → s 0.357, b 437.5. Den groben Anker für den Zufallssplit liefert EXP-003d (Median 5975 bei s ≈ 0.09, andere Testmengen).
- **M_share:** b = T∞ + A/(s − s0), angepasst T∞ = 249, A = 52.2, s0 = 0.081. Die Konzentration wirkt nur über s.
- **M_eps:** log2 b linear in log2 ε durch die Mediane von ε 2 und ε 8. Die Gewichte selbst wirken. *Dieses Modell ist am unteren Ende schon durch gesehene Daten widerlegt:* Es sagt für ε 1 b ≈ 1030 vorher, beobachtet wurde aber keine Generalisierung bis 2000 (4/4). Es dient hier nur als Alternative für den oberen Bereich.
- M_share selbst passt am unteren Ende auch nur knapp: Für s = 0.115 sagt es 1780 vorher, beobachtet wurde > 2000. Der untere Bereich hängt stark an s0; bei s0 0.07–0.10 liegt ε 1 bei 1650–3460. **Der obere Bereich ist dagegen robust:** Bei jedem s0 zwischen 0.07 und 0.10 ergibt sich log2(b32/b8) zwischen −0.12 und −0.15 und b(ε 4) zwischen 506 und 518.

| Arm | Median s | M_share: Median b | M_eps: b |
|---|---|---|---|
| R | 0.090 | 4000 (zensiert) | 4000 |
| ε 0.5 | 0.094 | 4000 (bei s0 = 0.07: 2770) | 1373 |
| ε 1 | 0.112 | 1912 (s0-abhängig 1650–3460) | 1031 |
| ε 2 | 0.181 | 772 | 775 |
| ε 4 | 0.277 | 514 | 582 |
| ε 8 | 0.354 | 440 | 438 |
| ε 16 | 0.401 | 412 | 329 |
| ε 32 | 0.430 | 398 | 247 |

**Entscheidungsregeln (vorab festgelegt, über die 10 Einheiten; Exploration, kein FINDINGS-Urteil):**
- **V1 (trennt die Modelle, primär für diese Vorhersage):** Median log2(b(ε 32)/b(ε 8)), dieselbe Größe wie in `analyze.py`. Bei ≥ −0.40 spricht das für M_share (vorhergesagt −0.14), bei ≤ −0.60 für M_eps (−0.82), dazwischen *unentschieden*. Bei ≥ +0.25 (Umkehr) sind beide falsch.
- **V2 (quantitativ, Zwischenpunkt, nicht kalibriert):** Median b(ε 4) in [450, 575] trifft M_share. Der Wert von M_eps (582) liegt knapp außerhalb, V2 trennt also schwach.
- **V3 (unterer Bereich, schwach bestimmt, nur beschreibend):** Unter M_share (s0 ≥ 0.081) generalisiert ε 0.5 bis 4000 ähnlich selten wie R. Unter M_eps generalisiert es in der Mehrheit bis ≈ 1400.
- **Grenzen:** Die Kalibrierung lief auf der CPU, EXP-084 läuft auf der GPU (GPU-001: gleichwertig, nicht bitgleich; die Absolutwerte von V2 können sich verschieben, das Verhältnis in V1 weniger). Die Auswertung erfolgt alle 25 Schritte, bei ≈ 400 Schritten sind das ≈ 6 % je Rasterschritt. Beide Modelle sind phänomenologisch. Trifft M_share zu, zeigt das nur, dass s die Zeit **ordnet**, nicht, dass das Spektrum sie **verursacht** (mit ε ändert sich auch die Paarauswahl).

## Reproduktion (im Fenster, alles über den Wächter)

```
python lab/experiments/EXP-084-dose-curve/make_splits.py                     # reine Rechnung, prüft vorhandene Dateien bitgleich
python lab/tools/guarded_run.py -- python lab/experiments/EXP-084-dose-curve/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-084-dose-curve/smoke.txt --workers 1
python lab/tools/parallel_queue.py lab/experiments/EXP-084-dose-curve/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-084-dose-curve/analyze.py
```
