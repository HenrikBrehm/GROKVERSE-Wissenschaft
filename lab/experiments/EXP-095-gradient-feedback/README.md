---
id: EXP-095
status: vorbereitet
datum: 2026-09-28
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-095: Braucht die frühe Festlegung frische Gradienten entlang des Wegs? (Pilot, Exploration)

Zurück: [[LAB]] · [[FINDINGS]] (offene Frage nach EXP-093/094: Was macht die frühe Bewegung zielgenau?) · [[NOVEL_DIRECTIONS]] N48 · Vorgänger [[experiments/EXP-094-evaluations-vs-window/README|EXP-094]], [[experiments/EXP-093-lag-clock-range/README|EXP-093]]

**Festgelegt vor jedem EXP-095-Lauf** (Sitzung 42, 2026-09-28; `design.py`, `analyze.py`, Selbsttest grün über den Wächter; Trainer-Option `--pre-switch-grad-every` neu in dieser Sitzung, Tests grün).

## Bezug und Frage

EXP-094: Bei Λ = 24 und in Λ angeglichenen Adam-Fenstern bleibt bei wenigen großen Schritten ein Rückstand, der mit c wächst (d8 = +0.174 bei 3 Schritten). Zwei Erklärungen sind dort nicht getrennt: **(E) Auswertungen / Rückkopplung:** Die frühe Bewegung wird zielgenau, weil der Gradient unterwegs neu ausgewertet wird. Die gerade wachsenden Zielkomponenten verstärken ihren eigenen Gradienten, und das ist eine Rückkopplung, die über die erste Ordnung hinausgeht. Wenige Auswertungen = wenig Rückkopplung. **(S) Adam-Schritt:** Der grobe Adam-Schritt selbst (β₁′ 0.2, β₂′ 0.84 über 3 Schritte, Überschießen) ist das Problem, nicht die Zahl der Auswertungen.

**Eingriff:** Arm gk macht die normalen 24 Adam-Schritte (Lernrate, β 0.9/0.98, Weight Decay unverändert), wertet den Gradienten vor dem Wechsel aber nur alle k Schritte neu aus (dazwischen derselbe gespeicherte Gradient). g8 hat also dieselben 3 Auswertungen wie c8b, aber feine Adam-Schritte. g24 nutzt nur den Anfangsgradienten: Das ist ein direkter Test, ob die erste Ordnung (Richtung am Start) für die Festlegung bis Λ = 24 reicht.

## Aufbau

Wie EXP-094 (add 113, ω = 0-Splitpaare, Wechsel A → B und B → A bei t, danach 2000 Standardschritte, π gegen reine Läufe; GPU). **Seeds 3470–3485** (frisch, Dateisuche 28.09. ohne Treffer). Zellen: **n24** (Standard), **g4**, **g8**, **g24** (je t = 24, Gradient alle k Schritte), **c8b** (c = 8, t = 3, β′ 0.2/0.84; Replikation aus EXP-094). 12 Läufe je Seed, **192 GPU-Läufe** (≈ 17 min mit 8 Workern wie EXP-094).

## Vorhersagen und Lesarten (verbindlich, im Code)

e_k = π(n24) − π(gk), d8 = π(n24) − π(c8b), r8 = π(g8) − π(c8b); gepaarte Bootstrap-KIs über Seeds (10 000, rng 95).
- **„nicht trennbar“:** KI-Untergrenze von d8 ≤ 0.03 (Rückstand aus EXP-094 repliziert nicht).
- **„Auswertungen zählen“** (E): KI-Untergrenze von e8 > 0.03 und mittleres e8 ≥ 0.5 · mittleres d8.
- **„Adam-Schritt“** (S): KI von e8 innerhalb ±0.05.
- sonst **„teilweise“**; < 10 gültige Seeds → *nicht auswertbar*.
- **Beschreibend:** e4, e24, r8, Ordnung e4 ≤ e8 ≤ e24; Zellmittel von π, Zielanteil f und Norm N beim Wechsel; prospektive Prüfung der Geraden π(f) aus EXP-092/093 (MAE).
- **Erwartung (vorab):** eher (E). Mit eingefrorenem Gradienten sind Adams Schritte innerhalb eines Blocks fast gleich (m̂ = g, v̂ = g² ab Start), also ähnlich einem großen Vorzeichen-Schritt. Deshalb sollte g8 nahe bei c8b liegen, und g24 sollte am schwächsten festlegen. Gegen (E) spräche g8 ≈ n24. Dann trüge bis Λ = 24 die erste Ordnung, und der c8b-Rückstand läge am groben Adam-Schritt.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-094 (d8 = +0.174, Lesart „teilweise“, Frage), EXP-093 (Λ = 24, Schwelle 0.03), R9 (β′-Regel), Post-hoc-Gerade π(f). Keine Seeds aus diesen Blöcken. Die Wahl von k ∈ {4, 8, 24} folgt den EXP-094-Zellen (6 und 3 Auswertungen) plus dem Extremfall.

## Befehle

```
python lab/experiments/EXP-095-gradient-feedback/design.py          # Splits (schon erzeugt)
python lab/tools/guarded_run.py -- python lab/experiments/EXP-095-gradient-feedback/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-095-gradient-feedback/smoke.txt --workers 3
python lab/tools/parallel_queue.py lab/experiments/EXP-095-gradient-feedback/jobs.txt --workers 8
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-095-gradient-feedback/analyze.py
```

## Ergebnis

_noch nicht gerechnet_
