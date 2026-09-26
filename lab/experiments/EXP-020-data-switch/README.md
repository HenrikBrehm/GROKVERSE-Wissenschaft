---
id: EXP-020
status: abgeschlossen
datum: 2026-09-26
tags: [exp/abgeschlossen, neu/kandidat, befund/unklar]
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

## Nachtrag a (2026-09-26 06:20 Berlin, nach Codex-Review, **vor jedem Lauf**): neues Design

Codex (`codex_review_2026-09-26.txt`, „needs-attention“), 4 Befunde, selbst geprüft, alle **übernommen**. Die Tabelle
oben gilt nur noch, wo sie hier nicht ersetzt wird.
1. [high] *Wechselzeit und G-Trainingsmenge waren gekoppelt* (festes Ende bei 2000: späterer Wechsel = weniger G).
   Auch ein vollständig reversibler Lerner hätte dann F „behalten“. → **Gleiches G-Budget:** Jeder Wechsel-Lauf trainiert
   t Schritte auf F und danach **genau 2000 Schritte auf G** (`--steps t+2000`); K = Top-5 von W_E am Ende. t = 0 = nur G,
   2000 Schritte. Sekundär: Ist K über die letzten 500 G-Schritte stabil?
2. [high] *Lineare Interpolation in log(t + 25) erfindet einen Schwellenpunkt, und nicht-monotone Kurven konnten
   „stützen“* (Beispiel d = [−1, 1, −1, −1, −1, 1]). → **Keine Interpolation.** Die Festlegungszeit ist
   intervallzensiert: (letztes t mit d ≤ 0, erstes t mit d > 0]. Ein Seed **stützt H20 nur**, wenn d über das ganze
   Gitter nicht abnimmt **und** das erste t mit d > 0 vor gen_F liegt (das ganze Intervall vor der Generalisierung).
   Nicht monoton → *gegen*. Keine Kreuzung vor ∞ → *gegen*.
3. [medium] *Die Diagnose „neue Paare“ maß ganz G* (72 % davon schon aus F bekannt). → Beim Wechsel werden die
   Genauigkeiten auf G\F, F\G und F∩G getrennt mit Anzahlen gespeichert; G\F ist die Transfer-Diagnose.
4. [medium] *Die Warteschlange stoppte nur bei Exit 3/124.* → `freq_ban.py` endet bei „already completed“ jetzt mit 0;
   die Warteschlange stoppt bei **jedem** anderen Exit-Code. Nach dem Smoke prüft `check_smoke.py` Wechselschritt,
   Hashes und Teilmengen-Diagnose, sonst Abbruch.
Zusätzlich (eigener Punkt): gen_F war bei 2000 gedeckelt, dann wäre H20 trivial erfüllt. → Der Lauf „nur F“ läuft bis
höchstens 8000 Schritte (`--stop-after-gen 2000`), K wird trotzdem bei Schritt 2000 gelesen; zensiertes gen_F → Seed
für H20 *nicht auswertbar*.
Entscheidung unverändert: 5/5 auswertbare Seeds stützen → *bestätigt*; 4/4 → *richtungsgleich, zu wenige Seeds*;
mindestens ein *gegen* → *nicht bestätigt*; < 4 auswertbar → *nicht auswertbar*.
Budget neu: pro Seed ≈ 2000–8000 (nur F) + 2000 (nur G) + 9600 (Wechsel) Schritte à 0.13 s ≈ 30–45 min; 5 Seeds ≈ 2.5–3.5 h.
Vorgeschaltet: Die Reverse-Kontrolle (G → F) ist sinnvoll, aber nicht vorab festgelegt; sie wäre ein eigener Nachtrag.

## Nachtrag b (2026-09-26 06:53 Berlin, **vor jedem Lauf**): feineres Gitter am Anfang

Anlass (vorhandene Daten, keine EXP-020-Läufe): In EXP-016 ist die W_E-Top-5 schon bei Schritt 50 (Smoke) bzw. 250
(alle 12 Läufe der Seeds 10–15) genau die Zielmenge (Überlappung 5/5); danach sinkt die Überlappung bis Schritt 2000 auf
3–5, weil 2k-Harmonische einzelne Ziele verdrängen. Die Festlegung kann also vor Schritt 50 liegen; mit dem bisherigen
Gitter wäre dann nur „(0, 50]“ messbar. → Wechselzeiten jetzt **t ∈ {0, 10, 25, 50, 150, 400, 1000, ∞}**
(`analyze.py`, `queue.sh`, `queue_s5.sh`). Auswerteregeln unverändert. Budget + 10 Läufe (≈ 45 min).

## Nachtrag c (2026-09-26 13:52 Berlin, nach Ansicht von Seed 30, **vor** Ansicht der Seeds 31–34): Festlegung vor der Memorisierung?

Seed 30 (beschreibend): Festlegung in (25, 50], Trainingsgenauigkeit des Laufs „nur F“ bei Schritt 50 erst 0.10, Train ≥ 0.97
erst bei 120–130. **Sekundär, vorab für die Seeds 31–34:** In jedem gültigen Seed ist die Trainingsgenauigkeit des Laufs
„nur F“ an der oberen Intervallgrenze hi (nächster aufgezeichneter Schritt, alle 10 Schritte) ≤ 0.5 → *Festlegung vor der
Memorisierung bestätigt*; sonst *nicht bestätigt*. Seed 30 zählt nicht mit (daran gefunden). Auswertung von Hand aus
`dense.train_acc`; ändert H20 und seine Entscheidung nicht.

## Nachtrag d (2026-09-26 14:52 Berlin, nach Ansicht der Seeds 30–32, **vor** jedem Lauf der Seeds 33/34): fremde Frequenzen in Mischzuständen

Beschreibend, sekundär; ändert H20 nicht. Beobachtung an Seeds 30–32 (Exploration): In Läufen mit Wechsel bei t ≤ 50
enthält K Frequenzen außerhalb A = F ∪ G ∪ fold(2k) ∪ K_nurF ∪ K_nurG (Seed 30: 34, 39; Seed 31: 36, 42, 22; Seed 32: 8, 13),
bei t ≥ 150 nie. Diese Frequenzen stehen im Init-Spektrum von W_E (Schritt 0) auffällig weit oben (Ränge 1, 2, 4, 8, 11, 18, 29
von 56; Median 8). Deutung (Spekulation): Solange weder F noch G festgelegt ist, heben sich die Datensignale teilweise auf
und das Init-Spektrum setzt sich durch.
**Vorab für die frischen Seeds 33, 34** (Definition und Code: `conflict_freqs.py`, Stand dieses Commits):
- **P-d1** (je Seed, nur gültige Seeds mit allen 8 Läufen): mindestens eine fremde Frequenz in einem Lauf mit t ∈ {10, 25, 50}
  und keine in t ∈ {150, 400, 1000} → *erfüllt*, sonst *nicht erfüllt*.
- **P-d2** (gepoolt über beide Seeds): Median des Init-Rangs der verschiedenen fremden Frequenzen ≤ 14 → *erfüllt*.
  Zufall wäre ≈ 28. Keine fremde Frequenz → *nicht erfüllt*.
Grenze: 2 Seeds, keine Inferenzstatistik; die Beobachtung stammt aus denselben Läufen, aus denen die Deutung kommt.

## Ergebnis (2026-09-26 16:22 Berlin, alle 5 Seeds, `analyze.py`, `summary.json`)

**Vorab festgelegtes Urteil: *nicht bestätigt*** (4 von 5 Seeds stützen H20, einseitiger Vorzeichentest p = 0.19; für
*bestätigt* wären 5/5 nötig gewesen). Die Gegenstimme ist Seed 33, und zwar allein, weil d(t) nicht monoton ist:
d(0) = −4, d(10) = −5 (der reine G-Lauf enthält die Oberwelle 6 = 2 · 3 statt des G-Ziels 34).

| Seed | d(0) | d(10) | d(25) | d(50) | d(150…∞) | Intervall | gen_F | H20 |
|---|---|---|---|---|---|---|---|---|
| 30 | −3 | −3 | −1 | +1 | +3 | (25, 50] | 950 | stützt |
| 31 | −2 | −2 | 0 | +3 | +3 | (25, 50] | 625 | stützt |
| 32 | −4 | −4 | −3 | +3 | +3 | (25, 50] | 1225 | stützt |
| 33 | −4 | −5 | −5 | +2 | +3 | (25, 50] | 1325 | gegen (nicht monoton) |
| 34 | −4 | −3 | −3 | +3 | +5 | (25, 50] | 650 | stützt |

**Beschreibend (nicht Teil des Urteils):** Das Festlegungsintervall ist in **5/5 Seeds identisch (25, 50]** Schritte, weit vor
gen_F (625–1325). Ab t = 150 ist K nach 2000 G-Schritten in 5/5 Seeds exakt gleich K des Laufs „nur F“. Mit dem nachträglich
gewählten Oberwellen-erweiterten Maß d_h (JOURNAL Sitzung 9, Zyklus 7) ist d in allen Seeds monoton. Während der G-Phase
wächst der F-Anteil weiter (Zyklus 4), die Festlegung vertieft sich. **Nachtrag c:** Train-Acc „nur F“ bei Schritt 50 in den
Seeds 31–34: 0.108, 0.102, 0.089, 0.109, alle ≤ 0.5 → *Festlegung vor der Memorisierung bestätigt* (4/4).
**Nachtrag d (fremde Frequenzen):** P-d1 in Seed 33 erfüllt, in Seed 34 **nicht** (keine fremde Frequenz); P-d2 **nicht
erfüllt** (einzige frische fremde Frequenz 38 hat Init-Rang 34). Die Init-Deutung aus der Exploration (Seeds 30–32) hält an
den frischen Seeds **nicht**. Fremde Frequenzen treten bei frühem Wechsel in 4/5 Seeds auf, ihr Ursprung bleibt offen.
**Einordnung:** Die Messmethode (Datenwechsel) zeigt eine sehr gleichförmige kritische Periode; das vorab festgelegte Urteil
fällt wegen einer zu strengen Monotonie-Regel auf *nicht bestätigt*. Das wird nicht nachträglich umgedeutet; ein
Folgeversuch sollte d_h vorab festlegen.

## Post hoc (Sitzung 14, 2026-09-26 21:52 Berlin, explorativ, bereits ausgewertete Seeds 30–34): kontinuierliches Persistenzmaß

`posthoc_beta_persistence.py` / `.json` (reine Nachrechnung, kein Training): β_X = Steigung von log W_E-Leistung auf log M0 des Splits X
am Laufende; D = β_F − β_G; π(t) = (D(t) − D_nurG) / (D_nurF − D_nurG) je Seed (0 = wie „nur G“, 1 = wie „nur F“).

| Wechsel bei t | 10 | 25 | 50 | 150 | 400 | 1000 |
|---|---|---|---|---|---|---|
| π̄ [min, max] über 5 Seeds | 0.15 [0.09, 0.26] | 0.38 [0.28, 0.48] | 0.72 [0.61, 0.89] | 1.00 [0.96, 1.04] | 1.01 [0.96, 1.06] | 1.04 [0.99, 1.08] |

Glatter Übergang mit Halbwert bei ≈ 30–35 Schritten und sehr kleiner Streuung; passt zum Kippen des Dominanzmaßes in (25, 50] (oben),
ohne dessen Schwellen. Grenzen: nur 5 Seeds, post hoc; F und G teilen ≈ 73 % der Paare (Persistenz kann an geteilten Paaren hängen; das
trennt [[experiments/EXP-053-p3-overlap-design/README|EXP-053]]); die Wechselläufe enden bei t + 2000, die reinen bei 2000 (β wächst mit
der Zeit, daher π > 1 bei t = 1000 möglich).

*Korrektur nach adversarieller Prüfung (Sitzung 14, Claude-Subagent, alle Zahlen selbst nachgerechnet, keine Fehler im Code):*
(1) β ist praktisch ein Maß über die 10 Zielfrequenzen (≈ 85–90 % der Varianz von log M0 liegt auf den 5 Zielen; ohne die Ziele wird π
Rauschen). π misst also die Aufteilung der Leistung zwischen F- und G-Zielen; die Übereinstimmung mit dem Log-Verhältnis ist keine
unabhängige Bestätigung. (2) Werte über 1 sind ein Artefakt der späteren Endschritte (D der reinen F-Läufe wächst nach 2000 um 5–10 %;
bei gleichem Endschritt 0.99/0.99 statt 1.01/1.04). Richtig: **π ≈ 1 (0.94–1.04) ab t = 150.** Bestand hat: der Verlauf 0.15 / 0.38 / 0.72
bei 10 / 25 / 50, monoton, Halbwert ≈ 34 Schritte (aus drei Punkten interpoliert), und dass π bei t = 25 Seeds trennt, deren Top-5 nur
grob (0–2 F, 2–5 G) unterscheidbar sind. Reproduktion für EXP-035/037: `posthoc_pi_other.py` / `.json`.

## Post hoc (Sitzung 15, 2026-09-26 22:42–22:50 Berlin, explorativ, bereits ausgewertete Seeds): π über die G-Phase, Fenstermodell

- `posthoc_pi_trajectory.py`: π bei jedem gespeicherten Schritt der G-Phase (Normierung mit den reinen Läufen beim selben Schritt) ist von
  Schritt 250 bis zum Ende nahezu konstant (Drift je Seed ≤ 0.10), der Kontrast wächst ≈ 2.3-fach. *Einschränkung (Gegenprüfung):* π ist
  gegen gemeinsame affine Abbildungen des Log-Spektrums invariant; das heißt „gemeinsame Umskalierung“, nicht „eingefroren“.
- `posthoc_window_model.py`: Fenster T* ≈ 69 Schritte (bzw. exponentiell τ ≈ 45) passt; sagt EXP-037 mit RMSE 0.09 (0.05) voraus, eine
  Konstante 0.5 aber schon mit 0.14. Nur „verträglich mit einem frühen Fenster von ≈ 50–100 Schritten“.
- `posthoc_clock_crossover.py`: Top-5-Kreuzung unter reinem Takt aus den Split-Dateien: 32–40 (beobachtet (25, 50] in 5/5). Folge für
  EXP-042 siehe dort, Nachträge b und c. Einzelheiten und Prüfung: [[JOURNAL]] Sitzung 15, Zyklus 1.
