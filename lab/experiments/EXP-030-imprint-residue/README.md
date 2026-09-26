---
id: EXP-030
status: abgeschlossen
datum: 2026-09-26
tags: [exp/abgeschlossen, neu/kandidat, befund/positiv]
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

## Ergebnis (Sitzung 7, 09:58 Berlin; Festlegung committet 9470d85 vor der Auswertung)

| Größe (Mittel über 10 Seeds) | Wert |
|---|---|
| ρ_M = Spearman(M0, K-Indikator) | 0.235 (fremde Masken 0.008) |
| **ρ_M·A250 (M0 gegeben W_E bei 250)** | **0.036** |
| Δ = ρ_M − ρ_M·A | 0.199, positiv in 10/10 Seeds, p = 0.001 |
| ρ_A250 / ρ_A250·M | 0.467 / 0.417 |
| gleiche Rechnung mit A bei 500 / 1000 | ρ_M·A 0.038 / 0.041 |

**Urteil: *Rest gestützt*** (p < 0.05, ρ_M·A ≤ ½ ρ_M). Was M0 über die Endfrequenzen verrät, steckt fast vollständig schon im
W_E-Zustand bei Schritt 250 (kurz nach Beginn der Memorisierung). Umgekehrt enthält dieser Zustand viel mehr über K als
M0 (0.42 nach Herausrechnen von M0; vermutlich die Init-Lotterie nach He et al. 2026 und EXP-012).
**Einordnung:** Mediation über Korrelation, kein Eingriff. Zusammen mit EXP-016 (Split steuert K kausal) und EXP-029
(maskenspezifische Ausrichtung vor der Generalisierung) ergibt sich ein konsistentes Bild: Die Maske wirkt über den frühen
Abdruck in W_E auf die Endwahl. Ob die Generalisierung den übrigen Abdruck aktiv abbaut, bleibt offen (Codex, EXP-029).

## Befehle

    python lab/tools/guarded_run.py -- python lab/experiments/EXP-030-imprint-residue/analyze.py
