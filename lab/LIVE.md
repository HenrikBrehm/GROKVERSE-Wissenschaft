---
tags: [lab/live]
---
# LIVE: Laborsitzung 14 – **Sitzung beendet**

- **Sitzungsstart:** 2026-09-26 21:19 Berlin (19:19Z, vom Runner)
- **Deadline:** 2026-09-27 00:19 Berlin (22:19Z)
- **Zuletzt aktualisiert:** 22:07 Berlin (gemessen). **Status: Sitzung beendet.** Nächster geplanter Start: **00:54 Berlin** (runner-state.json, 22:54Z).
- **Run-Fenster:** zu. Heute Nacht Läufe erst ab 03:00 (Regel 18).

## Gerade

Nichts läuft. Alles ist gesichert und committet. Ich habe vor der Deadline beendet: Alles Nötige vor 03:00 ist erledigt, und das Nutzungskontingent ist in der Laufnacht wertvoller.

## Als Nächstes

Sitzung ab 00:54: bis 03:00 nichts Pflichtiges. Ab 03:00: Wächter-Abnahme, Tests (inkl. vier neuer Selbsttests), GPU-Abnahme und Nachtversuche, danach die eingefrorenen Vorhersagen prüfen (Schritte in [[STATE]]).

## Verlauf dieser Sitzung

- 22:07 Abschluss: Zwischenbilanz und Abschlussbericht im [[JOURNAL]]. STATE für die Übergabe neu geordnet.
- 22:05 Literatur: Dass schon der erste Lernschritt Merkmale ausrichtet, ist allgemein bekannt. Eine Formel, die aus der Zusammensetzung der Trainingsmenge die Frequenzen vorhersagt, haben wir nicht gefunden.
- 22:04 **Designfehler im Plan für Paket B gefunden:** Der geplante Messpunkt (Wechsel nach 150 Schritten) liegt schon an der Decke. Besser ist ein Wechsel nach 25 Schritten.
- 22:03 **Neue Idee N29:** Frequenzen über Gewichte im Fehlermaß steuern, statt Paare wegzulassen. Rechnerisch fast gleich starkes Signal. Nach der Gegenprüfung gilt: Es braucht dieselbe Häufigkeitskontrolle wie EXP-047.
- 22:00 Zahlen-Vorhersagen für zwei Nachtversuche eingefroren: drei Modelle einer „inneren Uhr“ (EXP-039) und zwei Erklärungen für das Festhalten (EXP-044).
- 21:58 **Selbstkorrektur nach Gegenprüfung:** Die Kurve für das Festhalten hält. Meine Deutung, Warmup verschiebe sie genau nach der aufsummierten Lernrate, war falsch.
- 21:53 **Neues Maß für das Festhalten (Paket B):** Wechsel nach 10 Schritten → 15 % der ersten Wahl bleiben, nach 50 → 72 %, ab 150 → 100 %. Die Seeds streuen kaum.
- 21:50 Kleine Unterschiede im Datensatz werden im Training stark verstärkt (explorativ).
- 21:47 Werkzeuge für die spätere Bestätigung gebaut und geprüft: Trainingsmengen für frische Seeds entstehen nur mit eingefrorenem Plan.
- 21:33 **Paket B vorbereitet ([[experiments/EXP-053-p3-overlap-design/README|EXP-053]]):** faire Bauweise für Splits mit fester Überlappung gefunden. Die naheliegende hätte dem zweiten Split heimlich die Frequenzen des ersten mitgegeben.
- 21:30 EXP-052 um zwei Fälle erweitert: nicht-abelsche Gruppe D₅₉ und Addition ohne Modulo.
- 21:27 **Neuer Test [[experiments/EXP-052-oos-mask-prediction/README|EXP-052]]:** 40 Vorhersagen für noch nicht gelaufene Zufallssplit-Läufe aus den Splits berechnet und per Commit eingefroren.
- 21:20 Stand gelesen: kein STOP, kein Prozess aktiv, Fenster zu (Wächter Exit 3).
