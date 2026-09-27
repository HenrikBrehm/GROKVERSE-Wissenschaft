---
id: EXP-080
status: vorbereitet
datum: 2026-09-27
tags: [exp/vorbereitet, neu/kandidat]
verwandt: ["[[NOVEL_DIRECTIONS]]", "[[experiments/EXP-079-head-symmetry/README|EXP-079]]", "[[confirm/N29c_REGISTRATION|N29c]]", "[[FINDINGS]]", "[[paper/related_work]]", "[[JOURNAL]]"]
---
# EXP-080: Hält der Pfad, den der Wechsel verlangt? Aufgabenwechsel a + b → a − b (Leitung) gegen a² + b² (Inhalt) mit QK- oder VO-Reset (PILOT, N36)

Zurück zu [[LAB]] · [[NOVEL_DIRECTIONS]] N36 · Programm B (Persistenz), entscheidet zwischen zwei ausdrücklichen Konkurrenzmodellen (Regel 18c) · Anlass: Dong 2026 (QK-Reset hilft in Sprachmodellen,
Value nicht) gegen K4e (bei uns Wertepfad > QK).
Festgelegt 2026-09-27, Sitzung 26, 15:50 Berlin (gemessen), **vor jedem EXP-080-Lauf**. **Pilot**, Seeds **800–809** (bisher ungenutzt), kein Bestätigungsurteil.

## Startbedingung

Nur starten, wenn [[experiments/EXP-079-head-symmetry/README|EXP-079]] *symmetrisch* ergibt (sonst ist a − b kein reiner Leitungswechsel; dann EXP-080 nicht rechnen und im JOURNAL begründen).
Code ungetestet: vorher ein Smoke (`--post-steps 1000`, eine Zeile, Ausgabe prüfen).

## Konkurrenzmodelle

- **N36 („der benötigte Pfad hält“):** Beim Wechsel zu a − b (antisymmetrisch, braucht positionsabhängige Leitung) hilft ein QK-Reset mehr als ein VO-Reset; beim Wechsel zu a² + b² (symmetrisch,
  neuer Inhalt) hilft ein VO-Reset mehr. → Wechselwirkung I > 0.
- **„Der Wertepfad hält immer“:** Der VO-Reset hilft in beiden Wechseln mehr (B_vo > B_qk), keine Wechselwirkung.

## Aufbau

- Modell und Optimierer der Studie (arch25k, add 113, eigener zufälliger 30-%-Split des Seeds, Vollbatch-AdamW lr 1e-3, wd 1). `train_switch.py`: t Schritte auf a + b, dann **gleiche Paare, neue Labels**
  (a − b bzw. a² + b² mod 113), optional Reset von W_Q, W_K („qk“) oder W_V, W_O („vo“) auf die Init samt AdamW-Zustand (wie `--reset-at-switch`), dann 2000 Schritte.
- Gitter: 10 Seeds × t ∈ {50, 1000} × {sub, sq} × {none, qk, vo} = **120 Läufe**, GPU, 1 Thread (`jobs.txt`); ≈ 15 min bei 10 parallel (≈ 0.03 s/Schritt).
- **Maß:** auc1000 = mittlerer Trainingsverlust (neue Labels) über die ersten 1000 Schritte nach dem Wechsel; Nutzen B_R = auc1000(none) − auc1000(R).
  Wechselwirkung I = [B_qk − B_vo](sub) − [B_qk − B_vo](sq) je Seed.

| | |
|---|---|
| **Primär** | I bei t = 50 (wie K4e), Mittel über 10 Seeds, einseitiger exakter Vorzeichentest, Bootstrap-KI |
| **Lesart vorab** | Ī > 0 und p < 0.05 → *Wechselwirkung wie N36 (Pilot)* · KI-Untergrenze von B_vo − B_qk > 0 in **beiden** Aufgaben und KI von I enthält 0 → *Wertepfad wirkt in beiden stärker (Pilot)* · sonst *unklar* · < 8 gültige Seeds → *nicht auswertbar* |
| **Sekundär (nur berichtet)** | dasselbe bei t = 1000 („gealtertes“ Netz wie bei Dong); B_R je Aufgabe; Testgenauigkeit der neuen Aufgabe nach 2000 Schritten; Trainingsgenauigkeit auf a + b beim Wechsel |
| **Gültig** | result.json passt zu Seed, t, Aufgabe, Reset, 2000 Schritten, cuda; auc endlich |
| **Was dagegen spräche** | B_vo > B_qk auch bei a − b: Der Wertepfad hält unabhängig davon, was der Wechsel verlangt; der Dong-Gegensatz läge dann an Maß, Größe oder Aufgabe, nicht an Leitung gegen Inhalt |
| **Grenzen** | Pilot, 10 Seeds, eine Architektur; Lerngeschwindigkeit (Plastizität) statt Festhalten alter Frequenzen, also ein anderes Maß als K4e; ein Reset stört auch den Rest des Netzes (Nutzen = Nettoeffekt); a² + b² ist 2-zu-1 in jedem Operanden (x und −x); Symmetrie der Attention (EXP-079) ist notwendig, nicht hinreichend |

## Literatur

Suche Sitzung 25 (N36, [[NOVEL_DIRECTIONS]]): QK = Leitung, OV = Inhalt ist Standard (Elhage et al. 2021); eine Vorhersage, welcher Teil-Reset je nach Art des Wechsels hilft, nicht gefunden (vorläufig).
Dong 2026 (arXiv 2607.27281) prüft QK- gegen Value-Resets nur für einen Wechsel-Typ (zurückgehaltene Fähigkeit in Sprachmodellen).

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

N29c (VO > QK beim Frequenzwechsel, Seeds 2320–2339), Dong 2026 (Gegensatz). Keine Läufe mit Aufgabenwechsel gesehen. Wahl t = 50 folgt K4e, t = 1000 folgt der „Alterung“ bei Dong.

## Befehle (ab 00:00, nur nach EXP-079 *symmetrisch*)

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-080-route-vs-content/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-080-route-vs-content/jobs.txt --workers 10
python lab/tools/guarded_run.py -- python lab/experiments/EXP-080-route-vs-content/analyze.py
```
