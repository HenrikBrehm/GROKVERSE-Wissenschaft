---
tags: [lab/live]
---
# LIVE: Laborsitzung 14

- **Sitzungsstart:** 2026-09-26 21:19 Berlin (19:19Z, vom Runner)
- **Deadline:** 2026-09-27 00:19 Berlin (22:19Z)
- **Zuletzt aktualisiert:** 21:53 Berlin (gemessen).
- **Run-Fenster:** zu. Heute Nacht Läufe erst ab 03:00 (Regel 18). Diese Sitzung: nur Code, Rechnung auf Dateien, Literatur.

## Gerade

Ich werte alte, schon gespeicherte Läufe neu aus (kein Training): Wie lange hält die erste Frequenzwahl nach einem Datenwechsel, gemessen als stetige Größe statt als Ja/Nein?

## Als Nächstes

Ab 03:00 (nächste Sitzung): Wächter-Abnahme, Tests (jetzt auch EXP-052-Selbsttest), Nachtprogramm.

## Verlauf dieser Sitzung

- 21:53 **Neues Maß für das Festhalten (Paket B):** Aus alten Wechselläufen ergibt sich eine glatte Kurve. Wechselt man nach 10 Schritten, bleiben 15 % der ersten Wahl übrig, nach 50 Schritten 72 %, ab 150 Schritten 100 %. Die Seeds streuen kaum. Mit Lernraten-Warmup verschiebt sich die Kurve so, wie es die aufsummierte Lernrate vorhersagt, und nicht nach der Schrittzahl (explorativ, 1–2 Seeds).
- 21:50 Kleine Unterschiede im Datensatz werden im Training stark verstärkt (explorativ).

- 21:49 Auswertung der späteren Bestätigung als Code fertig (nur mit eingefrorenem Plan startbar). Literatur: eine neue Arbeit zu kritischen Zeitfenstern bei Transformern, aber ohne Frequenzen oder Datenwahl.

- 21:47 Werkzeug für die Bestätigungs-Trainingsmengen geprüft: baut exakt die Konstruktion der Pilotversuche nach. Das Tor gegen verfrühtes Erzeugen ist jetzt strenger.

- 21:44 Bestätigungsblock technisch vorbereitet (Trainingsmengen nur mit eingefrorenem Plan). Planungswerkzeug nach Prüfung verbessert. Eigene Fehlannahme korrigiert: Der Vergleich M0c gegen M0 ist doch trennscharf (Simulation).

- 21:39 Neue Nebenfrage: Kann man aus den Gewichten erkennen, auf welcher Teilmenge ein Netz trainiert wurde? Das wird an EXP-052 mitgemessen. Notfallplan steht, falls die Grafikkarte die Abnahme nicht besteht.

- 21:38 Werkzeug für die Stichprobenplanung geschrieben: Nach der Nacht rechnet es aus, wie viele Seeds die Bestätigung braucht. Die Hauptgröße der Bestätigung fehlte in drei Nachtauswertungen.
- 21:34 Literatur zu Paket B (Lyle et al. 2025, Volltext): Ein vierter Versuchsarm (höhere Lernrate nach dem Wechsel) trennt das dritte Erklärungsmodell ab.

- 21:33 **Paket B vorbereitet ([[experiments/EXP-053-p3-overlap-design/README|EXP-053]]):** Für den Persistenztest muss der zweite Split einen festen Anteil Paare mit dem ersten teilen. Die naheliegende Bauweise hätte dem zweiten Split heimlich die Frequenzen des ersten mitgegeben. Eine faire Bauweise ist gefunden und nachgerechnet.
- 21:30 EXP-052 um zwei Fälle erweitert: nicht-abelsche Gruppe D₅₉ und gewöhnliche Addition ohne Modulo. Zweite Prüfung ohne Blocker.

- 21:27 **Neuer Test [[experiments/EXP-052-oos-mask-prediction/README|EXP-052]]:** Vorhersagen für 30 noch nicht gelaufene Zufallssplit-Läufe (add 97, mul 113, nicht-abelsche Gruppe D₅₉) aus den Splits berechnet und per Commit eingefroren. Unabhängige Prüfung: kein Blocker.

- 21:20 Stand gelesen: kein STOP, kein Prozess aktiv, Fenster zu (Wächter Exit 3). Nichts Pflichtiges offen.
