---
id: EXP-012
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-009-freq-commitment/SUMMARY|EXP-009]]", "[[experiments/EXP-010-init-swap/README|EXP-010]]", "[[experiments/EXP-011-init-magswap/README|EXP-011]]"]
---
# EXP-012: Wer wählt die Frequenzen? Init-Gradient statt Init-Spektrum

**Status:** vorbereitet. Definition fixiert am 2026-09-26 um ~03:08 Berlin (Sitzung 4), **bevor**
irgendein Prädiktor berechnet wurde. Kriterienänderungen gehören in EXP-012b.

## Auslöser (Beobachtung, Sitzung 4)

EXP-003d-Baseline Seed 10: Die finalen Top-5 {7, 14, 19, 35, 39} hatten im Init-Spektrum von `W_E` die
Ränge 26, 6, 15, 43, 21 (0 = stärkste). Bei Schritt **250** sind 4 von 5 schon die Top-4
({7, 14, 19, 39, 41}), und das bleibt bis zum Grokking bei Schritt 3925 so. Die Wahl fällt also in den
ersten ~250 Schritten, und zwar überwiegend **nicht** nach der Init-Leistung von `W_E`
(EXP-009: r̄ = 0.386, deutlich, aber schwach). Vermutung: Es entscheidet, welche Frequenzen der
**Gradient** am Anfang bevorzugt. Der hängt von den übrigen zufälligen Gewichten (v. a. `W_U`, Attention,
MLP) und vom Trainingssplit ab.

| | |
|---|---|
| **Fragestellung** | Sagt ein bei Schritt 0 berechenbares Frequenzmaß die finale Frequenzmenge besser voraus als die Init-Leistung von `W_E`? |
| **Prädiktoren (je Leistung pro Frequenz k = 1..56, berechnet bei Init)** | `E0`: Leistung von `W_E[:p]` (EXP-009, Referenz) · `U0`: Leistung von `W_U[:, :p]ᵀ` (Unembedding über Ausgabetoken) · `G0`: Leistung des Full-Batch-Gradienten ∂L/∂`W_E[:p]` bei Schritt 0 (gleiche Verlustfunktion wie im Training) · `A1`: Leistung von sign(`G0`) (≈ erster Adam-Schritt ohne Weight Decay) |
| **Referenz, kein Prädiktor** | `E250`: Leistung von `W_E` bei Schritt 250 (aus `spectra.npy`, nur für Seeds 10–19) |
| **Zielmenge K** | Seeds 0–9: Top-5 des gespeicherten 25k-Modells (`EXP-009/summary.json`, `k_final`) · Seeds 10–19: `final_top_m_freqs` der EXP-003d-Baselines (Crossing + 25) |
| **Maß** | r̄ = mittlerer normierter Rang von K in der Ordnung des Prädiktors (0 = stärkste, 1 = schwächste), wie EXP-009 |
| **Phase 1, Exploration** | Seeds 0–9 (gespeicherte Transformer-Läufe). Init per `set_seed` + `make_dataset` + `build_model` in derselben Reihenfolge wie das Training rekonstruiert; der Split-Hash muss mit dem gespeicherten Lauf übereinstimmen, sonst ist der Seed ungültig. Ausgewählt wird **der Prädiktor mit dem kleinsten r̄ unter U0, G0, A1** |
| **Phase 2, Bestätigung** | Seeds 10–19 (frisch). Nur der in Phase 1 gewählte Prädiktor X. **H12:** r̄(X) < r̄(E0), einseitiger exakter Vorzeichentest über die Seed-Differenzen r̄_E0 − r̄_X (2¹⁰). Zusätzlich r̄(X) gegen die Monte-Carlo-Null 0.5 (wie EXP-009) |
| **Entscheidung** | *bestätigt*: p < 0.05 im Vorzeichentest **und** r̄(X) < 0.5 mit p < 0.05 · *richtungsgleich, n. s.*: r̄(X) < r̄(E0), p ≥ 0.05 · *widerspricht*: r̄(X) ≥ r̄(E0) · < 8 gültige Seeds: *nicht auswertbar* |
| **Was dagegen spräche** | Kein Init-Prädiktor schlägt E0; dann entsteht die Wahl erst durch die Dynamik der ersten Schritte (nicht aus einer einzelnen Init-Größe ablesbar) |
| **Budget** | reine Init-Rekonstruktion + ein Forward/Backward pro Seed, Sekunden. Über `guarded_run.py` im Fenster |
| **Hinweis zur Unabhängigkeit** | Für Seed 10 waren K_end und die Init-Ränge von E0 vor der Festlegung bekannt, kein anderer Prädiktor. Seeds 11–19: noch nicht gelaufen |
| **Grenzen** | nur Transformer; K bei Seeds 0–9 und 10–19 zu verschiedenen Zeitpunkten gemessen (25k vs. Crossing + 25) |

## Befehl

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-012-init-gradient/predict.py --phase 1
python lab/tools/guarded_run.py -- python lab/experiments/EXP-012-init-gradient/predict.py --phase 2 --predictor X
```
