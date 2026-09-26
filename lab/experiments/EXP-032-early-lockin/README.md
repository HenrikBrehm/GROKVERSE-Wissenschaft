---
id: EXP-032
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-032: Wie früh legt sich das Netz fest? Feines Umschaltraster in den ersten 50 Schritten

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N12) · Vorgänger
[[experiments/EXP-026-parity-crossover/README|EXP-026]].

## Anlass

EXP-026 (beschreibend): Die F-Neigung springt zwischen t_s = 0 (−0.002) und t_s = 50 (+0.165) und bleibt danach auf einem
Plateau. Der dortige Rangtest über alle Stufen passte nicht zur Stufenform (*Anker ok, Trend n. s.*). Hier wird die Stufe
mit neuen Läufen und einem passenden Kriterium vermessen.

## Versuch (vorab festgelegt 2026-09-26 10:31 Berlin, vor jedem EXP-032-Lauf)

| Punkt | Festlegung |
|---|---|
| **Frage** | Nach wie vielen Schritten mit σ_3 = 3x + x² ist die F-Neigung des danach rein quadratischen Netzes festgelegt? |
| **Arme** | t_s ∈ {1, 5, 10, 20} neu (`train_sigma.py --alpha 3 --switch-step t_s --alpha-after 0`), dazu t_s = 0 und 50 aus EXP-026 (gleicher Code bis auf Protokoll-Schnappschüsse bei 5/10/20, die das Training nicht berühren) |
| **Einheiten** | EXP-016-Splits Seeds 10–14, Arm F → 20 neue Läufe |
| **Messgröße** | ds = Anteil(F) − Anteil(H) am normierten h = 2-Spektrum bei Schritt 5000 (wie EXP-026 Nachtrag b) |
| **Primär 1 (Monotonie im Anstieg)** | Spearman(Rang t_s, ds) über die 30 Läufe mit t_s ∈ {0, 1, 5, 10, 20, 50}, Permutation innerhalb der Splits (10 000×), einseitig p < 0.05 |
| **Primär 2 (Halbwertszeit)** | t½ = kleinstes t_s, dessen mittleres ds ≥ ½ · mittleres ds(50) ist |
| **Entscheidung** | Primär 1 erfüllt und t½ ≤ 20 → *Festlegung in ≤ 20 Schritten*; Primär 1 erfüllt und t½ = 50 → *Festlegung zwischen 20 und 50*; Primär 1 nicht erfüllt → *nicht aufgelöst*. Nur mit vollständigem 6 × 5-Raster, jedes Endnetz generalisiert (Test ≥ 0.9), sonst *nicht auswertbar* |
| **Sekundär** | Anteil F und Amplitude r (Median, ausgabegewichtet) am Umschaltschritt aus den Schnappschüssen bei 1/5/10/20/50; Generalisierungsschritt je Arm |
| **Erwartung** | t½ ≤ 20: AdamW-Schritte (1e-3) überholen die Init-Amplitude (≈ 0.007) nach wenigen Schritten |
| **Was dagegen spräche** | t½ = 50 oder kein Anstieg bis 20 |
| **Grenzen** | 5 Splits; die Einheiten 10–14 F sind aus EXP-026 bekannt (dort nur t_s = 0 und ≥ 50) |
| **Budget** | 20 × ~88 s ≈ 30 min |

## Befehle

    sh lab/experiments/EXP-032-early-lockin/queue.sh
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-032-early-lockin/analyze.py
