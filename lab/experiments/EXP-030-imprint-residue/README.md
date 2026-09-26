---
id: EXP-030
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-030: Ist die M0 → K-Vorhersage (EXP-015) nur der Rest des frühen Abdrucks in W_E?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N13) · Vorgänger
[[experiments/EXP-029-memo-imprint-random/README|EXP-029]] · [[experiments/EXP-015-mask-spectrum/README|EXP-015]] ·
[[experiments/EXP-012-init-gradient/README|EXP-012]] (W_E bei Schritt 250 sagt K voraus, bekannt).

## Anlass

Codex-Angriff auf N13 (`EXP-029/codex_conclusion_review_2026-09-26.txt`): „Rest“ ist erst belegt, wenn M0 über den frühen
W_E-Abdruck hinaus **nichts** mehr über K verrät (Mediation). Sonst könnte K später über einen eigenen, ebenfalls
M0-korrelierten Prozess gewählt werden.

## Versuch (vorab festgelegt 2026-09-26 09:58 Berlin, vor der Auswertung; keine neuen Läufe)

| Punkt | Festlegung |
|---|---|
| **Daten** | EXP-003d-Baselines Seeds 10–19; K = `final_top_m_freqs` (Top-5 von W_E am Laufende, gen + 25) |
| **Größen je Seed, über die 56 Frequenzen** | A = W_E-Leistung bei Schritt **250** (Memorisierungsphase); M = M0 der eigenen Maske; k = Indikator „Frequenz ∈ K“. ρ_M = Spearman(M, k); ρ_M·A = partielle Spearman-Korrelation von M und k gegeben A (Pearson der Residuen der Ränge nach linearer Regression auf den Rang von A); ρ_A = Spearman(A, k) |
| **Voraussetzung** | mittleres ρ_M > 0 und mittleres ρ_A > 0, sonst *nicht auswertbar* |
| **Primär (Mediation)** | Δ = ρ_M − ρ_M·A je Seed; exakter einseitiger Vorzeichen-Flip-Test auf Δ̄ > 0 |
| **Entscheidung** | *Rest gestützt*: p < 0.05 **und** mittleres ρ_M·A ≤ ½ · mittleres ρ_M · *M0 wirkt auch direkt*: mittleres ρ_M·A > ½ · mittleres ρ_M · sonst *unklar* |
| **Sekundär** | ρ_A·M (Abdruck sagt K über M0 hinaus voraus); dasselbe mit A bei Schritt 500 und 1000; fremde Masken als Kontrolle für ρ_M |
| **Was dagegen spräche** | ρ_M·A ≈ ρ_M: M0 hängt mit K über einen Weg zusammen, der nicht durch den frühen Abdruck läuft |
| **Grenzen** | Mediation über Korrelation, kein Eingriff. k ist binär (5 von 56), die partielle Korrelation ist deshalb grob. Seeds 10–19 sind für M0 → K (EXP-015) und den Abdruck (EXP-029) schon ausgewertet; die Mediation selbst habe ich nicht angesehen |

## Befehle

    python lab/tools/guarded_run.py -- python lab/experiments/EXP-030-imprint-residue/analyze.py
