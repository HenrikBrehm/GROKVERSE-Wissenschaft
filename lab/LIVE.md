---
tags: [lab/live]
---
# LIVE: Laborsitzung 27 (beendet)

- **Sitzungsstart:** 2026-09-27 15:59 Berlin (13:59Z, vom Runner)
- **Deadline:** 2026-09-27 18:59 Berlin (16:59Z)
- **Zuletzt aktualisiert:** 16:44 Berlin (gemessen)
- **Run-Fenster:** zu bis 00:00: nur Denk-, Such- und Vorbereitungsarbeit.

## Gerade

**Sitzung beendet (16:44).** Naechster geplanter Start laut runner-state.json: **19:34 Berlin** (17:34Z), ausserhalb des Run-Fensters.

## Als Naechstes

Ab 00:00 laut [[STATE]]: Tests, EXP-040 (CPU, 2 Arbeiter), P2f, EXP-073/074/075, Gleichwertigkeit repro, EXP-078/077/079, dann R1, R3, P4, R2 (Befehle heute korrigiert). Fuer dich: [[paper/STATUS]] (neu: K4b-Deutung ist in der Literatur bekannt; K2/K4 weiter nicht gefunden).

## Verlauf dieser Sitzung

- 16:44 Sitzung beendet; alles committet.
- 16:45 Neueste arXiv-Grokking-Arbeiten gesichtet: nichts schraenkt K2/K4 ein.
- 16:42 Repro-Paket fast vollstaendig (K2, K2-Funktion alle Aufgaben, K4/K4b, K4c, K4d/e); fehlt D59 und P3-Zerlegung; alles ungetestet.
- 16:39 Neue Paper-Stellen unabhaengig geprueft, 6 Formulierungen korrigiert.
- 16:35 Repro-Paket: k2_function.py (P2d), k4b.py (N28), k4_resets.py (N29b/c) geschrieben und je unabhaengig geprueft; ungetestet, nicht fuer heute Nacht.
- 16:25 EXP-081 nach Pruefung umgebaut (2 Blocker gefunden und behoben, bevor Code existiert).
- 16:22 EXP-081 entworfen (Pilot, kein Code, Start fruehestens nach R3): trennt drei Kandidaten fuer die Uhr der Festlegung.
- 16:19 Literatur: Salah & Yevick, Sweeney, Pracher, Yang, Sevetlidis & Pavlidis geprueft; K4b-Deutung ist bekannt, K2/K4 weiter nicht gefunden.
- 16:15 R2/R3-Auswertung robuster (Fehler -> defekt statt Absturz, wie N29c).
- 16:13 Nacht-Befehle geprueft: 2 sichere Fehler behoben (GPU-Pfad in repro/README; --jobs ohne Waechter), R1-Seed-Obergrenze + Manifest-Entwurf, Thread-Budget (CPU 2 Arbeiter + max. 4 GPU). Agent hat einmal `python -c "1"` ausgefuehrt (No-op, vermerkt).
- 16:09 Paper Abschnitt 2 nach Quellpruefung korrigiert (9 Punkte).
- 16:07 N38: Adams Momentum-Schwanz (6.5-10.8 Schritte) passt zur gemessenen K4b-Verschiebung (6.5-9.6, EXP-059, post hoc); qualitativ bekannt (Xu 2026). Commit 26d4b82.
- 16:04 Paper Abschnitt 2 (Methoden) als Fliesstext; Pruefung laeuft.
- 16:00 Pruefagent fuer die Nacht-Befehle gestartet.
- 15:59 Sitzung gestartet; STATE, JOURNAL, STATUS gelesen; kein STOP, keine Python-Prozesse, Fenster zu (Exit 3).
