---
id: EXP-020
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[experiments/EXP-016-engineered-split/README|EXP-016]]", "[[experiments/EXP-013-lockin-curve/README|EXP-013]]", "[[experiments/EXP-009-freq-commitment/SUMMARY|EXP-009]]", "[[NOVEL_DIRECTIONS]]"]
---
# EXP-020: Datenwechsel mitten im Training: kausale Festlegungszeit der Frequenzwahl

**Status:** vorbereitet, **nicht ausgeführt**. Definition fixiert 2026-09-26 06:16 Berlin (Sitzung 5), bevor ein
Lauf mit Datenwechsel existierte. Code: `make_splits.py` (Splits, erzeugt), Optionen `--switch-split-file`,
`--switch-step` in `freq_ban.py`, `analyze.py`, `queue.sh`. Tests im Fenster ok (14/14, 06:12): Splits und
fail-closed-Argumentprüfung. **Der Wechsel in der Trainingsschleife ist in keinem echten Lauf geprüft:** vorher
Smoke mit `--steps 60 --switch-step 30` und Kontrolle von `events.switch` und der Trainingsgenauigkeit.

## Idee

EXP-009 und EXP-013 messen die Festlegung der Frequenzwahl **korrelativ** (ab wann ist K am Spektrum ablesbar).
[[experiments/EXP-016-engineered-split/README|EXP-016]] zeigt: Ein konstruierter Split gibt die Frequenzen vor. Das
erlaubt einen **Eingriff**: Das Netz trainiert bis Schritt t auf Split F (Zielfrequenzen F), dann auf Split G
(disjunkte Zielfrequenzen G). Behält es F oder wechselt es zu G? Die Zeit t, ab der F überwiegt, ist eine **kausale**
Festlegungszeit. Nächstverwandt: Achille et al. 2019, *Critical Learning Periods* (https://arxiv.org/abs/1711.08856),
Defizit früh im Training mit bleibender Wirkung, Bildklassifikation. Ein Datenwechsel mit messbarer Merkmalsidentität
(welche Frequenzmenge) bei modularer Addition wurde in der Suche vom 2026-09-26 nicht gefunden (vorläufig).

## Design

- Seeds 30–34 (frisch). Pro Seed gemeinsame Testmenge T* (20 %), aus dem Rest zwei konstruierte Trainingsmengen F und G
  (ε = 2, disjunkte Zielmengen, gleiche Ziehungsschlüssel; sie teilen ≈ 2740–2800 von 3831 Paaren, der Wechsel tauscht
  also ≈ 28 % der Paare aus). M0-Top-5 = Zielmenge in allen 10 Mengen.
- Wechselzeit t ∈ {0, 50, 150, 400, 1000, ∞}. t = 0 heißt: nur G (Lauf mit `--split-file train_G`, ohne Wechsel);
  t = ∞: nur F. Alle Läufe genau 2000 Schritte (`--steps 2000 --stop-after-gen 2000`), K = Top-5 von W_E bei 2000.
- 5 Seeds × 6 Läufe = 30 Läufe à ≈ 4.5 min ≈ 2.3 h.

| | |
|---|---|
| **Fragestellung** | Ab welcher Trainingszeit auf F hält das Netz an F fest, obwohl die Daten danach G bevorzugen? |
| **Messgröße** | d(t) = \|K(t) ∩ F\| − \|K(t) ∩ G\| bei Schritt 2000 |
| **Primärgröße** | t½ pro Seed: erste Gitterstelle mit d > 0, linear interpoliert in log(t + 25) zur letzten Stelle mit d ≤ 0 |
| **H20** | Die Festlegung geht dem Grokking voraus: t½ < gen_F (gen_F = erster Schritt mit Test-Acc ≥ 0.95 auf T* im Lauf t = ∞; nicht erreicht bis 2000 → 2000) |
| **Test** | Vorzeichentest über die 5 Seeds, einseitig; *bestätigt* nur bei 5/5 (p = 1/32) |
| **Gültig** | d(0) < 0 und d(∞) > 0 (sonst hat die Konstruktion in diesem Seed nicht gesteuert; der Seed zählt dann als *nicht auswertbar*, nicht als Gegenbeleg); alle 6 Läufe `completed`, Hashes passen |
| **Entscheidung** | 5/5 → *bestätigt* · 4 gültige, alle t½ < gen_F → *richtungsgleich, zu wenige Seeds* · t½ ≥ gen_F (oder keine Kreuzung vor ∞) in ≥ 1 gültigen Seed → *nicht bestätigt* · < 4 gültige Seeds → *nicht auswertbar* |
| **Sekundär** | ganze Kurve d(t) je Seed; Mischzustände (K enthält F und G); Test-Acc bei 2000 je t; Vergleich t½ mit dem korrelativen Lock-in (EXP-009: Median L/g 0.29); Trainingsgenauigkeit auf den neuen Paaren direkt vor dem Wechsel |
| **Erwartung** | t½ zwischen 50 und 400 (Amarine-Repo: ~3/4 der Frequenzen nach 462 Schritten fest; EXP-009) |
| **Was dagegen spräche** | Kurve ohne Schwelle (das Netz folgt immer den aktuellen Daten, d(1000) < 0): Dann gibt es keine Festlegung, nur Nachführung. Oder t½ nach gen_F |
| **Grenzen** | Adam-Zustand läuft über den Wechsel weiter (gewollt: natürlicher Eingriff); der Wechsel ändert auch die Menge der auswendig gelernten Paare (≈ 28 %). Nur Transformer, ε = 2 |

## Befehle

```
python lab/experiments/EXP-020-data-switch/make_splits.py --seeds 30-34
# Smoke (Pflicht):
python lab/tools/guarded_run.py -- python lab/experiments/EXP-001-freq-ban/freq_ban.py --seed 30 --condition baseline --steps 60 --stop-after-gen 2000 --split-file lab/experiments/EXP-020-data-switch/splits/seed30_train_F.npy --test-file lab/experiments/EXP-020-data-switch/splits/seed30_test.npy --switch-split-file lab/experiments/EXP-020-data-switch/splits/seed30_train_G.npy --switch-step 30 --out-root lab/experiments/EXP-020-data-switch/raw_smoke
sh lab/experiments/EXP-020-data-switch/queue.sh
python lab/experiments/EXP-020-data-switch/analyze.py
```
