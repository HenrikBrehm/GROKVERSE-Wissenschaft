---
id: EXP-017
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-015-mask-spectrum/README|EXP-015]]", "[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-017: Frequenzwahl ohne Zufalls-Init (Recursive Feature Machine)

**Status:** vorbereitet, **nicht ausgeführt**. Definition fixiert 2026-09-26 ~03:40 Berlin (Sitzung 4). Code `rfm.py`
(ungetestet). Idee N3b in [[NOVEL_DIRECTIONS]].

## Idee

Mallinar et al. 2025 (https://arxiv.org/abs/2407.20199) zeigen Grokking bei modularer Arithmetik mit Recursive Feature
Machines (RFM): Kernel-Regression, deren Merkmalsmatrix M iterativ durch den Average Gradient Outer Product (AGOP)
ersetzt wird. RFM hat **keine zufällige Initialisierung** (M₀ = I). Wählt RFM bestimmte Fourier-Frequenzen, kann die
Wahl nur aus dem Trainingssplit stammen. Das ist ein Test von N3 ohne jede Init-Konfundierung.

## Aufbau (eigene Implementierung, nicht die der Autoren)

- Daten: Split von Seed s wie im Training (`make_dataset`, p = 113, 30 %), Eingabe = [onehot(a), onehot(b)] ∈ R^226,
  Ziel = onehot(c) − 1/p.
- Kern: Gauß-Kern mit Mahalanobis-Metrik k(x, z) = exp(−(x−z)ᵀM(x−z) / (2L²)), L² = 1 (Abweichung von den Autoren,
  die meines Wissens einen anderen Kern nutzen; das wird nicht als Replikation bezeichnet).
- Iteration t = 1..T (T = 15): α = (K + λI)⁻¹Y, λ = 1e-3; M ← AGOP über die Trainingspunkte, skaliert auf Spur 2p.
- Frequenzmaß: Leistung pro Frequenz k des a-Blocks M[:p, :p] und des b-Blocks, Σ_k-Diagonale von Fᴴ M_blk F,
  k und p−k zusammengefasst; K_RFM = Top-5.

| | |
|---|---|
| **Fragestellung** | Konzentriert RFM seine Merkmale auf wenige Frequenzen, und sagt das Masken-Spektrum M0 des Splits diese voraus? |
| **Vorbedingung (sonst *nicht auswertbar*)** | Bei ≥ 8 von 10 Splits: Test-Acc ≥ 0.9 am Ende **und** Top-5-Anteil der Frequenzleistung ≥ 2 × 5/56 |
| **Primär** | Splits der Seeds 0–9: r̄ von K_RFM in der M0-Ordnung, passende gegen fremde Masken (Permutation wie EXP-015 Nachtrag b), p < 0.05 → *bestätigt* |
| **Sekundär** | Überlappung K_RFM mit den finalen Transformer-Frequenzen desselben Splits (EXP-009 `k_final`) gegen fremde Seeds |
| **Was dagegen spräche** | RFM wählt Frequenzen, M0 sagt sie nicht voraus → M0 erfasst nur die Gradientenstruktur neuronaler Netze |
| **Budget** | pro Split T Iterationen, je ein 3831er Gleichungssystem und ein AGOP über 3831 Punkte; Minuten. Über den Wächter, ein Job |
| **Grenzen** | eigener Kern und eigene Hyperparameter; keine Replikation von Mallinar et al. |

## Befehl

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-017-rfm-split/rfm.py --seeds 0-9 --iters 15
```
