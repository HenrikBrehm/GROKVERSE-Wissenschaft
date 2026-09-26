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

## Nachtrag a (2026-09-26 09:15 Berlin, nach Codex-Review, vor jedem EXP-026-Lauf): Umbau zum Umschaltversuch

Codex-Review (`codex_review_2026-09-26.txt`, „needs-attention“, 4 × high, 2 × medium), selbst geprüft, **alle
übernommen**: (1) Getrennt trainierte α-Stufen sind keine Uhr, denn α verändert die gesamte Optimierung; ein
Umschlag in α zeigte eine Grenze zwischen Trainingsdynamiken, nicht den Zeitpunkt der Wahl. (2) Das h = 2-Spektrum
gewichtet ein gemischtes Netz falsch. (3) Das Spearman-Kriterium hätte ohne echten Vorzeichenwechsel „bestätigt“
geliefert. (4) Der Median von r über alle Neuronen hängt an irrelevanten Neuronen. (5) α* war genauer angegeben, als das
Raster erlaubt, und α = 0 bekam eine erfundene Untergrenze. (6) Das Raster wurde nicht vollständig verlangt.
**Die Tabelle oben ist damit ersetzt.** Gültig ist:

| Punkt | Festlegung |
|---|---|
| **Frage** | Ab welcher Umschaltzeit t_s bleibt die Wahl der Ziele F erhalten, wenn ein Netz bis t_s mit σ_3 = 3x + x² (Nutzen am Start → F) und danach mit reinem x² (Nutzen → H) trainiert? Das ist die kausale Festlegungszeit auf **einer** Trajektorie (Aufbau wie EXP-020, hier für die Aktivierung statt die Daten) |
| **Arme** | t_s ∈ {0, 50, 250, 1000, 2500, nie}; t_s = 0 ist das reine x²-Netz, „nie“ ist σ_3 durchgehend. `--alpha 3 --switch-step t_s --alpha-after 0`; AdamW-Zustand bleibt beim Umschalten erhalten |
| **Einheiten** | EXP-016-Splits Seeds 10–14, Arm F, Init-Seed = Split-Seed → 30 Läufe; nur das vollständige 6 × 5-Raster wird ausgewertet, sonst *nicht auswertbar*. Unvollständige Läufe beenden die Warteschlange (Exit 4) |
| **Messgröße** | d = ov(Top-5, F) − ov(Top-5, H) des h = 2-Spektrums bei Schritt 5000 (für alle t_s < 5000 ist das Endnetz rein quadratisch, dort ist h = 2 richtig). Für „nie“ zusätzlich d_lin (h = 1, linearer Pfad) |
| **Anker (Vorzeichenwechsel, Pflicht)** | mittleres d(t_s = 0) < 0 **und** mittleres d(nie) > 0 **und** mittleres d_lin(nie) > 0. Sonst: *Uhr nicht ablesbar* |
| **Primär** | Spearman(Rang t_s, d) > 0 über 30 Läufe, Permutation von t_s innerhalb jedes Splits (10 000×), p < 0.05 → *Uhr ablesbar*; mit Ankern, aber p ≥ 0.05 → *Anker ok, Trend n. s.* |
| **Festlegungsintervall** | nur bei *Uhr ablesbar*: t* ∈ (t_lo, t_hi], t_hi = kleinstes t_s, ab dem alle mittleren d > 0 sind. Kein Punktschätzer. **A (früh):** t_hi ≤ 250 (vor dem sichtbaren Generalisieren, ~1300–1500 im x²-Netz). **B (spät):** t_hi ≥ 2500 oder nie. Sonst Zwischenlage (t_hi = 1000) |
| **Erwartung (AGF: Wahl am Start)** | A |
| **Was dagegen spräche** | B: Die Endaktivierung bestimmt die Wahl, der Nutzen am Start ist nicht bindend. Keine Anker: Der lineare Anteil lenkt trainierte Netze nicht auf F (dann trägt die Paritätsrechnung nicht) |
| **Nebenmessungen (nur berichtet)** | Generalisierungszeit je Arm (Optimierungsfortschritt), Amplitude r(t) (Median, ausgabegewichtet), Test-Genauigkeit |
| **Grenzen** | Das Umschalten ist selbst ein Eingriff (Funktionssprung, AdamW-Momente passen danach nicht). Später Wechsel in F nach Umschalten wäre ebenfalls möglich; das Intervall ist nur so fein wie das Raster. Die α-Stufen-Idee (Umschlagpunkt als Amplitudenmaß) ist verworfen, nicht getestet |
| **Budget** | 30 × ~83 s ≈ 42 min, Reihenfolge der Warteschlange: Anker zuerst (0, nie), dann 250, 1000, 50, 2500 |
| **Auswerter** | an synthetischen Fällen geprüft (früh → A (50, 250], spät → B, alles H oder alles F → nicht ablesbar, fehlende Zelle → nicht auswertbar) |

## Nachtrag b (2026-09-26 09:18 Berlin, vor jedem EXP-026-Lauf): kontinuierliche Messgröße statt Top-5

Anlass: EXP-024 Arm Q ist ausgewertet (siehe dort). Post hoc zeigte sich, dass das gewichtete Spektrum dieser Zwei-Hot-Netze
**fast flach** ist (Anteil je Frequenz ≈ 5/56; am Ende H 0.102, F 0.084 von 1). Die Top-5-Überlappung hängt dann an kleinen
Unterschieden und ist verrauscht. **Primäre Messgröße ab jetzt:** ds = Anteil(F) − Anteil(H) am normierten h = 2-Spektrum
bei Schritt 5000; Anker und Spearman-Test unverändert, nur mit ds statt d (für „nie“ zusätzlich ds_lin > 0). Die
Top-5-Differenz d wird sekundär berichtet. Auswerter erneut an den synthetischen Fällen geprüft (`test_analyze.py`, über
den Wächter, 5/5).
**Grenze, neu:** Der Arm t_s = 0 ist das reine x²-Netz und damit praktisch identisch mit EXP-024 Arm Q auf Seeds 10–14 F,
dessen Ergebnis (gemittelt über 19 Einheiten) ich bereits kenne. Der Anker d(0) < 0 ist daher nicht unabhängig von
EXP-024; der eigentliche Test ist der Verlauf über t_s und der Anker „nie“.

## Befehle

    sh lab/experiments/EXP-026-parity-crossover/queue.sh           (jeder Lauf über guarded_run.py)
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-026-parity-crossover/analyze.py
