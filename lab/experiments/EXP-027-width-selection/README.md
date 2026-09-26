---
id: EXP-027
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-027: Wird die Split-Neigung zur Auswahl, wenn das Netz zu schmal für alle Frequenzen ist?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N11) · Vorgänger
[[experiments/EXP-024-quadratic-agf-mask/README|EXP-024]] · teilt Läufe mit [[experiments/EXP-026-parity-crossover/README|EXP-026]].

## Anlass

EXP-024 Arm Q (Sitzung 7): Das breite x²-Netz (512 Neuronen) nutzt praktisch alle 56 Frequenzen; der Split neigt die
Leistung nur leicht zu den halben Zielen H (Anteil 0.102 gegen F 0.084, Zufall 0.089). Nach Morwani et al. 2023
(Theorem 7) braucht die Max-Margin-Lösung, die jede Frequenz nutzt, mindestens 4(p−1) = 448 Neuronen. Ein schmaleres
Netz muss auswählen. Dann könnte die Neigung des Nutzens (AGF) zur Auswahl werden, wie beim Transformer (EXP-016).

## Versuch (vorab festgelegt 2026-09-26 09:21 Berlin, vor jedem EXP-027-Lauf)

| Punkt | Festlegung |
|---|---|
| **Frage** | Wächst die Bevorzugung der halben Ziele H, wenn die Breite unter 448 sinkt? |
| **H27** | ds_H = Anteil(H) − Anteil(F) am normierten h = 2-Spektrum bei Schritt 5000 steigt mit sinkender Breite |
| **Modell** | `EXP-026/train_sigma.py --alpha 0 --width w` (reines x², sonst wie EXP-024: ohne Biases, CE, AdamW 1e-3, wd 1.0, Init-Skala 0.1, 5000 Schritte, Init-Seed = Split-Seed; die W_out-Init skaliert mit 1/√w) |
| **Einheiten** | EXP-016-Splits Seeds 10–14, Arm F |
| **Stufen** | w ∈ {32, 64, 128, 512}. w = 512 wird **nicht** neu trainiert: Es ist rechnerisch identisch mit EXP-026 Arm t_s = 0 (α = 0 ab Schritt 0, gleiche Init) und wird von dort gelesen |
| **Primär** | Spearman ρ(Rang −w, ds_H) über 20 Einheiten > 0, Permutation von w innerhalb jedes Splits (10 000×), einseitig p < 0.05 → *bestätigt*; ρ ≤ 0 → *widerspricht*; sonst *richtungsgleich, n. s.* Nur mit vollständigem 4 × 5-Raster, sonst *nicht auswertbar* |
| **Sekundär** | ov(Top-5, H) und ov(Top-5, F) je Breite; Test-Genauigkeit und Generalisierungszeit je Breite; effektive Zahl genutzter Frequenzen exp(Entropie des Anteilsspektrums) |
| **Was dagegen spräche** | ds_H flach oder fallend: Schmale Netze wählen dann nach der Init (Lotterie je Neuron, He et al. 2026), nicht nach dem Split |
| **Grenzen** | Schmale Netze könnten schlechter generalisieren; dann vergleicht die Breite auch den Lösungstyp. Die Init-Skala von W_out hängt von w ab. Die Seeds 10–14 F sind aus EXP-024 bekannt (nur als Mittel über 19 Einheiten angesehen) |
| **Budget** | 15 neue Läufe, ≤ 80 s je Lauf ≈ 15–20 min; läuft nach EXP-026 (braucht dessen t_s = 0-Läufe) |

## Befehle

    sh lab/experiments/EXP-027-width-selection/queue.sh
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-027-width-selection/analyze.py
