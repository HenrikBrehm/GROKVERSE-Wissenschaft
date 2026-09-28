---
tags: [lab/live]
---
# LIVE: Laborsitzung 45

- **Sitzungsstart:** 2026-09-28 21:49 Berlin (19:49Z, vom Runner)
- **Deadline:** 2026-09-29 00:49 Berlin (22:49Z)
- **Zuletzt aktualisiert:** 00:03 Berlin
- **Run-Fenster:** offen seit 23:59 (durchgehend bis 06.10.); Grenze dieser Sitzung 00:49.

## Gerade

R10 rechnet (8 GPU-Worker, ≈ 2 min je Lauf; wird in der nächsten Sitzung fertig). RFM-Reproduktionstest (p = 61) läuft auf der CPU.

## Als Nächstes

RFM-Tor prüfen → RFM-Läufe; Nanda unabhängig nachrechnen; vor 00:49 Stand sichern. Nächste Sitzung: R10 fertig → Auswertung → Nachrechnung → L0-Patch ([[NACHT_2026-09-29]]).

## Verlauf dieser Sitzung

- 00:03 **Nanda (Regel 20c): in allen vier Aufgaben tragen die gesteuerten Frequenzen die Lösung** (je 20/20; auf eigene Ziele beschränkt Fehler ≈ 0, auf fremde 11–18). RFM-Selbsttest: Testfehler diagnostiziert (Matrixwurzel verstärkt Rundung), korrigiert.
- 23:59 Fenster offen: R10-Queue und Nanda gestartet.
- 22:56 Paper: Konsistenzprüfung nach allen heutigen Änderungen (7 Punkte behoben, alle Zahlen stimmen); Abb. 1 als zweiteiliges Bild.
- 22:48 Vorhersager (Maske gegen Init-Energie) an R4 kalibriert und unabhängig bestätigt: Maske 0.34, Init-Energie 0.19, Zufall 0.09; Gewicht eingefroren für den Test an unberührten Läufen heute Nacht.
- 22:40 L0: Schalter CONFLICT_B16 + Auswertung (Standard aus, Joblisten unverändert). Vorab-Vorhersage an 18 unberührten Machbarkeitsläufen: Zufallssplits folgen ihrer eigenen Maske auch unter Minibatch.
- 22:37 Vor dem Lauf geprüft: Nanda-Skript (Hash-Prüfung ergänzt) und EXP-103 (zweite Vergleichsregel) – keine Blocker.
- 22:27 Paper: Tabelle 1 mit allen 19 Bestätigungsblöcken; Zitate Gromov/Zhong ergänzt; Erklärung für den Nutzer (29.09.) um die Abendbefunde ergänzt.
- 22:23 R4-Befund unabhängig bestätigt (auch kein Artefakt bei Schritt 0, Placebo null); in FINDINGS (Hinweis) und Paper §3 als Nachauswertung.
- 22:20 R4 nachträglich (Exploration): eigenes Maskenspektrum sagt gelernte Frequenzen voraus, Kontrast 0.54 [0.52, 0.57] (Spearman, Schritt 2000), 60/60; Nachrechnung läuft.
- 22:18 Simulierte Gutachter-Prüfung umgesetzt: Textkorrekturen; R5-RMST 5.8/6.9 (post hoc); L0-Machbarkeit um Batch 16 erweitert (nur dort kann die Reihenfolge laut erster Ordnung wirken).
- 22:09 EXP-104 vor dem Lauf geprüft: 2 Blocker gefunden und behoben (Splitgröße 3842 braucht `--train-frac 0.3009`; Suchmuster der Auswertung), gemeinsame Testmenge je Seed. EXP-105 (Leiter Stufe 2) als Entwurf.
- 22:03 EXP-104 vorbereitet (12 GPU-Läufe, 2 Seeds, Exploration, nach L0): Steuern flache Splits, und blockiert ihre Symmetrie das Grokking?
- 22:02 N53, Nachtrag: 10 Tauschzüge (< 1 % der Paare) brechen die Symmetrie, Häufigkeiten bleiben exakt flach, Zielanteil 0.64–0.73. Die Zugzahl regelt die Steuerstärke.
- 22:00 N53 (neu, reine Rechnung): Split {a − λb ∈ D} hat exakt gleich viele a, b und c und trotzdem Zielanteil 0.66–0.72 (P1: 0.17–0.19). Risiko: Verschiebungssymmetrie (vgl. Tomàs Bernal et al.).
- 21:58 Abb.-1-Unterschrift: das fehlende Ziel 25 hat den kleinsten Maskenanteil der fünf Ziele.
- 21:57 R10-Deutungssätze je Ausgang VOR dem Ergebnis festgelegt ([[paper/R10_DEUTUNGEN]]).
- 21:56 Bildunterschriften unabhängig geprüft: 2 Fehler in Abb. 3 (π/C über beide Richtungen gemittelt) korrigiert, Abb. 3 neu gezeichnet.
- 21:54 Literatur L0-Umfeld: Hancock 2026 (Online-Batch-Auswahl ändert die Grokking-Zeit kaum; keine Frequenzen), schränkt nichts ein.
- 21:53 Paper: Bildunterschriften Abb. 1–4 geschrieben; Titel Abb. 3 korrigiert.
- 21:51 Nachtstart geprüft: R10-Code seit dem Einfrieren unverändert, gebundene Läufe werden übersprungen.
- 21:50 Sitzung gestartet; kein STOP, keine Python-Prozesse, Fenster zu.
