---
tags: [lab/live]
---
# LIVE: Laborsitzung 71

- **Sitzungsstart:** 2026-10-01 15:19 Berlin (13:19Z, vom Runner)
- **Deadline:** 2026-10-01 18:19 Berlin (16:19Z)
- **Zuletzt aktualisiert:** 17:41

## Gerade

- **Sitzung 71 beendet.** Pause nach der LeDoux-Linie (Regel 23) ist vorgemerkt; es rechnen nur noch EXP-144 (3 Läufe) und die Reste des EXP-143-Nebenarms beim GPU-Dienst.
- Nächster geplanter Start: 01.10. 18:54 Berlin (wertet EXP-144 aus, danach „Pause aktiv“).

## Als Nächstes

1. EXP-144 auswerten (nächste Sitzung).
2. Danach Pause (Regel 23).

## Verlauf dieser Sitzung
- 17:41 EXP-144, erster Lauf fertig: Das breitere Netz lernt 86 % der Trainingsaufgaben (kleines: 36 %), aber nicht die Regel. Sitzung gesichert.
- 17:26 EXP-143 fertig: auch nach 512 Durchgängen kein Lernen der Regel → keine Aussage zu Menge gegen Reihenfolge; unabhängig nachgerechnet. Leitfragen zur LeDoux-Linie für dich angelegt ([[paper/erklaerung/LEITFRAGEN_LEDOUX]]).
- 16:56 EXP-143 (250 000 Schritte) ausgewertet: keine Aussage zu Menge gegen Reihenfolge, weil das kleine Netz nichts lernt. Nachfolger EXP-144 mit 4-mal breiterem Netz geprüft, getestet und eingereicht.
- 16:30 Paper: R15-Text nach unabhängiger Prüfung korrigiert (u. a. ein Fehler beim Zusammenbau des Manuskripts behoben).
- 16:27 R15 unabhängig nachgerechnet (alle Werte stimmen); FINDINGS, Übersicht und Paper ergänzt.
- 16:25 **R15 fertig: beide Lagen bestätigt** (Zahlen bis 400 mit 14 000 Paaren und bis 306 mit 9425 Paaren). Gezielt: 10/10 lernen. Zufall gleicher Größe: 0/10.
- 15:54 EXP-143 gestartet (15:48): drei Läufe auf der Grafikkarte, schnell und stabil.
- 15:34 **Vorläufe EXP-143 über 3 Seeds:** In allen drei prägt die gezielte Auswahl ihre 5 Ziele, und die sortierte Reihenfolge hebt Frequenz 101 auf Platz 1 (unabhängig nachgerechnet). Ob die Reihenfolge ein ganzes Muster ihres Sortierschlüssels einprägt (Oberwellen), bleibt unklar – das Signal ist zu schwach. Gromov-Zitat im Volltext wörtlich bestätigt.
- 15:24 Seed 14301 wiederholt beide frühen Effekte: Die gezielte Auswahl prägt ihre 5 Ziele, die sortierte Reihenfolge hebt k = 101 auf Rang 1. Oberwellen-Test vorab im JOURNAL festgelegt.
- 15:21 Start; STATE gelesen, kein STOP, Fenster offen; Dienst läuft (R15 20/30).
