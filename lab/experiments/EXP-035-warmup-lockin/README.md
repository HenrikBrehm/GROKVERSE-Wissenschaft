---
id: EXP-035
status: vorbereitet
datum: 2026-09-26
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-035: Verschiebt ein Lernraten-Warmup die Festlegung des Transformers? (Schrittzahl oder Parameterstrecke)

Zurück: [[LAB]] · [[BACKLOG]] · [[JOURNAL]] · [[NOVEL_DIRECTIONS]] (N12) · Grundlage
[[experiments/EXP-020-data-switch/README|EXP-020]] · verwandt [[experiments/EXP-032-early-lockin/README|EXP-032]],
[[experiments/EXP-033-optimizer-lockin/README|EXP-033]].

## Anlass

EXP-020, Seed 30 (beschreibend, 13:38): Der Transformer legt seine Frequenzwahl zwischen 25 und 50 AdamW-Schritten fest; ab
150 Schritten auf F bleibt K nach 2000 G-Schritten exakt wie im Lauf „nur F“. Im Zwei-Hot-Netz (EXP-032/033) fiel die
Festlegung bei einer bestimmten Merkmalsamplitude, und der Weg dorthin (AdamW, GD, signGD) war für das Entstehen der
Neigung nicht entscheidend. Übertragen: Hängt die Festlegung an der **Zahl der Schritte** (Datenexposition) oder an der
**zurückgelegten Parameterstrecke**? Adams frühe Schritte sind vorzeichenartig und etwa so groß wie die Lernrate
(Abuduweili & Liu 2024, https://arxiv.org/abs/2412.02153), die Strecke ist also etwa die aufsummierte Lernrate Λ(t) = Σ lr_s.
Ein linearer Warmup über W = 200 Schritte macht die Strecke in den ersten Schritten viel kleiner, die Schrittzahl bleibt gleich.

## Versuch (vorab festgelegt 2026-09-26 13:41 Berlin, vor jedem EXP-035-Lauf; EXP-020 hat bis dahin nur Seed 30 fertig)

| Punkt | Festlegung |
|---|---|
| **Frage** | Verschiebt ein Warmup die kausale Festlegungszeit der Frequenzwahl (EXP-020-Protokoll) zu späteren Schritten? |
| **H35 (Strecke)** | Die Festlegung fällt bei gleicher aufsummierter Lernrate Λ. Mit Warmup (lr_t = 1e-3 · min(1, t/200)) ist Λ(25) = 1.6, Λ(50) = 6.4, Λ(100) = 25.2, Λ(141) = 50.1, Λ(150) = 56.6, Λ(250) = 150.5 (in Einheiten lr). Seed 30 (ohne Warmup (25, 50]) → mit Warmup erwartet (100, 150] |
| **Alternative (Schrittzahl)** | Das Intervall bleibt wie ohne Warmup |
| **Code** | `freq_ban.py --warmup 200` (neu, Standard 0 = unverändert; Lauf-IDs enden auf `_wu200`), sonst genau EXP-020 (Splits, 2000 G-Schritte nach dem Wechsel, „nur F“ bis 8000 mit Stop gen + 2000, K = Top-5 von W_E) |
| **Gitter** | t ∈ {0 (nur G), 25, 50, 100, 150, 250, ∞ (nur F)}, jeweils mit Warmup |
| **Seeds** | 30, 31, 32 in dieser Reihenfolge (weitere, falls Budget), nur Seeds mit gültigem EXP-020-Intervall (lo, hi] und hi ≤ 150 zählen |
| **Messung** | Festlegungsintervall mit Warmup (lo_w, hi_w] nach der EXP-020-Regel (`EXP-020/analyze.py` wiederverwendet: Gültigkeit d(0) < 0 < d(∞), Hashes, Schrittzahlen) |
| **Primär** | Verzögert: hi_w > hi (ohne Warmup) |
| **Entscheidung** | ≥ 3 auswertbare Seeds nötig. Alle verzögert → ***Festlegung folgt der Parameterstrecke (H35 gestützt)***; keiner → ***Festlegung folgt der Schrittzahl***; gemischt → ***unklar***; < 3 auswertbar → *nicht auswertbar* |
| **Sekundär** | Stimmt das Warmup-Intervall in Λ-Einheiten mit dem Intervall ohne Warmup überein (quantitative H35)? gen_F mit Warmup; Monotonie |
| **Was dagegen spräche** | hi_w = hi: Die ersten Datenkontakte legen fest, unabhängig davon, wie weit sich die Gewichte bewegen |
| **Grenzen** | Warmup ändert auch Adams Momentenschätzung und die Dynamik nach dem Warmup; eine Warmup-Länge; grobes Gitter; Seeds 30–32 sind aus EXP-020 bekannt (die Warmup-Läufe sind neu) |
| **Budget** | 7 Läufe pro Seed à 4–7 min ≈ 35 min pro Seed → 3 Seeds ≈ 1.75 h |

**Neuheit:** vorläufig; EXP-020 selbst ist nach der Suche vom 2026-09-26 nicht gefunden, Warmup als Eingriff in die kritische
Periode der Frequenzwahl ebenso wenig (nicht gezielt gesucht, nachholen).

## Befehle

    sh lab/experiments/EXP-035-warmup-lockin/queue.sh 30 31 32
    python lab/tools/guarded_run.py -- python lab/experiments/EXP-035-warmup-lockin/analyze.py
