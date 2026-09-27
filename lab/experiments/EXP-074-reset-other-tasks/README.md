---
id: EXP-074
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-044-generalize-lockin/README|EXP-044]]", "[[experiments/EXP-067-exclusion-part/README|EXP-067]]", "[[experiments/EXP-069-attention-part/README|EXP-069]]", "[[confirm/N29b_REGISTRATION|N29b]]", "[[confirm/N29c_REGISTRATION|N29c]]", "[[JOURNAL]]"]
---
# EXP-074: Gilt das Reset-Muster (Attention/Wertepfad, nicht MLP/Muster) auch bei add 97 und mul 113? (PILOT)

Zurück zu [[LAB]] · [[FINDINGS]] „Grenzen“ Punkt 2 (Persistenz- und Reset-Befunde nur bei add 113) · Regel 15c (Verallgemeinerung zuerst).
Festgelegt 2026-09-27, Sitzung 24, **vor jedem EXP-074-Lauf** (außerhalb des Fensters; Läufe ab 00:00). **Pilot**, bekannte Seeds 80–89 (EXP-044), kein Urteil.

- **Frage:** Senkt ein Reset der Attention (bzw. des Wertepfads W_V, W_O) beim Wechsel nach 50 Schritten die Persistenz der ersten Wahl auch bei add 97 und mul 113 stark, ein Reset des MLP und des
  Musters (W_Q, W_K) dagegen kaum, wie bei add 113 (K4d, K4e)?
- **Protokoll:** EXP-044 (Splits F/G mit ≈ 38 % geteilten Paaren, gemeinsame Testmenge, nur F→G, Wechsel bei t = 50, danach 2000 Schritte auf G), GPU, 1 Thread, `--save-model`.
  Arme: normal, rsattn, rsvo, rsqk, rsmlp (`--reset-at-switch`, Gewichte auf die Init + AdamW-Zustand gelöscht). 2 Aufgaben × 10 Seeds × 5 Arme = 100 Läufe. Reine F/G-Läufe aus EXP-044.
- **Maß:** π wie EXP-044 (`pi_persistence.py`), je Seed Δπ_X = π_normal − π_rsX.
- **Referenz add 113** (post hoc aus gespeicherten Läufen, `reference_add113.py`, Sitzung 24, bekannte Seeds 400–409, EXP-056-Protokoll ω = 0, beide Richtungen): Median π normal 1.04;
  Δπ attn 0.84 (10/10 > 0.3), vo 0.57 (9/10), qk 0.13 (2/10), mlp 0.15 (1/10), unembed −0.04.
- **Lesart vorab (je Aufgabe):** *Reset-Muster verallgemeinert*, wenn Median Δπ_attn ≥ 0.4 mit ≥ 8/10 über 0.3, Median Δπ_vo ≥ 0.3, Median Δπ_mlp < 0.3 und Median Δπ_qk < Median Δπ_vo.
  *Nicht verallgemeinert*, wenn Median Δπ_attn < 0.2. Sonst *unklar*.
- **Gültigkeit:** je Seed alle 7 Läufe über den gemeinsamen Lader ok, Reset vom Trainer geprüft, L(F) − L(G) ≥ 1, π_normal ≥ 0.5 (sonst gibt es nichts zu senken); ≥ 8 gültige Seeds je Aufgabe.
- **Bereits gesehene Daten:** π aus EXP-044 an denselben Seeds (add 97 π(50) 0.86, mul 113 0.72); Reset-Ergebnisse bei add 113 (EXP-067/069, N29b/c) und die Referenz oben. Davon beeinflusst: Wahl der Arme
  und die Schwellen (Hälfte bzw. gut die Hälfte der add-113-Effekte).
- **Grenzen:** anderes Überlappungsprotokoll als add 113 (38 % geteilte Paare statt 0 %, nur eine Richtung); π ist ein Energiemaß; die Resets zeigen Empfindlichkeit, keinen Speicherort (wie K4d/e).
- **Budget:** 100 Läufe à 2050 Schritte, GPU 8 parallel, ≈ 10–12 min.

```
python lab/tools/parallel_queue.py lab/experiments/EXP-074-reset-other-tasks/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-074-reset-other-tasks/analyze.py
```
