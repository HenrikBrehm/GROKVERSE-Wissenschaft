---
id: EXP-032
status: abgeschlossen
datum: 2026-09-26
tags: [exp/abgeschlossen, neu/kandidat, befund/positiv]
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

## Ergebnis (Sitzung 7, 11:09 Berlin)

30/30 gültig (20 neu, t_s = 0 und 50 aus EXP-026); alle Endnetze generalisieren (Test 1.0).

| t_s | 0 | 1 | 5 | 10 | 20 | 50 |
|---|---|---|---|---|---|---|
| mittleres ds bei 5000 | −0.002 | +0.024 | **+0.094** | +0.131 | +0.147 | +0.165 |
| mittleres ds am Umschaltschritt | 0.002 | 0.003 | 0.034 | 0.067 | 0.098 | 0.117 |
| Amplitude r am Umschaltschritt (Median) | 0.0094 | 0.0095 | 0.0118 | 0.0167 | 0.0290 | 0.0725 |
| Generalisierungsschritt | 1390 | 1560 | 1990 | 2140 | 2370 | 2730 |

Spearman ρ = 0.91, Permutations-p = 1e-4; t½ = 5 (erste Stufe mit ds ≥ ½ · ds(50)).
**Urteil: *Festlegung in ≤ 20 Schritten*** (vorab festgelegt). Schon **5 Schritte** mit linearem Anteil legen die halbe
End-Neigung fest, zu einem Zeitpunkt, an dem die Merkmale erst ~25 % über der Init-Amplitude liegen.
**Beschreibend:** Die Neigung am Umschaltschritt wird bis zum Ende etwa verdreifacht (0.034 → 0.094 bei t_s = 5), das spricht
für ein Verstärken des frühen Vorsprungs („wer zuerst wächst, gewinnt“) statt bloßen Erhaltens. Jeder zusätzliche frühe
Schritt mit linearem Anteil verzögert die Generalisierung (1390 → 2730 Schritte).
**Grenzen:** 5 Splits, eine Architektur, eine Lernrate; AdamW normiert die ersten Schritte stark (Schrittweite ≈ lr pro
Parameter unabhängig vom Gradientenbetrag), was die frühe Festlegung begünstigen könnte. Ob das bei SGD oder kleinerer
Lernrate ebenso schnell geht, ist offen.

## Befehle

    sh lab/experiments/EXP-032-early-lockin/queue.sh
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-032-early-lockin/analyze.py
