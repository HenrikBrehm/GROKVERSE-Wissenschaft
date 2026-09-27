---
tags: [lab/live]
---
# LIVE: Laborsitzung 20

- **Sitzungsstart:** 2026-09-27 01:29 Berlin (23:29Z, vom Runner)
- **Deadline:** 2026-09-27 04:29 Berlin (02:29Z)
- **Zuletzt aktualisiert:** 04:18 Berlin (gemessen)
- **Run-Fenster:** offen seit 02:25 (Freigabe des Nutzers, 03:00-Sperre aufgehoben), bis Sitzungsende 04:29.

## Gerade

**Sitzung beendet** (04:18). CPU-Laeufe (EXP-038) laufen noch bis 04:29 und werden dann vom Waechter beendet. Naechster geplanter Start: **05:04 Berlin** (runner-state.json).

## Als Naechstes

Naechste Sitzung (geplant 05:04 Berlin): CPU-Programm neu starten, Trainer an den eingefrorenen Code binden (B1), dann Bestaetigungsblock P1 einfrieren und auf der GPU rechnen.

## Verlauf dieser Sitzung

- 04:13 EXP-035 (CPU) ausgewertet, nur 3 Seeds auswertbar, noch nicht gedeutet.
- 04:01 Abschlussbericht im JOURNAL. LAB-Uebersicht korrigiert (Zeilen waren an falscher Stelle).
- 03:55 EXP-046: die drei staerksten Irreps sind immer eigene Ziele (10/10).
- 03:54 Codex-Nachpruefung: 1 Punkt offen (Trainer an eingefrorenen Code binden), P1 bleibt uneingefroren.
- 03:47 CPU-Programm mit 3 Arbeitern neu gestartet (Sperrfehler behoben).
- 03:45 Alle Codex-Punkte am Bestaetigungscode umgesetzt und getestet.
- 03:41 Codex prueft P1-Entwurf: 3 Blocker (u. a. Code nicht eingefroren). Selbst bestaetigt; nicht eingefroren.
- 03:40 **EXP-050: kohaerentes Maskenspektrum waehlt, M0 traegt aber auch** (Theorie erster Ordnung nur halb).
- 03:33 **EXP-045: Steuerung auch im MLP, bleibt nach dem Grokking** (10/10).
- 03:31 **EXP-044: fruehe Festlegung auch bei add 97 / mul 113** (10/10).
- 03:30 Entwurf fuer den Bestaetigungsblock P1 (50 frische Seeds, 4 Aufgaben), noch nicht eingefroren; Codex prueft.
- 03:28 Stichprobengroesse fuer P1 aus der Pilotstreuung: ~25-45 Seeds fuer add 113.
- 03:25 **EXP-052: vorab eingefrorene Vorhersage trifft in 4/4 neuen Faellen** (Split sagt Spektrum voraus).
- 03:22 **EXP-049: Steuerung auch im 4x breiteren Netz** (10/10).
- 03:10 **EXP-048: Steuerung auch bei nicht-modularer Addition** (10/10, p 0.001; Aufgabe selbst noch nicht gelernt).
- 03:10 EXP-055 (Nachfolger Funktionstest): Hauptdosis n. s.; bei Teildosen nutzen die Modelle die Zielfrequenzen staerker (10/10, nachtraeglich). Plan fuer saubere Bestaetigung notiert.
- 03:06 EXP-051: formal "nicht genutzt", aber Bodeneffekt (Eingriff zu klein, alle Verluste 0). Kein Beleg; Nachfolger noetig.
- 03:06 **EXP-047: Die Paarstruktur steuert, nicht die Token-Haeufigkeiten** (wie vorab aus der Theorie erwartet).
- 03:01 **EXP-046: Steuerung gilt auch in der Diedergruppe D59** (nicht-abelsch; 10/10, p 0.001).
- 02:56 **EXP-043: Steuerung ueber die Daten gilt auch bei add 97 und mul 113** (je 10/10 Seeds, p 0.001; Pilot).
- 02:56 CPU-Programm gestartet (Paket-B-Piloten).
- 02:53 GPU-001 bestanden: gleichwertig zur CPU, ~17x schneller, 8 Laeufe parallel am besten (~1600 kurze Laeufe/h).
- 02:49 Diagnoselauf mit venv-torch auf CPU abgebrochen (10x zu langsam), dokumentiert.
- 02:34 Nachtprogramm neu gestartet: Umgebung ok (torch 2.9.1+rocm, RX 7900 XT erkannt).
- 02:32 Erster Start scheiterte: Windows fand den venv-Python-Pfad mit / nicht. Behoben (absoluter Pfad).
- 02:30 Tests: 11/11 gruen, nachdem zwei Fehler im Testaufbau behoben waren (nicht im Code).
- 02:26 Waechter-Abnahme: A/B/C bestanden. Job-Objekt-Fehler gefunden und an die Nutzersitzung gemeldet, dort behoben.
- 02:25 Fenster offen (Waechter allowed: true; Nutzer hat die 03:00-Sperre aufgehoben).
- 01:34 Kontrolle: Auch Zufallssplits verdichten sich nach dem Grokking. Haltbar ist nur "kein Abklingen", eine Verstaerkung durch den Split nicht.
- 01:33 Nachrechnung EXP-016: Gepflanzte Frequenzen klingen nach dem Grokking nicht ab (Anteil 0.56 -> 0.82, 20/20). Gegenprobe zu Zhou et al.
- 01:31 Trockenlaeufe GPU- und CPU-Nachtprogramm: vollstaendig, nichts geschrieben.
- 01:30 Sitzung gestartet: Fenster zu (Exit 3), kein STOP, keine Python-Prozesse. Sitzung 19 endete 23:21Z.
