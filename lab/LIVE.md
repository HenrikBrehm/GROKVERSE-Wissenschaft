---
tags: [lab/live]
---
# LIVE: Laborsitzung 8

- **Sitzungsstart:** 2026-09-26 11:59 Berlin (09:59Z, vom Runner)
- **Deadline:** 2026-09-26 14:59 Berlin (12:59Z)
- **Zuletzt aktualisiert:** 12:17 Berlin
- **Run-Fenster:** offen (heute Ausnahme bis 18:00 Berlin).

## Gerade

Warteschlange `queue_s5.sh` läuft: **EXP-020** Seed 30, Datenwechsel-Läufe (F → G nach t Schritten). Die ersten beiden Läufe waren nach 6 bzw. 4 min fertig.
EXP-020 ist der Datenwechsel-Versuch: Ab wann hält der Transformer an seiner ersten Frequenzwahl fest? (Gegenstück zu EXP-032 im Spielzeugnetz.)

## Als Nächstes

Nach Seed 30 (~12:45): Warteschlange kurz anhalten, **EXP-033** laufen lassen (~70 min), danach EXP-020 fortsetzen.

## Verlauf dieser Sitzung

- 12:15 **EXP-033 vorab festgelegt:** Ist die „Festlegung in 5 Schritten“ nur ein Effekt von Adams großen ersten Vorzeichen-Schritten? Test: dieselbe frühe Phase mit reinem Gradientenabstieg bis zur gleichen Merkmalsgröße. Codex hat das erste Design zerlegt (u. a. Pseudoreplikation); neu gebaut mit 10 Splits und Vorzeichen-Arm.
- 12:03 Literatur: Adams erster Schritt ist ein reiner Vorzeichen-Schritt (Abuduweili & Liu 2024). Das erklärt, warum in EXP-032 alle Splits nach 5 Schritten exakt gleich weit gewachsen sind.
- 12:00 Stand gelesen, Wächter ok (im Fenster), `queue_s5.sh` gestartet (Log `lab/runner/logs/queue_s5.log`).
