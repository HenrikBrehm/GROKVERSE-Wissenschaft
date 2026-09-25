# EXP-003b: Bestätigung von F6 an unberührten Läufen

**Status:** Definition fixiert am 2026-09-25 um ~17:05 Berlin, **bevor** die Zielgröße oder ein
Merkmal dieser Läufe angesehen wurde. Angesehen wurden vorher nur Dateinamen, die
Checkpoint-Schlüssel und das Feld `embedding_object` eines Laufs.

**Anlass:** EXP-003 bestimmte F6 (Top-8-Fourier-Konzentration des Embeddings bei Schritt 2000)
als Kandidaten (ρ = −0.71 im Transformer). Die Bestätigung fiel *teilweise* aus: MLP-512 mit
ρ = −0.65 und p = 0.024 (einseitig), MLP-572 mit ρ = −0.41 und p = 0.11.

| | |
|---|---|
| **Daten** | `training/external/twohot10/runs/m2h_*_seed{0..9}_arch25k`: 10 Läufe der Two-hot-MLP, extern gerechnet. Diese Architektur und diese Läufe kamen in EXP-003 nicht vor |
| **Merkmal** | F6 fest, unverändert bis auf das Objekt: Das Modell hat kein `W_E`, deshalb wird `W_in[:p]` verwendet. Das ist das Embedding-Objekt, das die Studie für diese Architektur selbst festlegt (`embedding_object = "W_in_a_half"` in `run.json`) |
| **Zielgröße** | wie in EXP-003 (`transitions.primary.generalization.first_crossing_step`) |
| **Test** | Spearman ρ, einseitig (ρ < 0), 20 000 Permutationen, RNG-Seed 0 |
| **Entscheidung** | *bestätigt*: ρ < 0 und p < 0.05 · *richtungsgleich, nicht signifikant*: ρ < 0 und p ≥ 0.05 · *widerspricht*: ρ ≥ 0 |
| **Grenzen** | Die Seeds 0–2 teilen den Split mit den lokalen m2h-Läufen. Zweck ist hier nur die Bestätigung, eine Plattform-Reproduktion ist nicht das Ziel. n = 10. Andere Merkmale (F1–F5) werden informativ mitberichtet, aber nicht bewertet |

Reproduktion: `python lab/experiments/EXP-003-early-prediction/confirm_b.py`
