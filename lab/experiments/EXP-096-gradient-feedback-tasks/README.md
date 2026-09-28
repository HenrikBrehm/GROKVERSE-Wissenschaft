---
id: EXP-096
status: vorbereitet
datum: 2026-09-28
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-096: Braucht die frühe Festlegung auch bei add 97 und mul 113 neu ausgewertete Gradienten? (Pilot, Exploration)

Zurück: [[LAB]] · [[FINDINGS]] (Antwort auf die offene Frage nach EXP-094; Regel 15c: Verallgemeinerung) · Vorgänger [[experiments/EXP-095-gradient-feedback/README|EXP-095]] · Bestätigung an add 113: [[confirm/R10_REGISTRATION_DRAFT|R10]] · Splitbau [[experiments/EXP-044-generalize-lockin/README|EXP-044]]

**Festgelegt vor jedem EXP-096-Lauf** (Sitzung 42, 2026-09-28, nach 18:00 Berlin, Fenster zu; `design.py`, `analyze.py` **ungetestet**. Selbsttest, Splits und Smoke erst ab 00:00 über den Wächter).

## Frage und Aufbau

Gilt der EXP-095-Befund (weniger Gradientenauswertungen bei gleichen 24 Adam-Schritten → schwächere Festlegung) über add 113 hinaus? Aufgaben **add 97** und **mul 113** (Gruppenbasis nach EXP-043), Splits nach EXP-044 (F und G mit disjunkten Zielmengen, unabhängige Schlüssel, ≈ 37 % geteilte Paare, gemeinsame Testmenge), eine Richtung F → G, Wechsel bei t = 24, danach 2000 Standardschritte; GPU. **Seeds 3560–3575** (frisch: Dateisuche 28.09. ohne Treffer). Zellen: n24 (Standard), g8 (Gradient alle 8 Schritte), g24 (nur Anfangsgradient). Reine F- und G-Läufe (2000 Schritte). 16 Seeds × 2 Aufgaben × 5 Läufe = **160 GPU-Läufe** (≈ 15–20 min mit 8 Workern).

## Vorhersagen und Lesarten (verbindlich, im Code)

π je Seed und Zelle wie EXP-044 (`pi_persistence.py`): L = log[P(F-Ziele)/P(G-Ziele)] der End-W_E-Gruppenleistung, π = (L(Wechsel) − L(nur G)) / (L(nur F) − L(nur G)); gültig: alle fünf Läufe über den gemeinsamen Lader ok (inkl. Gradientenplan), L(F) − L(G) ≥ 1. Je Aufgabe gepaart über Seeds (Bootstrap 10 000, rng 96): e₈ = π(n24) − π(g8), e₂₄ = π(n24) − π(g24).
- **„verallgemeinert“:** KI-Untergrenzen von e₈ und e₂₄ > 0.
- **„nicht verallgemeinert“:** KI-Obergrenzen von e₈ und e₂₄ < 0.03.
- sonst **„unklar“**; < 10 gültige Seeds → *nicht auswertbar*.
- **Beschreibend:** Zellmittel von π, Zielanteil f, Norm N, Ziel- und Restleistung T/R der Bewegung beim Wechsel (prüft den Post-hoc-Befund aus EXP-095 Nachtrag a prospektiv: g24 R ×≈1.5 bei T ≈ gleich; g8 T kleiner).
- **Erwartung:** „verallgemeinert“ bei add 97 (gleiche Gruppe, anderes p); bei mul 113 offen (EXP-044: π(50) 0.72, Festlegung dort langsamer).

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-095 (Zellen, Effektgrößen, T/R post hoc), EXP-044/074 (Splitbau, π-Niveaus bei add 97 / mul 113 an den Seeds 80–89). Keine Seeds aus diesen Blöcken. c8b entfällt (kein Kern der Frage; Zählervorbehalt).

## Befehle (ab 00:00, alles über den Wächter bzw. parallel_queue)

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-096-gradient-feedback-tasks/analyze.py --selftest
python lab/experiments/EXP-096-gradient-feedback-tasks/design.py
python lab/experiments/EXP-096-gradient-feedback-tasks/design.py --jobs > lab/experiments/EXP-096-gradient-feedback-tasks/jobs.txt
python lab/experiments/EXP-096-gradient-feedback-tasks/design.py --smoke > lab/experiments/EXP-096-gradient-feedback-tasks/smoke.txt
python lab/tools/parallel_queue.py lab/experiments/EXP-096-gradient-feedback-tasks/smoke.txt --workers 3
python lab/tools/parallel_queue.py lab/experiments/EXP-096-gradient-feedback-tasks/jobs.txt --workers 8
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-096-gradient-feedback-tasks/analyze.py
```
Vor dem Block: Code und Jobs committen (Festlegung). Nach dem Smoke einmal `analyze.py` laufen lassen und nur prüfen, dass die drei Smoke-Läufe ohne Laderfehler gefunden werden (Werte nicht lesen).

## Ergebnis

_noch nicht gerechnet_
