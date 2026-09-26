---
id: EXP-023
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-019-coherent-mask/README|EXP-019]]", "[[experiments/EXP-015-mask-spectrum/README|EXP-015]]", "[[BEFUND-split-mechanismus]]"]
---
# EXP-023: Getrennte Wertepfade je Position: folgt die Frequenzwahl dann M0 statt M0c?

**Status:** vorbereitet, **nicht ausgeführt**. Definition fixiert 2026-09-26 07:00 Berlin (Sitzung 5), bevor ein Lauf
existierte. Code: `split_value.py` (Variante im Labor, Studiencode unverändert), Option `--split-value` in `freq_ban.py`,
`analyze.py`, `queue.sh`. Test `test_split_value_variant` im Fenster ok (15/15, 07:00): Die übrigen Gewichte sind
bitgleich zur Baseline-Init; mit W_V1 := W_V rechnet die Variante exakt wie das Original. **Kein echter Trainingslauf
mit `--split-value` bisher:** vorher Smoke mit `--steps 50`.

## Idee

Sitzung 5 (post hoc, [[BEFUND-split-mechanismus]]): Im ersten W_E-Gradienten interferieren linke und rechte
Eingabeposition frequenzweise nach dem Kreuzterm der Maske; deshalb beschreibt M0c den Gradienten im Transformer besser als
M0. In der MLP (getrennte Pfade) ist es umgekehrt, und ein In-silico-Eingriff (eigene Wertematrix für Position 1)
beseitigt die Interferenz im ersten Gradienten. Offen ist, ob das auch die **finale** Frequenzwahl kausal bestimmt.
Eingriff hier: Position 1 bekommt im ganzen Training eine eigene Wertematrix W_V1 (aus eigenem Generator, gleiche
Verteilung wie W_V); alle anderen Gewichte, der Split und die Init sind wie in der EXP-003d-Baseline B_i.

| | |
|---|---|
| **Fragestellung** | Verliert M0c seinen Vorhersagevorteil gegenüber M0, wenn die beiden Positionen getrennte Wertepfade haben? |
| **Läufe** | Seeds 10–19, `--split-value`, sonst exakt wie EXP-003d (`baseline`, `--stop-after-gen 25`, Obergrenze 15000) |
| **K** | `final_top_m_freqs` (W_E-Top-5 bei gen + 25), wie in den Baselines |
| **Primärgröße** | Δd_i = [r̄_sv(M0c) − r̄_sv(M0)] − [r̄_B(M0c) − r̄_B(M0)] (r̄ wie EXP-015; kleiner = besser) |
| **H23** | Δd̄ > 0 (im Eingriff wird M0c relativ zu M0 schlechter) |
| **Test** | Vorzeichen-Permutationstest über die gültigen Seeds, einseitig |
| **Entscheidung** | *bestätigt*: Δd̄ > 0, p < 0.05 · *richtungsgleich, n. s.*: Δd̄ > 0, p ≥ 0.05 · *widerspricht*: Δd̄ ≤ 0 · < 8 gültige: *nicht auswertbar* |
| **Gültig** | sv-Lauf und B_i `completed` und gekreuzt; gleicher `split_hash`; W_E-Spektrum bei Schritt 0 gleich (rtol 1e-6); `split_value` = true |
| **Sekundär** | r̄_sv(M0) gegen r̄_sv(M0c) direkt; Überlappung K_sv mit K_B; gen_sv gegen gen_B; Kreuzterm-Korrelation im ersten Gradienten des sv-Modells (Erwartung ≈ 0) |
| **Was dagegen spräche** | Δd̄ ≤ 0: Die Interferenz im ersten Gradienten bestimmt die finale Wahl nicht (oder andere Pfade übernehmen) |
| **Grenzen** | **Geringe Teststärke:** Der M0c-Vorteil in den Baselines ist klein (Seeds 10–17: r̄ 0.222 gegen 0.277); r̄ ist verrauscht. Die Variante hat 16384 Parameter mehr. Nur Transformer, p = 113 |
| **Budget** | 10 Läufe à ≈ 8–25 min (wie EXP-003d), ≈ 2–3 h; nach den EXP-003d-Baselines 18/19 |

## Befehle

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed 10 --condition baseline --steps 50 --split-value --out-root lab/experiments/EXP-023-split-value/raw_smoke
sh lab/experiments/EXP-023-split-value/queue.sh
python lab/tools/guarded_run.py -- python lab/experiments/EXP-023-split-value/analyze.py
```
