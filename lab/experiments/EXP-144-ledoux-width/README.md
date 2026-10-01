---
id: EXP-144
status: abgeschlossen
datum: 2026-10-01
tags: [exp/abgeschlossen, befund/unklar]
verwandt: ["[[experiments/EXP-143-ledoux-regime/README|EXP-143]]", "[[experiments/EXP-049-width-steering/README|EXP-049]]", "[[FINDINGS]]", "[[BACKLOG]]"]
---
# EXP-144: LeDoux-Regime mit 4-facher Breite (d 512) – Pilot

Zurück zu [[LAB]]. **Exploration (ein Seed je Arm), keine Bestätigung.** Nachfolger von [[experiments/EXP-143-ledoux-regime/README|EXP-143]] (dort kein dritter Nachtrag-Strang mehr, Regel 15b).

**Bezug zu FINDINGS:** wie EXP-143: K2 und L0 gegen den LeDoux-Einwand (Regel 20b, Priorität 1). Grenze (ii) im Paper lautet „nothing was tested near LeDoux's 0.3 %“.

## Anlass (Sitzung 71, 16:46 Berlin (gemessen), vor jedem d-512-Ergebnis außer dem Smoke)

In EXP-143 (d 128, wd 0.1, 250 000 Schritte ≈ 213 Epochen) generalisiert keiner der beiden i.i.d.-Arme, und keiner lernt auch nur die Trainingsmenge (Train-Genauigkeit am Ende 0.36 F-iid, 0.41 R-iid; F-stride 0.15), Q1 = „im Budget keine Aussage“. Die Train-Genauigkeit stagniert bzw. sinkt in der zweiten Hälfte – vermutlich eine Kapazitätsgrenze des 1-Schicht-Modells mit d 128 bei 300 000 Paaren (LeDoux: 2 Schichten, d 256). Eine Frage nach „Menge gegen Reihenfolge“ braucht ein Modell, das in diesem Regime lernt. Die 4-fache Breite ist unsere einzige geprüfte Breitenvariante (P4: K2 bei d 512 bestätigt, 15/15).

## Vorab

- **Änderung gegenüber EXP-143 primär:** nur `--d-model 512` (n_heads 4, d_head 128, d_mlp 2048, wie EXP-049/P4) über die Hülle `freq_ban_large.py` (neue Option, Sitzung 71; `--d-model 128` gibt bitgleiche Gewichte wie der Trainer ohne Option, Test `lab/tools/test_freq_ban_large.py`). Gleiche Splits (Seed 14300, p 9973, N 300 000, ε 2), gleiche Test-Stichprobe, Batch 256, AdamW lr 1e-3, wd 0.1, 250 000 Schritte, Stopp 5000 nach gen, Auswertung alle 1000, Spektrum alle 2500. GPU über den Dienst (`52a7zzz_exp144_width`, gpu_gb 5, vor dem wd-1.0-Nebenarm von EXP-143).
- **Smoke (vor der Festlegung, gesehen):** R-iid, 1500 Schritte: läuft, 0.026 s/Schritt unter Last (250 000 ≈ 1.8 h), Train 0.017, Test 1e-4.
- **Arme (Reihenfolge = Priorität):** F-iid, R-iid, R-stride, F-stride.
- **Lesarten:** Q1–Q3 **wörtlich wie EXP-143** (README dort, inkl. Nachtrag d: Stride-Familie, M1: Q3 nur bei generalisiertem F-stride; Auswertung mit `EXP-143-ledoux-regime/analyze.py --root lab/experiments/EXP-144-ledoux-width/raw`). Hier gilt Q2/Q3 am 250 000-Budget (keine 600 000-Arme vorab).
- **Q0 (neu, beschreibend):** Lernt die Breite die Trainingsmenge (Train-Genauigkeit ≥ 0.9 bis Schritt 250 000) in den i.i.d.-Armen? Nein in beiden → „Breite allein behebt es nicht“, dann ist die nächste Stellschraube die Tiefe/LeDoux' Modell, nicht mehr Breite.
- **Was dagegen spräche:** die Gegenausgänge von Q1–Q3; ein nicht generalisierender Arm heißt nur „nicht im Budget“.
- **Grenzen:** 1 Seed, Splits von EXP-143 schon gesehen (nur ihr Verhalten bei d 128), ein Budget, andere Architektur als LeDoux.
- **Bereits gesehene Daten und davon beeinflusste Entscheidungen:** alle EXP-143-Ergebnisse bis 16:46 (drei fertige d-128-Arme, R-stride bis ≈ 100 000 Schritte; frühe CPU-Prägung, 3 Seeds) – sie haben die Wahl „mehr Breite“ und Q0 bestimmt; der d-512-Smoke (R-iid, 1500 Schritte).

## Nachtrag a (Sitzung 71, 16:55 Berlin (gemessen), vor dem Start des ersten EXP-144-Laufs): LeDoux' Aufbau im Volltext

LeDoux 2026 §4.1.2 (HTML-Volltext): zweischichtiger Pre-LayerNorm-Transformer, Einbettung 256, 4 Köpfe, Feedforward 2048; AdamW wd 0.1, β (0.9, 0.999), lr 1e-3 mit Cosine-Abfall über 5000 Epochen, Batch 256; Stride erreicht 90 % Train bei ≈ Epoche 140 und 99.5 % Test bei Epoche 487; **Random (i.i.d.) lernt dort nur auswendig und generalisiert in 5000 Epochen nicht.** Unser EXP-144: 1 Schicht ohne LayerNorm, d 512, Feedforward 2048 (gleich), β (0.9, 0.98), konstante lr, 213 Epochen. Folgen für die Lesart (keine Änderung an Q0–Q3): R-iid ohne gen ist bei LeDoux der erwartete Ausgang; die informative Zelle für Q1 ist F-iid; Q2 kann im 213-Epochen-Budget auch bei passendem Modell nur „nicht im Budget“ ergeben (LeDoux: Epoche 487).

## Befehle

```
python lab/tools/guarded_run.py -- python lab/tools/test_freq_ban_large.py
python lab/experiments/EXP-144-ledoux-width/make_jobs.py > lab/queue/staging/52a7zzz_exp144_width.jobs   (dann mv nach lab/queue/inbox/)
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-143-ledoux-regime/analyze.py --root lab/experiments/EXP-144-ledoux-width/raw [--traj]
```

## Zwischenstand (Sitzung 71, 17:40 Berlin (gemessen); 1 von 4 Armen fertig, keine Lesart gelesen)

- **F-iid (d 512, 250 000 Schritte):** kein gen (Test höchstens 0.00095); Train-Genauigkeit steigt bis ≈ 15 000 Schritte auf ≈ 0.85, Spitze **0.911**, am Ende **0.864** (d 128: 0.36). Top-5 = die 5 Ziele von Schritt 2500 bis 250 000, T/med Spitze ≈ 5.5, am Ende 4.51; k = 101 neutral.
- **Hinweis zu Q0 (vor dem Lesen, ohne Änderung der Regel):** „Train ≥ 0.9 bis Schritt 250 000“ ist mehrdeutig (erreicht vs. am Ende). Berichtet werden beide Werte (Spitze und Ende); Q0 wird erst gelesen, wenn auch R-iid fertig ist.
- Laufen beim Dienst: R-iid, R-stride, F-stride (je ≈ 1 h bei ≈ 100 Schritten/s).

## Ergebnis (Sitzung 72, 19:18 Berlin (gemessen); alle 4 Arme fertig, je 250 000 Schritte ≈ 214 Epochen)

Auswertung: `EXP-143-ledoux-regime/analyze.py --root lab/experiments/EXP-144-ledoux-width/raw --traj`. **Kein Arm generalisiert.**

| Arm | Train Spitze (Schritt) | Train Ende | Test höchstens | Top-5 am Ende | Ziele in Top-5 | T/med |
|---|---|---|---|---|---|---|
| F-iid | 0.911 (184 000) | 0.864 | 0.00095 | 1100, 1296, 1691, 2142, 2511 | 5 | 4.51 |
| R-iid | 0.910 (184 000) | 0.862 | 0.00085 | 128, 1822, 2875, 3743, 4744 | 0 | 1.01 |
| R-stride | 0.371 (122 000) | 0.254 | 0.00215 | 101, 202, 303, 504, 909 | 0 | 0.98 |
| F-stride | 0.404 (120 000) | 0.270 | 0.0010 | 101, 202, 303, 1296, 2511 | 2 | 3.26 |

**Lesarten (vorab):**
- **Q0:** an der Spitze erfüllt (beide i.i.d.-Arme ≥ 0.9 ab Schritt 109 000), am Ende knapp nicht (0.864 / 0.862). Lesart: Die 4-fache Breite hebt die Anpassung an die Trainingsmenge von 0.36/0.41 (d 128) auf ≈ 0.9; Generalisierung bleibt im Budget aus. Mehr Breite allein macht das Regime für unsere Frage nicht lesbar.
- **Q1 = „im Budget keine Aussage“** (F-iid und R-iid ohne gen).
- **Q2 = „nicht im Budget“** (R-stride generalisiert nicht; Stride-Familie über k = 101 in den Top-5).
- **Q3 nur beschreibend** (M1: F-stride generalisiert nicht). Muster wäre „beide“: Stride-Frequenzen (101 und Vielfache) und 2 der 5 F-Ziele in den Top-5.

**Beschreibend:** In beiden Stride-Armen dominieren 303 > 202 > 101 (Verhältnis zum Median am Ende 129.5 / 93.6 / 77.6 in F-stride, 161.8 / 109.8 / 69.6 in R-stride; k = 101 also Rang 3, nicht Rang 1; über den Verlauf erreicht k = 101 bis ≈ 900 × Median). 202 und 303 liegen außerhalb der vorab definierten Stride-Familie (Residuen 52 und 78 > 26); Familienanteil und Familienmaß unterschätzen das Stride-Signal daher, Q2/Q3 ändern sich nicht. Die Stride-Reihenfolge senkt die Train-Genauigkeit gegenüber i.i.d. stark (0.25–0.27 gegen 0.86). Bei i.i.d. bleibt das Spektrum der R-Menge flach (Top-5 nur ≈ 1.2 × Median, also Rauschen), die F-Menge trägt ihre 5 Ziele durchgehend.

**Einordnung:** passt zu LeDoux (§4.1.2/§5): i.i.d. lernt dort nur auswendig; Stride generalisiert dort erst bei Epoche 487 mit einem anderen Modell (2 Schichten, LayerNorm, Cosine-lr). Unser Budget (214 Epochen) und Modell (1 Schicht) reichen dafür nicht. Die Frage „Menge gegen Reihenfolge“ im LeDoux-Regime bleibt **offen**; Grenze (ii) im Paper bleibt unverändert. Kein Nachfolgeversuch (Regel 23).

**Unabhängige Nachrechnung (19:19 gemessen, Claude-Agent, eigener numpy-Code, nur lesend):** alle Zahlen reproduziert; 4/4 completed, keine NaN, cuda, d 512, gleiche Init-Prüfsumme in allen Armen, Split-/Test-Hashes passen zu den Dateien. Übernommen: k = 101 ist Rang 3 (303 und 202 davor), ein früherer Eindruck „Rang 1“ war falsch; 202/303 liegen außerhalb der Familie. F-iid lief auf Commit d63580bc, die übrigen auf 201718a7 (kein Unterschied in lab/tools/ zwischen beiden).

**Grenzen:** 1 Seed je Arm, Splits aus EXP-143 schon gesehen, ein Budget, andere Architektur als LeDoux. Exploration, keine Bestätigung.
