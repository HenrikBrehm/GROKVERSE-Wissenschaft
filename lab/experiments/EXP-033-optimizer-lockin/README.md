---
id: EXP-033
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-033: Ist die 5-Schritte-Festlegung aus EXP-032 ein AdamW-Artefakt?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N12) · Vorgänger
[[experiments/EXP-032-early-lockin/README|EXP-032]] · [[experiments/EXP-026-parity-crossover/README|EXP-026]].

## Anlass

EXP-032: 5 Schritte mit σ_3 = 3x + x² legen die halbe F-Neigung des danach rein quadratischen Netzes fest. Einwand
(eigener, gestützt durch Abuduweili & Liu 2024, https://arxiv.org/abs/2412.02153): Der erste Adam-Schritt ist ein reiner
Vorzeichen-Schritt der Größe lr pro Parameter, unabhängig davon, wie klein der Gradient ist. Bei Init-Einträgen von ≈ 0.0067
verschiebt jeder Schritt jeden Eintrag um ≈ 15 %. In EXP-032 ist die Amplitude r am Umschaltschritt über alle 5 Splits
**praktisch gleich** (t_s = 5: 0.01180–0.01185; t_s = 20: 0.02893–0.02897), ebenso ds am Umschaltschritt (0.035 ± 0.004).
Das passt zu gleichförmigen Vorzeichen-Schritten. „5 Schritte“ ist also keine Eigenschaft der Lerndynamik, sondern der
Schrittgröße. Offen ist, ob die **Festlegung selbst** (ein kleiner früher Vorsprung wird bis zum Ende verstärkt und
beibehalten) an der Adam-Geometrie hängt oder ob jeder Weg zum gleichen Zustand dasselbe Ergebnis gibt.

## Versuch (vorab festgelegt 2026-09-26 12:20 Berlin, vor jedem EXP-033-Lauf)

| Punkt | Festlegung |
|---|---|
| **Frage** | Entsteht die bleibende F-Neigung auch, wenn die σ_3-Phase mit reinem Gradientenabstieg (GD) statt AdamW läuft, bei gleicher erreichter Merkmalsamplitude r? |
| **Einheiten** | EXP-016-Splits Seeds 10–14, Arm F (wie EXP-032), gleiche Init |
| **Phase 1** | σ_3. Arm **AR** (Kontrolle): AdamW wie EXP-032, t_s ∈ {5, 10, 20} Schritte. Arm **GD**: `torch.optim.SGD` ohne Momentum und ohne Weight Decay, volle Batch, bis Median-r ≥ Ziel-r; Ziel-r je Split und Stufe = r am Umschaltschritt des EXP-032-Laufs (t_s = 5/10/20) |
| **Phase 2** | Beide Arme: reines x², **frischer** AdamW (lr 1e-3, wd 1, β 0.9/0.98), 5000 Schritte. Nur Phase 1 unterscheidet die Arme |
| **Anker** | EXP-032 t_s = 0 (nur x², 5000 Schritte AdamW ab Init): ds₀ je Split |
| **GD-Lernrate** | Vorab per Smoke nur an Phase 1 gewählt (`--phase1-only`, Split 10, Ziel r = 0.0290): größte lr aus {0.3, 1, 3, 10, 30}, die das Ziel ohne NaN erreicht und dabei die Trainings-Acc nicht springen lässt; bei mehreren gültigen die kleinste, die ≤ 3000 Schritte braucht. Das Ergebnis (ds) wird im Smoke nicht berechnet |
| **Messgröße** | ds = Anteil(F) − Anteil(H) am normierten h = 2-Spektrum am Ende von Phase 2 (wie EXP-032) |
| **Primär P33a** | GD-Neigung über dem Anker: ds(GD) > ds₀ in ≥ 13 der 15 Einheiten (Split × Stufe); Vorzeichentest einseitig p ≈ 0.004 |
| **Primär P33b** | Quotient Q = Mittel ds(GD) / Mittel ds(AR) über die 15 Einheiten |
| **Entscheidung** | P33a erfüllt und 0.5 ≤ Q ≤ 2 → ***zustandsbestimmt*** (Festlegung nicht an AdamW gebunden); P33a erfüllt und Q > 2 → ***GD stärker***; P33a erfüllt und Q < 0.5 → ***AdamW verstärkt, Festlegung schwach vorhanden***; P33a nicht erfüllt → ***AdamW-gebunden*** (ohne Adam-Phase-1 keine bleibende Neigung). Gültig nur, wenn ≥ 12 GD-Einheiten das Ziel-r erreichen und alle Endnetze Test ≥ 0.9 haben; sonst *nicht auswertbar* |
| **Sekundär** | ds am Umschaltschritt je Arm (ist GD gleich weit geneigt?); Verstärkungsfaktor ds_Ende / ds_Umschalt; Phase-1-Schritte von GD; AR gegen EXP-032 (Wirkung des frischen Optimierers); Generalisierungsschritt |
| **Erwartung (schwach)** | *zustandsbestimmt* oder *GD stärker*: GD folgt dem Gradienten ohne Vorzeichen-Rauschen; der lineare Anteil liefert die F-Richtung direkt |
| **Was dagegen spräche** | ds(GD) ≈ ds₀: Dann braucht die Festlegung die Adam-Geometrie der ersten Schritte |
| **Grenzen** | Ziel-r ist ein Median über Neuronen, nicht die ganze Verteilung; W_out wächst unter GD anders (berichtet: ‖W_out‖ am Umschaltschritt). Eine Architektur, 5 Splits |
| **Budget** | Smoke 5 × ≤ 1 min; 15 AR-Läufe ≈ 90 s, 15 GD-Läufe ≈ 2–4 min → ≈ 1–1.5 h |

## Befehle

    # Smoke (lr-Wahl, nur Phase 1):
    for L in 0.3 1 3 10 30; do python lab/tools/guarded_run.py -- python lab/experiments/EXP-033-optimizer-lockin/train_opt.py --seed 10 --opt1 gd --switch-r 0.0290 --gd-lr $L --max-phase1 5000 --phase1-only --out lab/experiments/EXP-033-optimizer-lockin/raw_smoke; done
    sh lab/experiments/EXP-033-optimizer-lockin/queue.sh <lr>
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-033-optimizer-lockin/analyze.py
