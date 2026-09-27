---
tags: [lab/live]
---
# LIVE: Laborsitzung 21

- **Sitzungsstart:** 2026-09-27 04:19 Berlin (02:19Z, vom Runner)
- **Deadline:** 2026-09-27 07:19 Berlin (05:19Z)
- **Zuletzt aktualisiert:** 06:24 Berlin (gemessen)
- **Run-Fenster:** offen (00:00-13:00), bindend ist die Sitzungsdeadline.

## Gerade

Codex prueft nachtraeglich die neue Trainer-Option (Adam-Reset) und greift die EXP-057-Deutung an. GPU frei. CPU: Paket-B-Piloten laufen weiter.

## Als Naechstes

Codex-Befunde einarbeiten, STATE + Abschlussbericht (Deadline 07:19).

## Verlauf dieser Sitzung

- 06:21 **EXP-057 (Pilot): Setzt man nur den Adam-Zustand zurueck, verschwindet das Gedaechtnis der ersten 25 Schritte fast ganz.** Ueberraschend; erst Kontrollen, dann Bestaetigung.
- 06:13 Zerlegung: Die fruehen Ziele tragen 20 % der Leistung (Zufall 9 %). Es gibt also echtes Erhalten plus langsameres Umlernen.
- 06:10 Codex: P3 gilt statistisch; "Festlegung im Netz" ist damit aber noch nicht bewiesen (enge Formulierung uebernommen).
- 06:04 **P3 BESTAETIGT** (30/30 frische Seeds): Nach nur 25 Schritten haelt das Netz ein Drittel seiner fruehen Frequenzwahl gegen 2000 Schritte auf voellig anderen Daten.
- 05:51 P1 als bestaetigte Kernaussage in FINDINGS (Wortlaut nach Codex-Pruefung: enge Fassung).
- 05:44 **P2 nicht auswertbar**: 3 von 50 Modellen waren nach 2000 Schritten noch nicht fertig generalisiert (Regel verlangte alle 50). Mein Designfehler; beschreibend schwaecher als im Pilot.
- 05:39 **P1 BESTAETIGT** in allen 4 Aufgaben (je 50/50 frische Seeds): konstruierte Daten steuern, welche Frequenzen das Netz lernt.
- 05:17 **P3 eingefroren** (f8adf45): Persistenz ohne gemeinsame Daten, 30 frische Seeds. Alle drei Bestaetigungen sind damit vor jedem Lauf festgelegt.
- 05:13 Codex prueft P3 zweimal; 8 Punkte uebernommen.
- 05:03 P3-Entwurf und Code fertig, an echten Pilotdaten geprueft.
- 04:59 Kontrolle: Ein blosser Gewichtsrest erklaert die Persistenz nicht (0.003-0.06 statt 0.34). Das Netz verstaerkt die fruehe Wahl selbst.
- 04:57 **EXP-056: Persistenz auch ohne gemeinsame Daten** (10/10 Seeds); Einfluss der Ueberlappung unklar (Pilot).
- 04:56 Bestaetigungsblock P1/P2 gestartet (420 Laeufe, GPU).
- 04:51 **EXP-038 (CPU): Festlegung ist doppelt vorhanden** - W_E allein oder der Rest des Netzes allein genuegt, 5/5 (Pilot).
- 04:49 Zwei echte Bestaetigungslaeufe als Test: laufen und sind korrekt an den Code gebunden.
- 04:46 **P1 und P2 eingefroren** (Manifest 733e829): 50 frische Seeds, 4 Aufgaben, Auswertung festgelegt, bevor ein Lauf existiert.
- 04:45 EXP-056 gestartet (P3-Pilot, Seeds 400-409, GPU).
- 04:43 EXP-056 vorab festgelegt: Ueberlappung 0/20/40 %, Wechsel nach 25 Schritten.
- 04:40 Codex-Pruefung P2: Test gewechselt (t-Test statt Vorzeichentest), Regeln geschaerft.
- 04:38 P2-Mass skalenfrei gemacht (log-Loss-Verhaeltnis), t-Test nachgeruestet.
- 04:33 Codex-Pruefung B1: 7 Punkte, alle uebernommen und getestet (u. a. Code-Pruefung waehrend des Laufs).
- 04:31 P2-Entwurf und Auswertecode geschrieben (Loss bei halber Dosis, 50 frische Modelle aus P1).
- 04:25 EXP-035 eingeordnet: Warmup verzoegert die Festlegung (3/3 Seeds, nur Pilot).
- 04:24 B1 gebaut: jeder Bestaetigungslauf wird an den eingefrorenen Code gebunden (Selbsttests gruen).
- 04:20 CPU-Programm neu gestartet (3 Arbeiter).
- 04:19 Sitzung gestartet: Fenster offen, kein STOP, keine Python-Prozesse.
