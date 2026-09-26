---
id: EXP-014
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-012-init-gradient/README|EXP-012]]", "[[experiments/EXP-010-init-swap/README|EXP-010]]", "[[experiments/EXP-009-freq-commitment/SUMMARY|EXP-009]]"]
---
# EXP-014: Wählt der Trainingssplit oder die Init die Frequenzen?

**Status:** vorbereitet, **nicht ausgeführt**. Definition fixiert 2026-09-26 ~03:15 Berlin (Sitzung 4), bevor ein
gekreuzter Lauf existierte. Code: Option `--split-seed` in `freq_ban.py` (Unit-Test
`test_split_seed_leaves_init_rng_untouched` im Fenster ok, 10/10). Auswertung `analyze.py` (ungetestet).

## Warum

Bei Init ist die Ausgabe fast gleichverteilt, der Gradient an `W_E[a]` ist daher ungefähr
Σ_b M(a, b) · Jᵀ (W_U[:, a+b] − Mittel), wobei M die Maske der Trainingspaare ist. Wären **alle** Paare im
Training, wäre diese Summe für jedes a gleich und enthielte keine Frequenzstruktur. Die Frequenzvorliebe des
ersten Gradienten ([[experiments/EXP-012-init-gradient/README|EXP-012]]: bester Init-Prädiktor) entsteht also
aus dem Zusammenspiel von **zufälligem 30-%-Split** und zufälligen Gewichten. Welcher Faktor dominiert, ist offen.
Beide lassen sich trennen: Der Split hat einen eigenen `torch.Generator`, die Init nutzt den globalen RNG.

| | |
|---|---|
| **Fragestellung** | Folgt die finale Frequenzmenge eher der Init oder eher dem Split? |
| **Design** | Für i = 10..19: gekreuzter Lauf mit Init i und Split i+1 (19 → 10), sonst wie EXP-003d (`baseline`, `--stop-after-gen 25`). Vergleich mit den EXP-003d-Baselines B_i (gleiche Init) und B_{i+1} (gleicher Split) |
| **Maße pro i** | ov_init = \|K_cross ∩ K(B_i)\|, ov_split = \|K_cross ∩ K(B_{i+1})\|, D = ov_split − ov_init. Zufallsüberlappung zweier 5er-Mengen aus 56: 25/56 ≈ 0.45 |
| **Primär** | D̄, **zweiseitiger** Vorzeichen-Permutationstest über die gültigen i (keine Richtung vorab bevorzugt) |
| **Entscheidung** | *Split dominiert*: D̄ > 0, p < 0.05 · *Init dominiert*: D̄ < 0, p < 0.05 · sonst *kein dominanter Faktor* · < 8 gültige: *nicht auswertbar* |
| **Sekundär (berichtet)** | ov_init und ov_split je gegen 0.45 (MC-Null mit zufälligen 5er-Mengen). Beide nahe 0.45 hieße: echte Wechselwirkung oder Chaos |
| **Gültigkeit** | alle drei Läufe `completed` und gekreuzt (gen ≠ None); `split_hash` von cross = von B_{i+1}; Init-Spektrum bei Schritt 0 von cross = von B_i (rtol 1e-6) |
| **Budget** | 10 Läufe à ≈ 8–20 min, nach den EXP-003d-Baselines |
| **Grenzen** | nur Transformer; ein Split-Partner pro Init; ov misst Mengenüberlappung, nicht Rangstruktur |

## Befehl

```
python lab/tools/guarded_run.py --min-minutes 33 -- python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed I --split-seed J --condition baseline --stop-after-gen 25 --out-root lab/experiments/EXP-014-split-vs-init/raw
python lab/experiments/EXP-014-split-vs-init/analyze.py
```

## Nachtrag a (2026-09-26 ~03:30 Berlin, nach Codex-Review, **vor jedem Kreuzlauf**)

Codex: Das zyklische Design nutzt jede Baseline zweimal (B_{i+1} geht positiv in D_i und negativ in D_{i+1} ein); der
zeilenweise Vorzeichentest ist dann nicht gültig. **Übernommen.** Neues Design mit unabhängigen Einheiten:
5 disjunkte Paare (10,11), (12,13), (14,15), (16,17), (18,19), jeweils **beide** Richtungen (Init a × Split b und
Init b × Split a), zusammen 10 Kreuzläufe. Pro Paar D_u = Σ ov_split − Σ ov_init über beide Richtungen.
Test **einseitig** (Split > Init), Richtung begründet durch die Gradient-Vorschau (ρ 0.34 vs. −0.01) und die Befunde
von [[experiments/EXP-015-mask-spectrum/README|EXP-015]], festgelegt vor jedem Kreuzlauf. Mit 5 Einheiten ist das
kleinste p = 1/32; *Split dominiert* verlangt also D_u > 0 in (fast) allen Paaren. Weniger als 5 gültige Einheiten:
*nicht auswertbar*. Die Zufallsvergleiche ov gegen 0.45 bleiben sekundär.
Befehl je Richtung: `freq_ban.py --seed a --split-seed b --condition baseline --stop-after-gen 25 --out-root lab/experiments/EXP-014-split-vs-init/raw`.
