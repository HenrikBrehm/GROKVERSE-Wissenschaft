---
id: EXP-071
status: laufend
datum: 2026-09-27
tags: [exp/laufend]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-070-ov-alignment/README|EXP-070]]", "[[experiments/EXP-060-early-lead/README|EXP-060]]", "[[experiments/EXP-059-momentum-exposure/README|EXP-059]]", "[[NOVEL_DIRECTIONS]]", "[[JOURNAL]]"]
---
# EXP-071: Sagt die OV-Ausrichtung beim Wechsel die Persistenz je Seed voraus? (EXPLORATION)

Zurueck zu [[LAB]] · [[FINDINGS]] (Programm B, offene Frage N32: warum entsteht der Ausschluss zwischen t = 25 und 50?) · Vorgaenger [[experiments/EXP-070-ov-alignment/README|EXP-070]],
[[experiments/EXP-060-early-lead/README|EXP-060]] (W_E-Vorsprung sagt pi nicht voraus). Festgelegt 2026-09-27, Sitzung 24, 12:35 Berlin, **vor jedem EXP-071-Lauf**.
**Exploration**, bekannte Seeds 400-409 (pi-Werte aus EXP-059 bekannt), kein Urteil.

- **Bereits gesehene Daten:** pi_normal(t) je Seed aus EXP-059 (t = 10, 15, 20, 25, 30, 35, 50); L und E fuer reine A-Laeufe bei t = 10, 25, 50 aus EXP-070 (Mediane).
  Die Seed-Ebene von L gegen pi wurde nicht angesehen.
- **Umdeutung aus EXP-059:** pi(t) ist keine Schwelle, sondern steigt glatt (0.01 / 0.07 / 0.19 / 0.30 / 0.39 / 0.56 / 1.05). Die Frage "warum 25-50" wird daher zu: Welche Zustandsgroesse
  beim Wechsel bestimmt pi, ueber die Schrittzahl hinaus?
- **Laeufe:** reine Laeufe (EXP-056-Splits, omega = 0) mit `--steps t --save-model`, erster Split A und B, t in {10, 15, 20, 25, 30, 35, 50}, Seeds 400-409. A bei t = 10, 25, 50 aus EXP-070
  (gleicher Code, GPU); 110 neue Laeufe, GPU. Der Zustand eines reinen Laufs bei t entspricht dem Vorwechselzustand des Wechsellaufs in EXP-059 (gleicher Seed, Split, Geraet; nicht bitgleich geprueft).
- **Merkmale je Seed und t:** L = Mittel aus log(g_eigen/g_fremd) beider Richtungen (OV-Verstaerkung wie EXP-070), E = dasselbe fuer die W_E-Energie.
- **Mass:** Spearman rho zwischen Merkmal und pi_normal(t) ueber die 10 Seeds, getrennt je t (7 Werte).
- **Lesart vorab:** L traegt Seed-Information, wenn der Median der 7 rho(L) > 0.3 ist und >= 5/7 positiv; keine Information, wenn Median |rho| < 0.1. Dazwischen unklar.
  Zusaetzlich beschreibend: rho(E) zum Vergleich (EXP-060 erwartet ~ 0); ob pi ueber alle (Seed, t) enger an L als an t haengt (Spearman gepoolt).
- **Dagegen spraeche:** rho(L) ~ 0 oder negativ: Dann bestimmt nicht die OV-Ausrichtung, sondern etwas anderes (z. B. die Schrittzahl selbst, MLP/Unembedding-Zustand) die Persistenz.
- **Grenzen:** 10 bekannte Seeds, 7 abhaengige Korrelationen, lineares OV-Mass ohne Muster; reine Laeufe statt gespeicherter Vorwechselzustaende.
- **Budget:** 110 Laeufe <= 50 Schritte, GPU 8 parallel, wenige Minuten; nur im Fenster bis 13:00.

```
python lab/tools/parallel_queue.py lab/experiments/EXP-071-ov-lead-predicts/jobs.txt --workers 8
python lab/tools/guarded_run.py -- python lab/experiments/EXP-071-ov-lead-predicts/analyze.py
```
