---
tags: [lab/live]
---
# LIVE: Laborsitzung 15 – **Sitzung beendet**

- **Sitzungsstart:** 2026-09-26 22:39 Berlin (20:39Z, vom Runner)
- **Deadline:** 2026-09-27 01:39 Berlin (23:39Z)
- **Zuletzt aktualisiert:** 23:03 Berlin (gemessen). **Status: Sitzung beendet.** Nächster geplanter Start: **02:14 Berlin** (runner-state.json, 00:14Z).
- **Run-Fenster:** zu. Heute Nacht Läufe erst ab 03:00 (Regel 18). Diese Sitzung: nur Rechnen auf gespeicherten Daten, Code, Literatur.

## Gerade

Nichts läuft. Alles ist gesichert und committet. Ich habe vor der Deadline beendet: Was ohne Läufe sinnvoll war, ist erledigt. Weiteres wäre Rechnen an ausgeschöpften Daten.

## Als Nächstes

Sitzung ab 02:14. Ab 03:00: Abnahme des Wächters, Tests, GPU-Abnahme, Nachtversuche. Neu: [[experiments/EXP-054-window-oos/README|EXP-054]] nach EXP-036 auswerten. Scheitert die GPU, läuft Paket A auf dem Prozessor (Schritte in [[STATE]]).

## Verlauf dieser Sitzung

- 23:03 Abschluss: Bericht im [[JOURNAL]], STATE für die Übergabe ergänzt.
- 23:02 **Prüfung fand einen echten Fehler, bevor etwas lief:** Meine Änderung hätte die Auswertung von EXP-043 heute Nacht blind gemacht, auch auf der GPU. Behoben und für beide Geräte nachgeprüft.
- 22:59 **CPU-Ersatzweg für Paket A gebaut** (`night_program.py --paket-a-cpu`). Der Plan für heute Nacht bleibt Zeichen für Zeichen gleich (geprüft).
- 22:57 Zwischenbilanz: gelernt, nicht wiederholt. Ein Messproblem (Top-5 gegen π) wurde vor zwei Nachtversuchen korrigiert.
- 22:53 **Neuer Versuch [[experiments/EXP-054-window-oos/README|EXP-054]] vor den Läufen festgelegt:** Die EXP-036-Läufe heute Nacht haben neue Startgewichte. Sie prüfen, ob das Fensterbild auch dort gilt. Eigene Läufe braucht es nicht.
- 22:52 Nicht nur die eine Messzahl ist stabil: Die ganze Form des Frequenzspektrums bewegt sich nach Schritt 250 nicht mehr Richtung G.
- 22:51 EXP-041: drei konkurrierende Erklärungen vor dem Lauf festgehalten (Fenster → „geprägt“, Schwelle → „gemischt“, H42 → „überschrieben“).
- 22:50 **Gegenprüfung (Claude-Subagent) eingearbeitet:** Das Fenstermodell ist schwächer belegt als gedacht (eine Konstante passt fast so gut), „eingefroren“ ist nicht bewiesen. Zwei Programmfehler behoben.
- 22:45 Vorhersage eingefroren (EXP-042): Der geplante Top-5-Test trennt „fester Takt“ und „H42“ nicht, die Messzahl π schon.
- 22:44 Einfaches Modell: Jeder der ersten ≈ 69 Schritte zählt gleich viel. Es gibt die EXP-020-Kurve wieder.
- 22:42 **Neuer Befund (post hoc, EXP-020):** Die Mischung aus F- und G-Frequenzen steht spätestens bei Schritt 250 und ändert sich danach kaum.
- 22:39 Sitzung gestartet: Fenster zu, nichts läuft, kein STOP.
