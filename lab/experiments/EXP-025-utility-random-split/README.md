---
id: EXP-025
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-025: Sagt der architekturspezifische AGF-Nutzen die Frequenzwahl auch unter Zufallssplits voraus?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N11) · Vorgänger
[[experiments/EXP-024-quadratic-agf-mask/README|EXP-024]] (konstruierte Splits) · Gegenstück beim Transformer:
[[experiments/EXP-015-mask-spectrum/README|EXP-015]] (M0 sagt K voraus, r̄ 0.28).

## Versuch (vorab festgelegt 2026-09-26 08:55 Berlin, vor jedem EXP-025-Lauf und vor der EXP-024-Auswertung)

| Punkt | Festlegung |
|---|---|
| **Frage** | Unter den gewöhnlichen 30 %-Zufallssplits der Studie (Seeds 10–19) ist das Masken-Spektrum fast flach. Sagt der exakte Nutzen U_act(k) der eigenen Aktivierung (x² bzw. ReLU) trotzdem voraus, welche Frequenzen das trainierte Zwei-Hot-Netz lernt, und zwar besser als der Nutzen der jeweils anderen Aktivierung? |
| **Modell** | wie EXP-024 (`train_twohot.py --random-split`), 512 Neuronen, ohne Biases, CE, AdamW 1e-3, wd 1.0, Init-Skala 0.1, 5000 Schritte, Init-Seed = Split-Seed. Split = `make_dataset(get_config("arch25k", seed=s))`, Testmenge = Komplement |
| **K** | Top-5 der reskalierungsinvarianten Eingabeleistung bei Schritt 5000 (EXP-024 Nachtrag a) |
| **Prädiktoren** | U_quad(k), U_relu(k): exakter Nutzen auf der tatsächlichen Maske (16 × 16 Phasen, `utility_relu.utility`); M0 (sekundär) |
| **Primär (Spezifität)** | d = r̄(U_andere, K) − r̄(U_eigene, K) über alle 20 Einheiten (10 Seeds × 2 Arme); exakter einseitiger Vorzeichen-Flip-Test auf d̄ > 0 |
| **Ko-primär** | r̄(U_eigene, K) über die 20 Einheiten gegen die Monte-Carlo-Null 0.5 (`mc_null_p`, wie EXP-012) |
| **Entscheidung** | *bestätigt*: beide p < 0.05 · *teilweise*: nur eines · *widerspricht*: d̄ ≤ 0 · *richtungsgleich, n. s.*: sonst · < 16 vollständige Läufe: *nicht auswertbar* |
| **Sekundär** | r̄ mit fremden Masken (U_eigene der anderen Seeds), r̄(M0), Test-Genauigkeit |
| **Was dagegen spräche** | d̄ ≤ 0 oder r̄ ≈ 0.5: Unter natürlichen Splits dominiert dann die Init (He et al. 2026: Betrag und Phase je Neuron), nicht der Split |
| **Grenzen** | Die Seeds 10–19 der Zufallssplits sind für den Transformer schon ausgewertet (EXP-015), für diese Netze aber frisch. Beide Arme teilen denselben Split pro Seed (abhängige Einheiten). Die Nutzenrechnung ist eine Aussage über den Start (kleine Init); AdamW und CE weichen von der AGF-Annahme ab |
| **Budget** | 20 Läufe × ~60–80 s ≈ 25 min, dazu ~1 min Nutzenrechnung. Ein Job gleichzeitig |

## Nachtrag a (2026-09-26 09:19 Berlin, Sitzung 7, vor jedem EXP-025-Lauf)

EXP-024 post hoc: Die gewichteten Spektren dieser Zwei-Hot-Netze sind fast flach (Anteil je Frequenz ≈ 5/56), die Top-5
K sind deshalb verrauscht. Primär- und Ko-Primärtest bleiben **unverändert**. Neu, nur sekundär: ρ_own − ρ_other =
Spearman(U_eigene, Endspektrum) − Spearman(U_andere, Endspektrum) über alle 56 Frequenzen, Vorzeichen-Flip-Test über die
20 Einheiten. Ein Widerspruch zwischen primärem und sekundärem Ergebnis wird berichtet, nicht aufgelöst.

## Befehle

    sh lab/experiments/EXP-025-utility-random-split/queue.sh        (jeder Lauf über guarded_run.py)
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-025-utility-random-split/analyze.py
