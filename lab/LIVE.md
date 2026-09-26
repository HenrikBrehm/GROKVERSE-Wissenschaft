---
tags: [lab/live]
---
# LIVE: Laborsitzung 17

- **Sitzungsstart:** 2026-09-27 00:19 Berlin (22:19Z, vom Runner)
- **Deadline:** 2026-09-27 03:19 Berlin (01:19Z)
- **Zuletzt aktualisiert:** 00:37 Berlin (gemessen)
- **Run-Fenster:** zu. Läufe erst ab 03:00 (Regel 18). Diese Sitzung hat also nur ~10 min Fenster am Ende.

## Gerade

Warten bis 03:00. Die Vorbereitung ist vollständig, alles ist committet. Vor 03:00 darf nichts laufen, und weitere Planung ohne die Nachtdaten wäre nur Beschäftigung.

## Als Nächstes

03:00–03:09: Wächter-Abnahme (harmloser 60-s-Job + STOP) und die Tests über den Wächter. Das Nachtprogramm selbst startet die nächste Sitzung
(beginnt direkt nach dem Ende dieser Sitzung, beim nächsten Runner-Takt), weil ein Start um 03:05 an der Deadline 03:19 abgebrochen würde.

## Verlauf dieser Sitzung

- 00:35 Zwei Schwachstellen im Nachtprogramm behoben (noch ungetestet, zweite Prüfung ohne Befund): Ein Abbruch an der Sitzungsgrenze gilt nicht mehr als Fehlschlag, und die GPU-Abnahme wiederholt bereits bestandene Stufen nicht.
- 00:28 Vorab-Prüfung des Nachtcodes: nichts, was abstürzt; drei Stellen, die Fensterzeit kosten würden.
- 00:24 Literatur-Nachsuche fertig: nichts gefunden, das unsere Kernfragen schon beantwortet. Neue Idee N31 (Reihenfolge der Daten gegen ihre Zusammensetzung) notiert, nicht geplant.
- 00:22 Geprüft: Die kurze STOP-Probe um 03:00 kann den Runner nicht abschalten (während einer Sitzung feuert kein Tick).
- 00:19 Sitzung gestartet: Fenster zu, nichts läuft, kein STOP.
