---
id: EXP-045
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet]
verwandt: ["[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/EXP-043-generalize-steering/README|EXP-043]]", "[[experiments/EXP-024-quadratic-agf-mask/README|EXP-024]]", "[[BEFUND-split-mechanismus]]", "[[FINDINGS]]"]
---
# EXP-045: Steuerung über die Daten in einer anderen Architektur (MLP mit gemeinsamem Embedding)

**Status:** vorbereitet, **nicht ausgeführt**, Code ungetestet. Definition fixiert 2026-09-26 19:26 Berlin (Sitzung 11), vor jedem Lauf.
Ziel in [[FINDINGS]]: K2 über die Architektur verallgemeinern (Regel 15c). GPU, nach bestandenem GPU-001.

## Idee

K2 ([[experiments/EXP-016-engineered-split/README|EXP-016]]) ist nur am 1-Schicht-Transformer gezeigt. Das MLP der Studie
(`arch = mlp`: gemeinsames Embedding W_E, beide Operanden konkateniert, eine ReLU-Schicht, 512 Neuronen) hat keinen
Attention-Wertepfad. Nach [[BEFUND-split-mechanismus]] (post hoc) beschreibt dort M0 den ersten Gradienten besser als M0c, im
Transformer umgekehrt; EXP-015 fand post hoc, dass M0 die finalen Frequenzen auch in allen MLPs mit vorhersagt. Frage: Ist die
Steuerung kausal auch im MLP da? Das Zwei-Hot-MLP aus [[experiments/EXP-024-quadratic-agf-mask/README|EXP-024]] (ReLU folgte
dem Split, blieb aber memorierend) ist eine andere Architektur ohne gemeinsames Embedding.

| | |
|---|---|
| **Fragestellung** | Gibt ein konstruierter Split auch dem MLP mit gemeinsamem Embedding die gelernten Frequenzen vor? |
| **H45** | Δ̄ > 0 |
| **Bedingungen** | Seeds 90–99, Arme F/G (EXP-043-Konstruktion, add 113, ε = 2, frische Zielmengen, getrennte Ströme), Preset `arch25k` mit `arch = mlp`, **10 000 Schritte** fest (`--stop-after-gen 100000`), GPU |
| **K (primär)** | Top-5 der W_E-Leistung (k = 1..56) bei Schritt **10 000** (das Studien-MLP generalisiert im Median bei 9 250 Schritten; der Endzustand soll die gelernte Lösung sein, nicht nur der Memorisierungsabdruck) |
| **Primär, Test, Urteil** | Δ_i wie EXP-016; einseitiger Vorzeichen-Permutationstest über 10 Seeds; *steuerbar* (Δ̄ > 0, p < 0.05) · *richtungsgleich, n. s.* · *widerspricht* (Δ̄ ≤ 0) · < 8 gültig: *nicht auswertbar* |
| **Gültig** | beide Arme `completed` mit ≥ 10 000 Schritten, `arch = mlp`, `device = cuda`, Hash = Datei |
| **Sekundär** | Δ bei Schritt 2000 (Vergleich mit dem EXP-016-Zeitpunkt); gen und Test-Acc (Komplement, beschreibend); Schnappschüsse 250/5000 |
| **Erwartung** | *steuerbar*, eventuell schwächer als im Transformer (Δ̄ 4–7) |
| **Was dagegen spräche** | Δ̄ ≤ 0 oder n. s.: Die Steuerung wäre an den Transformer gebunden (z. B. an den geteilten Wertepfad) |
| **Grenzen** | Ein MLP-Typ, eine Aufgabe; das MLP generalisiert eventuell bis 10 000 nicht, dann beschreibt K einen memorierenden Zustand (wird mit gen berichtet); 10 Seeds |
| **Budget** | 20 Läufe × 10 000 Schritte auf der GPU (MLP ist billig), J parallel |

## Befehle

```
python lab/experiments/EXP-043-generalize-steering/make_split.py --seed I --task add --p 113 --arm F|G --out lab/experiments/EXP-045-mlp-steering/splits   # erzeugt
sh lab/experiments/EXP-045-mlp-steering/queue.sh J
python lab/tools/guarded_run.py -- python lab/experiments/EXP-045-mlp-steering/analyze.py
```

Offline-Prüfung der Splits: Zielmenge = M0-Top-5 in 20/20, Anteil 0.181–0.202.
