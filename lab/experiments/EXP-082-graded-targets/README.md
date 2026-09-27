---
id: EXP-082
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet, neu/kandidat, programm/C]
---
# EXP-082: Ordnet eine vorgegebene Abstufung der Zielstärken die gelernten Frequenzen? (Eingriff statt Korrelation, Pilot)

Zurück: [[LAB]] · [[FINDINGS]] (Programm C: mechanistische Vorhersage) · [[NOVEL_DIRECTIONS]] N39 · Korrelative Vorgänger: [[confirm/C1_REGISTRATION|C1]], [[confirm/C3_REGISTRATION|C3]] · [[JOURNAL]] Sitzung 28.

**Status:** vorbereitet, Sitzung 28 (2026-09-27, ≈ 17:45 Berlin), vor jedem Lauf. Splits geschrieben (numpy), Jobliste und Auswertung fertig, **ungetestet**. Exploration an Pilot-Seeds (600–609, vorher unbenutzt), kein Urteil für FINDINGS; bei klarem Ergebnis → Bestätigungsblock an frischen Seeds.

## Frage und Bezug

C1–C3 zeigen (explorativ), dass die zufällige Schwankung des Paarspektrums die Rangfolge der fünf Ziele vorhersagt. Das ist eine Korrelation. Hier wird die Rangfolge **vorgegeben**: Jedes Ziel bekommt in der
Split-Konstruktion eine eigene Amplitude a_i (zufällig permutiert, unabhängig von Init und k). Folgt die gelernte Rangfolge den vorgegebenen a_i, ist die Wirkung der Datenzusammensetzung auf die Feinordnung ein Eingriffsbefund.

## Aufbau (vorab)

- add 113, 1-Schicht-Transformer (arch25k), AdamW lr 1e-3, wd 1, 30 % der Paare, 2000 Schritte, GPU (`freq_ban.py`, wie P1). Seeds 600–609 × Arme F/G (disjunkte Ziele) × zwei Stufungen = 40 Läufe.
- Konstruktion (`make_split.py`): wie P1 (ε = 2), aber `wave = mean_i a_i cos(...)`. **strong:** a ∈ {0.4, 0.7, 1.0, 1.3, 1.6}; **weak:** a ∈ {0.90, 0.95, 1.00, 1.05, 1.10}.
- Numpy-Prüfung des Hebels (`--design`, vor jedem Lauf): strong ordnet das realisierte M0c fast perfekt (ρ 0.995, M0c max/min 3.8, Zielanteil 0.20 wie P1 0.19); weak: ρ 0.66, max/min 1.47 (natürliche Schwankung in P1/R1: 1.30), Zielanteil 0.19.
- **Maß:** je Arm Spearman über die 5 Ziele zwischen a_i und der W_E-Energie bei Schritt 2000; Einheit Seed (Mittel F/G).
- **Hypothesen:** H-strong: Mittel ≥ 0.6. **H-weak (Hauptfrage):** Mittel > 0, exakter einseitiger Vorzeichentest p < 0.05 (10 Seeds).
- **Was dagegen spräche:** H-weak Mittel ≤ 0 → Unterschiede in natürlicher Größe ordnen nicht kausal (C1 wäre dann eher Ko-Variation mit etwas anderem). H-strong verfehlt → auch starke Abstufungen setzen sich nicht durch (Sättigung/Wettbewerb dominiert).
- **Beschreibend:** ρ mit dem realisierten M0c, ρ mit der Init-Energie, Zielanteil, generalisierte Arme.
- **Power (grob):** Erwartet für weak ρ ≈ 0.3 (0.66 × Hebel, C1-Größe 0.44); SD je Seed ≈ 0.35 → SE ≈ 0.11, Power etwa 0.6–0.7. Pilot; ein „n. s.“ ist kein Gegenbeleg.
- **Budget:** 40 Läufe à 2000 Schritte, GPU ≈ 0.03 s/Schritt bei 8 parallel → ≈ 5–10 min. Abbruch bei NaN oder fehlendem Fortschritt.

## Befehle (nur im Fenster, alles über den Wächter)

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-082-graded-targets/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-082-graded-targets/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-082-graded-targets/analyze.py
```

Splits neu erzeugen (deterministisch, überschreibt nie): `python lab/experiments/EXP-082-graded-targets/make_split.py --write`.
