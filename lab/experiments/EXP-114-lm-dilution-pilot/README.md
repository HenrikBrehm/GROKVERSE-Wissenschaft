---
id: EXP-114
status: vorbereitet
datum: 2026-09-29
tags: [exp/vorbereitet, lm-leiter]
---
# EXP-114: Fehlt die frühe Steuerung im LM wegen der Verdünnung durch Text? (Pilot, 1 Seed)

Zurück: [[LAB]] · [[FINDINGS]] · [[BACKLOG]] (Sitzung 50) · Anlass [[experiments/EXP-113-lm-ladder-stage2b/README|EXP-113]] Nachtrag 1 · [[JOURNAL]] Sitzung 50

**Bezug zu FINDINGS:** offene Frage „Verallgemeinerung von K2 auf Sprachmodelle“ (Programm A, Regel 20e). Exploration (1 Seed, F/G), keine Bestätigung, kein Urteil über K2.

## Vorab (Sitzung 50, 11:48 Berlin gemessen, vor jedem Lauf)

- **Anlass:** In EXP-113 (`answer`, K = 8 Rechensätze je Sequenz, ≈ 34 % Rechen-Tokens) ist Δ_pow bis Schritt 4000 ≈ 0 bei Fakten auf Zufall; im Spielzeugmodell und in Stufe 1 (EXP-102) steuert die Maske schon früh, vor dem Lernen. Weight Decay und Lernrate erklären das nach EXP-103/R1 kaum (BACKLOG Sitzung 50).
- **Hypothese (b) Verdünnung:** Mit gebundenen Embeddings bekommen die Zahl-Zeilen an jeder Textposition einen zielunabhängigen Gradienten (Softmax über alle Tokens); Adam normiert je Koordinate, so schrumpft der Anteil des Maskensignals am Update. Weniger Text → frühe Steuerung kehrt zurück.
- **Aufbau:** unveränderter Trainer `lm_stage2.py` (Stand 7a63509f), Seed 3862, P1-Splits seed3802 F/G, Testmenge wie EXP-113, `--loss answer`, **`--arith-facts 19`** (≤ 19 wegen Kontext 256: längste Schablone 13 Tokens je Satz; Rechenanteil ≈ 79 %), 4000 Schritte, GPU-Dienst (`jobs.txt`, `raw_k19`). Vergleich: EXP-113 `answer` Seed 3862 (K = 8), gleiche Init, gleiche Splits.
- **Störgröße:** K = 19 zeigt ≈ 2.4× so viele Fakten je Schritt. Verglichen wird deshalb (1) je Lauf-Paar die Reihenfolge von Steuerung und Faktenlernen (unabhängig von der Zeitachse) und (2) Δ_pow bei gleicher Zahl gesehener Fakten (Faktenrunden aus den Läufen, linear interpoliert).
- **Lesarten (vorab):** **„Verdünnung gestützt“**: bei K = 19 erreicht Δ_pow > 1 einen Snapshot, an dem noch nicht beide Läufe Trainingsfakten ≥ 0.1 haben (Steuerung vor dem Lernen), **und** bei gleicher Faktenzahl liegt Δ_pow(K 19) über Δ_pow(K 8) an allen gemeinsamen Punkten bis zum Lernbeginn von K 8. **„Verdünnung nicht gestützt“**: bei K = 19 bleibt Δ_pow ≤ 1 bis zum Lernbeginn (wie H-folgt). Sonst „unklar“. Lernt K = 19 bis 4000 keine Fakten und bleibt Δ_pow ≤ 1: „nicht gestützt (Budget)“.
- **Was dagegen spräche:** siehe „nicht gestützt“; dann bleiben Tiefe/Warmup/Minibatch-Struktur als Kandidaten.
- **Budget/Abbruch:** ≈ 0.3 s/Schritt unter Last → ≈ 20–25 min je Lauf; harte Grenze 120 min (Dienst). Abbruch bei NaN (Trainer) oder Absturz.
- **Bereits gesehene Daten:** EXP-113 `answer` Seed 3862 bis Schritt 4000 (Δ_pow ≈ 0), EXP-105-Pilot, EXP-102/103, R1. Davon beeinflusst: die Frage selbst und die Wahl K = 19.
- **Auswertung:** `analyze.py` (vor dem Ergebnis geschrieben), liest die fertigen Läufe von EXP-114 und die Snapshots von EXP-113 (`answer`, Seed 3862; braucht dessen fertige Läufe).
