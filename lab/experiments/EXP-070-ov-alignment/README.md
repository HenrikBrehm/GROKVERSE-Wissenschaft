---
id: EXP-070
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/negativ]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-069-attention-part/README|EXP-069]]", "[[confirm/N29b_REGISTRATION|N29b]]", "[[NOVEL_DIRECTIONS]]", "[[BACKLOG]]", "[[JOURNAL]]"]
---
# EXP-070: Richtet sich der Wertepfad der Attention zwischen Schritt 25 und 50 auf die Frequenzen des ersten Splits aus? (EXPLORATION)

Zurück zu [[LAB]] · [[BACKLOG]] „N32“ (Mechanismus-Messung) · [[NOVEL_DIRECTIONS]] N32 · Vorgänger [[experiments/EXP-069-attention-part/README|EXP-069]].
Festgelegt 2026-09-27 (Sitzung 23), **vor jedem EXP-070-Lauf**. **Exploration**, bekannte Seeds 400–409, kein Urteil.

- **Frage:** Wird der OV-Kreis der Attention (W_V·W_O je Kopf) zwischen t = 25 und t = 50 auf die Zielfrequenzen des ersten Splits A ausgerichtet, also genau im Fenster, in dem der Ausschluss entsteht (N29)?
- **Läufe:** reine A-Läufe (EXP-056-Splits, ω = 0) mit `--steps t --save-model`, t ∈ {10, 25, 50, 100}, je Seed 400–409; 40 kurze Läufe, GPU. Dazu die Init (gleiche Init für alle t, aus dem Seed neu gebaut).
- **Maß je Modell:** X = W_E[:113]. Für eine Frequenzmenge S: Verstärkung g_S = Σ_h ‖(P_S X) · W_V[h] W_O[h]‖² / ‖P_S X‖². Kennzahl **L = log(g_A / g_B)**
  (A = Ziele von Split A, B = Ziele von Split B, nie trainiert, dient als gleich große Kontrolle). Zum Vergleich die Energieverhältnis-Kennzahl **E = log(‖P_A X‖² / ‖P_B X‖²)** (reine W_E-Seite).
- **Erwartung unter N32-Wertepfad (V):** L steigt zwischen t = 25 und 50 deutlich (Median-Anstieg größer als zwischen 10 und 25). **Dagegen spräche:** L bleibt ≈ 0 oder steigt nur gleichmäßig mit E mit.
- **Grenzen:** Exploration; OV ohne Attention-Muster und ohne LayerNorm-Effekte (dieses Modell hat keine LayerNorm); nur A-Läufe (kein Wechsel); Verstärkung ist eine lineare Größe.
- **Budget:** 40 Läufe à ≤ 100 Schritte, Sekunden je Lauf.

```
python lab/tools/parallel_queue.py lab/experiments/EXP-070-ov-alignment/jobs.txt --workers 6
python lab/tools/guarded_run.py -- python lab/experiments/EXP-070-ov-alignment/analyze.py
```

## Ergebnis (Sitzung 23, Läufe 11:42–11:44, Auswertung 11:44 Berlin, gemessen; `summary.json`): Exploration

40/40 kurze Läufe ok; die aus dem Seed neu gebaute Init stimmt in allen 40 Läufen mit dem vom Trainer gespeicherten W_E bei Schritt 0 überein.

| t | 0 | 10 | 25 | 50 | 100 |
|---|---|---|---|---|---|
| Median L = log(g_A / g_B) (OV-Verstärkung) | 0.04 | 0.08 | 0.30 | 0.47 | 0.77 |
| Median E = log(Energie A / B in W_E) | −0.02 | −0.01 | 0.10 | 0.32 | 0.82 |

Anstieg von L: 10 → 25 um 0.22, 25 → 50 um 0.18; stärker zwischen 25 und 50 nur in 2/10 Seeds.
- **Lesart:** Die vorab genannte Erwartung (ein Sprung der OV-Ausrichtung genau im Fenster 25–50) trifft **nicht** zu; L steigt gleichmäßig. Die zeitliche Form des Ausschlusses (N29) lässt sich damit
  nicht einfach durch ein plötzliches Ausrichten des Wertepfads erklären. *Beschreibend auffällig:* Die OV-Ausrichtung läuft der W_E-Energie voraus (t = 25: L 0.30 gegen E 0.10).
- **Grenzen:** eine lineare Größe ohne Attention-Muster; reine A-Läufe; die Wirkung eines Resets (EXP-069) und diese Ausrichtung müssen nicht dasselbe messen.
