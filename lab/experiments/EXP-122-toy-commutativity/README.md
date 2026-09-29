---
id: EXP-122
status: abgeschlossen
datum: 2026-09-29
tags: [exp/abgeschlossen, neu/kandidat, befund/positiv]
---
# EXP-122: Trägt Kommutativität die Test-Genauigkeit auf dem Grokking-Plateau des Spielzeugmodells?

Zurück: [[LAB]] · [[NOVEL_DIRECTIONS]] N57 · Anlass [[experiments/EXP-119-lm-speed-r5/README|EXP-119 Nachtrag 1]] (im LM besteht das Plateau des Zufallssplits aus Kommutativität) · [[JOURNAL]] Sitzung 54 Zyklen 10–12

**Bezug zu FINDINGS:** keine Kernaussage; Exploration zu einer neuen Beobachtung (N57), klein und billig (Regel 9). Klärt, ob das LM-Plateau eine allgemeine Eigenschaft des Grokking-Plateaus oder eine Besonderheit des LM ist.

## Vorab (Sitzung 54, 23:44 Berlin gemessen, vor jedem Lauf)

- **Frage:** Ist die Test-Genauigkeit eines Zufallssplits kurz vor dem Grokking vor allem auf Paaren, deren Tauschpaar (b, a) trainiert wurde?
- **Aufbau:** `lab/paper/repro/train.py` (Full-Batch, konstante Lernrate; im R4-Repro bitgleich zu freq_ban) auf 4 R4-Zufallssplits, deren eingefrorene Läufe generalisierten (Seed/Split/Generalisierungsschritt: 2600/u0_s1/5750, 2601/u0_s1/5075, 2603/u1_s0/5450, 2603/u1_s1/3475), bis 50 % und 90 % des Generalisierungsschritts, `--save-model`; Testmenge = Komplement. GPU, 8 Läufe à 1750–5175 Schritte.
- **Maß:** acc_swap (zurückgehaltene Paare mit Tauschpaar im Training) und acc_other; diff = acc_swap − acc_other.
- **Lesart (bei 90 %):** „Kommutativität zuerst“: diff ≥ 0.3 in ≥ 3/4; „gleichzeitig“: |diff| < 0.1 in ≥ 3/4; sonst „teilweise“. 50 % beschreibend. Technisch: Genauigkeit der Auswertung (CPU) = Trainer (GPU) bis auf ≤ 2 Vorhersagen, sonst „nicht auswertbar“.
- **Bereits gesehen:** Test-Kurven dieser R4-Läufe (0.01–0.2 vor dem Grokking, 0.37 bzw. 0.66 kurz davor bei 2601/u0_s1 und 2603/u1_s1); daraus: kein volles Plateau bei 0.3. Davon beeinflusst: Wahl von 90 % als Messpunkt.
- **Grenzen:** 4 Läufe, eine Aufgabe, bekannte Splits.

**Befehle:** `python lab/tools/parallel_queue.py lab/experiments/EXP-122-toy-commutativity/jobs.txt --workers 2` · `PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-122-toy-commutativity/analyze.py`

## Ergebnis (Sitzung 54, 30.09. 00:02 Berlin gemessen; 8/8 Läufe ohne Fehler, GPU; `summary.json`, `queue.log`)

**Vorab-Lesart: „Kommutativität zuerst“** (diff ≥ 0.3 in 4/4 Läufen bei 90 %). Technische Kontrolle bestanden (Auswertung = Trainer bis < 10⁻⁷).

| Seed / Split (Gen.-Schritt) | 50 %: acc_swap / acc_other | 90 %: acc_swap / acc_other | Test gesamt 50 % / 90 % |
|---|---|---|---|
| 2600 / u0_s1 (5750) | 0.353 / 0.003 | 0.917 / 0.202 | 0.108 / 0.416 |
| 2601 / u0_s1 (5075) | 0.422 / 0.017 | 0.963 / 0.452 | 0.138 / 0.605 |
| 2603 / u1_s0 (5450) | 0.674 / 0.030 | 0.980 / 0.443 | 0.220 / 0.602 |
| 2603 / u1_s1 (3475) | 0.560 / 0.016 | 0.952 / 0.540 | 0.179 / 0.663 |

(≈ 30 % der Testpaare haben ihr Tauschpaar im Training: n_swap 2647–2675 von 8938.)

**Deutung (Exploration, 4 Läufe, eine Aufgabe):** Auch im Spielzeugmodell entsteht auf dem Grokking-Plateau zuerst die Vertauschungsregel: Bei halbem Weg zum Grokking ist die Test-Genauigkeit fast nur auf Paaren mit trainiertem Tauschpartner (die übrigen liegen beim Zufall, 1/113 ≈ 0.009), kurz vor dem Grokking sind diese fast vollständig richtig und die übrigen folgen. Die allmählich steigende Test-Kurve vor dem Grokking ist also zum großen Teil Kommutativität. Das korrigiert meinen „ersten Blick“ (Zyklus 11): Ein Plateau *bei 0.3* gibt es im Spielzeugmodell nicht, weil die Kommutativität dort allmählich entsteht und nicht wie im LM vollständig und dann stehen bleibt; die Kommutativität geht aber auch hier voran.
**Offen:** Wann beginnt sie (vor oder nach der Memorisation)? Hängt der zweite Schritt (übrige Paare) mit der Frequenzwahl zusammen? Wie verhält sich ein konstruierter Split? Literatur gezielter prüfen (Nanda et al. 2023 „progress measures“, Power et al. 2022).

## Nachtrag 1 (Sitzung 54, 30.09. 00:04 gemessen, VOR den Läufen): Konstruierte Splits

Frage: Gehen auch konstruierte Splits (P2d, add 113, Generalisierung nach 575–1475 Schritten) durch eine Kommutativitäts-Phase, oder überspringen sie sie? Gleiches Maß, 4 eingefrorene P2d-Läufe (2230 F/G, 2231 F/G) mit `train.py` bis 50 % und 90 % ihres Generalisierungsschritts (`jobs_p2d.txt`, `analyze_p2d.py`, beide vor den Läufen). **Lesart bei 50 %:** „auch Kommutativität zuerst“: acc_other ≤ 0.1 und diff ≥ 0.3 in ≥ 3/4; „ohne Kommutativitätsphase“: |diff| < 0.1 in ≥ 3/4; sonst „teilweise“. 90 % beschreibend. Bereits gesehen: Generalisierungsschritte der P2d-Läufe; sonst nichts zu Zwischenständen.

**Ergebnis Nachtrag 1 (00:08 gemessen; 8/8 Läufe, `summary_p2d.json`, `queue_p2d.log`): Vorab-Lesart „teilweise“.**

| Seed/Arm (Gen.-Schritt) | 50 %: acc_swap / acc_other | 90 %: acc_swap / acc_other |
|---|---|---|
| 2230 F (575) | 0.711 / 0.201 | 0.993 / 0.868 |
| 2230 G (1125) | 0.614 / 0.143 | 0.979 / 0.811 |
| 2231 F (800) | 0.854 / 0.334 | 0.996 / 0.874 |
| 2231 G (1475) | 0.360 / 0.053 | 0.984 / 0.839 |

Beschreibend: Die Kommutativität liegt auch bei konstruierten Splits vorn (diff bei 50 % 0.31–0.52), aber die übrigen Paare generalisieren schon früh mit (0.05–0.33 bei 50 %, 0.81–0.87 bei 90 %), während sie bei den Zufallssplits bei 50 % beim Zufall lagen (≤ 0.03) und bei 90 % erst 0.20–0.54 erreichten. Vorsichtige Lesart (4 + 4 Läufe, verschiedene Seeds, keine Vorab-Hypothese zum Vergleich): Konstruierte Splits verkürzen vor allem die zweite Stufe, die Generalisierung auf Paare ohne Tauschpartner. Das passt zur EXP-119-Beobachtung im LM (dort fehlt bei R die zweite Stufe ganz).

**Unabhängige Code-Prüfung (00:18, Claude-Agent, nur lesend): kein Fehler.** Indexkonvention (a·113 + b, x = [a, b, =]) und Tauschindex in beiden Skripten richtig; Genauigkeiten = Trainer bis 10⁻⁸; Diagonalpaare (a = a) liegen immer in „sonst“, ohne sie ändert sich „sonst“ um ≤ 0.002. **Kontrolle (vom Prüfer an allen 8 Modellen gerechnet):** Genauigkeit getrennt danach, ob ein *anderer* Nachbar im Training ist – (a, b+1), (a+1, b), (b+1, a), zufällige Umbenennung: Unterschied höchstens 0.022 (gegen 0.35–0.67 beim Tauschpaar bei 50 %). Der Vorteil hängt also spezifisch am Tauschpaar. LM-Skript ebenfalls geprüft (Split- und Test-Hashes = Läufe, Prompt wie Trainer).
