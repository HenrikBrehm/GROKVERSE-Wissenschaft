---
tags: [lab/live]
---
# LIVE: Laborsitzung 8

- **Sitzungsstart:** 2026-09-26 11:59 Berlin (09:59Z, vom Runner)
- **Deadline:** 2026-09-26 14:59 Berlin (12:59Z)
- **Zuletzt aktualisiert:** 14:31 Berlin
- **Run-Fenster:** offen (heute Ausnahme bis 18:00 Berlin).

## Gerade

Letzte zwei Läufe der Sitzung: EXP-020 Seed 32, Wechsel bei t = 50 und 25 (bis ~14:41). Abschlussbericht ist geschrieben.

## Als Nächstes

Nächste Sitzung (16:59): `sh lab/experiments/queue_s8.sh`: Rest EXP-020 → EXP-035 → EXP-034.

## Verlauf dieser Sitzung

- 14:31 Warteschlange kontrolliert angehalten, Abschlussbericht im JOURNAL; noch zwei Einzelläufe bis ~14:41.
- 14:16 **EXP-020 Seed 31 wie Seed 30:** Festlegung zwischen Schritt 25 und 50, vor der Memorisierung (Train-Acc 11 %). 2 von 5 Seeds.
- 13:53 Seed 30: Die Festlegung fällt, bevor das Netz die Trainingsdaten gelernt hat (Train-Acc 10 % bei Schritt 50).
- 13:52 Sammel-Warteschlange `queue_s8.sh` für die nächsten Sitzungen geschrieben (ein Befehl).
- 13:51 Gegenprobe mit einem anderen Maß: Mit früher σ_3-Phase nutzt das Endnetz 4,6–4,7 von 5 Zielfrequenzen, ohne sie nur 0,4, egal mit welchem Optimierer. Der Befund ist robust.
- 13:50 EXP-020 Seed 30: In den Mischzuständen tauchen zwei fremde Frequenzen (34, 39) auf. Herkunft offen, notiert.
- 13:49 Beobachtung in den EXP-033-Daten: Die frühe Neigung wird vor allem um die Generalisierung verstärkt, nicht während der Memorisierung. Als Vorhersage für EXP-034 festgelegt.
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
