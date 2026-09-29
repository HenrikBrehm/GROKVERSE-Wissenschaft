---
id: EXP-122
status: vorbereitet
datum: 2026-09-29
tags: [exp/vorbereitet, neu/kandidat]
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
