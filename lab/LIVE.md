---
tags: [lab/live]
---
# LIVE: Laborsitzung 8

- **Sitzungsstart:** 2026-09-26 11:59 Berlin (09:59Z, vom Runner)
- **Deadline:** 2026-09-26 14:59 Berlin (12:59Z)
- **Zuletzt aktualisiert:** 13:47 Berlin
- **Run-Fenster:** offen (heute Ausnahme bis 18:00 Berlin).

## Gerade

EXP-020 läuft wieder (Transformer-Datenwechsel, Seed 30 fast fertig, dann Seeds 31–34). Nebenher: Dokumentation, danach Denkarbeit zu EXP-034.

## Als Nächstes

Nächste Sitzungen: EXP-020 fertig, dann EXP-035 (Warmup, Transformer) und EXP-034 (GD in beiden Phasen).

## Verlauf dieser Sitzung

- 13:47 **EXP-035 vorab festgelegt:** Wenn der Transformer langsamer anläuft (Lernraten-Warmup), legt er sich dann später fest? Codex fand 5 Schwachstellen, alle behoben, bevor ein Lauf startete.
- 13:38 **EXP-020, erster Seed (vorläufig):** Der Transformer legt sich nach 25–50 Trainingsschritten auf seine Frequenzen fest. Wer 150 Schritte F gesehen hat, behält F exakt, auch nach 2000 Schritten nur mit G. Noch 4 Seeds.
- 13:33 Vorhersage für EXP-034 festgelegt: Der Split 69 sollte sich am schwächsten festlegen (lineare Rechnung). Auswertung von EXP-034 synthetisch getestet (5/5).
- 13:31 **EXP-034 vorab festgelegt** und nach Codex umgebaut: Hält die Festlegung auch, wenn *beide* Phasen ohne AdamW laufen? Und schon bei der 5-Schritte-Amplitude? Frische Splits 60–69.
- 13:21 Codex greift die Schlussfolgerung an → eingeschränkt: Belegt ist nur, dass AdamW in der *frühen* Phase nicht nötig ist; die späte Phase lief immer mit AdamW.
- 13:18 **EXP-033 Ergebnis:** Die frühe Festlegung ist **kein AdamW-Artefakt der ersten Phase**. Reiner Gradientenabstieg bis zur gleichen Merkmalsgröße legt das Netz genauso fest (10/10 Splits), sogar etwas stärker, wie die lineare Rechnung vorhergesagt hatte (10/10).
- 13:17 EXP-020 fortgesetzt.
- 12:30 EXP-033: Treffgenauigkeit der Amplitude verbessert (Nachtrag c, bevor ein Ergebnis angesehen wurde); Split 10 fertig, 9 Splits folgen (~45 min).
- 12:20 EXP-033 Pilot: GD-Lernrate 3 nach vorab festgelegter Regel gewählt.

- 12:18 EXP-020-Warteschlange angehalten, EXP-033 wartet auf das Ende des laufenden Laufs.
- 12:17 **Rechnung ohne Training:** Beim reinen Gradientenabstieg wachsen zuerst die Richtungen, die schon auf den Zielfrequenzen liegen (10/10 Splits). Daraus die Vorhersage: GD neigt sich am Umschaltschritt stärker zu F als AdamW.

- 12:14 **EXP-033 vorab festgelegt:** Ist die „Festlegung in 5 Schritten“ nur ein Effekt von Adams großen ersten Vorzeichen-Schritten? Test: dieselbe frühe Phase mit reinem Gradientenabstieg bis zur gleichen Merkmalsgröße. Codex hat das erste Design zerlegt (u. a. Pseudoreplikation); neu gebaut mit 10 Splits und Vorzeichen-Arm.
- 12:03 Literatur: Adams erster Schritt ist ein reiner Vorzeichen-Schritt (Abuduweili & Liu 2024). Das erklärt, warum in EXP-032 alle Splits nach 5 Schritten exakt gleich weit gewachsen sind.
- 12:00 Stand gelesen, Wächter ok (im Fenster), `queue_s5.sh` gestartet (Log `lab/runner/logs/queue_s5.log`).
