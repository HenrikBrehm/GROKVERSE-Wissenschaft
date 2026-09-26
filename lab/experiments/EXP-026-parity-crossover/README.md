---
id: EXP-026
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-026: Umschlagpunkt ungerade/gerade: Bei welcher Merkmalsamplitude fällt die Frequenzwahl?

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N11, N12) · Vorgänger
[[experiments/EXP-024-quadratic-agf-mask/README|EXP-024]] · Splits aus [[experiments/EXP-016-engineered-split/README|EXP-016]].

## Anlass (Sitzung 7, 09:03 Berlin, Rechnung ohne Training)

`EXP-024/utility_parity.py` (exakter AGF-Nutzen, 19 EXP-016-Einheiten, 8 × 8 Phasen, Merkmale mit Amplitude 1):

| Aktivierung | ov(Top-5, F) | ov(Top-5, H) |
|---|---|---|
| x (ungerader Anteil) | 5.00 | 0.21 |
| \|x\| (gerader Anteil) | 0.21 | 2.21 |
| ReLU = (x + \|x\|)/2 | 4.58 | 0.37 |
| σ_α = αx + x², α = 0 / 0.25 / 0.5 / 1 / 2 / 4 / 8 | 0.26 / 0.47 / 0.95 / 2.53 / 4.79 / 4.95 / 5.00 | 3.05 / 3.00 / 2.95 / 1.63 / 0.32 / 0.26 / 0.21 |

Der ungerade Anteil der Aktivierung greift die Maske bei k ab (→ Ziele F), der gerade bei 2k (→ halbe Ziele H).
Für σ_α ist nur α/r wichtig (σ_α(r z) = r²((α/r) z + z²)), r = Merkmalsamplitude. Der Nutzen schlägt bei
**α/r ≈ 1** um (zwischen 0.5 und 2). Die Amplitude r wächst im Training von r_init ≈ 0.0094 (Init-Skala 0.1) an.
**Idee (neu für das Labor, Neuheit vorläufig):** Der Umschlagpunkt α* eines trainierten Netzes ist ein *Messinstrument*:
Er zeigt, bei welcher Amplitude r ≈ α* und damit zu welchem Trainingszeitpunkt die Frequenzwahl tatsächlich fällt.
Fällt sie am Start (AGF-Bild), liegt α* nahe r_init; entscheidet die Endlösung, liegt α* nahe r_final.

## Versuch (vorab festgelegt 2026-09-26 09:05 Berlin, vor jedem EXP-026-Lauf; EXP-024-Ergebnisse noch nicht angesehen)

| Punkt | Festlegung |
|---|---|
| **Frage** | Wo liegt der Umschlagpunkt α* zwischen F- und H-Wahl für trainierte σ_α-Netze, und liegt er näher an der Anfangs- oder der Endamplitude? |
| **Modell** | `train_sigma.py` = `EXP-024/train_twohot.py` mit σ_α(x) = αx + x²; sonst identisch (512 Neuronen, ohne Biases, CE, Vollbatch, AdamW 1e-3, wd 1.0, Init-Skala 0.1, 5000 Schritte, Init-Seed = Split-Seed) |
| **Einheiten** | EXP-016-Splits Seeds 10–14, Arm F (5 unabhängige Splits) |
| **Stufen** | α ∈ {0, 0.003, 0.03, 0.3, 3} (α = 0 ist das quadratische Netz, neu gelaufen wegen Amplitudenaufzeichnung) → 25 Läufe |
| **Messgröße** | d = ov(Top-5, F) − ov(Top-5, H) bei Schritt 5000 (gewichtetes Spektrum wie EXP-024, h = 2); Amplitude r(t) = Median über Neuronen von √mean_a(u² + v²) an den Schnappschüssen |
| **Primär (Umschlag existiert)** | Spearman ρ(Rang α, d) über 25 Läufe > 0, einseitiger Permutationstest (Permutation von α innerhalb jedes Splits, 10 000×), p < 0.05 → *Umschlag bestätigt*; sonst *kein Umschlag nachgewiesen* |
| **Sekundär (wann)** | α̂* = geometrisches Mittel aus größtem α mit mittlerem d < 0 und kleinstem α mit mittlerem d > 0 (Mittel über die 5 Splits; bei α = 0 als untere Stufe gilt 0.001). **A (Start):** α̂* ≤ 3 · r(0). **B (Ende):** α̂* ≥ r(5000)/3 (Median von r bei Schritt 5000 über die α-Stufen neben α̂*). Beide wahr: *nicht unterscheidbar*. Keiner: *Zwischenlage*, dann t* = erster Schnappschuss mit r(t) ≥ α̂* berichten |
| **Erwartung (Nutzen am Start)** | α = 0, 0.003 → H (α/r_init ≤ 0.3); α ≥ 0.03 → F; also A |
| **Was dagegen spräche** | Kein monotoner Umschlag (dann trägt die Parität die Wahl nicht) oder α̂* ≫ r_init (dann fällt die Wahl nicht am Start) |
| **Grenzen** | 5 Stufen im Faktor-10-Raster: α̂* nur auf ~1 Dekade genau. Die AGF-Rechnung nimmt Merkmale einer Frequenz und kleine Init an; AdamW normiert Schritte, was r(t) anders wachsen lässt als Gradientenfluss. Der Umschlag in α könnte auch aus anderen Effekten des linearen Terms entstehen (z. B. leichteres Anpassen) |
| **Budget** | 25 Läufe × ~83 s ≈ 35 min. Smoke: α = 3 und α = 0.003 am EXP-024-Smoke-Split Seed 9 (nur Laufbarkeit, Endlichkeit, Zeit). Bei Divergenz dürfen lr/Init **vor** der Hauptserie geändert werden (hier nachtragen) |

## Befehle

    sh lab/experiments/EXP-026-parity-crossover/queue.sh           (jeder Lauf über guarded_run.py)
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-026-parity-crossover/analyze.py
