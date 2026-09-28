---
id: EXP-093
status: vorbereitet
datum: 2026-09-28
tags: [exp/vorbereitet, neu/kandidat]
---
# EXP-093: Bis zu welcher Lernrate gilt die Momentum-Verzögerungs-Uhr? (Pilot, Exploration)

Zurück: [[LAB]] · [[FINDINGS]] (K5, offene Mechanismusfrage) · [[NOVEL_DIRECTIONS]] N48 · Vorgänger [[experiments/EXP-092-momentum-lag-clock/README|EXP-092]] · [[confirm/R9_REGISTRATION_DRAFT|R9]]

**Festgelegt vor jedem EXP-093-Lauf** (Sitzung 41, 2026-09-28, 14:29 Berlin gemessen; `design.py`, `analyze.py`, Selbsttest grün über den Wächter).

## Warum dieser Versuch (Bezug, Regel 15b)

EXP-092 stützte die Lag-Uhr Λ_eff = c·t − c·lag(β₁, t) in vier von fünf neuen Zellen (Abweichung ≤ 0.015), verfehlte aber c = 4, t = 6 deutlich (−0.107 [−0.16, −0.06]). Bevor K5 um die Lag-Uhr erweitert oder eine Bestätigung (R10) entworfen wird, muss ihr **Gültigkeitsbereich** bekannt sein. Kein Nachtrag zu EXP-092, sondern ein eigener Versuch mit frischen Seeds; c = 4 wird dabei repliziert.

## Aufbau

Wie EXP-092 (add 113, ω = 0-Splitpaare, Wechsel A → B und B → A, danach 2000 Standardschritte, π gegen reine Läufe; GPU). **Seeds 3420–3435** (frisch: Dateisuche 28.09. ohne Treffer). Eichung n20/n25/n30 (Standard); **Λ = 24 fest**, Lernratenfaktor c in den Schritten 1 … t: c2 (t = 12), c3 (8), c4 (6), c6 (4), c8 (3). 18 Läufe je Seed, **288 GPU-Läufe** (6 Worker neben dem Repro-Paket, erwartet ≈ 55 min).

Vorhergesagte relative Lage (Lag-Uhr, geeicht auf n25 = 0, n30 = 1): c2 −0.57, c3 −0.64, c4 −0.62, c6 −0.49, c8 −0.31 (n20 −0.95). Die Lag-Uhr sagt also für c2–c8 fast gleiche π, bei c8 sogar etwas höher (kürzeres Momentum-Fenster in Λ, weil nur 3 Schritte).

## Lesarten (verbindlich, im Code)

Je Zelle Residuum r_c = π(c) − Lag-Vorhersage (je Seed über n25/n30 geeicht), Bootstrap-KI. *trifft*: KI in ±0.03; *verfehlt*: KI-Obergrenze < −0.03 (oder Untergrenze > +0.03); sonst *offen*. Lesart über c2 … c8: **„Grenze zwischen c_a und c_b“** (erst nur *trifft*, dann nur *verfehlt*), **„keine Grenze bis c = 8“**, **„Uhr verfehlt schon bei c = 2“**, sonst **„gemischt“**. < 10 gültige Seeds → *nicht auswertbar*.
**Erwartung vor dem Lauf** (aus R9: c = 2 lag post hoc auf der Kurve; EXP-092: c = 4 darunter): Grenze zwischen c2 und c4, Residuum wachsend mit c. **Zwei Post-hoc-Kandidaten für den Fehlschlag** (nicht getrennt prüfbar mit diesem Aufbau, nur beschreibend): (a) Adams erste Schritte sind fast vorzeichenartig und unselektiv, ihr Anteil an Λ wächst wie ≈ 2/t → Residuum folgt 2/t; (b) Überschießen großer Schritte → Residuum folgt c. Hier sind c und 2/t fast gleich geordnet; ein trennender Test braucht eine Trainer-Option (z. B. erste k Schritte mit lr × 1, dann × c), die erst nach Prüfung gebaut wird.

## Bereits gesehene Daten und davon beeinflusste Entscheidungen

EXP-092 (Wahl der Frage, Λ = 24 wie dort c4, Schwelle ±0.03 wie dort), R9 (c = 2 post hoc auf der Kurve), EXP-091 (c = 2 stabil). Keine Seeds aus diesen Blöcken.

## Befehle

```
python lab/tools/guarded_run.py -- python lab/experiments/EXP-093-lag-clock-range/analyze.py --selftest
python lab/tools/parallel_queue.py lab/experiments/EXP-093-lag-clock-range/smoke.txt --workers 3
python lab/tools/parallel_queue.py lab/experiments/EXP-093-lag-clock-range/jobs.txt --workers 6
PYTHONIOENCODING=utf-8 python lab/tools/guarded_run.py -- python lab/experiments/EXP-093-lag-clock-range/analyze.py
```

## Ergebnis

(noch nicht gelaufen)
