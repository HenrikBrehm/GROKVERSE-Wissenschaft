---
tags: [lab/live]
---
# LIVE: Laborsitzung 8

- **Sitzungsstart:** 2026-09-26 11:59 Berlin (09:59Z, vom Runner)
- **Deadline:** 2026-09-26 14:59 Berlin (12:59Z)
- **Zuletzt aktualisiert:** 12:18 Berlin
- **Run-Fenster:** offen (heute Ausnahme bis 18:00 Berlin).

## Gerade

EXP-020 Seed 30 (Wechsel bei t = 50) läuft zu Ende. Die Warteschlange `queue_s5.sh` ist dafür angehalten (Stand 3 von 8 Seed-30-Läufen fertig).
Danach startet automatisch **EXP-033** (`EXP-033/queue.sh`, Log `lab/runner/logs/queue_exp033.log`): zuerst 5 Pilotläufe zur GD-Lernrate, dann 35 Läufe.

## Als Nächstes

EXP-033 beobachten (~70 min), auswerten; danach `queue_s5.sh` fortsetzen.

## Verlauf dieser Sitzung

- 12:18 EXP-020-Warteschlange angehalten, EXP-033 wartet auf das Ende des laufenden Laufs.
- 12:17 **Rechnung ohne Training:** Beim reinen Gradientenabstieg wachsen zuerst die Richtungen, die schon auf den Zielfrequenzen liegen (10/10 Splits). Daraus die Vorhersage: GD neigt sich am Umschaltschritt stärker zu F als AdamW.

- 12:14 **EXP-033 vorab festgelegt:** Ist die „Festlegung in 5 Schritten“ nur ein Effekt von Adams großen ersten Vorzeichen-Schritten? Test: dieselbe frühe Phase mit reinem Gradientenabstieg bis zur gleichen Merkmalsgröße. Codex hat das erste Design zerlegt (u. a. Pseudoreplikation); neu gebaut mit 10 Splits und Vorzeichen-Arm.
- 12:03 Literatur: Adams erster Schritt ist ein reiner Vorzeichen-Schritt (Abuduweili & Liu 2024). Das erklärt, warum in EXP-032 alle Splits nach 5 Schritten exakt gleich weit gewachsen sind.
- 12:00 Stand gelesen, Wächter ok (im Fenster), `queue_s5.sh` gestartet (Log `lab/runner/logs/queue_s5.log`).
