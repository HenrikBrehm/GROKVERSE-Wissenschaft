---
id: EXP-144
status: vorbereitet
datum: 2026-10-01
tags: [exp/vorbereitet]
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

## Ergebnis

Offen.
