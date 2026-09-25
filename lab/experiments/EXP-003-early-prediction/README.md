# EXP-003: Frühvorhersage des Generalisierungszeitpunkts

**Status:** Definition fixiert am 2026-09-25 um ~16:50 Berlin (Sitzung 2), **bevor** ein Merkmal
gegen die Zielgröße ausgewertet wurde. Vorher angesehen wurden nur die Zielgröße selbst, also die
Generalisierungsschritte je Lauf, und das Checkpoint-Format.

**Art:** reine Auswertung **gespeicherter** Studienläufe (`training/runs/*_arch25k`). Es gibt weder
Training noch Testsuite, und die Studie wird nicht verändert. Deshalb wurde die Auswertung auch
außerhalb des Run-Fensters ausgeführt (Auftrag §7: „vorhandene Ergebnisse sichten“). Diese Deutung
ist im JOURNAL vermerkt.

## Definition

| | |
|---|---|
| **Fragestellung** | Sagen Größen, die bis Schritt 2000 messbar sind, innerhalb einer festen Konfiguration voraus, welcher Seed früher generalisiert? |
| **Hypothese H-E3** | Mindestens ein Frühmerkmal korreliert über Seeds monoton mit dem Generalisierungsschritt, und zwar architekturübergreifend mit gleichem Vorzeichen. |
| **Zielgröße** | `transitions.primary.generalization.first_crossing_step` (test ≥ 0.95, Raster 25) aus `run.json` |
| **Merkmale (alle ≤ Schritt 2000, vorab fixiert)** | F1 `test_loss` bei 2000 · F2 `test_loss(2000) − test_loss(1000)` · F3 `log10 train_loss` bei 2000 · F4 L2-Norm aller Parameter bei 2000 · F5 Norm(2000)/Norm(500) · F6 Anteil der Top-8-Fourier-Frequenzen an der Leistung von `W_E[:p]` bei 2000 (Frequenzen 1..56, cos+sin, summiert über d_model) |
| **Explorationsgruppe** | Transformer, p = 113, frac 0.3, wd 1.0, ohne Grokfast, Seeds 0–9 (n = 10; gen 5625–10275) |
| **Bestätigungsgruppen** | MLP d_mlp 512, Seeds 0–9 (n = 10) · MLP d_mlp 572, Seeds 0–9 (n = 10). Andere Architektur; in der Exploration nicht angesehen |
| **Statistik** | Spearman ρ; p-Wert per Permutation (20 000 Permutationen, fester RNG-Seed 0). Exploration zweiseitig, Bestätigung einseitig in der Richtung der Exploration |
| **Auswahlregel** | Das Merkmal mit dem größten \|ρ\| in der Exploration wird zum Kandidaten. Liegt \|ρ\| < 0.5, gibt es keinen Kandidaten. Berichtet wird trotzdem alles |
| **Entscheidungsregel** | *bestätigt*: Der Kandidat hat in **beiden** MLP-Gruppen dasselbe Vorzeichen mit einseitigem p < 0.05 · *teilweise*: nur in einer Gruppe · *nicht bestätigt*: in keiner Gruppe |
| **Gegen H-E3 spricht** | kein Kandidat, oder *nicht bestätigt* |
| **Grenzen (vorab)** | n = 10 je Gruppe. Die Seeds sind über die Gruppen hinweg dieselben (mutmaßlich derselbe Split je Seed), die MLP-Gruppen sind also nicht unabhängig voneinander. Korrelation ist keine Ursache. Die 6 Merkmale wurden in der Exploration nicht auf Mehrfachtests korrigiert, das leistet der Bestätigungsschritt |
| **Budget** | Nur Checkpoints laden, < 2 min CPU. Kein Abbruchkriterium nötig |

## Reproduktion

```
python lab/experiments/EXP-003-early-prediction/early_predict.py
```
Ausgabe: `features.csv` (Merkmale je Lauf), `summary.json`, `SUMMARY.md`.
