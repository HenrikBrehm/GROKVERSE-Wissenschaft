---
id: EXP-074
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/unklar]
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

## Nachtrag Sitzung 32 (21:18 Berlin, gemessen, **vor jedem EXP-074-Lauf**): Zeitkosten der Resets (prospektiv)

Anlass: Post hoc an N29b/N29c (Sitzung 32, Zyklen 12–13) verzögerten Resets bei einem Wechsel nach 50 Schritten die Generalisierung in der Reihenfolge, in der sie die Persistenz senken: VO > QK in 19/20 Seeds, Attention > MLP in 15/20. Unmittelbarer Verlustschaden erklärte das nicht. Hier wird das **vor dem Lauf** an add 97 und mul 113 geprüft (Bezug: [[NOVEL_DIRECTIONS]] N43, [[confirm/R6_REGISTRATION_DRAFT|R6]]). Das Urteil der ursprünglichen Registrierung bleibt unverändert; dies ist eine zusätzliche, explorative Lesart.

- **Maß:** b = min(erste Testgenauigkeit ≥ 0.95, 2000) ab Schritt 0; Einheit = Seed × Aufgabe (20 Einheiten, eine Richtung F→G).
- **Q1 (primär für diesen Nachtrag):** log2 b(VO) − log2 b(QK) > 0, gepoolt, exakter einseitiger Vorzeichentest. **Q2:** Attention − MLP > 0. **Q3:** Attention − ohne Reset > 0.
- **Beschreibend:** jeder Arm gegen „nur G“ aus EXP-044 (gleiche Splits und Testmenge), also C(50) mit und ohne Reset je Aufgabe.
- **Gültigkeit:** alle fünf Arme und der G-Lauf je Einheit, gleiche Test- und Init-Prüfsumme; mindestens 16 Einheiten, sonst *nicht auswertbar*.
- **Was dagegen spräche:** Q1 nicht in der Mehrheit, dann ist die VO-Verzögerung aus N29c aufgaben- oder blockspezifisch.
- **Befehle (im Fenster, nach den EXP-074-Läufen):** `python lab/tools/guarded_run.py -- python lab/experiments/EXP-074-reset-other-tasks/time_cost.py --selftest`, dann ohne `--selftest`. Ungetestet (nur Syntaxprüfung).

## Ergebnis (Sitzung 36, 2026-09-28, Läufe 02:18–02:26, Auswertung 02:27 Berlin, gemessen)

100/100 Läufe ok (GPU, `--workers 8`). **Lesart nach Regel: *unklar* für beide Aufgaben.** add 97 (10 gültig): Median Δπ attn 0.32 (5/10 > 0.3), vo 0.25, qk −0.01, mlp 0.07.
mul 113 (9 gültig): attn 0.31 (5/9), vo 0.28, qk −0.00, mlp −0.00. Die Rangfolge wie bei add 113 (Attention/Wertepfad senken π, QK und MLP praktisch nicht) zeigt sich in beiden Aufgaben,
aber schwächer als die Schwelle für „verallgemeinert“ (attn ≥ 0.4, ≥ 8/10 über 0.3). `time_cost.py` wurde in dieser Sitzung nicht mehr gerechnet (offen). [[JOURNAL]] Sitzung 36.

## Ergebnis Nachtrag Zeitkosten (Sitzung 37, 2026-09-28 02:30 Berlin, gemessen)

20/20 Einheiten gültig. **Q1 gestützt:** log2 b(VO) − log2 b(QK) Mittel +0.99, 18/18 positiv (2 Gleichstände), p = 3.8e-6: Ein VO-Reset beim Wechsel nach 50 Schritten verzögert das Grokking bei add 97 und mul 113 deutlich stärker als ein QK-Reset (wie N29c). **Q2 nicht gestützt:** Attention − MLP Mittel -0.18, 4/13 positiv, p = 0.95 (Richtung eher umgekehrt als in N29b). **Q3 nicht gestützt:** Attention − ohne Reset +0.02, 5/14, p = 0.91. Beschreibend C(50) gegen nur G: add 97 none 0.29, attn 0.32, mlp 0.47, qk -0.20, vo 0.52; mul 113 none 0.44, attn 0.45, mlp 0.66, qk -0.14, vo 1.12. Lesart: Die VO-gegen-QK-Asymmetrie der Zeitkosten verallgemeinert auf zwei weitere Aufgaben; die Attention-gegen-MLP-Aussage aus N29b nicht. Exploration an bekannten Seeds. [[JOURNAL]] Sitzung 37.
