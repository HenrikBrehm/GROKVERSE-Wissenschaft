---
tags: [lab/live]
---
# LIVE: Laborsitzung 8

- **Sitzungsstart:** 2026-09-26 11:59 Berlin (09:59Z, vom Runner)
- **Deadline:** 2026-09-26 14:59 Berlin (12:59Z)
- **Zuletzt aktualisiert:** 12:30 Berlin
- **Run-Fenster:** offen (heute Ausnahme bis 18:00 Berlin).

## Gerade

**EXP-033 läuft** (seit 12:20): Pilot fertig, GD-Lernrate 3 gewählt (76 Schritte bis zur Ziel-Amplitude). Jetzt 10 Splits × (AdamW, GD, Vorzeichen) + 5 AdamW-behalten.
EXP-020 ist pausiert (Seed 30: 4 von 8 Läufen fertig).

## Als Nächstes

EXP-033 beobachten (~70 min), auswerten; danach `queue_s5.sh` fortsetzen.

## Verlauf dieser Sitzung

- 12:30 EXP-033: Treffgenauigkeit der Amplitude verbessert (Nachtrag c, bevor ein Ergebnis angesehen wurde); Split 10 fertig, 9 Splits folgen (~45 min).
- 12:20 EXP-033 Pilot: GD-Lernrate 3 nach vorab festgelegter Regel gewählt.

- 12:18 EXP-020-Warteschlange angehalten, EXP-033 wartet auf das Ende des laufenden Laufs.
- 12:17 **Rechnung ohne Training:** Beim reinen Gradientenabstieg wachsen zuerst die Richtungen, die schon auf den Zielfrequenzen liegen (10/10 Splits). Daraus die Vorhersage: GD neigt sich am Umschaltschritt stärker zu F als AdamW.

- 12:14 **EXP-033 vorab festgelegt:** Ist die „Festlegung in 5 Schritten“ nur ein Effekt von Adams großen ersten Vorzeichen-Schritten? Test: dieselbe frühe Phase mit reinem Gradientenabstieg bis zur gleichen Merkmalsgröße. Codex hat das erste Design zerlegt (u. a. Pseudoreplikation); neu gebaut mit 10 Splits und Vorzeichen-Arm.
- 12:03 Literatur: Adams erster Schritt ist ein reiner Vorzeichen-Schritt (Abuduweili & Liu 2024). Das erklärt, warum in EXP-032 alle Splits nach 5 Schritten exakt gleich weit gewachsen sind.
- 12:00 Stand gelesen, Wächter ok (im Fenster), `queue_s5.sh` gestartet (Log `lab/runner/logs/queue_s5.log`).
