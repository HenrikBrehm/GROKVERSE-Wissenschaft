---
tags: [lab/live]
---
# LIVE: Laborsitzung 10

- **Sitzungsstart:** 2026-09-26 17:29 Berlin (15:29Z, vom Runner)
- **Deadline:** 2026-09-26 20:29 Berlin (18:29Z)
- **Zuletzt aktualisiert:** 18:48 Berlin
- **Run-Fenster:** offen bis 18:00 (heutige Ausnahme), danach erst wieder ab 00:00.

## Gerade

Denkarbeit (Fenster zu): Befunde aus gespeicherten Läufen, Vorhersagen für die Nacht festlegen.

## Als Nächstes

Ab 00:00 (nächste Sitzung, Start 22:29) läuft `queue_s10.sh`: EXP-035 Rest → EXP-038 → EXP-036 → EXP-039 → EXP-040 → EXP-034 → EXP-042 → EXP-041.

## Verlauf dieser Sitzung

- 18:48 Codex hat das Trainingsprogramm auf Fehler geprüft (4 Funde, u. a. konnten alte Dateien fälschlich als fertig gelten). 4 Reparaturen eingebaut; getestet wird das in der Nacht automatisch vor den Läufen.
- 18:38 **EXP-042 vorbereitet:** Lernt das Netz nach dem Datenwechsel eher um, wenn der neue Datensatz stärker in Richtung seiner eigenen Frequenzen zieht? Codex: Das trennt nicht sauber zwischen „stärkerer Zug“ und „weniger gemeinsame Daten“, Aussage deshalb eingeengt. Alle neuen Versuche stehen in der Nacht-Queue.
- 18:27 **Korrektur:** Codex hat den Befund von 18:21 zerlegt: Die „wenigen Endzustände“ entstehen vor allem durch die reinen F-/G-Läufe, die Übereinstimmungen habe ich im Nachhinein herausgesucht, und der Vergleich war schief gebaut. Vorhersage für Seed 32 zurückgezogen; bleibt nur eine unkalibrierte Beobachtung.
- 18:21 **Neuer Befund aus alten Daten:** Pro Seed gibt es nur wenige verschiedene Endzustände, und ganz verschiedene Eingriffe landen teils *exakt* im selben Zustand, vor allem, wenn gleich viel Lernrate aufsummiert war. Für Seed 32 (noch ohne Warmup-Läufe) als Vorhersage festgelegt.
- 18:18 Rechnung: Die Bewegung von W_E wächst unter Adam fast genau mit der aufsummierten Lernrate (0.11 pro Einheit). Daraus eine Zahl-Vorhersage für EXP-040.
- 18:14 **Neuer Versuch EXP-041 vorbereitet:** Kann man mit 150 Schritten auf besonderen Daten festlegen, welche Frequenzen ein danach ganz normal trainiertes Netz benutzt? Und klappt das auch umgekehrt? Literatur: Eine Arbeit von 2026 zeigt, dass schon die *Reihenfolge* der Daten die Frequenz bestimmt, aber ohne Datenwechsel. Codex fand im ersten Entwurf ein zirkuläres Maß, repariert.
- 18:01 **Neue Idee EXP-040:** Vielleicht fällt die Wahl, sobald das Lernsignal so groß ist wie die zufälligen Startwerte. Test: Startwerte halb so groß → Festlegung früher, doppelt so groß → später. Codex fand 3 Schwächen, eingebaut. Literatur: nächstverwandte Arbeit (He et al. 2026, „Frequenz-Lotterie“) sagt nichts über den Zeitpunkt.
- 17:53 **Neuer Versuch EXP-039 „Lernraten-Uhr“ vorbereitet:** Wenn die Festlegung an der aufsummierten Lernrate hängt, muss doppelte Lernrate sie auf 12–25 Schritte vorziehen und halbe auf 50–100 verschieben. Codex fand 3 Schwächen im Design, eingebaut. Testlauf ok. Läuft in der Nacht nach EXP-036.
- 17:51 EXP-035 Seed 31: Auch hier legt sich das Netz mit Warmup später fest (bei t = 50 noch auf der G-Seite, ohne Warmup schon F).
- 17:41 Codex hat die neue Prüfung angegriffen (4 Punkte, alle berechtigt). Eingebaut: Beide Datensätze müssen die Frequenz wirklich wachsen lassen, und ein zusätzlicher Test prüft, ob „beide“ mehr erklärt als „einer allein“. Die Protokoll-Option wurde im Fenster getestet und funktioniert.
- 17:35 **Vorhersage für EXP-036 jetzt sauber festgelegt:** Sind die „Konfliktfrequenzen“ die, die beide Datensätze in den ersten 20 Schritten anschieben? Dafür speichert das Training jetzt auch sehr frühe Spektren.
- 17:36 EXP-035 Seed 30 fertig: Mit Warmup legt sich das Netz erst zwischen Schritt 100 und 150 fest (ohne Warmup: 25–50). Ein Seed, noch kein Urteil.
- 17:30 Stand gelesen; EXP-035 läuft (Seed 30: 5 von 7 Läufen fertig).
