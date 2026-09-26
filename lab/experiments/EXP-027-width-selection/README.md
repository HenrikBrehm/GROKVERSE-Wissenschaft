---
id: EXP-027
status: abgeschlossen
datum: 2026-09-26
tags: [exp/abgeschlossen, neu/kandidat, befund/negativ]
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

## Nachtrag a (09:30 Berlin, nach Codex-Review, vor jedem EXP-027-Lauf)

Codex (`codex_review_2026-09-26.txt`, „needs-attention“, 2 × high, 2 × medium) bestätigte, dass die Wiederverwendung von
EXP-026 t_s = 0 als Breite 512 rechnerisch identisch ist. Selbst geprüft, übernommen:
1. **Güte-Schwelle:** Jeder Lauf braucht Train-Genauigkeit ≥ 0.99 und Test-Genauigkeit ≥ 0.90, sonst ist das Raster
   *nicht auswertbar*. Nicht generalisierende Netze können nichts bestätigen.
2. **Kalibrierte Statistik statt ds_H:** Schmale Netze haben konzentriertere Spektren, dann streut ds_H stärker, und die
   Permutation über Breiten wäre nicht kalibriert. Neu je Lauf: q_H bzw. q_F = Perzentil des Anteils von H bzw. F unter
   20 000 zufälligen 5er-Mengen desselben Spektrums. Ohne Bevorzugung sind beide gleichverteilt, unabhängig von der
   Konzentration. **Primär jetzt u = q_H − q_F**, Spearman(Rang −w, u), Permutation innerhalb der Splits, Schwelle
   p < 0.05 wie gehabt. ds_H, Top-5 und n_eff nur berichtet.
3. **Init-Skala und Schwelle:** Die W_out-Init hat jetzt je Eintrag dieselbe Streuung wie bei 512 (0.1/√512), unabhängig
   von w (für w = 512 unverändert). Zusätzliche Breite **256** nahe der Schwelle 448. Stufen jetzt {32, 64, 128, 256, 512},
   20 neue Läufe.
4. **Herkunft:** Seed, lr, wd, Init-Skala, Zufallssplit-Schalter, Split-Verzeichnis, Breite und Endaktivierung werden
   geprüft.
Nicht übernommen (Grenze): Init-Wiederholungen je Split und Breite und Training bis zur Konvergenz statt fester
Schrittzahl (Budget). Ein positiver Befund belegt nicht, dass genau die Kapazitätsgrenze von Morwani die Ursache ist;
AdamW und Weight Decay können mit der Breite wechselwirken.
Auswerter an vier synthetischen Fällen geprüft (Trend → bestätigt, kein Trend → nicht bestätigt, Güte verfehlt,
falsche Herkunft), über den Wächter.

## Nachtrag b (10:32 Berlin): EXP-027b vorab festgelegt, bevor ich die EXP-027-Ergebnisgröße angesehen habe

Beobachtung während des Laufs (nur Gültigkeitsgröße): Die 32er-Netze erreichen Test 0.83–0.86 und verfehlen damit die
Güte-Schwelle 0.90; EXP-027 wird nach seiner Regel *nicht auswertbar* sein. Die Ergebnisgröße u habe ich nicht angesehen.
**EXP-027b** (neue, unabhängige Einheiten): EXP-016-Splits **Seeds 15–19**, Arm F; Breiten **{64, 128, 256, 512}**
(512 neu trainiert, `--alpha 0`); sonst alles wie Nachtrag a (u = q_H − q_F, Spearman über Rang −w, Permutation innerhalb der
Splits, p < 0.05; Güte-Schwelle Train ≥ 0.99, Test ≥ 0.90; vollständiges 4 × 5-Raster). Entscheidung wie EXP-027.
`queue_b.sh`, `analyze_b.py`.

## Ergebnis EXP-027 (Sitzung 7, 10:39 Berlin)

25/25 Läufe gültig in der Herkunft, aber alle 5 Läufe mit Breite 32 verfehlen die Güte-Schwelle (Test 0.83–0.86).
**Urteil nach der Vorab-Regel: *nicht auswertbar (Güte-Schwelle verfehlt)*.**

Beschreibend (Mittel je Breite, nicht bewertet):

| Breite | 512 | 256 | 128 | 64 | 32 |
|---|---|---|---|---|---|
| u = q_H − q_F | +0.02 | −0.14 | −0.09 | +0.07 | +0.14 |
| q_H | 0.58 | 0.57 | 0.47 | 0.48 | 0.49 |
| n_eff (effektive Zahl genutzter Frequenzen) | 52.3 | 49.8 | 45.4 | 40.3 | 30.4 |
| Test-Genauigkeit | 1.00 | 1.00 | 1.00 | 0.99 | 0.85 |

Kein erkennbarer Trend der H-Bevorzugung mit der Breite; auch bei 512 ist q_H auf diesen 5 Splits nur 0.58. Die Netze werden
mit sinkender Breite konzentrierter, nutzen aber selbst mit 32 Neuronen noch ≈ 30 Frequenzen effektiv; eine Auswahl
weniger Frequenzen wie beim Transformer entsteht nicht. EXP-027b (Nachtrag b) läuft wie festgelegt.

## Ergebnis EXP-027b (Sitzung 7, 11:24 Berlin)

20/20 gültig, Güte-Schwelle überall erfüllt (Breite 64: Test 0.994). Spearman(Rang −w, u) = −0.16, Permutations-p = 0.74.
**Urteil: *widerspricht*.** Schmalere Netze bevorzugen die halben Ziele nicht stärker.

| Breite | 512 | 256 | 128 | 64 |
|---|---|---|---|---|
| u = q_H − q_F | +0.23 | +0.36 | +0.10 | +0.16 |
| q_H | 0.75 | 0.58 | 0.69 | 0.66 |
| n_eff | 52.2 | 50.1 | 45.1 | 40.1 |

Beschreibend: Auf diesen frischen Splits ist die H-Neigung in allen Breiten vorhanden (u > 0 in allen vier Breiten;
passt zu EXP-024 Arm Q), hängt aber nicht von der Breite ab. Die Idee „Kapazitätsgrenze → Auswahl“ ist **verworfen**.

## Befehle

    sh lab/experiments/EXP-027-width-selection/queue.sh
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-027-width-selection/analyze.py
