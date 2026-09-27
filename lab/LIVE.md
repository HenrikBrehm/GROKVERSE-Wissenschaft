---
tags: [lab/live]
---
# LIVE: Laborsitzung 23

- **Sitzungsstart:** 2026-09-27 09:39 Berlin (07:39Z, vom Runner)
- **Deadline:** 2026-09-27 12:39 Berlin (10:39Z)
- **Zuletzt aktualisiert:** 11:11 Berlin (gemessen)
- **Run-Fenster:** offen (00:00-13:00), bindend ist die Sitzungsdeadline.

## Gerade

N29b laeuft (etwa 25/120). Danach: auswerten, dann EXP-069 (Muster oder Werte der Attention?) als kurzer Pilot, falls die Zeit reicht.

## Als Naechstes

N29b-Auswertung (ohne Codex, Guthaben leer), EXP-069, Abschlussbericht bis 12:29.

## Verlauf dieser Sitzung

- 11:11 EXP-069 vorab festgelegt; Neuheitssuche zu N32 (Attention haelt die fruehe Wahl): nicht gefunden, vorlaeufig.
- 11:09 EXP-039 ausgewertet: unklar (Lernraten-Uhr passt besser als Schrittuhr, aber nicht in jedem Seed). EXP-040-Auswertungsfehler vor jedem Lauf behoben.
- 11:06 N29b eingefroren und gestartet (Codex hat kein Guthaben mehr; eigene Pruefung).
- 10:58 **EXP-067 (Pilot, 10 Seeds):** Ueberraschung: Setzt man beim Wechsel nur die Attention zurueck, lernt das Netz die neuen Frequenzen doch und rechnet mit ihnen. MLP- oder Ausgabe-Reset tun das nicht.
- 10:54 Vorbereitung D59: Trainer kann jetzt Modelle speichern (alte Laeufe unberuehrt).
- 10:52 EXP-067 gestartet (Trainer-Option neu, Tests gruen, Codex ok, alter und neuer Code bitgleich).
- 10:49 FINDINGS: P2e im engen Wortlaut nach Codex.
- 10:44 **P2e BESTAETIGT:** Der P2d-Befund gilt auch bei Multiplikation mod 113 (0.29) und Addition mod 97 (0.29), je 20/20 frische Seeds. Deutung eng: Empfindlichkeit entlang amplitudenstarker Richtungen.
- 10:24 **EXP-068 (Exploration):** Bei gleich viel entfernter Energie reagiert das Netz auf die dominante Frequenzmenge NICHT staerker. Die gemessene Funktion folgt der Energie; das ist jetzt als Grenze in FINDINGS vermerkt.
- 10:21 FINDINGS: N29 als K4c im engen Wortlaut nach Codex eingetragen.
- 10:17 **N29 bestaetigt:** zwischen 25 und 50 Schritten kippt, auf welche Frequenzen das Netz am Ende angewiesen ist. Nachtraeglich: Die Energie in W_E zeigt dieselbe Richtung.
- 10:16 N29-Block fertig (80/80); P2e zweite Warteschlange gestartet.
- 10:09 EXP-067 vorab festgelegt (Pilot).
- 10:07 P2e eingefroren (zweiter Anlauf) und gestartet.
- 10:04 P2e-Probelauf deckt einen Klammerfehler in der Auswertung auf; behoben, Selbsttest erweitert.
- 09:59 N29 eingefroren, Probelauf durch den Lader ok, Block gestartet.
- 09:54 Codex: zwei Blocker in N29 (Auswahlregel, fehlende Datei im Code-Hash), behoben und nachgeprueft.
- 09:50 P2e festgelegt (Entwurf, Code getestet): P2d-Mass an frischen Seeds fuer mul 113 und add 97.
- 09:48 **EXP-066 (Exploration):** Der P2d-Effekt zeigt sich auch bei Multiplikation mod 113 (0.16) und Addition mod 97 (0.22), in allen 100 Seed-Werten positiv.
- 09:45 N29 festgelegt (Entwurf, Code getestet): Wechsel bei 25 gegen 50 Schritte, 20 frische Seeds, 4000 Schritte Nachtraining.
- 09:41 CPU-Programm neu gestartet (EXP-039 laeuft weiter).
