---
id: EXP-098
status: vorbereitet
datum: 2026-09-28
tags: [exp/vorbereitet]
---
# EXP-098: Tickt die Festlegung auch bei add 97 und mul 113 in Λ, wenn Adams Fenster in Λ gemessen werden? (Pilot, Exploration)

Zurück: [[LAB]] · [[FINDINGS]] (Kernaussage **K5**, bisher nur add 113; Regel 15c: Verallgemeinerung zuerst) · Bestätigung [[confirm/R9_REGISTRATION_DRAFT|R9]] · Schwesterversuch [[experiments/EXP-096-gradient-feedback-tasks/README|EXP-096]] · Splits wie [[experiments/EXP-044-generalize-lockin/README|EXP-044]]

**Festgelegt vor jedem EXP-098-Lauf** (Sitzung 43, 2026-09-28, Fenster zu; `design.py`, `analyze.py`; ungetestet bis 29.09. 00:00). Kein neuer Trainer-Code: `--lr-scale` und `--pre-switch-betas` gibt es seit Sitzung 40.

## Frage und Bezug

K5 (R9, add 113): Bei gleichem Λ = 25 legen 100 Schritte mit lr × 0.25 stärker fest als 25 Standardschritte (+0.161). Werden Adams Fenster vor dem Wechsel in Λ angeglichen (β′ = 1 − c(1 − β) = 0.975/0.995), verschwindet der Unterschied (+0.015, Äquivalenz ±0.1). Gilt das auch bei add 97 und mul 113? Wenn ja, ist K5 keine Eigenheit von add 113. Wenn nicht, ist das genauso ein Befund („gilt nur bei add 113“).

## Aufbau

Splits nach EXP-044 (je Aufgabe und Seed: gemeinsame Testmenge, F und G mit disjunkten Zielmengen, unabhängige Schlüssel, ≈ 37 % geteilte Paare), eine Richtung F → G. **Seeds 3660–3675** (frisch; Dateisuche 28.09. Sitzung 43 ohne Treffer; Spanne 15, also keine Stromüberschneidung s ↔ s + 16 wie bei R11). Je Aufgabe und Seed 5 Läufe: rein F, rein G, **n25** (Wechsel nach 25 Standardschritten), **l100** (Wechsel nach 100 Schritten mit lr × 0.25, Standard-β), **l100b** (wie l100, vor dem Wechsel β′ = 0.975/0.995). Danach je 2000 Standardschritte. **160 GPU-Läufe** (≈ 25 min mit 8 Workern).

## Vorhersagen und Lesarten (verbindlich, im Code)

π wie EXP-044 (Log-Verhältnis der W_E-Gruppenleistung am Ende gegen die reinen Läufe). e₁ = π(l100) − π(l100b), d₁ = π(l100b) − π(n25); gepaarte Bootstrap-KIs über Seeds (10 000, rng 98). Je Aufgabe, in dieser Reihenfolge:
- **„verallgemeinert“:** KI-Untergrenze von e₁ > 0 und KI von d₁ innerhalb ±0.1.
- **„nur Richtung“:** KI-Untergrenze von e₁ > 0, d₁ nicht innerhalb ±0.1.
- **„nicht verallgemeinert“:** KI-Obergrenze von e₁ < 0.03.
- sonst **„unklar“**; < 10 gültige Seeds → *nicht auswertbar* (gültig: alle 5 Läufe ok, L(F) − L(G) ≥ 1).
- **Beschreibend:** Zellmittel von π, Zielanteil f und Norm N der W_E-Bewegung beim Wechsel.
- **Erwartung (vorab):** „verallgemeinert“ bei beiden Aufgaben. Der Mechanismus (Adams β₁-Verzögerung macht die frühe Bewegung unselektiver) hängt nicht an der Aufgabe. Bei mul 113 legt das Netz bis t = 25 schwächer fest (EXP-044: π(25) 0.22). Der Unterschied e₁ könnte dort kleiner sein.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

R9 und die Piloten EXP-089/090 (Zellen, β′-Regel, Äquivalenzgrenze ±0.1), EXP-044 (Splitkonstruktion, π(25)). Die Seeds sind neu.

## Befehle (ab 00:00; mit dem eingefrorenen Trainer, also vor dem EXP-097-Patch oder danach, aber nicht mitten im Block)

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-098-window-clock-tasks/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-098-window-clock-tasks/smoke.txt --workers 3
python lab/tools/guarded_run.py -- python lab/experiments/EXP-098-window-clock-tasks/analyze.py --smoke-check
python lab/tools/parallel_queue.py lab/experiments/EXP-098-window-clock-tasks/jobs.txt --workers 8
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-098-window-clock-tasks/analyze.py
```
Splits, `jobs.txt` und `smoke.txt` sind schon erzeugt (`design.py`, reines numpy, Sitzung 43).

## Ergebnis

*(noch nicht ausgeführt)*
