---
id: EXP-072
status: abgeschlossen
datum: 2026-09-27
tags: [exp/abgeschlossen, befund/positiv]
verwandt: ["[[FINDINGS]]", "[[experiments/EXP-046-dihedral-steering/README|EXP-046]]", "[[confirm/P1_REGISTRATION_DRAFT|P1]]", "[[confirm/P2e_REGISTRATION|P2e]]", "[[BACKLOG]]", "[[JOURNAL]]"]
---
# EXP-072: Generalisiert D59 ueberhaupt, und bleibt die gesteuerte Irrep-Wahl dabei erhalten? (PILOT)

Zurueck zu [[LAB]] · [[FINDINGS]] Programm A (Verallgemeinerung von K2 und K2-Funktion auf die einzige nicht-abelsche Aufgabe) · [[BACKLOG]] "P2e/D59".
Festgelegt 2026-09-27, Sitzung 24, 12:36 Berlin, **vor jedem EXP-072-Lauf**. **Pilot**, bekannte Seeds 1000-1004 (P1-Splits), kein Urteil.

- **Anlass (gemessen, 12:35):** Alle 100 P1-D59-Laeufe (2000 Schritte) haben Train 1.0, aber Test im Median 0.03 (0/100 ueber 0.9; Maximum ueber den Verlauf im Median 0.03).
  K2 fuer D59 (P1 bestaetigt) ist also eine Aussage ueber die Irrep-Wahl **vor** dem Grokking. Ein Funktionsmass wie P2d/P2e (Logit-Abstand auf ungesehenen Paaren) ist an solchen
  Modellen nicht sinnvoll. Vor einer Registrierung "P2f" muss klar sein, ob und wann D59 in diesem Aufbau generalisiert.
- **Fragen:** (1) Erreicht D59 (arch25k, train_frac 0.3, AdamW lr 1e-3, wd 1.0) in 20000 Schritten Test >= 0.9? Wann? (2) Bleiben die gesteuerten Irreps nach dem Grokking dominant
  (Top-5 aus den Endspektren, Anteil der eigenen Ziele in den Top-5, beide Arme)?
- **Laeufe:** Seeds 1000-1004, Arme F und G (P1-Splits `confirm_exp1_eps2.0_D59_seed*_{F,G}`), `group_train.py --steps 20000 --save-model`, GPU. 10 Laeufe.
- **Messgroessen:** generalization_step (Test >= Schwelle "primary"), Test-Genauigkeit am Ende, Irrep-Spektrum alle 250 Schritte, Top-5 am Ende gegen die Zielmengen der Splits.
- **Lesart vorab:** >= 8/10 generalisiert -> P2f mit dieser Schrittzahl planen (Stichprobe aus der Streuung des P2f-Masses an diesen Modellen, Exploration).
  <= 2/10 -> in diesem Aufbau kein Grokking in 20000 Schritten; dann P2f nicht mit dem Funktionsmass, sondern Alternative pruefen (mehr Daten, laengere Laeufe) und das als Grenze von
  Programm A in FINDINGS vermerken. Dazwischen: unklar, Schrittzahl anpassen.
- **Grenzen:** 5 bekannte Seeds; 20000 Schritte sind ein Budget, kein Nachweis, dass spaeter nichts passiert (Auftrag §5).
- **Budget:** GPU, 10 parallel; allein 0.023 s/Schritt (P1) -> ~8 min je Lauf, parallel erwartet 10-20 min. Abbruch bei NaN oder > 40 min. Start 12:37 im Rest-Fenster: Der Waechter beendet die Laeufe um ~12:57; result.json wird alle 500 Schritte geschrieben, ein abgebrochener Lauf liefert also den Verlauf bis dahin (kein Nachweis, dass spaeter nichts passiert).

```
python lab/tools/parallel_queue.py lab/experiments/EXP-072-d59-grok/jobs.txt --workers 10
```

## Ergebnis (Sitzung 24, Laeufe 12:37-12:46, Auswertung 12:46 Berlin, gemessen; `summary.json`): Pilot

10/10 Laeufe `completed` (20000 Schritte, je ~0.03 s/Schritt bei 10 parallel), alle mit `model_final.pt`.

- **(1) D59 generalisiert:** 9/10 am Ende Test 1.0; erster Test >= 0.9 bei Median 4575 Schritten (2875-8150). Ausnahme Seed 1004 F: Test 0.83 nach 20000 Schritten.
  P1 (2000 Schritte) lag also ganz vor dem Grokking.
- **(2) Gesteuerte Irreps nach dem Grokking:** eigene Ziele unter den Top-5 der W_E-Irrep-Leistung im Mittel 4.7/5 bei Schritt 2000 und **3.7/5 am Ende** (Zufall: 5 * 5/29 = 0.86).
  Die Steuerung schwaecht sich beim Grokking ab, bleibt aber weit ueber Zufall; in keinem Lauf unter 3/5.
- **Lesart vorab erfuellt:** >= 8/10 generalisiert -> P2f mit laengeren Laeufen planen. Vorschlag: 12000 Schritte (max. erster Uebergang 8150 + Reserve), Funktionsmass als
  Irrep-Variante des P2d-Masses (Projektion auf die isotypischen Komponenten, 4 Spalten je Irrep); Pilot des Masses an diesen 10 Modellen im naechsten Fenster.
- **Grenzen:** 5 bekannte Seeds (P1-Splits), 10 Laeufe; Top-5-Zaehlung ist grob.
