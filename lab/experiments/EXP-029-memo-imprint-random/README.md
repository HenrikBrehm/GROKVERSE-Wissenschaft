---
id: EXP-029
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-029: Prägt die Memorisierung auch bei Zufallssplits das Masken-Spektrum in W_E ein?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N13) · Geschwister
[[experiments/EXP-028-memo-imprint/README|EXP-028]] (konstruierte Splits) · Grundlage
[[experiments/EXP-015-mask-spectrum/README|EXP-015]] (M0 sagt K am Ende schwach voraus, r̄ 0.28).

## Anlass (explorativ, Sitzung 7, Studienläufe Seeds 0–9, `EXP-015/posthoc_m0_timecourse.py`)

ρ = Spearman(W_E-Leistungsspektrum, M0 der Trainingsmaske) über das Training, Mittel über 10 Seeds: Init −0.02, vor der
Memorisierung 0.19, **Memorisierungsphase 0.48 (erste Hälfte) / 0.44 (zweite Hälfte)**, nach der Generalisierung 0.19,
Ende (25 000) 0.14. In 10/10 Seeds ist ρ im Memorisierungsfenster höher als nach dem Grokking. Kalibrierung für die
Baselines, die 25 Schritte nach der Generalisierung stoppen (`calibration_seeds0-9.py`): ρ am geloggten Schritt nahe
gen + 25 liegt in 9/10 Seeds unter dem Mittel des Memorisierungsfensters (Mittel 0.38 gegen 0.47).

## Versuch (vorab festgelegt 2026-09-26 09:49 Berlin; die Zeitverläufe der Baselines 10–19 habe ich nicht angesehen, nur ihre
Endfrequenzen K in EXP-015/019)

| Punkt | Festlegung |
|---|---|
| **Daten** | EXP-003d-Baselines Seeds 10–19 (`EXP-003-early-prediction/raw_d/*`, Spektren alle 250 Schritte, Stopp bei gen + 25). Keine neuen Läufe |
| **Größen je Seed** | ρ_init (Schritt 0); ρ_memo = Mittel von ρ über alle Spektren mit Schritt ≥ Memorisierung und < Generalisierung; ρ_end = ρ am letzten Spektrum (gen + 25) |
| **P29a (Einprägung, primär)** | ρ_memo > ρ_init in ≥ 9/10 Seeds (Vorzeichentest einseitig, p = 0.011) **und** mittleres ρ_memo ≥ 0.30 |
| **P29b (Beginn des Verblassens, primär)** | ρ_memo > ρ_end in ≥ 9/10 Seeds |
| **Entscheidung** | beide → *bestätigt*; eine → *teilweise*; keine → *nicht bestätigt*; < 8 Seeds mit ≥ 3 Spektren im Fenster → *nicht auswertbar* |
| **Sekundär** | ρ_memo erste gegen zweite Fensterhälfte; Schritt des Maximums von ρ; Top-5-Überlappung mit den M0-Top-5 im Fenster gegen am Ende |
| **Was dagegen spräche** | ρ_memo ≈ ρ_init oder ≈ ρ_end: Dann ist das explorative Muster an 0–9 nicht stabil |
| **Grenzen** | Eine Assoziation; kausal ist nur EXP-016 (Steuerung durch konstruierte Splits). ρ_end liegt kurz nach dem Grokking, das große Verblassen danach ist in den Baselines nicht beobachtbar. Die Wahl ρ (Spearman über alle 56 Frequenzen) und die Fenstergrenzen sind aus der Exploration übernommen |

## Befehle

    python lab/tools/guarded_run.py -- python lab/experiments/EXP-029-memo-imprint-random/analyze.py
