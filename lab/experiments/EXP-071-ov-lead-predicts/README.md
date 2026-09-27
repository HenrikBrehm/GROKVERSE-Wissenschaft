---
id: EXP-071
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/unklar]
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

## Ergebnis (Sitzung 24, Laeufe 12:33-12:39, Auswertung 12:39 Berlin, gemessen; `summary.json`): Exploration

110/110 Laeufe ok, 70/70 (Seed, t)-Zellen vollstaendig. (Auswertung: scipy fehlt im globalen Python; Spearman als Pearson auf Raengen nachgebaut, vor dem ersten Ergebnis.)

| t | 10 | 15 | 20 | 25 | 30 | 35 | 50 |
|---|---|---|---|---|---|---|---|
| rho(L, pi) je t | 0.21 | 0.36 | 0.48 | 0.49 | 0.44 | 0.16 | 0.20 |
| rho(E, pi) je t | -0.33 | -0.14 | 0.02 | 0.20 | 0.30 | 0.30 | 0.18 |

- **Vorab-Regel:** Median rho(L) = 0.36 > 0.3, 7/7 positiv -> formal *"L traegt Seed-Information"*. Zum Vergleich W_E-Energie E: Median 0.18.
- **Einschraenkung (die Vorab-Regel hat sie uebersehen):** Die 7 Korrelationen stammen von denselben 10 Seeds und sind stark abhaengig; "7/7 positiv" ist im Kern **eine** Korrelation auf
  Seed-Ebene. *Post hoc* (nach dem Ergebnis gewaehlt): je Seed Mittel der z-Werte ueber t, dann Pearson mit Permutationstest (20000): **L r = 0.45, p = 0.09** (einseitig); E r = 0.11, p = 0.40.
  L und E sind auf Seed-Ebene stark korreliert (0.81).
- **Gepoolt:** pi haengt ueber alle (Seed, t) an t (rho 0.91) nicht schwaecher als an L (0.89) oder E (0.90): Die OV-Ausrichtung erklaert den **zeitlichen** Verlauf nicht besser als die Schrittzahl.
- **Lesart:** Schwacher Hinweis, dass Seeds mit staerkerer OV-Ausrichtung beim Wechsel etwas fester an ihrer ersten Wahl haengen, besonders bei t = 15-30; bei n = 10 bekannten Seeds nicht belastbar.
  Negativ fuer die staerkere Form (L als "Uhr" der Festlegung). **Urteil: unklar (schwacher Hinweis).**
- **Folge:** Bestaetigung nur lohnend mit frischen Seeds und genug n: fuer r = 0.45 (einseitig, alpha 0.05, Power 0.8) etwa n = 30-40 Seeds. Gegen die offenen Fragen in [[FINDINGS]] priorisieren.
